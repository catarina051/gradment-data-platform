# Phase 2.5 — Frontend Telemetry Integration Guide

**System:** Private GradMent Frontend (`gradment_front`, Next.js SPA) → Backend REST Ingestion (`GradMentBack`, `POST /api/telemetry/event`)  
**Target Table:** `analytics_events` (MySQL)  
**Client Telemetry Module:** `src/lib/telemetry.ts`  
**Client Listener Component:** `src/components/TelemetryListener.tsx`  
**Scope:** Client-Side Events (`app_opened`, `screen_viewed`, `frontend_error_occurred`)  

---

## 1. Architecture & Ingestion Flow

Phase 2.5 completes the client-to-backend bridge by connecting the Next.js SPA UI directly to the `POST /api/telemetry/event` endpoint created in Phase 2:

```
[ Next.js React UI (gradment_front) ]
   ├── Root Layout Mount ─────────> trackAppOpened() ──────────────┐
   ├── Router Path Change ────────> trackScreenViewed() ───────────┼──> POST /api/telemetry/event ──> EventCollector ──> analytics_events
   └── Global Error Listener ────> trackFrontendError() ───────────┘
```

> [!IMPORTANT]
> **Session Anchor Resolved:** With Phase 2.5 completed, `app_opened` now fires on application launch per browser tab session. This anchors `session_id` and enables accurate DAU, WAU, MAU, and session boundary aggregation for Phase 3 and Phase 4.

---

## 2. Session ID Management & De-duplication

1. **Persistent Tab Session ID (`session_id`)**:
   - Stored in browser `sessionStorage` under key `gradment_analytics_session_id`.
   - Uses `crypto.randomUUID()` with fallback generator.
   - Remains constant for the lifetime of a browser tab.

2. **Single-Trigger `app_opened` Safeguard**:
   - `trackAppOpened()` checks `sessionStorage` key `gradment_app_opened_fired`.
   - Ensures `app_opened` fires exactly once when a new tab session starts, preventing over-counting on component re-renders.

3. **Route Navigation `screen_viewed`**:
   - `TelemetryListener` uses `usePathname` from `next/navigation`.
   - Tracks `screen_viewed` strictly on path changes, tracking `screen_name`, `feature_key`, and `referrer_screen`.

---

## 3. Exception Safety Guarantee

All telemetry calls in `src/lib/telemetry.ts` wrap `fetch()` calls in `try / catch` blocks. Network timeouts, CORS errors, or endpoint failures swallow errors gracefully and log warnings in development mode, guaranteeing that **telemetry issues never disrupt the student UI or block page rendering**.

---

## 4. Verification & Testing

- TypeScript compilation (`npx tsc --noEmit`) in `gradment_front`: **0 errors**.
- Root layout integration: `<TelemetryListener />` mounted inside `RootLayout` (`src/app/(app)/layout.tsx`).
- Code committed in `gradment_front` on branch `feature/analytics-frontend-telemetry` (commit `e33b333`).
