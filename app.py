import streamlit as st
import pandas as pd

# Título de la app
st.title("Visualizador de Garantías (Datos Compartidos con Mesa)")

# Subida de archivos
st.subheader("Subí los archivos necesarios")
ARCHIVO_GARANTIAS = st.file_uploader("Archivo de garantías", type=["xlsx"])
ARCHIVO_PRECIOS = st.file_uploader("Archivo de precios de títulos", type=["xlsx"])
ARCHIVO_AFOROS = st.file_uploader("Archivo de aforos", type=["xlsx"])

# Validación de que todos los archivos estén subidos
if ARCHIVO_GARANTIAS and ARCHIVO_PRECIOS and ARCHIVO_AFOROS:
    # Cargar los datos
    df_garantias = pd.read_excel(ARCHIVO_GARANTIAS)
    df_precios = pd.read_excel(ARCHIVO_PRECIOS)
    df_aforos = pd.read_excel(ARCHIVO_AFOROS)

    # Convertir a string para hacer merge
    df_precios["Cód."] = df_precios["Cód."].astype(str)
    df_garantias["Instrumento - Código Caja"] = df_garantias["Instrumento - Código Caja"].astype(str)
    df_aforos["Código CVSA"] = df_aforos["Código CVSA"].astype(str)

    # Merge de datos.
    df_precios_aforo = df_precios.merge(df_aforos, left_on="Cód.", right_on="Código CVSA", how="left")

    df_merged = df_garantias.merge(df_precios_aforo, left_on="Instrumento - Código Caja", right_on="Cód.", how="left")

    df_merged["ValorTotalAforo"] = df_merged["Saldo"] * df_merged["Valor"] * df_merged["Aforo"] /100

    # Mostrar tabla
    st.subheader("Datos actuales:")
    columnas_a_mostrar = ['Comitente - Número', 'Custodia', 'Instrumento - Código Caja',"Instrumento - Símbolo",'Saldo',"Valor","Aforo","ValorTotalAforo"]
    st.dataframe(df_merged[columnas_a_mostrar])

    # Agregar nueva fila
    st.subheader("Agregar nueva fila:")
    nuevo_comitente = st.text_input("Comitente - Número")
    nueva_custodia = st.text_input("Custodia")
    nuevo_codigo = st.text_input("Instrumento - Código Caja")
    nuevo_saldo = st.number_input("Saldo", value=0.0)

    if st.button("Agregar fila"):
        nueva_fila = {
            'Comitente - Número': nuevo_comitente,
            'Custodia': nueva_custodia,
            'Instrumento - Código Caja': nuevo_codigo,
            'Saldo': nuevo_saldo
        }
        df_garantias = pd.concat([df_garantias, pd.DataFrame([nueva_fila])], ignore_index=True)
        st.success("Fila agregada correctamente. Volvé a subir el archivo actualizado para ver los cambios.")

    # Egreso de saldo existente
    st.subheader("Egresar saldo:")
    comitente_egreso = st.text_input("Comitente para egreso")
    codigo_egreso = st.text_input("Código Caja para egreso")
    saldo_egreso = st.number_input("Saldo a egresar", value=0.0, key="egreso")

    if st.button("Egresar"):
        mask = (
            (df_garantias['Comitente - Número'].astype(str) == comitente_egreso) &
            (df_garantias['Instrumento - Código Caja'].astype(str) == codigo_egreso)
        )
        if df_garantias[mask].empty:
            st.error("No se encontró esa combinación para egreso.")
        else:
            index = df_garantias[mask].index[0]
            if df_garantias.at[index, 'Saldo'] < saldo_egreso:
                st.error("El saldo a egresar excede el disponible.")
            else:
                df_garantias.at[index, 'Saldo'] -= saldo_egreso
                st.success("Egreso realizado. Volvé a subir el archivo actualizado para ver los cambios.")

    # Descarga por comitente
    st.subheader("Descargar archivos separados por Comitente")
    df_mostrar = df_merged[columnas_a_mostrar]

    comitentes_unicos = df_mostrar["Comitente - Número"].dropna().unique()

    for comitente in comitentes_unicos:
        df_filtrado = df_mostrar[df_mostrar["Comitente - Número"] == comitente]

        nombre_archivo = f"comitente_{comitente}.xlsx"
        with pd.ExcelWriter(nombre_archivo, engine='xlsxwriter') as writer:
            df_filtrado.to_excel(writer, index=False)

        with open(nombre_archivo, "rb") as file:
            st.download_button(
                label=f"📥 Descargar {comitente}",
                data=file,
                file_name=nombre_archivo,
                key=f"download_{comitente}"
            )


else:
    st.warning("Por favor, subí los 3 archivos necesarios para continuar.")
