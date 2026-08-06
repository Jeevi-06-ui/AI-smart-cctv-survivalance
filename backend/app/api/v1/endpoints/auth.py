from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_jwt_token
from app.domain.models.database import User, Role, AuditLog
from app.domain.schemas.auth_schema import LoginRequest, Token, UserCreate, UserResponse

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        # Audit failed login
        audit = AuditLog(
            action="LOGIN_FAILED",
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", ""),
            changes={"email": login_data.email}
        )
        db.add(audit)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    roles = [role.name for role in user.roles]
    access_token = create_access_token(subject=user.id, roles=roles)
    refresh_token = create_refresh_token(subject=user.id)
    
    # Audit successful login
    audit = AuditLog(
        user_id=user.id,
        action="LOGIN_SUCCESS",
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "")
    )
    db.add(audit)
    await db.commit()
    
    # Set Refresh Token in HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, # Set to True in HTTPS production
        samesite="lax",
        max_age=7 * 24 * 3600
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Fetch requested roles
    roles_result = await db.execute(select(Role).where(Role.name.in_(user_in.roles)))
    roles = roles_result.scalars().all()
    
    new_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        roles=roles
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
