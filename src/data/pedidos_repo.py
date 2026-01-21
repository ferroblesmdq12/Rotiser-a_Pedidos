# src/data/pedidos_repo.py
from typing import Dict, Tuple

import pandas as pd
import gspread

from src.data.sheets_client import open_worksheet
from src.data.schemas import COL_ESTADO, COL_SHEET_ROW, ESTADOS_VALIDOS


def get_pedidos_df(spreadsheet_id: str, worksheet_name: str) -> pd.DataFrame:
    """
    Lee la pestaña del Google Sheet (que viene del Google Form) y devuelve un DataFrame
    con nombres de columnas normalizados para la app.
    Además agrega la columna _sheet_row para poder persistir updates por fila.
    """
    ws = open_worksheet(spreadsheet_id, worksheet_name)
    values = ws.get_all_values()

    if not values or len(values) < 2:
        return pd.DataFrame()

    header = values[0]
    rows = values[1:]

    df = pd.DataFrame(rows, columns=header)

    # Track sheet row number for updates (row 1 is header, first data row is 2)
    df[COL_SHEET_ROW] = range(2, 2 + len(df))

    # Map: headers reales del Form -> columnas internas usadas por la app
    col_map = {
        "Timestamp": "fecha_hora",
        "Tu nombre": "nombre_cliente",
        "Teléfono de contacto": "telefono",
        "¿Qué querés pedir ?": "mensaje",
        "Tipo de entrega": "tipo_entrega",
        "Dirección (solo si es Delivery)": "direccion",
        "Medio de pago": "medio_pago",
        # Estado puede venir como ESTADO, Estado o estado
        "ESTADO": COL_ESTADO,
        "Estado": COL_ESTADO,
        "estado": COL_ESTADO,
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Si no existe estado, lo creamos para que la UI no se rompa
    if COL_ESTADO not in df.columns:
        df[COL_ESTADO] = ""

    df[COL_ESTADO] = df[COL_ESTADO].fillna("").astype(str)

    return df


def _find_col_index(header_row: list, col_name: str) -> int:
    """
    Devuelve índice 1-based (gspread) de la columna.
    Permite matching exacto o case-insensitive (por ejemplo, ESTADO vs estado).
    """
    # Match exacto
    if col_name in header_row:
        return header_row.index(col_name) + 1

    # Match case-insensitive
    header_lower = [str(h).strip().lower() for h in header_row]
    target = str(col_name).strip().lower()

    if target in header_lower:
        return header_lower.index(target) + 1

    raise ValueError(f"La hoja no tiene la columna requerida: '{col_name}'")


def update_estados(
    spreadsheet_id: str,
    worksheet_name: str,
    updates: Dict[int, str],
) -> Tuple[int, int]:
    """
    updates: {sheet_row_number: new_estado}
    Returns (updated_count, skipped_count)

    - Localiza la columna 'estado' aunque en la hoja figure como 'ESTADO' (case-insensitive).
    - Valida que el estado esté dentro de ESTADOS_VALIDOS.
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

        cell_list.append(gspread.Cell(row=int(row_num), col=int(col_estado), value=estado_clean))

    if cell_list:
        ws.update_cells(cell_list, value_input_option="USER_ENTERED")

    return len(cell_list), skipped
