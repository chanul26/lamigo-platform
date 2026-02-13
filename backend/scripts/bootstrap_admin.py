#!/usr/bin/env python3
"""
Bootstrap the LamiGo Multi-Tenant system.

Creates a Firebase user (admin@citypack.lk), an Organization (CityPack),
and a User record linking the Firebase UID to the org with role SUPER_ADMIN.
On database failure, the Firebase user is removed to avoid ghost accounts.

Usage (from backend/):
    python scripts/bootstrap_admin.py
"""
import os
import secrets
import sys
from pathlib import Path
from typing import Optional

# Ensure backend root is on path and load .env from backend/
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
os.chdir(BACKEND_ROOT)

from dotenv import load_dotenv

load_dotenv(BACKEND_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
ADMIN_EMAIL = "admin@citypack.lk"


def main() -> None:
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL is not set in .env", file=sys.stderr)
        sys.exit(1)

    # Resolve path relative to backend root so it works from any cwd
    raw_path = (FIREBASE_SERVICE_ACCOUNT_PATH or "").strip().strip('"\'')
    if not raw_path:
        print(
            "ERROR: FIREBASE_SERVICE_ACCOUNT_PATH is not set in .env\n"
            "  Set it in backend/.env, e.g.: FIREBASE_SERVICE_ACCOUNT_PATH=config/serviceAccountKey.json",
            file=sys.stderr,
        )
        sys.exit(1)
    resolved_path = Path(os.path.expanduser(raw_path))
    if not resolved_path.is_absolute():
        resolved_path = (BACKEND_ROOT / resolved_path).resolve()
    if not resolved_path.is_file():
        print(
            "ERROR: Firebase service account JSON file not found.",
            file=sys.stderr,
        )
        print(f"  Looked at: {resolved_path}", file=sys.stderr)
        print(
            "  Put your key at backend/config/serviceAccountKey.json and in .env set:\n"
            "  FIREBASE_SERVICE_ACCOUNT_PATH=config/serviceAccountKey.json",
            file=sys.stderr,
        )
        sys.exit(1)
    firebase_key_path = str(resolved_path)

    import firebase_admin
    from firebase_admin import credentials, auth
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db import Base, Organization, User

    # Generate a secure password and keep for one-time display
    password = secrets.token_urlsafe(20)
    firebase_uid: Optional[str] = None

    # Initialize Firebase (idempotent)
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)

    try:
        user_record = auth.create_user(
            email=ADMIN_EMAIL,
            password=password,
            email_verified=True,
        )
        firebase_uid = user_record.uid
    except Exception as e:
        print(f"ERROR: Failed to create Firebase user: {e}", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(DATABASE_URL, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)

    try:
        with Session() as session:
            org = Organization(name="CityPack")
            session.add(org)
            session.flush()

            user = User(
                firebase_uid=firebase_uid,
                org_id=org.id,
                role="SUPER_ADMIN",
                email=ADMIN_EMAIL,
            )
            session.add(user)
            session.commit()

            print("Bootstrap completed successfully.")
            print(f"  Organization ID: {org.id}")
            print(f"  Firebase UID:     {firebase_uid}")
            print(f"  Admin email:      {ADMIN_EMAIL}")
            print(f"  One-time password (save it): {password}")
    except Exception as e:
        print(f"ERROR: Database operation failed: {e}", file=sys.stderr)
        if firebase_uid:
            try:
                auth.delete_user(firebase_uid)
                print("Firebase user deleted to avoid ghost account.", file=sys.stderr)
            except Exception as delete_err:
                print(
                    f"WARN: Could not delete Firebase user: {delete_err}",
                    file=sys.stderr,
                )
        sys.exit(1)


if __name__ == "__main__":
    main()
