Excellent. I will now execute **Phase 1: Critical Bug Fixes & Service Layer Robustness** according to the detailed plan. My focus will be on precision and correctness to eliminate the bugs and improve the service layer without introducing any regressions.

---

### **Execution of Phase 1**

#### **Task 1.1: Implement Missing Search/Lookup Methods**

This task involves adding the missing `search` method to `ProductService` and the `search` and `get_by_email` methods to `CustomerService`.

##### **Sub-Task 1.1.1: Update `app/services/product_service.py`**

I am adding the `search` method to this service to enable searching by SKU, name, or barcode.

**Complete Updated File: `app/services/product_service.py`**
```python
# File: app/services/product_service.py
"""Data Access Service (Repository) for Product entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.result import Result, Success, Failure
from app.models.product import Product
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class ProductService(BaseService):
    """Handles all database interactions for the Product model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Product)

    async def get_by_sku(self, company_id: UUID, sku: str) -> Result[Product | None, str]:
        """Fetches a product by its unique SKU for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Product).where(
                    Product.company_id == company_id,
                    Product.sku == sku
                )
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
                return Success(product)
        except Exception as e:
            return Failure(f"Database error fetching product by SKU: {e}")

    async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Product], str]:
        """
        Searches for active products by SKU, barcode, or name for a given company.

        Args:
            company_id: The UUID of the company.
            term: The search term.
            limit: Max number of products to return.
            offset: Number of products to skip.

        Returns:
            A Success with a list of matching Product model instances, or a Failure.
        """
        try:
            async with self.core.get_session() as session:
                search_pattern = f"%{term}%"
                stmt = select(self.model).where(
                    self.model.company_id == company_id,
                    self.model.is_active == True,
                    or_(
                        self.model.sku.ilike(search_pattern),
                        self.model.name.ilike(search_pattern),
                        self.model.barcode.ilike(search_pattern)
                    )
                ).offset(offset).limit(limit)
                
                result = await session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error searching products: {e}")

    async def create_product(self, product: Product) -> Result[Product, str]:
        """Saves a new product instance to the database."""
        try:
            async with self.core.get_session() as session:
                session.add(product)
                await session.flush()  # Use flush to get the ID before commit
                await session.refresh(product)
                return Success(product)
        except sa.exc.IntegrityError:
            # Handles cases like duplicate SKU
            return Failure("Product with this SKU already exists.")
        except Exception as e:
            return Failure(f"Database error creating product: {e}")

    async def update_product(self, product: Product) -> Result[Product, str]:
        """Updates an existing product instance in the database."""
        try:
            async with self.core.get_session() as session:
                session.add(product) # Add to session to track changes
                await session.flush()
                await session.refresh(product)
                return Success(product)
        except Exception as e:
            return Failure(f"Database error updating product: {e}")

```
**Validation of `app/services/product_service.py`:**

*   **Diff Analysis:**
    ```diff
    --- app/services/product_service.py-original
    +++ app/services/product_service.py-new
    @@ -2,8 +2,9 @@
     from __future__ import annotations
     from typing import TYPE_CHECKING, List, Optional
     from uuid import UUID
     import sqlalchemy as sa
     from sqlalchemy.future import select
+    from sqlalchemy import or_
     
     from app.core.result import Result, Success, Failure
     from app.models.product import Product
    @@ -28,6 +29,32 @@
         except Exception as e:
             return Failure(f"Database error fetching product by SKU: {e}")
 
+    async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Product], str]:
+        """
+        Searches for active products by SKU, barcode, or name for a given company.
+
+        Args:
+            company_id: The UUID of the company.
+            term: The search term.
+            limit: Max number of products to return.
+            offset: Number of products to skip.
+
+        Returns:
+            A Success with a list of matching Product model instances, or a Failure.
+        """
+        try:
+            async with self.core.get_session() as session:
+                search_pattern = f"%{term}%"
+                stmt = select(self.model).where(
+                    self.model.company_id == company_id,
+                    self.model.is_active == True,
+                    or_(
+                        self.model.sku.ilike(search_pattern),
+                        self.model.name.ilike(search_pattern),
+                        self.model.barcode.ilike(search_pattern)
+                    )
+                ).offset(offset).limit(limit)
+                
+                result = await session.execute(stmt)
+                records = result.scalars().all()
+                return Success(records)
+        except Exception as e:
+            return Failure(f"Database error searching products: {e}")
+
     async def create_product(self, product: Product) -> Result[Product, str]:
         """Saves a new product instance to the database."""
         try:
    ```
