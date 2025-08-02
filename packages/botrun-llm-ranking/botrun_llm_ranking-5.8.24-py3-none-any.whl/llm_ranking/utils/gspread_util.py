import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Optional


def read_google_sheet(
    credentials_path: str, spreadsheet_id: str, sheet_name: str
) -> pd.DataFrame:
    """
    讀取 Google Spreadsheet 指定 sheet，回傳 pandas DataFrame。
    """
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=scopes
    )
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    )
    values = result.get("values", [])
    if not values:
        return pd.DataFrame()
    # 第一列為欄位名稱
    df = pd.DataFrame(values[1:], columns=values[0])
    return df


def write_google_sheet(
    credentials_path: str,
    spreadsheet_id: str,
    sheet_name: str,
    df: pd.DataFrame,
) -> Optional[str]:
    """
    將 DataFrame 寫入 Google Spreadsheet 的新頁籤(sheet_name)。
    若成功回傳頁籤名稱，否則回傳 None。
    """
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=scopes
    )
    service = build("sheets", "v4", credentials=credentials)
    # 新增頁籤
    requests = [{"addSheet": {"properties": {"title": sheet_name}}}]
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()
    except Exception as e:
        # 若頁籤已存在則略過
        pass
    # 寫入資料
    values = [df.columns.tolist()] + df.values.tolist()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=sheet_name,
        valueInputOption="RAW",
        body={"values": values},
    ).execute()
    return sheet_name
