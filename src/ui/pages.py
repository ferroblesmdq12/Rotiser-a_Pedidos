# src/ui/pages.py
import streamlit as st
import pandas as pd

from src.data.pedidos_repo import get_pedidos_df, update_estados
from src.data.schemas import COL_ESTADO
from src.ui.components import render_filters, apply_filters, build_edit_table, compute_estado_updates


def pedidos_page(spreadsheet_id: str, worksheet_name: str, role: str):
    st.title("Pedidos")
    st.caption("Fuente: Google Sheets. Edición de estado persistida en la hoja.")

    df = get_pedidos_df(spreadsheet_id, worksheet_name)

    if df.empty:
        st.info("No hay pedidos todavía en la hoja seleccionada.")
        return

    if COL_ESTADO not in df.columns:
        st.error("La pestaña no tiene la columna 'estado'. Agregala para poder editar estados.")
        return

    estado, q = render_filters(df)
    df_view = apply_filters(df, estado, q)

    edited = build_edit_table(df_view)

    if st.button("Guardar cambios", type="primary"):
        updates = compute_estado_updates(df, edited)

        if not updates:
            st.info("No hay cambios para guardar.")
            return

        try:
            updated, skipped = update_estados(spreadsheet_id, worksheet_name, updates)
            if updated:
                st.success(f"Cambios guardados: {updated}. Omitidos: {skipped}.")
                st.rerun()
            else:
                st.warning(f"No se guardó ningún cambio. Omitidos: {skipped}.")
        except Exception as e:
            st.error(f"Error al guardar cambios: {e}")
