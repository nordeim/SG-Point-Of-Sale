Of course. With the core managers and a key service now under test coverage, we have established a robust foundation for application reliability.

I will now proceed with the final planned step for this phase.

### **Phase 4 Plan: Implement Comprehensive Test Suite**

**Previous Steps (Completed):**
*   **Sub-Task 4.1:** Test Fixture Setup.
*   **Sub-Task 4.2:** `SalesManager` Unit Tests.
*   **Sub-Task 4.3:** `InventoryManager` Unit Tests.
*   **Sub-Task 4.4:** `ProductManager` and `CustomerManager` Unit Tests.
*   **Sub-Task 4.5:** `ProductService` Unit Tests.

**Current Step (To Be Executed):**
*   **Sub-Task 4.6:** Finalize Phase 4 by creating a test suite for `CompanyManager` and `UserManager`.

---

### **Phase 4, Sub-Task 4.6: `CompanyManager` & `UserManager` Unit Tests**

**Objective:** To complete the foundational test suite by adding coverage for the last two critical managers: `CompanyManager` (for managing company data) and `UserManager` (for handling users and their roles). This will ensure all primary business logic entities are validated.

**Execution Plan & Checklist:**

1.  **Create Test File for `CompanyManager`:**
    *   [x] Create a new file: `tests/unit/business_logic/managers/test_company_manager.py`.
    *   [x] Implement `test_get_company_success` to verify that company details can be correctly retrieved.
    *   [x] Implement `test_update_company_success` to validate the update logic.
    *   [x] Implement `test_update_company_duplicate_reg_no_fails` to ensure the business rule preventing duplicate registration numbers is enforced.

2.  **Create Test File for `UserManager`:**
    *   [x] Create a new file: `tests/unit/business_logic/managers/test_user_manager.py`.
    *   [x] Implement `test_create_user_success` to verify user creation and role assignment.
    *   [x] Implement `test_create_user_duplicate_username_fails` to validate the unique username business rule.
    *   [x] Implement `test_update_user_roles` to ensure that a user's roles can be correctly changed (clearing old ones and adding new ones).
    *   [x] Implement `test_deactivate_user_success` to verify the soft-delete functionality.

All steps in this plan have been meticulously completed.

---

### **Generated and Updated Files**

Here are the complete new files for this final sub-task.

#### 1. New File: `tests/unit/business_logic/managers/test_company_manager.py`

```python
# File: tests/unit/business_logic/managers/test_company_manager.py
"""
Unit tests for the CompanyManager class.
"""
import pytest

from app.core.result import Success, Failure
from app.business_logic.dto.company_dto import CompanyUpdateDTO
from tests.factories import CompanyFactory

pytestmark = pytest.mark.asyncio

class TestCompanyManager:
    """Test suite for company-related business logic."""

    async def test_get_company_success(self, test_core):
        """Verify that company details can be successfully retrieved."""
        # --- Arrange ---
        company = CompanyFactory()

        # --- Act ---
        result = await test_core.company_manager.get_company(company.id)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.id == company.id
        assert result.value.name == company.name

    async def test_update_company_success(self, test_core):
        """Verify that updating a company's information is successful."""
        # --- Arrange ---
        company = CompanyFactory(name="Old Company Name")
        update_dto = CompanyUpdateDTO(
            name="New Company Name",
            registration_number=company.registration_number, # Not changing
            address="123 New Address, Singapore"
        )

        # --- Act ---
        result = await test_core.company_manager.update_company(company.id, update_dto)

        # --- Assert ---
        assert isinstance(result, Success)
        assert result.value.id == company.id
        assert result.value.name == "New Company Name"
        assert result.value.address == "123 New Address, Singapore"

    async def test_update_company_duplicate_reg_no_fails(self, test_core):
        """Verify failure when trying to update to a registration number that already exists."""
        # --- Arrange ---
        company1 = CompanyFactory(registration_number="REG123")
        company2 = CompanyFactory(registration_number="REG456")

        update_dto = CompanyUpdateDTO(
            name=company2.name,
            registration_number=company1.registration_number # Attempt to use company1's reg number
        )

        # --- Act ---
        result = await test_core.company_manager.update_company(company2.id, update_dto)

        # --- Assert ---
        assert isinstance(result, Failure)
        assert "is already in use" in result.error

```

#### 2. New File: `tests/unit/business_logic/managers/test_user_manager.py`

```python
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
```

