from kfinance.models.competitor_models import CompetitorSource
from kfinance.models.permission_models import Permission
from kfinance.tool_calling.shared_models import KfinanceTool, ToolArgsWithIdentifier


class GetCompetitorsFromIdentifierArgs(ToolArgsWithIdentifier):
    # no description because the description for enum fields comes from the enum docstring.
    competitor_source: CompetitorSource


class GetCompetitorsFromIdentifier(KfinanceTool):
    name: str = "get_competitors_from_identifier"
    description: str = "Retrieves a list of company_id and company_name that are competitors for a given company, optionally filtered by the source of the competitor information."
    args_schema = GetCompetitorsFromIdentifierArgs
    accepted_permissions: set[Permission] | None = {Permission.CompetitorsPermission}

    def _run(
        self,
        identifier: str,
        competitor_source: CompetitorSource,
    ) -> dict:
        ticker = self.kfinance_client.ticker(identifier)
        return self.kfinance_client.kfinance_api_client.fetch_competitors(
            company_id=ticker.company_id, competitor_source=competitor_source
        )