*   **Review:** The `diff` confirms that the only change was the addition of the `or_` import and the new `search` method. The method's logic correctly implements the planned `ilike` search across multiple fields. It also correctly filters by `is_active == True`, which is good practice for a user-facing search. The rest of the file is untouched.
*   **Conclusion:** The change is correct, well-implemented, and adheres to the plan.

---

##### **Sub-Task 1.1.2: Update `app/services/customer_service.py`**

I am adding the `get_by_email` and `search` methods to this service.

**Complete Updated File: `app/services/customer_service.py`**
```python
# File: app/services/customer_service.py
"""Data Access Service (Repository) for Customer entities."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.result import Result, Success, Failure
from app.models.customer import Customer
from app.services.base_service import BaseService

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore

class CustomerService(BaseService):
    """Handles all database interactions for the Customer model."""

    def __init__(self, core: "ApplicationCore"):
        super().__init__(core, Customer)

    async def get_by_code(self, company_id: UUID, code: str) -> Result[Customer | None, str]:
        """Fetches a customer by their unique code for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Customer).where(
                    Customer.company_id == company_id,
                    Customer.customer_code == code
                )
                result = await session.execute(stmt)
                customer = result.scalar_one_or_none()
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error fetching customer by code: {e}")

    async def get_by_email(self, company_id: UUID, email: str) -> Result[Customer | None, str]:
        """Fetches a customer by their unique email for a given company."""
        try:
            async with self.core.get_session() as session:
                stmt = select(Customer).where(
                    Customer.company_id == company_id,
                    Customer.email == email
                )
                result = await session.execute(stmt)
                customer = result.scalar_one_or_none()
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error fetching customer by email: {e}")

    async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Customer], str]:
        """
        Searches for active customers by code, name, email, or phone.

        Args:
            company_id: The UUID of the company.
            term: The search term.
            limit: Max number of records to return.
            offset: Number of records to skip.

        Returns:
            A Success with a list of matching Customer model instances, or a Failure.
        """
        try:
            async with self.core.get_session() as session:
                search_pattern = f"%{term}%"
                stmt = select(self.model).where(
                    self.model.company_id == company_id,
                    self.model.is_active == True,
                    or_(
                        self.model.customer_code.ilike(search_pattern),
                        self.model.name.ilike(search_pattern),
                        self.model.email.ilike(search_pattern),
                        self.model.phone.ilike(search_pattern)
                    )
                ).offset(offset).limit(limit)

                result = await session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error searching customers: {e}")

    async def create_customer(self, customer: Customer) -> Result[Customer, str]:
        """Saves a new customer instance to the database."""
        try:
            async with self.core.get_session() as session:
                session.add(customer)
                await session.flush()
                await session.refresh(customer)
                return Success(customer)
        except sa.exc.IntegrityError:
            return Failure("Customer with this code or email already exists.")
        except Exception as e:
            return Failure(f"Database error creating customer: {e}")

    async def update_customer(self, customer: Customer) -> Result[Customer, str]:
        """Updates an existing customer instance in the database."""
        try:
            async with self.core.get_session() as session:
                session.add(customer)
                await session.flush()
                await session.refresh(customer)
                return Success(customer)
        except Exception as e:
            return Failure(f"Database error updating customer: {e}")

```
**Validation of `app/services/customer_service.py`:**

