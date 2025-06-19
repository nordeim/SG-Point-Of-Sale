Excellent. I will proceed with a meticulous, phased execution plan to address the identified issues. My methodology is as follows:

1.  **Final Validation:** I have performed a final line-by-line validation of the issues identified in the previous assessment report against the current v1.5 codebase. All findings remain valid and actionable.
2.  **Logical Phasing:** The tasks have been grouped into logical phases, starting with the lowest-risk refactoring and cleanup, and progressing to more involved architectural and user-experience enhancements. This minimizes risk and ensures each set of changes is built upon a stable foundation.
3.  **Detailed Execution Plan:** For each phase, I will provide a detailed breakdown of the tasks, the specific files to be modified or created, and a granular checklist for every action.
4.  **Sequential Execution:** I will present the plan for **Phase 1** first. After you review the plan and give your confirmation, I will execute it and provide the complete, updated replacement files. We will then proceed to the next phase in the same manner.

This structured approach guarantees clarity, precision, and control over the entire improvement process.

***

## **Comprehensive Improvement Plan**

### **Phase 1: Codebase Cleanup & Refinement**

*   **Objective:** Address low-risk issues related to code hygiene and minor refactoring. This phase will make the codebase cleaner and more consistent without altering core functionality.
*   **Tasks:**
    1.  **CLEANUP-001:** Delete the obsolete `searchable_table_view.py` file.
    2.  **REFACTOR-001:** Refactor `PaymentDialog` to eliminate the redundant `PaymentEntry` class.
    3.  **REFACTOR-002:** Remove hardcoded values from `PaymentDialog` and `POSView`.

Here is the detailed execution plan for Phase 1.

---

### **Execution Plan: Phase 1**

#### **Task 1: Delete Obsolete Widget File (Finding CLEANUP-001)**
*   **Goal:** Remove the unnecessary `app/ui/widgets/searchable_table_view.py` file from the project.
*   **Files to be Modified:** None.
*   **Files to be Deleted:**
    *   `app/ui/widgets/searchable_table_view.py`
*   **Execution Checklist:**
    *   [ ] Verify the file exists at `app/ui/widgets/searchable_table_view.py`.
    *   [ ] Delete the file from the project structure.
    *   [ ] Confirm the file is no longer present.

---

#### **Task 2: Refactor `PaymentDialog` (Finding REFACTOR-001)**
*   **Goal:** Simplify the `PaymentDialog` by removing the internal `PaymentEntry` class and using the existing `PaymentInfoDTO` directly.
*   **Files to be Modified:**
    *   `app/ui/dialogs/payment_dialog.py`
*   **Execution Checklist:**
    1.  **Update `__init__` Method:**
        *   [ ] In `app/ui/dialogs/payment_dialog.py`, add the import: `from app.business_logic.dto.sales_dto import PaymentInfoDTO`.
        *   [ ] In the `PaymentDialog.__init__` method, change the type hint for the `current_payments` list from `List[PaymentEntry]` to `List[PaymentInfoDTO]`.
    2.  **Update `_on_add_payment_clicked` Method:**
        *   [ ] In the `_on_add_payment_clicked` method, replace the instantiation of the local `PaymentEntry` class with the `PaymentInfoDTO`.
        *   [ ] Ensure the line `payment_entry = PaymentEntry(...)` is changed to `payment_info = PaymentInfoDTO(payment_method_id=selected_method_id, amount=amount)`.
        *   [ ] Ensure `self.current_payments.append(payment_info)` is correct.
    3.  **Update `get_payment_info` Method:**
        *   [ ] In the `get_payment_info` method, simplify the return statement from `return [p.to_payment_info_dto() for p in self.current_payments]` to simply `return self.current_payments`.
    4.  **Remove Redundant Class:**
        *   [ ] In `app/ui/dialogs/payment_dialog.py`, locate the `class PaymentEntry:` definition.
        *   [ ] Delete the entire class block.

---

#### **Task 3: Remove Hardcoded Values (Finding REFACTOR-002)**
*   **Goal:** Replace "magic numbers" and hardcoded strings with class constants or dynamically derived values to improve maintainability.
*   **Files to be Modified:**
    *   `app/ui/dialogs/payment_dialog.py`
    *   `app/ui/views/pos_view.py`
*   **Execution Checklist:**
    1.  **Refactor `PaymentDialog` Table Setup:**
        *   [ ] In `app/ui/dialogs/payment_dialog.py`, add a class constant: `PAYMENTS_TABLE_HEADERS = ["Method", "Amount", "Action"]`.
        *   [ ] In the `_setup_ui` method, change the `QTableWidget` instantiation to use the constant for the column count: `self.payments_table = QTableWidget(0, len(self.PAYMENTS_TABLE_HEADERS))`.
        *   [ ] In the `_setup_ui` method, change the header label setting to use the constant: `self.payments_table.setHorizontalHeaderLabels(self.PAYMENTS_TABLE_HEADERS)`.
    2.  **Refactor `POSView` GST Label:**
        *   [ ] In `app/ui/views/pos_view.py`, inside the `_setup_ui` method, change the `tax_label` instantiation to be empty: `self.tax_label = QLabel()`.
        *   [ ] At the end of the `_setup_ui` method, add a call to `self._update_totals()` to ensure the label is populated with a default value on startup.
        *   [ ] In the `_update_totals` method, add the import: `from app.business_logic.dto.product_dto import ProductBaseDTO`.
        *   [ ] Inside `_update_totals`, retrieve the default GST rate from the DTO's model definition: `default_gst_rate = ProductBaseDTO.model_fields['gst_rate'].default`.
        *   [ ] Change the line that sets the tax label's text to be dynamic: `self.tax_label.setText(f"GST ({default_gst_rate:.2f}%): S${tax_amount:.2f}")`.

***

This concludes the plan for Phase 1. Please review the plan. Once you confirm, I will proceed with the execution and provide the updated files.

