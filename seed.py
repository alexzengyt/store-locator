from app.database import SessionLocal
from app.models import User
from app.utils import hash_password

def seed_users():
    db = SessionLocal()
    
    users = [
        User(email="admin@test.com", username="admin", hash_password=hash_password("AdminTest123!"), role="admin"),
        User(email="marketer@test.com", username="marketer", hash_password=hash_password("MarketerTest123!"), role="marketer"),
        User(email="viewer@test.com", username="viewer", hash_password=hash_password("ViewerTest123!"), role="viewer"),
    ]
    
    for user in users:
        existing = db.query(User).filter(User.email == user.email).first()
        if not existing:
            db.add(user)
    
    db.commit()
    db.close()
    print("Users seeded successfully")

if __name__ == "__main__":
    seed_users()