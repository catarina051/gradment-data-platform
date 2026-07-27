# Phase 2 — Backend Event Instrumentation Guide

**System:** GradMent Backend (CodeIgniter 4) → GradMent Data Platform  
**Target Table:** `analytics_events` (Production MySQL)  
**Service Class:** `App\Services\EventCollector`  
**Scope:** 18 Critical & High Priority Events (Medium/Low events remain as stubs in `events_catalog.yml`)  

---

## 1. Architecture & Exception Safety Principle

The backend instrumentation uses a **fire-and-forget, decoupled service architecture**:

```
Controller Action (e.g. AvaliacaoController::salvar)
   ├── 1. Execute normal business logic (save rating to MySQL)
   ├── 2. On SUCCESS only: EventCollector::track('discipline_rated', $payload)
   │     ├── Normalizes 'docente' string fields (trim + space collapse)
   │     ├── Generates UUID v4 event_id & session_id
   │     ├── Wraps in try/catch block (swallows all exceptions, logs silently)
   │     └── Writes 1 row to `analytics_events` table
   └── 3. Return normal HTTP response to student
```

> [!IMPORTANT]
> **Exception Safety Guarantee:** `EventCollector::track()` is wrapped entirely in a `try/catch (\Throwable $e)` block. An error during event emission (e.g. database timeout or disk full) will **never** throw an exception into calling controller code or break the student's request.

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

## 3. List of 18 Instrumented Events (Critical & High Priority)

| Priority | Event Name | Category | Controller Hook Point | Key Payload Attributes |
|---|---|---|---|---|
| **Critical** | `user_registered` | Auth & Reg | `RegisterController::create` | `university_id`, `course_id`, `registration_source` |
| **Critical** | `login_succeeded` | Auth & Reg | `AuthController::login` (success) | `method` |
| **Critical** | `login_failed` | Auth & Reg | `AuthController::login` (failed) | `method`, `failure_reason` |
| **Critical** | `discipline_rated` | Ratings | `AvaliacaoController::salvar` | `discipline_id`, `docente`, `academic_period`, `oferta_id`, `dificuldade`, `esforco`, `passou` |
| **Critical** | `professor_rated` | Ratings | `AvaliacaoController::avaliarDocente` | `docente`, `discipline_id`, `academic_period`, `didatica_score` |
| **Critical** | `api_error_occurred` | Errors | `BaseController::handleException` | `error_code`, `endpoint`, `http_status` |
| **Critical** | `frontend_error_occurred` | Errors | `TelemetryController::reportError` | `error_name`, `screen_name` |
| **Critical** | `app_opened` | System | `InitController::bootstrap` | `is_cold_start`, `platform` |
| **High** | `registration_failed` | Auth & Reg | `RegisterController::create` (fail) | `failure_reason` |
| **High** | `screen_viewed` | Navigation | `NavigationController::trackView` | `screen_name`, `feature_key`, `referrer_screen` |
| **High** | `search_performed` | Search | `SearchController::query` | `query_length`, `result_count`, `search_scope` |
| **High** | `search_result_opened` | Search | `SearchController::openResult` | `search_scope`, `result_position` |
| **High** | `material_downloaded` | Downloads | `MaterialController::download` | `material_type`, `course_id`, `docente`, `academic_period` |
| **High** | `material_uploaded` | Uploads | `MaterialController::upload` (success)| `material_type`, `course_id`, `file_size_kb`, `academic_period` |
| **High** | `upload_failed` | Uploads | `MaterialController::upload` (failed) | `material_type`, `failure_reason` |
| **High** | `planning_session_started` | Planning | `PlanejamentoController::iniciar` | `academic_period` |
| **High** | `planning_session_completed`| Planning | `PlanejamentoController::salvar` | `courses_planned`, `academic_period`, `had_conflicts_resolved` |
| **High** | `validation_error_occurred` | Errors | `BaseController::onValidationError` | `form_name`, `failed_fields_count` |

*(Note: The 21 Medium & Low priority events remain as valid TODO stubs in `events_catalog.yml` for future implementation).*

---

## 4. CodeIgniter Controller Instrumentation Example

```php
use App\Services\EventCollector;

class AvaliacaoController extends BaseController
{
    public function salvar()
    {
        // 1. Business Logic
        $model = new AvaliacaoDisciplinaModel();
        $saved = $model->insert($data);

        if ($saved) {
            // 2. Event Emission (Non-blocking)
            EventCollector::track('discipline_rated', [
                'discipline_id'   => (int)$this->request->getPost('disciplina_id'),
                'docente'         => $this->request->getPost('docente'), // Auto-normalized by EventCollector
                'academic_period' => $this->request->getPost('ano_periodo') ?? '2026.1',
                'oferta_id'       => $this->request->getPost('oferta_id') ? (int)$this->request->getPost('oferta_id') : null,
                'dificuldade'     => (int)$this->request->getPost('dificuldade'),
                'esforco'         => (int)$this->request->getPost('esforco'),
                'passou'          => (bool)$this->request->getPost('passou'),
                'has_comment'     => !empty($this->request->getPost('comentario')),
            ]);

            return $this->response->setJSON(['status' => 'success']);
        }
    }
}
```

---

## 5. Verification & Testing

- Unit test suite: `backend/tests/unit/EventCollectorTest.php`
- Run tests via PHPUnit:
  ```bash
  vendor/bin/phpunit backend/tests/unit/EventCollectorTest.php
  ```
