# File: app/business_logic/managers/user_manager.py
"""Business Logic Manager for User, Role, and Permission operations."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import bcrypt

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.user_dto import UserDTO, UserCreateDTO, UserUpdateDTO, RoleDTO
from app.models import User, Role, UserRole
from sqlalchemy.orm import selectinload
# FIX: Add missing 'select' import from sqlalchemy
from sqlalchemy import select

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.user_service import UserService, RoleService

class UserManager(BaseManager):
    """Orchestrates business logic for users and roles."""
    @property
    def user_service(self) -> "UserService": return self.core.user_service
    @property
    def role_service(self) -> "RoleService": return self.core.role_service

    def _hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed one."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def create_user(self, company_id: UUID, dto: UserCreateDTO) -> Result[UserDTO, str]:
        """Creates a new user and assigns roles."""
        user_res = await self.user_service.get_by_username(company_id, dto.username)
        if isinstance(user_res, Failure): return user_res
        if user_res.value: return Failure(f"Username '{dto.username}' already exists.")

        hashed_password = self._hash_password(dto.password)
        new_user = User(company_id=company_id, password_hash=hashed_password, **dto.dict(exclude={'password', 'roles'}))
        
        try:
            async with self.core.get_session() as session:
                session.add(new_user)
                await session.flush()

                for role_id in dto.roles:
                    user_role = UserRole(
                        user_id=new_user.id,
                        role_id=role_id,
                        outlet_id=self.core.current_outlet_id
                    )
                    session.add(user_role)
                
                await session.flush()
                await session.refresh(new_user, attribute_names=['user_roles'])
                return Success(UserDTO.from_orm(new_user))
        except Exception as e:
            return Failure(f"Database error creating user: {e}")

    async def update_user(self, user_id: UUID, dto: UserUpdateDTO) -> Result[UserDTO, str]:
        """Updates an existing user's details, password, and roles."""
        async with self.core.get_session() as session:
            try:
                stmt = select(User).where(User.id == user_id).options(selectinload(User.user_roles))
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return Failure("User not found.")

                update_data = dto.dict(exclude_unset=True, exclude={'password', 'roles'})
                for key, value in update_data.items():
                    setattr(user, key, value)
                
                if dto.password:
                    user.password_hash = self._hash_password(dto.password)

                # FIX: More efficient and atomic role update logic
                existing_role_map = {ur.role_id: ur for ur in user.user_roles}
                target_role_ids = set(dto.roles)
                
                # Remove roles that are no longer assigned
                roles_to_remove = [user_role for role_id, user_role in existing_role_map.items() if role_id not in target_role_ids]
                for user_role in roles_to_remove:
                    await session.delete(user_role)

                # Add new roles
                for role_id in target_role_ids:
                    if role_id not in existing_role_map:
                        new_assignment = UserRole(
                            user_id=user.id,
                            role_id=role_id,
                            outlet_id=self.core.current_outlet_id 
                        )
                        session.add(new_assignment)
                
                await session.flush()
                await session.refresh(user, attribute_names=['user_roles'])
                
                return Success(UserDTO.from_orm(user))
            except Exception as e:
                return Failure(f"Database error updating user: {e}")

    async def deactivate_user(self, user_id: UUID) -> Result[bool, str]:
        """Deactivates a user (soft delete)."""
        user_res = await self.user_service.get_by_id(user_id)
        if isinstance(user_res, Failure): return user_res
        
        user = user_res.value
        if not user: return Failure("User not found.")
        
        user.is_active = False
        update_result = await self.user_service.update(user)
        if isinstance(update_result, Failure): return update_result
        
        return Success(True)

    async def get_all_users(self, company_id: UUID) -> Result[List[UserDTO], str]:
        """Retrieves all users for a given company."""
        res = await self.user_service.get_all(company_id, options=[selectinload(User.user_roles).selectinload(UserRole.role)])
        if isinstance(res, Failure): return res
        return Success([UserDTO.from_orm(u) for u in res.value])

    async def get_all_roles(self, company_id: UUID) -> Result[List[RoleDTO], str]:
        """Retrieves all roles for a given company."""
        res = await self.role_service.get_all(company_id)
        if isinstance(res, Failure): return res
        return Success([RoleDTO.from_orm(r) for r in res.value])
