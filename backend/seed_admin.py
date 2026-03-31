"""
Seed script to create initial admin user in the database.

Usage:
    python seed_admin.py

This script creates an admin user with:
- Email: admin@obras.local
- Password: ChangeMe123!
- Role: ADMIN
"""

import asyncio
import sys
import uuid
from datetime import datetime
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def seed_admin_user():
    """Create initial admin user if it doesn't exist."""
    
    import bcrypt
    
    # Get database URL from environment or use default
    from app.core.config import settings
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin already exists using raw SQL
            result = await db.execute(
                text("SELECT id FROM users WHERE email = :email AND deleted_at IS NULL"),
                {"email": "admin@obras.local"}
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print("✓ Admin user already exists: admin@obras.local")
                await engine.dispose()
                return
            
            # Create new admin user using raw SQL
            admin_password = "ChangeMe123!"
            admin_id = str(uuid.uuid4())
            # Hash password with bcrypt directly
            salt = bcrypt.gensalt(rounds=12)
            hashed_pw = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
            now = datetime.utcnow()
            
            await db.execute(
                text("""
                    INSERT INTO users (id, email, full_name, hashed_password, role, is_active, created_at, updated_at, deleted_at)
                    VALUES (:id, :email, :full_name, :hashed_password, :role, :is_active, :created_at, :updated_at, NULL)
                """),
                {
                    "id": admin_id,
                    "email": "admin@obras.local",
                    "full_name": "System Administrator",
                    "hashed_password": hashed_pw,
                    "role": "ADMIN",
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            
            await db.commit()
            
            print("✓ Admin user created successfully!")
            print(f"  Email: admin@obras.local")
            print(f"  Password: {admin_password}")
            print("\n⚠️  IMPORTANT: Change this password immediately after first login!")
            print("   Update the password in the API or database to a secure value.")
            print("\n✓ You can now login via: POST /api/v1/auth/login")
            
        except Exception as e:
            print(f"✗ Error creating admin user: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


async def main():
    """Main entry point."""
    try:
        print("🔧 Creating initial admin user...\n")
        await seed_admin_user()
        print("\n✓ Database seeding completed!")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
