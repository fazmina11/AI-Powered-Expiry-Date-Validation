from app.routes.auth import login
from app.database import SessionLocal
from app.schemas.auth import UserCreate
import traceback

try:
    db = SessionLocal()
    form_data = UserCreate(email='test@example.com', password='wrong')
    print(login(form_data, db))
except Exception as e:
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()
