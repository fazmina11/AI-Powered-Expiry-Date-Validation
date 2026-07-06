# Legacy Auth — Preserved for Firebase Re-integration

This folder was created during the **temporary auth removal refactor** (2026-07-05).

## Contents

| File | Original Path | Description |
|------|--------------|-------------|
| `auth_routes.py` | `app/routes/auth.py` | FastAPI routes: POST /login, POST /register, GET /me |
| `auth_service.py` | `app/services/auth.py` | JWT generation, bcrypt hashing, get_current_user() |
| `user_schema.py` | `app/schemas/user.py` | Pydantic: UserCreate, UserOut, Token |
| `user_model.py` | `app/models/user.py` | SQLAlchemy User model (users table — NOT deleted) |

## Why This Was Removed

Authentication is being **rebuilt using Firebase Admin SDK**.
The current backend JWT + bcrypt system is being replaced by Firebase ID Token verification.

## How To Restore

1. Move files back to their original paths.
2. Re-add to `requirements.txt`: `passlib[bcrypt]==1.7.4`, `python-jose[cryptography]==3.3.0`
3. Re-add the `auth` router to `main.py`.
4. Re-add `Depends(get_current_user)` to protected business routes.

## IMPORTANT

The `users` database table is **NOT deleted**. It is preserved for Firebase UID mapping.
