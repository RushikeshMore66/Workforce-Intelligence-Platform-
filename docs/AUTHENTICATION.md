# Authentication Architecture

This document describes the Phase 4 Real JWT Authentication & Session Integration implementation.

## 1. Backend Authentication Contract

The backend uses FastAPI's `OAuth2PasswordBearer` to enforce authentication.
- **Login Endpoint**: `POST /api/v1/auth/login`
- **Request Schema**: `LoginRequest` (requires `email` and `password`).
- **Response Schema**: `TokenResponse` (returns `access_token`, `token_type` = "bearer", `expires_in`).
- **Token Format**: Standard JWT.
- **Protected Routes**: Require the header `Authorization: Bearer <token>`.
- **Refresh Tokens**: Not implemented in backend.
- **HttpOnly Cookies**: Not supported by backend.
- **Current User**: `GET /api/v1/auth/me` validates the token and returns `CurrentUserOut`.

## 2. Token Storage Architecture & Tradeoffs

Because the backend strictly requires `Authorization: Bearer <token>` and does not provide an HttpOnly secure cookie middleware, the frontend must persist the token in the browser (`localStorage`) to maintain session state across full page reloads.

**Security Tradeoff**: Storing JWTs in `localStorage` makes them accessible to JavaScript, presenting an XSS vulnerability risk. 
**Mitigation & Future Proofing**: To minimize scattered risks, token access is **strictly isolated** to `src/lib/auth/storage.ts`. Components and UI elements never read from or write to `localStorage`. If the backend introduces secure HttpOnly cookie support in the future, the frontend can be migrated safely by only modifying this single `storage.ts` module, with zero changes required in components.

## 3. AuthProvider Lifecycle

`AuthProvider` (`src/lib/auth/AuthProvider.tsx`) is the central state owner for authentication.
1. On application mount, it initializes in an `isLoading=true` state.
2. It attempts to fetch `GET /api/v1/auth/me` (using the underlying `storage.ts` token via `apiClient`).
3. If successful, `user` state is populated.
4. If unauthorized or failed, the `user` state is set to `null`.
5. `isLoading` is set to `false`, unblocking the application render tree.

## 4. API Client Integration & 401 Handling

The central `apiClient` (`src/lib/api/client.ts`) attaches the Bearer token to all requests.
When the API client receives a `401 Unauthorized` response:
- It intercepts the error.
- It fires a globally registered callback `onUnauthorized()`.
- The `AuthProvider` (which registers this callback on mount) handles the event by clearing its internal user state and invoking `authApi.logout()`.
- The `ProtectedRoute` component reacts to the state change and automatically redirects the user to `/login`.
- This callback approach prevents circular dependencies between the API client and React contexts.

## 5. Route Protection

The `ProtectedRoute` wrapper (`src/components/auth/ProtectedRoute.tsx`) secures application layouts.
- It reads `useAuth()`.
- If `isLoading` is true, a full-screen loading spinner is displayed to prevent flashing protected content.
- If `isAuthenticated` is false, it uses `useRouter` to redirect the user to `/login`, appending a `?next=` query parameter containing the URL they attempted to access.
- Only the `/login` route is public. The main application layout (`(app)/layout.tsx`) is wrapped entirely in `ProtectedRoute`.

## 6. Login Flow

The `/login` route provides a premium authentication UI.
1. The user inputs their email and password.
2. `useAuth().login()` is called, which calls `POST /api/v1/auth/login`.
3. The token is stored in `storage.ts`.
4. `GET /api/v1/auth/me` is fetched, populating the user context.
5. `ProtectedRoute` observes the `isAuthenticated` transition and allows navigation.
6. The login page redirects the user to their `?next=` return URL (or `/dashboard` by default). Note: External URLs are rejected to prevent Open Redirect attacks.

## 7. Logout Behavior

Logout simply:
- Clears the token from `storage.ts`.
- Clears the `user` state in `AuthProvider`.
- Redirects to `/login`.
*(No backend `/logout` endpoint exists).*

## 8. Mock Mode Behavior

When `NEXT_PUBLIC_USE_MOCK=true`, the `auth.ts` service intercepts the login call and validates against hardcoded mock credentials (`rajesh.mehta@apexsoftware.in` / `password`). It then sets a mock JWT and returns the mock user profile. The UI components remain completely agnostic to this transition.

## 9. Security Limitations & Phase 5 Readiness

- **No HttpOnly Cookies**: Discussed in section 2.
- **Frontend Protection Only**: `ProtectedRoute` only hides UI routes; actual security is enforced by backend API endpoints verifying the JWT.
- **No RBAC Yet**: Phase 4 focuses entirely on authentication (Who are you?). Phase 5 will implement Role-Based Access Control (What are you allowed to do?), reading the `role` claims and enforcing permissions.
