"""
Run with: python -m app.create_db
Creates all tables and (optionally) a default admin account for first login.
"""
from app.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password
import app.models  # noqa: F401


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@insightflow.ai").first()
        if not existing:
            admin = User(
                full_name="Admin",
                email="admin@insightflow.ai",
                hashed_password=hash_password("ChangeMe123!"),
                role=UserRole.admin,
                is_verified=True,
            )
            db.add(admin)
            db.commit()
            print("Created default admin: admin@insightflow.ai / ChangeMe123!  (change this password immediately)")
        else:
            print("Admin user already exists, skipping.")
    finally:
        db.close()

    print("Done.")


if __name__ == "__main__":
    main()
