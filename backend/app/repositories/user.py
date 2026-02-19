from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.user import User
from app.core.security import get_password_hash, verify_password


class UserRepository(BaseRepository[User]):
    """用户Repository"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(self.model).filter(self.model.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(self.model).filter(self.model.email == email).first()
    
    def create_user(self, username: str, email: str, password: str, role: str = "student") -> User:
        """创建用户"""
        hashed_password = get_password_hash(password)
        user_data = {
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "role": role
        }
        return self.create(user_data)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def update_last_login(self, user: User):
        """更新最后登录时间"""
        from datetime import datetime
        user.last_login = datetime.now()
        self.db.commit()
        self.db.refresh(user)
        return user

