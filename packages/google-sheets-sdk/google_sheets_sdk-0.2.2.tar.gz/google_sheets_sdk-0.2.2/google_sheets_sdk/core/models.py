import time as t
from dataclasses import InitVar, dataclass, field

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
class Token:
    email: InitVar[str]
    base_url: InitVar[str]

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
        base_url: str,
    ):
        self._iss = self._sub = email
        self._aud = base_url
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
