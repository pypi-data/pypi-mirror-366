from typing import Type

from pydantic import BaseModel, Field

from kfinance.kfinance import Company, ParticipantInMerger
from kfinance.models.permission_models import Permission
from kfinance.tool_calling.shared_models import KfinanceTool, ToolArgsWithIdentifier


class GetAdvisorsForCompanyInTransactionFromIdentifierArgs(ToolArgsWithIdentifier):
    transaction_id: int | None = Field(description="The ID of the merger.", default=None)


class GetAdvisorsForCompanyInTransactionFromIdentifier(KfinanceTool):
    name: str = "get_advisors_for_company_in_transaction_from_identifier"
    description: str = 'Get the companies advising a company in a given transaction. For example, "Who advised S&P Global during their purchase of Kensho?"'
    args_schema: Type[BaseModel] = GetAdvisorsForCompanyInTransactionFromIdentifierArgs
    accepted_permissions: set[Permission] | None = {Permission.MergersPermission}

    def _run(self, identifier: str, transaction_id: int) -> list:
        ticker = self.kfinance_client.ticker(identifier)
        participant_in_merger = ParticipantInMerger(
            kfinance_api_client=ticker.kfinance_api_client,
            transaction_id=transaction_id,
            company=Company(
                kfinance_api_client=ticker.kfinance_api_client,
                company_id=ticker.company.company_id,
            ),
        )
        advisors = participant_in_merger.advisors

        if advisors:
            return [
                {
                    "advisor_company_id": advisor.company.company_id,
                    "advisor_company_name": advisor.company.name,
                    "advisor_type_name": advisor.advisor_type_name,
                }
                for advisor in advisors
            ]
        else:
            return []
