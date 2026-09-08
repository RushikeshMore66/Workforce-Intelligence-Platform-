# Frontend ↔ Backend Integration Architecture

## 1. Environment Variables
- `NEXT_PUBLIC_API_URL`: Configures the base URL for the backend API.
  - Development Default: `http://localhost:8000`
  - The API client automatically appends `/api/v1` to this URL.
- `NEXT_PUBLIC_USE_MOCK`: Toggles between the Mock implementation (`true`) and the real FastAPI integration (`false`).

## 2. API Client Architecture
- **Centralized Client (`src/lib/api/client.ts`)**: The sole entry point for HTTP requests. It manages URL construction, headers, timeouts, and JSON serialization.
- **Path**: `src/lib/api/`
- **Request Wrapping**: Pre-appends `NEXT_PUBLIC_API_URL` and `/api/v1`.
- **Snake to Camel Case**: Intercepts JSON responses and automatically converts Python's `snake_case` keys to TypeScript's `camelCase` conventions.

## 3. Authentication Flow
- **Token Storage**: Currently uses `localStorage` (via `src/lib/auth/storage.ts`) for storing JWTs as a temporary mechanism.
- **Interception**: The API client pulls the token via `getAuthHeaders()` and attaches it as a `Bearer` token in the `Authorization` header on all requests.
- **Login**: `POST /auth/login` retrieves the JWT.
- **Session Identity**: `GET /auth/me` populates the user context.

## 4. Error Handling
- **Non-2xx Responses**: Captured and wrapped in `ApiRequestError`.
- **401 Unauthorized**: Handled centrally. The API client calls `onUnauthorized` callback (registered by the auth provider) to clear the session and redirect the user to `/login`.
- **403 Forbidden / 404 Not Found / 422 Unprocessable Entity**: Parsed into detail strings and presented to the UI via error boundaries or form-level error states.

## 5. Mock / Real Switch
- Repositories in `src/lib/api/` (e.g. `auth.ts`, `projects.ts`) read `process.env.NEXT_PUBLIC_USE_MOCK`.
- If `true`, they return data from `src/lib/api/mock/`.
- If `false`, they invoke `apiClient`.

## 6. CORS
- Configured in the FastAPI backend (`backend/app/config.py`).
- Development origins allowed: `http://localhost:3000` and `http://127.0.0.1:3000`.

## 7. Local Development Startup Order
1. **Database**: Ensure PostgreSQL (or local fallback) is running.
2. **Backend**: Run `alembic upgrade head`, then start the backend with `uvicorn app.main:app --reload --port 8000`.
3. **Frontend**: Start Next.js with `npm run dev`.
