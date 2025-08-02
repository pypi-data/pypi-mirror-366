import time as t
from dataclasses import InitVar, dataclass, field

import httpx
from jose import jwt
from pydantic import BaseModel
from pydantic.fields import Field

type Range = str
type Value = str | int | float
type SpreadsheetId = str


class Sheet(BaseModel):
    range_: Range = Field(
        ...,
        serialization_alias="range",
    )
    values: list[list[Value]]


@dataclass
class TokenData:
    email: InitVar[str]

    scope: str
    private_key: str
    private_key_id: str

    _iss: str = field(
        init=False,
    )
    _sub: str = field(
        init=False,
    )
    _aud: str = field(
        init=False,
        default="https://oauth2.googleapis.com/token",
    )
    _iat: float = field(
        init=False,
    )
    _exp: float = field(
        init=False,
    )

    def __post_init__(
        self,
        email: str,
    ):
        self._iss = self._sub = email
        self._refresh_expiration()

    def _as_dict(self):
        return {
            "scope": self.scope,
            "iss": self._iss,
            "sub": self._sub,
            "aud": self._aud,
            "iat": self._iat,
            "exp": self._exp,
        }

    def _refresh_expiration(self):
        self._iat = t.time()
        self._exp = self._iat + 3600

    def _is_expired(self):
        return not self._exp - t.time() > 60

    @property
    def encoded(self):
        if self._is_expired():
            self._refresh_expiration()
        return jwt.encode(
            self._as_dict(),
            self.private_key,
            headers={
                "kid": self.private_key_id,
            },
            algorithm="RS256",
        )

    async def generate(
        self,
        http_client: httpx.AsyncClient,
    ):
        try:
            response = await http_client.post(
                url="https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": self.encoded,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise
        else:
            json_response = response.json()
            return json_response["access_token"]


class UpdateValuesResponse(BaseModel):
    spreadsheet_id: SpreadsheetId = Field(
        ...,
        alias="spreadsheetId",
    )
    updated_range: str = Field(
        default=0,
        alias="updatedRange",
    )
    updated_rows: int = Field(
        default=0,
        alias="updatedRows",
    )
    updated_columns: int = Field(
        default=0,
        alias="updatedColumns",
    )
    updated_cells: int = Field(
        default=0,
        alias="updatedCells",
    )


class BatchUpdateValuesResponse(BaseModel):
    spreadsheet_id: SpreadsheetId = Field(
        ...,
        alias="spreadsheetId",
    )
    total_updated_rows: int = Field(
        default=0,
        alias="totalUpdatedRows",
    )
    total_updated_columns: int = Field(
        default=0,
        alias="totalUpdatedColumns",
    )
    total_updated_cells: int = Field(
        default=0,
        alias="totalUpdatedCells",
    )
    total_updated_sheets: int = Field(
        ...,
        alias="totalUpdatedSheets",
    )
    responses: list[UpdateValuesResponse]
