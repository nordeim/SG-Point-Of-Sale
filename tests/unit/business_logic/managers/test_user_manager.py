# File: tests/unit/business_logic/managers/test_user_manager.py
"""
Unit tests for the UserManager class.
"""
import pytest
from app.core.result import Success, Failure
from app.business_logic.dto.user_dto import UserCreateDTO, UserUpdateDTO
from app.models import User, Role, UserRole
from tests.factories import UserFactory, RoleFactory, OutletFactory

pytestmark = pytest.mark.asyncio

class TestUserManager:
    """Test suite for user and role management logic."""

    async def test_create_user_success_with_roles(self, test_core, db_session):
        """Verify successful user creation and role assignment."""
        # --- Arrange ---
        role1 = RoleFactory(company_id=test_core.current_company_id)
        role2 = RoleFactory(company_id=test_core.current_company_id)
        
        dto = UserCreateDTO(
            username="newuser",
            email="newuser@test.com",
            password="StrongPassword123",
            roles=[role1.id, role2.id]
        )

        # --- Act ---
        result = await test_core.user_manager.create_user(test_core.current_company_id, dto)

        # --- Assert ---
        assert isinstance(result, Success)
        user_dto = result.value
        assert user_dto.username == "newuser"
        
        # Verify roles were assigned in the database
        user_db = await db_session.get(User, user_dto.id)
        assigned_role_ids = {ur.role_id for ur in user_db.user_roles}
        assert assigned_role_ids == {role1.id, role2.id}

    async def test_create_user_duplicate_username_fails(self, test_core):
        """Verify that creating a user with a duplicate username fails."""
        # --- Arrange ---
        UserFactory(company_id=test_core.current_company_id, username="existinguser")
        role = RoleFactory(company_id=test_core.current_company_id)
        dto = UserCreateDTO(
            username="existinguser",
            email="another@email.com",
            password="password",
            roles=[role.id]
        )
        
        # --- Act ---
        result = await test_core.user_manager.create_user(test_core.current_company_id, dto)

        # --- Assert ---
        assert isinstance(result, Failure)
        assert "already exists" in result.error

    async def test_update_user_roles(self, test_core, db_session):
        """Verify that a user's roles can be correctly updated."""
        # --- Arrange ---
        user = UserFactory(company_id=test_core.current_company_id)
        role_to_remove = RoleFactory(company_id=test_core.current_company_id)
        role_to_keep = RoleFactory(company_id=test_core.current_company_id)
        role_to_add = RoleFactory(company_id=test_core.current_company_id)
        
        # Assign initial roles
        outlet = OutletFactory(company_id=test_core.current_company_id)
        test_core._current_outlet_id = outlet.id # Set context for role assignment
        db_session.add_all([
            UserRole(user_id=user.id, role_id=role_to_remove.id, outlet_id=outlet.id),
            UserRole(user_id=user.id, role_id=role_to_keep.id, outlet_id=outlet.id)
        ])
        await db_session.commit()

        update_dto = UserUpdateDTO(
            username=user.username,
            email=user.email,
            roles=[role_to_keep.id, role_to_add.id] # New set of roles
        )

        # --- Act ---
        result = await test_core.user_manager.update_user(user.id, update_dto)

        # --- Assert ---
        assert isinstance(result, Success)
        
        await db_session.refresh(user, attribute_names=['user_roles'])
        final_role_ids = {ur.role_id for ur in user.user_roles}
        assert final_role_ids == {role_to_keep.id, role_to_add.id}

    async def test_deactivate_user_success(self, test_core, db_session):
        """Verify that deactivating a user sets its is_active flag to False."""
        # --- Arrange ---
        user = UserFactory(company_id=test_core.current_company_id, is_active=True)

        # --- Act ---
        result = await test_core.user_manager.deactivate_user(user.id)
        
        # --- Assert ---
        assert isinstance(result, Success)
        
        updated_user = await db_session.get(User, user.id)
        assert updated_user.is_active is False
