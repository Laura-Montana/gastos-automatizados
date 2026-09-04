import os
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv

# Configuración de página
st.set_page_config(
    page_title="Dashboard de Gastos",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores extraída de la imagen
PALETA = ["#073042", "#245D75", "#568FA8", "#9CC8DB", "#DBF4FF"]

# Estilos CSS estilo Notion + Fintech
st.markdown(f"""
    <style>
    /* Estilo global tipo Notion */
    .stApp {{
        background-color: #FBFBFB;
        font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Apple Color Emoji, Arial, sans-serif;
        color: #37352F;
    }}
    
    /* Tarjetas redondeadas */
    div[data-testid="stMetric"] {{
        background-color: #FFFFFF;
        border: 1px solid #E9E9E7;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0px 1px 3px rgba(15, 15, 15, 0.05);
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem;
        font-weight: 600;
        color: {PALETA[0]};
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 0.85rem;
        font-weight: 500;
        color: #787774;
    }}

    /* Estilos para Sidebar estilo Notion */
    section[data-testid="stSidebar"] {{
        background-color: #F7F6F3;
        border-right: 1px solid #E9E9E7;
    }}

    /* Pestañas limpias */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 16px;
        border-bottom: 1px solid #E9E9E7;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        font-weight: 500;
        color: #787774;
        border-radius: 6px;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {PALETA[0]};
        background-color: #EFEFE2;
    }}
    
    /* Botones con bordes redondeados */
    .stButton>button {{
        border-radius: 8px;
        border: 1px solid #E9E9E7;
        background-color: #FFFFFF;
        color: {PALETA[0]};
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stButton>button:hover {{
        background-color: {PALETA[4]};
        border-color: {PALETA[3]};
        color: {PALETA[0]};
    }}
    </style>
""", unsafe_allow_html=True)

load_dotenv()

@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        return None
    
    try:
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

@st.cache_data(ttl=300)
def cargar_datos():
    if supabase:
        try:
            response = supabase.table("movimientos").select("*").order("fecha", desc=True).limit(1000).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                df['fecha'] = pd.to_datetime(df['fecha'])
                return df
        except Exception:
            pass
    
    try:
        df = pd.read_csv('data/movimientos.csv')
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except Exception:
        return crear_datos_ejemplo()

def crear_datos_ejemplo():
    fechas = pd.date_range(start='2024-01-01', periods=180, freq='D')
    data = {
        'fecha': fechas,
        'monto': [120, 250, 45, 310, 85, 95, 200, 150, 60, 180] * 18,
        'tipo': ['gasto'] * 140 + ['ingreso'] * 40,
        'comercio': ['Supermercado', 'Restaurante', 'Transporte', 'Tienda', 'Servicios'] * 36,
        'categoria': ['Mercado', 'Restaurantes', 'Transporte', 'Compras', 'Servicios'] * 36,
        'banco': ['Nequi', 'Bancolombia', 'Nu'] * 60,
    }
    return pd.DataFrame(data)

@st.cache_data
def cargar_categorias_personalizadas():
    try:
        with open('data/categorias_personalizadas.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def guardar_categoria_personalizada(comercio, categoria):
    # 1. Guardar en el mapa JSON
    categorias = cargar_categorias_personalizadas()
    categorias[comercio] = categoria
    
    os.makedirs('data', exist_ok=True)
    with open('data/categorias_personalizadas.json', 'w') as f:
        json.dump(categorias, f, indent=2)
    
    # 2. Actualizar registros en Supabase (si está conectado)
    if supabase:
        try:
            supabase.table("movimientos").update({"categoria": categoria}).eq("comercio", comercio).execute()
        except Exception as e:
            st.error(f"Error al actualizar Supabase: {e}")
            return False

    # 3. Limpiar la caché de datos para forzar la recarga
    st.cache_data.clear()
    return True

def main():
    st.title("Control Financiero")
    st.markdown("---")
    
    df = cargar_datos()
    
    if df.empty:
        st.warning("No hay registros disponibles.")
        return
    
    max_date = df['fecha'].max().date()
    min_date = df['fecha'].min().date()
    

# Sidebar con organización renovada
    with st.sidebar:
        st.subheader("Filtros")
        
        # Accesos rápidos de fecha
        periodo = st.radio(
            "Período rápido",
            ['Personalizado', 'Hoy', 'Este mes', 'Últimos 6 meses'],
            index=0
        )
        
        # Fecha real de hoy (sistema)
        hoy_real = datetime.now().date()
        
        if periodo == 'Hoy':
            fecha_inicio_val = hoy_real
            fecha_fin_val = hoy_real
        elif periodo == 'Este mes':
            fecha_inicio_val = hoy_real.replace(day=1)
            fecha_fin_val = hoy_real
        elif periodo == 'Últimos 6 meses':
            fecha_inicio_val = hoy_real - timedelta(days=180)
            fecha_fin_val = hoy_real
        else:
            fecha_inicio_val = min_date
            fecha_fin_val = max_date

        # Ajustamos los límites permitidos para que acepten fechas anteriores si se eligen los últimos 6 meses
        min_date_input = min(min_date, hoy_real, fecha_inicio_val)
        max_date_input = max(max_date, hoy_real, fecha_fin_val)
            
        fecha_inicio = st.date_input("Fecha inicial", fecha_inicio_val, min_value=min_date_input, max_value=max_date_input)
        fecha_fin = st.date_input("Fecha final", fecha_fin_val, min_value=min_date_input, max_value=max_date_input)
        
        st.markdown("---")
        
        categorias = ['Todas'] + sorted(df['categoria'].unique().tolist())
        categoria_seleccionada = st.selectbox("Categoría", categorias)
        
        bancos = ['Todos'] + sorted(df['banco'].unique().tolist())
        banco_seleccionado = st.selectbox("Banco", bancos)
        
        tipo_seleccionado = st.radio("Tipo de movimiento", ['Todos', 'Gastos', 'Ingresos'])
        
        if st.button("Actualizar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
            
        st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

    # Filtrado de DataFrame
    df_filtrado = df[
        (df['fecha'].dt.date >= fecha_inicio) &
        (df['fecha'].dt.date <= fecha_fin)
    ].copy()
    
    if categoria_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_seleccionada]
        
    if banco_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['banco'] == banco_seleccionado]
    
    if tipo_seleccionado == 'Gastos':
        df_filtrado = df_filtrado[df_filtrado['tipo'] == 'gasto']
    elif tipo_seleccionado == 'Ingresos':
        df_filtrado = df_filtrado[df_filtrado['tipo'] == 'ingreso']
    
    gastos = df_filtrado[df_filtrado['tipo'] == 'gasto']
    ingresos = df_filtrado[df_filtrado['tipo'] == 'ingreso']
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Gastos", f"${gastos['monto'].sum():,.2f}", delta=f"{len(gastos)} movs")
    with col2:
        st.metric("Total Ingresos", f"${ingresos['monto'].sum():,.2f}", delta=f"{len(ingresos)} movs")
    with col3:
        balance = ingresos['monto'].sum() - gastos['monto'].sum()
        st.metric("Balance", f"${balance:,.2f}", delta=f"${balance:,.2f}", delta_color="normal" if balance >= 0 else "inverse")
    with col4:
        st.metric("Movimientos", len(df_filtrado))
    with col5:
        promedio = gastos['monto'].mean() if len(gastos) > 0 else 0
        st.metric("Gasto Promedio", f"${promedio:,.2f}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución de Gastos")
        if len(gastos) > 0:
            gastos_por_categoria = gastos.groupby('categoria')['monto'].sum().reset_index()
            fig = px.pie(
                gastos_por_categoria,
                values='monto',
                names='categoria',
                color_discrete_sequence=PALETA
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos para mostrar en este período.")
            
    with col2:
        st.subheader("Comparativa por Meses")
        if len(df_filtrado) > 0:
            df_meses = df_filtrado.copy()
            df_meses['mes_año'] = df_meses['fecha'].dt.to_period('M').astype(str)
            resumen_mes = df_meses.groupby(['mes_año', 'tipo'])['monto'].sum().reset_index()
            
            fig = px.bar(
                resumen_mes,
                x='mes_año',
                y='monto',
                color='tipo',
                barmode='group',
                labels={'mes_año': 'Mes', 'monto': 'Monto ($)', 'tipo': 'Tipo'},
                color_discrete_map={'gasto': PALETA[1], 'ingreso': PALETA[3]}
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#37352F")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos para mostrar en este período.")

    # Gráficos de apoyo
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Gastos por Entidad Bancaria")
        if len(gastos) > 0:
            gastos_por_banco = gastos.groupby('banco')['monto'].sum().reset_index()
            fig = px.bar(
                gastos_por_banco,
                x='banco',
                y='monto',
                color_discrete_sequence=[PALETA[0]],
                labels={'banco': 'Banco', 'monto': 'Monto ($)'}
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos para mostrar en este período.")
            
    with col4:
        st.subheader("Evolución Temporal de Gastos")
        if len(gastos) > 0:
            gastos_diarios = gastos.groupby(gastos['fecha'].dt.date)['monto'].sum().reset_index()
            fig = px.line(
                gastos_diarios,
                x='fecha',
                y='monto',
                labels={'fecha': 'Fecha', 'monto': 'Monto ($)'}
            )
            fig.update_traces(line=dict(width=2, color=PALETA[0]))
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos para mostrar en este período.")

    st.markdown("---")
    
    # Gestión de Movimientos
    st.subheader("Gestión de Movimientos")
    tab1, tab2, tab3 = st.tabs(["Detalle de Movimientos", "Categorización Manual", "Estadísticas Avanzadas"])
    
    with tab1:
        df_mostrar = df_filtrado.sort_values('fecha', ascending=False).copy()
        df_mostrar['monto'] = df_mostrar['monto'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            df_mostrar[['fecha', 'comercio', 'monto', 'categoria', 'banco', 'tipo']],
            use_container_width=True,
            column_config={
                "fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                "comercio": "Comercio",
                "monto": "Monto",
                "categoria": "Categoría",
                "banco": "Banco",
                "tipo": "Tipo",
            },
            hide_index=True
        )
        
    with tab2:
            # Buscar en el DataFrame general (df) y no solo en el filtrado (df_filtrado)
            sin_categorizar = df[df['categoria'] == 'Sin categorizar'].copy()
            
            if len(sin_categorizar) == 0:
                st.success("Todos los movimientos de la base de datos están categorizados.")
            else:
                st.caption(f"Registros pendientes por categorizar: {len(sin_categorizar)}")
                
                # Crear lista única por comercio para no repetir la misma regla varias veces
                comercios_sin_cat = sorted(sin_categorizar['comercio'].unique().tolist())
                comercio_sel = st.selectbox("Seleccione el comercio a categorizar", comercios_sin_cat)
                
                if comercio_sel:
                    # Obtener un movimiento de ejemplo de este comercio
                    ejemplo = sin_categorizar[sin_categorizar['comercio'] == comercio_sel].iloc[0]
                    
                    col_det, col_acc = st.columns([2, 1])
                    with col_det:
                        st.markdown(f"**Comercio:** `{comercio_sel}`")
                        st.markdown(f"**Último monto registrado:** `${ejemplo['monto']:,.2f}`")
                        st.markdown(f"**Banco:** `{ejemplo['banco']}`")
                        st.caption("Al categorizar este comercio, se actualizarán todas las transacciones pasadas y futuras asociadas a él.")
                        
                    with col_acc:
                        nueva_categoria = st.text_input("Nueva categoría (Escribir)")
                        
                        # Filtrar categorías existentes excluyendo 'Sin categorizar'
                        categorias_existentes = sorted([c for c in df['categoria'].unique() if c != 'Sin categorizar'])
                        categoria_sugerida = st.selectbox("O elegir de la lista existente", [""] + categorias_existentes)
                        
                        # Prioridad a la escrita manualmente si ambas son llenadas
                        cat_final = nueva_categoria.strip() if nueva_categoria.strip() else categoria_sugerida
                        
                        if st.button("Guardar y Aplicar Categoría", type="primary", use_container_width=True):
                            if cat_final:
                                if guardar_categoria_personalizada(comercio_sel, cat_final):
                                    st.success(f"¡Listo! Se asignó '{cat_final}' a '{comercio_sel}'.")
                                    st.rerun()
                            else:
                                st.warning("Por favor escribe o selecciona una categoría válida.")

    with tab3:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.write("**Mayores Gastos por Categoría**")
            if len(gastos) > 0:
                top_cat = gastos.groupby('categoria')['monto'].sum().sort_values(ascending=False).head(5)
                for cat, monto in top_cat.items():
                    st.write(f"- **{cat}**: ${monto:,.2f}")
                    
        with col_t2:
            st.write("**Mayores Gastos por Comercio**")
            if len(gastos) > 0:
                top_com = gastos.groupby('comercio')['monto'].sum().sort_values(ascending=False).head(5)
                for com, monto in top_com.items():
                    st.write(f"- **{com}**: ${monto:,.2f}")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="Exportar datos a CSV",
            data=df_filtrado.to_csv(index=False),
            file_name=f"reporte_gastos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()