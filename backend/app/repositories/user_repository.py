from typing import Optional, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.models.database import User, Role, Permission, AuditLog

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == role_name))
        return result.scalars().first()

    async def get_roles_by_names(self, role_names: List[str]) -> List[Role]:
        result = await self.db.execute(select(Role).where(Role.name.in_(role_names)))
        return result.scalars().all()

    async def log_audit(self, user_id: Optional[uuid.UUID], action: str, ip: str, user_agent: str, metadata: dict = None):
        audit = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip,
            user_agent=user_agent,
            changes=metadata or {}
        )
        self.db.add(audit)
        await self.db.commit()
