# pharma-be

Backend API construido con FastAPI + Django ORM, desplegado en AWS Lambda via Mangum.

## Flujo de autenticación

```
FRONTEND                        FASTAPI BACKEND                    AWS COGNITO
   │                                   │                                │
   │──── POST /auth/register/ ────────►│                                │
   │     {email, password, ...}        │──── sign_up() ────────────────►│
   │                                   │──── admin_confirm_sign_up() ──►│
   │                                   │──── INSERT user (DB) ──────────┤
   │◄─── 201 {user_id, email, ...} ───│                                │
   │                                   │                                │
   │──── POST /auth/login/ ───────────►│                                │
   │     {email, password}             │──── admin_initiate_auth() ────►│
   │                                   │◄─── {AccessToken,              │
   │                                   │      IdToken,                  │
   │                                   │      RefreshToken} ────────────│
   │◄─── 200 {access_token,           │                                │
   │          id_token,                │                                │
   │          refresh_token,           │                                │
   │          expires_in} ────────────│                                │
   │                                   │                                │
   │  [guarda tokens en memoria]       │                                │
   │                                   │                                │
   │──── GET /users/ ─────────────────►│                                │
   │     Authorization: Bearer <JWT>   │                                │
   │                                   │──── verificar JWT ────────────►│
   │                                   │     (JWKS público de Cognito)  │
   │                                   │◄─── válido / inválido ─────────│
   │◄─── 200 {users} / 401 ───────────│                                │
   │                                   │                                │
   │──── POST /auth/refresh/ ─────────►│                                │
   │     {email, refresh_token}        │──── admin_initiate_auth() ────►│
   │                                   │     (REFRESH_TOKEN_AUTH)       │
   │◄─── 200 {access_token nuevo} ────│◄─── {AccessToken nuevo} ───────│
```

### Endpoints públicos

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register/` | Crea usuario en Cognito y en DB |
| POST | `/auth/login/` | Retorna `access_token`, `id_token`, `refresh_token` |
| POST | `/auth/refresh/` | Renueva el `access_token` con el `refresh_token` |

### Endpoints protegidos

Requieren header `Authorization: Bearer <access_token>`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/users/` | Lista usuarios paginados |
| POST | `/users/role/` | Asigna rol a un usuario |
| GET | `/users/role/` | Lista roles paginados |
| POST | `/users/permission/` | Asigna permiso a un rol |
| GET | `/users/permission/` | Lista permisos paginados |

### Variables de entorno requeridas

```env
STAGE=local
DEBUG=true
DATABASE=sqlite
DEPLOY_REGION=us-east-1
COGNITO_USER_POOL_ID=<user-pool-id>
COGNITO_CLIENT_ID=<client-id>
COGNITO_CLIENT_SECRET=<client-secret>
```
