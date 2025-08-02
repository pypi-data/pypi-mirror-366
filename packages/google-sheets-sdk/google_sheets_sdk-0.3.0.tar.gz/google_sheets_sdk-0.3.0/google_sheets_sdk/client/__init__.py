from dataclasses import dataclass, field
from typing import ClassVar

from httpx import AsyncClient, HTTPStatusError

from google_sheets_sdk.core import Settings, models


@dataclass
class Client:
    _BASE_URL: ClassVar[str] = "https://sheets.googleapis.com"

    http_client: AsyncClient
    settings: Settings = field(
        default_factory=Settings,  # type: ignore
    )

    _token_data: models.TokenData = field(
        init=False,
    )

    def __post_init__(self):
        self._token_data = models.TokenData(
            email=self.settings.CLIENT_EMAIL,
            scope=self.settings.SCOPE.unicode_string(),
            private_key=self.settings.PRIVATE_KEY,
            private_key_id=self.settings.PRIVATE_KEY_ID,
        )

    async def batch_clear_values(
        self,
        spreadsheet_id: models.SpreadsheetId,
        ranges: list[models.Range],
    ) -> None:
        try:
            response = await self.http_client.post(
                url=f"{self._BASE_URL}/v4/spreadsheets/{spreadsheet_id}/values:batchClear",
                json={
                    "ranges": ranges,
                },
                headers={
                    "Authorization": f"Bearer {await self._token_data.generate(self.http_client)}",
                },
            )
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise exc

    async def batch_update_values(
        self,
        spreadsheet_id: models.SpreadsheetId,
        sheets: list[models.Sheet],
    ) -> models.BatchUpdateValuesResponse:
        try:
            response = await self.http_client.post(
                url=f"{self._BASE_URL}/v4/spreadsheets/{spreadsheet_id}/values:batchUpdate",
                json={
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        sheet.model_dump(
                            mode="json",
                            by_alias=True,
                        )
                        for sheet in sheets
                    ],
                },
                headers={
                    "Authorization": f"Bearer {await self._token_data.generate(self.http_client)}",
                },
            )
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise exc
        else:
            return models.BatchUpdateValuesResponse(**response.json())
