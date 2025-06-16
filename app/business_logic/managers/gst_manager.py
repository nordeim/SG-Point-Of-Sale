# File: app/business_logic/managers/gst_manager.py
"""Business Logic Manager for GST compliance and reporting."""
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import date
from decimal import Decimal
import uuid

from app.core.result import Result, Success, Failure
from app.business_logic.managers.base_manager import BaseManager
from app.business_logic.dto.reporting_dto import GstReportDTO

if TYPE_CHECKING:
    from app.core.application_core import ApplicationCore
    from app.services.report_service import ReportService
    from app.services.company_service import CompanyService

class GstManager(BaseManager):
    """Handles logic related to Singapore GST compliance."""

    @property
    def report_service(self) -> "ReportService":
        return self.core.report_service

    @property
    def company_service(self) -> "CompanyService":
        return self.core.company_service

    async def generate_gst_f5_report(self, company_id: uuid.UUID, start_date: date, end_date: date) -> Result[GstReportDTO, str]:
        """
        Generates the data needed for an IRAS GST Form 5.
        Args:
            company_id: The UUID of the company.
            start_date: Start date of the GST period.
            end_date: End date of the GST period.
        Returns:
            A Success with a GstReportDTO, or a Failure.
        """
        company_result = await self.company_service.get_by_id(company_id)
        if isinstance(company_result, Failure) or company_result.value is None:
            return Failure(f"Company with ID {company_id} not found.")
        company = company_result.value

        data_result = await self.report_service.get_gst_f5_raw_data(company_id, start_date, end_date)
        if isinstance(data_result, Failure):
            return data_result
            
        data = data_result.value
        
        # Retrieve values from raw data, defaulting to 0 if not present
        box_1 = data.get("box_1_standard_rated_supplies", Decimal("0.00"))
        box_2 = data.get("box_2_zero_rated_supplies", Decimal("0.00"))
        box_3 = data.get("box_3_exempt_supplies", Decimal("0.00"))
        box_5 = data.get("box_5_taxable_purchases", Decimal("0.00"))
        box_6 = data.get("box_6_output_tax_due", Decimal("0.00"))
        box_7 = data.get("box_7_input_tax_claimed", Decimal("0.00"))

        # Perform final calculations as per IRAS Form 5 logic
        box_4 = (box_1 + box_2 + box_3).quantize(Decimal("0.01"))
        # For MVP, assume adjustments are zero. A full implementation would fetch these.
        box_8, box_9 = Decimal("0.00"), Decimal("0.00")
        
        box_13_net_gst = (box_6 + box_8 - box_7 - box_9).quantize(Decimal("0.01"))
        
        report_dto = GstReportDTO(
            company_id=company_id,
            company_name=company.name,
            company_gst_reg_no=company.gst_registration_number,
            start_date=start_date,
            end_date=end_date,
            box_1_standard_rated_supplies=box_1,
            box_2_zero_rated_supplies=box_2,
            box_3_exempt_supplies=box_3,
            box_4_total_supplies=box_4,
            box_5_taxable_purchases=box_5,
            box_6_output_tax_due=box_6,
            box_7_input_tax_claimed=box_7,
            box_8_adjustments_output_tax=box_8,
            box_9_adjustments_input_tax=box_9,
            box_13_net_gst_payable=box_13_net_gst
        )
        
        return Success(report_dto)
