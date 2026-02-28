#!/usr/bin/env python3
"""
Script to Provision a Station Manager (Heshadha's Request).
Usage: python scripts/create_manager.py
"""
import os
import sys
import secrets
from pathlib import Path
from typing import Optional

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
os.chdir(BACKEND_ROOT)

from dotenv import load_dotenv
load_dotenv(BACKEND_ROOT / ".env")

import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Organization, User

DATABASE_URL = os.getenv("DATABASE_URL")
FIREBASE_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

def create_station_manager():
    print("\n" + "="*50)
    print("   LamiGo: Create Station Manager (Terminal Mode)")
    print("="*50)

    station_name = input("1. Enter Station/Branch Name (e.g. Galle): ").strip()
    email = input(f"2. Enter Manager Email (e.g. manager@{station_name.lower()}.lk): ").strip()

    if not station_name or not email:
        print("Error: Station Name and Email are required.")
        return

    raw_path = (FIREBASE_KEY or "").strip().strip('"\'')
    resolved_path = Path(os.path.expanduser(raw_path))
    if not resolved_path.is_absolute():
        resolved_path = (BACKEND_ROOT / resolved_path).resolve()
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(str(resolved_path))
        firebase_admin.initialize_app(cred)
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    firebase_uid = None

    try:
        org = session.query(Organization).filter_by(name=station_name).first()
        if not org:
            print(f"   -> Branch '{station_name}' does not exist. Creating it...")
            org = Organization(name=station_name)
            session.add(org)
            session.flush()
        else:
            print(f"   -> Found existing Branch '{station_name}'.")

        try:
            user_record = auth.get_user_by_email(email)
            print(f"   -> User {email} already exists in Firebase. Using existing UID.")
            firebase_uid = user_record.uid
            temp_password = secrets.token_urlsafe(12)
            auth.update_user(firebase_uid, password=temp_password)
        except firebase_admin.auth.UserNotFoundError:
            print("   -> Creating new Identity in Firebase...")
            temp_password = secrets.token_urlsafe(12)
            user_record = auth.create_user(email=email, password=temp_password)
            firebase_uid = user_record.uid

        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            print("   -> User Object already exists in Database. Updating Role...")
            existing_user.role = "STATION_MANAGER"
            existing_user.org_id = org.id
        else:
            print("   -> Creating new User Object in Database...")
            new_manager = User(
                firebase_uid=firebase_uid,
                org_id=org.id,
                role="STATION_MANAGER",
                email=email
            )
            session.add(new_manager)
        
        session.commit()

        print("\n" + "="*50)
        print("✅ SUCCESS! Station Manager Provisioned.")
        print("="*50)
        print(f"🔑 Branch Object:  {station_name}")
        print(f"👤 Login Email:    {email}")
        print(f"🔐 Password:       {temp_password}")
        print("="*50)
        print("INSTRUCTION: Send these credentials to the user.")
        print("When they log in, they will access the '" + station_name + "' object.")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_station_manager()