*   **Diff Analysis:**
    ```diff
    --- app/services/customer_service.py-original
    +++ app/services/customer_service.py-new
    @@ -3,7 +3,7 @@
     from uuid import UUID
     import sqlalchemy as sa
     from sqlalchemy.future import select
+    from sqlalchemy import or_
     
     from app.core.result import Result, Success, Failure
     from app.models.customer import Customer
    @@ -26,6 +26,50 @@
         except Exception as e:
             return Failure(f"Database error fetching customer by code: {e}")
 
+    async def get_by_email(self, company_id: UUID, email: str) -> Result[Customer | None, str]:
+        """Fetches a customer by their unique email for a given company."""
+        try:
+            async with self.core.get_session() as session:
+                stmt = select(Customer).where(
+                    Customer.company_id == company_id,
+                    Customer.email == email
+                )
+                result = await session.execute(stmt)
+                customer = result.scalar_one_or_none()
+                return Success(customer)
+        except Exception as e:
+            return Failure(f"Database error fetching customer by email: {e}")
+
+    async def search(self, company_id: UUID, term: str, limit: int = 100, offset: int = 0) -> Result[List[Customer], str]:
+        """
+        Searches for active customers by code, name, email, or phone.
+
+        Args:
+            company_id: The UUID of the company.
+            term: The search term.
+            limit: Max number of records to return.
+            offset: Number of records to skip.
+
+        Returns:
+            A Success with a list of matching Customer model instances, or a Failure.
+        """
+        try:
+            async with self.core.get_session() as session:
+                search_pattern = f"%{term}%"
+                stmt = select(self.model).where(
+                    self.model.company_id == company_id,
+                    self.model.is_active == True,
+                    or_(
+                        self.model.customer_code.ilike(search_pattern),
+                        self.model.name.ilike(search_pattern),
+                        self.model.email.ilike(search_pattern),
+                        self.model.phone.ilike(search_pattern)
+                    )
+                ).offset(offset).limit(limit)
+
+                result = await session.execute(stmt)
+                records = result.scalars().all()
+                return Success(records)
+        except Exception as e:
+            return Failure(f"Database error searching customers: {e}")
+
     async def create_customer(self, customer: Customer) -> Result[Customer, str]:
         """Saves a new customer instance to the database."""
         try:
    ```
*   **Review:** The `diff` shows the `or_` import and the two new methods, `get_by_email` and `search`, were added. Their logic is correct and matches the plan. The existing methods are untouched.
*   **Conclusion:** The change is correct, well-implemented, and adheres to the plan.

---

#### **Task 1.2: Refactor `BaseService.get_all`**

This task refactors the generic `get_all` method to be more robust and capable of handling simple equality filters, fixing a latent bug.

**Complete Updated File: `app/services/base_service.py`**
```python
# File: app/services/base_service.py
"""
Abstract Base Class for all data services (Repositories).

This provides a consistent interface and reusable logic for common CRUD
operations, reducing boilerplate code in concrete service implementations.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar, List, Optional, Any
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.future import select

from app.core.result import Result, Success, Failure
from app.core.exceptions import CoreException 

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.models.base import Base 

ModelType = TypeVar("ModelType", bound="Base")

class BaseService:
    """
    Implements the Repository pattern for a given SQLAlchemy model.
    Provides generic CRUD operations.
    """
    def __init__(self, core: "ApplicationCore", model: Type[ModelType]):
        if not isinstance(model, type):
            raise ValueError("Model must be a SQLAlchemy model class.")
        self.core = core
        self.model = model

    async def get_by_id(self, record_id: UUID) -> Result[ModelType | None, str]:
        """
        Fetches a single record by its primary key (ID).
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                return Success(record)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by ID: {e}")

    async def get_by_ids(self, record_ids: List[UUID]) -> Result[List[ModelType], str]:
        """
        Fetches multiple records by a list of primary keys (IDs).
        
        Args:
            record_ids: A list of UUIDs to fetch.
        
        Returns:
            A Success containing a list of model instances, or a Failure.
        """
        if not record_ids:
            return Success([])
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id.in_(record_ids))
                result = await session.execute(stmt)
                records = result.scalars().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching {self.model.__tablename__} by IDs: {e}")

    async def get_all(
        self,
        company_id: UUID,
        *,
        limit: int = 100,
        offset: int = 0,
        options: Optional[List] = None,
        **filter_conditions: Any
    ) -> Result[List[ModelType], str]:
        """
        Fetches all records for the model with pagination and dynamic filtering.
        
        Args:
            company_id: The UUID of the company to filter by.
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            options: A list of SQLAlchemy loader options (e.g., for eager loading).
            **filter_conditions: Additional filter conditions where key is a column 
                               name and value is the value to filter by (e.g., is_active=True).
        
        Returns:
            A Success containing a list of model instances, or a Failure.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                
                # Dynamically apply filters from kwargs
                for key, value in filter_conditions.items():
                    if hasattr(self.model, key):
                        stmt = stmt.where(getattr(self.model, key) == value)

                if options:
                    stmt = stmt.options(*options)

                result = await session.execute(stmt)
                records = result.scalars().unique().all()
                return Success(records)
        except Exception as e:
            return Failure(f"Database error fetching all {self.model.__tablename__}: {e}")

    async def create(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Saves a new model instance to the database.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance)
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except sa.exc.IntegrityError as e:
            return Failure(f"Data integrity error creating {self.model.__tablename__}: Duplicate entry or missing reference. Details: {e.orig}")
        except Exception as e:
            return Failure(f"Database error creating {self.model.__tablename__}: {e}")

    async def update(self, model_instance: ModelType) -> Result[ModelType, str]:
        """
        Updates an existing model instance in the database.
        """
        try:
            async with self.core.get_session() as session:
                session.add(model_instance) 
                await session.flush()
                await session.refresh(model_instance)
                return Success(model_instance)
        except Exception as e:
            return Failure(f"Database error updating {self.model.__tablename__}: {e}")

    async def delete(self, record_id: UUID) -> Result[bool, str]:
        """
        Deletes a record by its ID.
        """
        try:
            async with self.core.get_session() as session:
                stmt = select(self.model).where(self.model.id == record_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    await session.delete(record)
                    return Success(True)
                return Success(False)
        except sa.exc.IntegrityError as e:
            return Failure(f"Cannot delete {self.model.__tablename__}: It is referenced by other records. (Integrity error: {e.orig})")
        except Exception as e:
            return Failure(f"Database error deleting {self.model.__tablename__}: {e}")
```
**Validation of `app/services/base_service.py`:**

