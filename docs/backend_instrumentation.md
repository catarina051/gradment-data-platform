# Phase 2 — Backend Event Instrumentation Guide

**System:** Private GradMent Backend (`GradMentBack`) → Data Platform  
**Target Table:** `analytics_events` (MySQL)  
**Service Class:** `App\Services\EventCollector`  
**Ingest Endpoint:** `POST /api/telemetry/event` (`App\Controllers\TelemetryController`)  
**Scope:** 18 Critical & High Priority Events (15 backend-native + 3 REST telemetry ingest)  

---

## 1. Architecture & Ingestion Strategy

Phase 2 implements a dual-channel event emission architecture:

```
[ Backend Controllers (CodeIgniter) ]
   └── 15 Native Events (Auth, Ratings, Downloads, Uploads, Errors)
          └── EventCollector::track($name, $payload) ──> [ analytics_events (MySQL) ]

[ Frontend Next.js Client (Phase 2.5) ]
   └── 3 Client-Side Events (app_opened, screen_viewed, frontend_error_occurred)
          └── POST /api/telemetry/event (TelemetryController)
                 └── EventCollector::track($name, $payload) ──> [ analytics_events (MySQL) ]
```

> [!IMPORTANT]
> **Practical Consequence & Phase 2.5 Integration Note:**
> Client-side events (`app_opened` for session anchor, `screen_viewed` on SPA route transition, and `frontend_error_occurred` on React Error Boundary) cannot originate inside PHP controller logic. In Phase 2, the REST API ingestion endpoint `POST /api/telemetry/event` (`TelemetryController`) was built in `GradMentBack` to receive these payloads.
> Until **Phase 2.5 (Frontend Telemetry Integration)** is executed to wire `gradment_front` (Next.js) to this endpoint, `analytics_events` will not receive live client-side session anchor rows (`app_opened`). Phase 2.5 is formally scheduled as the next phase to complete this client-to-backend bridge.

---

## 2. String Normalization for `docente` Attribute

As established in Phase 0 & Phase 1, `ofertas_disciplinas.docente` is a free-text string field in the operational database (no numeric `professor_id` foreign key exists).

To prevent whitespace fragmentation before data reaches the warehouse, `EventCollector::normalizePayload()` performs lightweight normalization:

```php
$cleaned = trim($val);
$cleaned = preg_replace('/\s+/', ' ', $cleaned);
```

- Input: `"   Prof.   João   Carlos   Silva  "`
- Emitted Payload: `"Prof. João Carlos Silva"`

Full fuzzy matching and entity deduplication are performed downstream in Phase 3 when building `dim_professors`.

---

## 3. Complete Breakdown of All 18 Critical & High Events

| Priority | Event Name | Category | Ingestion Channel / Controller Hook | Key Payload Attributes |
|---|---|---|---|---|
| **Critical** | `user_registered` | Auth & Reg | `AutenticacaoController::cadastro` | `university_id`, `course_id`, `registration_source` |
| **Critical** | `login_succeeded` | Auth & Reg | `AutenticacaoController::login` (success) | `method` |
| **Critical** | `login_failed` | Auth & Reg | `AutenticacaoController::login` (failed) | `method`, `failure_reason` |
| **Critical** | `discipline_rated` | Ratings | `AvaliacaoDisciplinaController::criar` | `discipline_id`, `docente`, `academic_period`, `oferta_id`, `dificuldade`, `esforco`, `passou` |
| **Critical** | `professor_rated` | Ratings | `AvaliacaoDisciplinaController::criar` | `docente`, `discipline_id`, `academic_period` |
| **Critical** | `api_error_occurred` | Errors | `ApiResponseTrait::respondErroCatalogado` (5xx) | `error_code`, `endpoint`, `http_status` |
| **Critical** | `frontend_error_occurred` | Errors | `POST /api/telemetry/event` (Ingest — Phase 2.5) | `error_name`, `screen_name` |
| **Critical** | `app_opened` | System | `POST /api/telemetry/event` (Ingest — Phase 2.5) | `is_cold_start`, `platform` |
| **High** | `registration_failed` | Auth & Reg | `AutenticacaoController::cadastro` (fail) | `failure_reason` |
| **High** | `screen_viewed` | Navigation | `POST /api/telemetry/event` (Ingest — Phase 2.5) | `screen_name`, `feature_key`, `referrer_screen` |
| **High** | `search_performed` | Search | `MateriaController::listar` | `query_length`, `result_count`, `search_scope` |
| **High** | `search_result_opened` | Search | `MateriaController::exibir` | `search_scope`, `result_position` |
| **High** | `material_downloaded` | Downloads | `MateriaArquivoController::obterLink` | `material_type`, `course_id`, `docente`, `academic_period` |
| **High** | `material_uploaded` | Uploads | `MateriaArquivoController::criar` | `material_type`, `course_id`, `file_size_kb`, `academic_period` |
| **High** | `upload_failed` | Uploads | `MateriaArquivoController::criar` (error) | `material_type`, `failure_reason` |
| **High** | `planning_session_started` | Planning | `CurriculoController::exibir` | `academic_period` |
| **High** | `planning_session_completed`| Planning | `CurriculoController::exibir` | `courses_planned`, `academic_period`, `had_conflicts_resolved` |
| **High** | `validation_error_occurred` | Errors | `ApiResponseTrait::respondErroValidacao` | `form_name`, `failed_fields_count` |

*(Note: The 21 Medium & Low priority events remain as valid TODO stubs in `events_catalog.yml` for future implementation).*

---

## 4. REST Telemetry Ingest Controller Implementation (`GradMentBack`)

```php
namespace App\Controllers;

use App\Services\EventCollector;

class TelemetryController extends BaseController
{
    public function receiveEvent()
    {
        $data = $this->request->getJSON(true) ?? $this->request->getPost();
        $eventName = (string) ($data['event_name'] ?? '');
        $payload   = is_array($data['payload'] ?? null) ? $data['payload'] : [];
        $sessionId = isset($data['session_id']) ? (string)$data['session_id'] : null;
        $userId    = isset($this->request->usuarioId) ? (int)$this->request->usuarioId : null;

        $ok = EventCollector::track($eventName, $payload, $userId, $sessionId);
        return $this->respondSucesso('Telemetry event recorded.', ['tracked' => $ok], 200);
    }
}
```

---

## 5. Verification & Testing

- Unit test suite in `GradMentBack`: `tests/unit/EventCollectorTest.php`
- Real PHPUnit Test Run Output:
  ```
  PHPUnit 10.5.63 by Sebastian Bergmann and contributors.
  Runtime:       PHP 8.2.12
  Tests: 4, Assertions: 7, PHPUnit Warnings: 1.
  ```
