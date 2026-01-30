# src/ui/components.py
from typing import Dict, Tuple

import pandas as pd
import streamlit as st

from src.data.schemas import ESTADOS_VALIDOS, COL_ESTADO, COL_SHEET_ROW


def render_filters(df: pd.DataFrame) -> Tuple[str, str]:
    col1, col2 = st.columns(2)

    with col1:
        estado = st.selectbox("Filtrar por estado", ["(Todos)"] + ESTADOS_VALIDOS)

    with col2:
        q = st.text_input("Buscar (nombre / teléfono / pedido / dirección)")

    return estado, q


def apply_filters(df: pd.DataFrame, estado: str, q: str) -> pd.DataFrame:
    out = df.copy()

    if estado != "(Todos)" and COL_ESTADO in out.columns:
        out = out[out[COL_ESTADO].astype(str) == estado]

    if q and q.strip():
        s = q.strip().lower()
        search_cols = [c for c in ["nombre_cliente", "telefono", "mensaje", "direccion"] if c in out.columns]
        if search_cols:
            mask = False
            for c in search_cols:
                mask = mask | out[c].astype(str).str.lower().str.contains(s, na=False)
            out = out[mask]

    return out


def build_edit_table(df_view: pd.DataFrame) -> pd.DataFrame:
    """
    Data editor that allows editing only 'estado'. Uses _sheet_row to map updates.
    """
    # Choose columns to show if they exist
    preferred = [c for c in [
        "pedido_id", "fecha_hora", "nombre_cliente", "telefono", "mensaje",
        "tipo_entrega", "direccion", "medio_pago", "total_estimado", "estado", "canal"
    ] if c in df_view.columns]

    # Ensure _sheet_row exists
    if COL_SHEET_ROW not in df_view.columns:
        df_view[COL_SHEET_ROW] = range(2, 2 + len(df_view))

    df_show = df_view[preferred + [COL_SHEET_ROW]].copy()

    edited = st.data_editor(
        df_show,
        hide_index=True,
        use_container_width=True,
        column_config={
            COL_ESTADO: st.column_config.SelectboxColumn(
                COL_ESTADO,
                options=ESTADOS_VALIDOS,
                required=False,
                help="Seleccioná el estado del pedido."
            ),
            COL_SHEET_ROW: st.column_config.NumberColumn(COL_SHEET_ROW, disabled=True)
        },
        disabled=[c for c in df_show.columns if c != COL_ESTADO],
        key="pedidos_editor"
    )

    return edited


def compute_estado_updates(df_original: pd.DataFrame, df_edited: pd.DataFrame) -> Dict[int, str]:
    """
    Returns {sheet_row: new_estado} for changes only.
    """
    if df_original.empty or df_edited.empty:
        return {}

    base = df_original.set_index(COL_SHEET_ROW)[COL_ESTADO].astype(str).to_dict()
    updates: Dict[int, str] = {}

    for _, row in df_edited.iterrows():
        sheet_row = int(row[COL_SHEET_ROW])
        new_estado = str(row.get(COL_ESTADO, "")).strip()
        old_estado = str(base.get(sheet_row, "")).strip()

        if new_estado and new_estado != old_estado:
            updates[sheet_row] = new_estado

    return updates
