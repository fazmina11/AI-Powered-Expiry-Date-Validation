from app.deps import get_current_user
from app.database import SessionLocal
from fastapi.security import HTTPAuthorizationCredentials
from app.services.auth import create_access_token
import traceback

credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials=create_access_token({'sub':'demo@example.com'}))
db = SessionLocal()
try:
    result = get_current_user(credentials=credentials, db=db)
    print(result)
except Exception as e:
    traceback.print_exc()
finally:
    db.close()
