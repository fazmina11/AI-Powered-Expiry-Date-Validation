"""
services/auth.py — DISABLED (auth-free development mode)

This file is a stub. The original auth service has been preserved in:
  app/legacy/auth/auth_service.py

Contents of the original file:
  - get_password_hash()      (passlib / bcrypt)
  - verify_password()        (passlib / bcrypt)
  - create_access_token()    (python-jose JWT)
  - get_current_user()       (FastAPI dependency — OAuth2PasswordBearer)
  - oauth2_scheme            (OAuth2PasswordBearer instance)

None of these are active during auth-free development.
They will be replaced by firebase_admin.verify_id_token() when
Firebase authentication is re-integrated.

DO NOT import passlib or python-jose here — they will be removed
from requirements.txt to keep the environment lean.
"""

# No functions exported — this module is intentionally empty during dev.
