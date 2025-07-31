from typing import Type

from pydantic import BaseModel

from kfinance.models.permission_models import Permission
from kfinance.models.price_models import HistoryMetadata
from kfinance.tool_calling.shared_models import KfinanceTool, ToolArgsWithIdentifier


class GetHistoryMetadataFromIdentifier(KfinanceTool):
    name: str = "get_history_metadata_from_identifier"
    description: str = "Get the history metadata associated with an identifier. History metadata includes currency, symbol, exchange name, instrument type, and first trade date."
    args_schema: Type[BaseModel] = ToolArgsWithIdentifier
    accepted_permissions: set[Permission] | None = None

    def _run(self, identifier: str) -> HistoryMetadata:
        return self.kfinance_client.ticker(identifier).history_metadata
