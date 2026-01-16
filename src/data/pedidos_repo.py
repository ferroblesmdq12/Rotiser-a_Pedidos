from typing import Dict, Tuple

import pandas as pd
import gspread

from src.data.sheets_client import open_worksheet, get_gspread_client
from src.data.schemas import COL_ESTADO, COL_SHEET_ROW, ESTADOS_VALIDOS


def get_pedidos_df(spreadsheet_id: str, worksheet_name: str) -> pd.DataFrame:
    ws = open_worksheet(spreadsheet_id, worksheet_name)
    values = ws.get_all_values()

    if not values or len(values) < 2:
        return pd.DataFrame()

    header = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows, columns=header)

    # Track sheet row number for updates (row 1 is header, first data row is 2)
    df[COL_SHEET_ROW] = range(2, 2 + len(df))

    # Ensure estado exists in df
    if COL_ESTADO not in df.columns:
        # If the sheet doesn't have 'estado', we can't support the dropdown update.
        # We'll keep it absent and let UI error out.
        return df

    df[COL_ESTADO] = df[COL_ESTADO].fillna("").astype(str)
    return df


def _find_col_index(header_row: list, col_name: str) -> int:
    if col_name not in header_row:
        raise ValueError(f"La hoja no tiene la columna requerida: '{col_name}'")
    return header_row.index(col_name) + 1  # 1-based for gspread


def update_estados(
    spreadsheet_id: str,
    worksheet_name: str,
    updates: Dict[int, str],
) -> Tuple[int, int]:
    """
    updates: {sheet_row_number: new_estado}
    Returns (updated_count, skipped_count)
    """
    if not updates:
        return 0, 0

    ws = open_worksheet(spreadsheet_id, worksheet_name)
    header = ws.row_values(1)
    col_estado = _find_col_index(header, COL_ESTADO)

    cell_list = []
    skipped = 0

    for row_num, estado in updates.items():
        estado_clean = (estado or "").strip()
        if not estado_clean:
            skipped += 1
            continue
        if estado_clean not in ESTADOS_VALIDOS:
            skipped += 1
            continue
        cell_list.append(gspread.Cell(row=row_num, col=col_estado, value=estado_clean))

    if cell_list:
        ws.update_cells(cell_list, value_input_option="USER_ENTERED")

    return len(cell_list), skipped
