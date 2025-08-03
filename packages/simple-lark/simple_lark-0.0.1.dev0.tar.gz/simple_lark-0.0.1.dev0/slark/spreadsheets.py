from typing import Any, List, Literal

from pydantic import BaseModel

from .auth import UserIdType
from .base import EndPointKit, api


class SpreadSheetCreateBody(BaseModel):
    title: str
    folder_token: str


class SpreadSheetCreated(BaseModel):
    title: str
    folder_token: str
    url: str
    spreadsheet_token: str


class SpreadSheetCreateResp(BaseModel):
    spreadsheet: SpreadSheetCreated


class BasicInfo(BaseModel):
    title: str
    owner_id: str
    token: str
    url: str


class BasicInfoResp(BaseModel):
    spreadsheet: BasicInfo


class ValueRange(BaseModel):
    range: str  # 格式为 <sheetId>!<开始位置>:<结束位置>。其中：
    # <sheetId> 为工作表 ID，开始位置和结束位置的格式为 <列字母><行数字>，例如 A1 表示第一列第一行。
    values: List[List[Any]]  # NOQA


class GridProperties(BaseModel):
    frozen_row_count: int
    frozen_column_count: int
    row_count: int
    column_count: int


class MergeRange(BaseModel):
    start_row_index: int
    end_row_index: int
    start_column_index: int
    end_column_inde: int


class SheetInfo(BaseModel):
    sheet_id: str
    title: str
    index: int
    hidden: bool
    grid_properties: GridProperties | None = None
    resource_type: Literal["sheet", "bitable", "#UNSUPPORTED_TYPE"]
    merges: List[MergeRange]  # NOQA


class QueryResp(BaseModel):
    sheets: List[SheetInfo]  # NOQA


class UpdateValuesResp(BaseModel):
    revision: int
    spreadsheetToken: str
    updatedCells: int
    updatedColumns: int
    updatedRange: str
    updatedRows: int


class SpreadSheets(EndPointKit):
    @api("/sheets/v3/spreadsheets", method="POST")
    def create(self, body: SpreadSheetCreateBody) -> SpreadSheetCreateResp:
        """
        创建 spreadsheet
        :see https://open.larkoffice.com/document/server-docs/docs/sheets-v3/spreadsheet/create
        :param body:
        :return:
        """

    @api("/sheets/v3/spreadsheets/:spreadsheet_token")
    def basic_info(self, spreadsheet_token: str, user_id_type: UserIdType = "open_id") -> BasicInfoResp:
        """
        获取表格基本信息
        see: https://open.larkoffice.com/document/server-docs/docs/sheets-v3/spreadsheet/get
        :param spreadsheet_token:
        :param user_id_type:
        :return:
        """

    @api("/sheets/v3/spreadsheets/:spreadsheet_token/sheets/query")
    def query_sheets(self, spreadsheet_token: str) -> QueryResp:
        """
        获取工作表
        https://open.larkoffice.com/document/server-docs/docs/sheets-v3/spreadsheet-sheet/query

        Args:
            spreadsheet_token: str
        """

    @api("/sheets/v2/spreadsheets/:spreadsheetToken/values", method="PUT")
    def write(self, spreadsheetToken: str, values: ValueRange) -> UpdateValuesResp:
        """
        更新表格数据
        see: https://open.larkoffice.com/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range
        :param spreadsheetToken:
        :param values:
        :return:
        """