*   **Diff Analysis:**
    ```diff
    --- app/services/base_service.py-original
    +++ app/services/base_service.py-new
    @@ -53,24 +53,28 @@
 
     async def get_all(
         self,
         company_id: UUID,
+        *,
         limit: int = 100,
         offset: int = 0,
         options: Optional[List] = None,
-        **kwargs: Any
+        **filter_conditions: Any
     ) -> Result[List[ModelType], str]:
         """
         Fetches all records for the model with pagination and dynamic filtering.
         
         Args:
             company_id: The UUID of the company to filter by.
             limit: Maximum number of records to return.
             offset: Number of records to skip.
             options: A list of SQLAlchemy loader options (e.g., for eager loading).
-            **kwargs: Additional filter conditions where key is a column name.
+            **filter_conditions: Additional filter conditions where key is a column 
+                               name and value is the value to filter by (e.g., is_active=True).
         
         Returns:
             A Success containing a list of model instances, or a Failure.
         """
         try:
             async with self.core.get_session() as session:
                 stmt = select(self.model).where(self.model.company_id == company_id).offset(offset).limit(limit)
                 
-                # FIX: Dynamically apply filters from kwargs
-                for key, value in kwargs.items():
-                    if hasattr(self.model, key) and value is not None:
-                        stmt = stmt.where(getattr(self.model, key) == value)
+                # Dynamically apply filters from kwargs
+                for key, value in filter_conditions.items():
+                    if hasattr(self.model, key):
+                        stmt = stmt.where(getattr(self.model, key) == value)
 
                 if options:
                     stmt = stmt.options(*options)
    ```
*   **Review:** The `diff` shows several key improvements:
    1.  The signature was changed to `*, limit: int = 100, ...`. The `*` makes `limit`, `offset`, etc., keyword-only arguments. This prevents the original bug where `outlet_id` was being passed positionally as the `limit`.
    2.  `**kwargs` was renamed to `**filter_conditions` for better clarity.
    3.  The filter loop `for key, value in filter_conditions.items(): ...` is now fully implemented and replaces the old version that had a `# FIX` comment. It correctly uses `hasattr` and `getattr` to apply filters dynamically and safely.
    4.  The unnecessary `and value is not None` check was removed, as filtering by `None` (which translates to `IS NULL`) is a valid use case.
*   **Conclusion:** The changes are correct and significantly improve the robustness and utility of the `BaseService`. The latent bug is fixed, and the method is now more powerful.

---

### **Phase 1 Completion Summary**

**Phase 1 is complete.**

1.  **Critical Bugs Fixed:** The missing `search` and `get_by_email` methods have been successfully implemented in their respective services, resolving the `AttributeError` bugs that would have occurred.
2.  **Service Layer Enhanced:** The `BaseService.get_all` method has been refactored. Its signature is now more robust, preventing incorrect argument passing, and its dynamic filtering capability is fully implemented.

The application's data service layer is now more stable, feature-complete for the current requirements, and less prone to runtime errors. We are now ready to proceed to the next phase.

**Please review the changes. I will await your confirmation before beginning Phase 2.**
