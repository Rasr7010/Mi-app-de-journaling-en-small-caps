import streamlit as st
import pandas as pd
from datetime import date
import altair as alt
import calendar
from supabase import create_client, Client

st.set_page_config(page_title="Trading Journal", page_icon="📈", layout="centered")

# ──────────────────────────────────────────────
#  INICIALIZACIÓN DE SUPABASE Y SESIÓN
# ──────────────────────────────────────────────
url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if 'user' not in st.session_state:
    st.session_state.user = None

# Restaurar sesión si existe
if 'access_token' in st.session_state and 'refresh_token' in st.session_state:
    try:
        supabase.auth.set_session(st.session_state['access_token'], st.session_state['refresh_token'])
    except:
        st.session_state.user = None

# ──────────────────────────────────────────────
#  TEMA OSCURO Y CSS (Simplificado para el Login)
# ──────────────────────────────────────────────
dark_theme_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background-color: #0a0e1a !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
h1, h2, h3 { color: #f8fafc !important; }
[data-testid="stSidebar"] { display: none !important; }
.section-label { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #3b82f6; margin-bottom: 8px; display: block; }
</style>
"""
st.markdown(dark_theme_css, unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  SISTEMA DE AUTENTICACIÓN (LOGIN / REGISTRO)
# ──────────────────────────────────────────────
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center;'>🔐 Trading Journal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Inicia sesión para acceder a tu historial privado</p>", unsafe_allow_html=True)
    
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
    
    with tab_login:
        email_login = st.text_input("Correo electrónico", key="login_email")
        pass_login = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Entrar", type="primary", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email_login, "password": pass_login})
                st.session_state.user = res.user
                st.session_state['access_token'] = res.session.access_token
                st.session_state['refresh_token'] = res.session.refresh_token
                st.rerun()
            except Exception as e:
                st.error("Error al iniciar sesión. Verifica tus credenciales.")
                
    with tab_registro:
        email_reg = st.text_input("Nuevo Correo electrónico", key="reg_email")
        pass_reg = st.text_input("Nueva Contraseña (mínimo 6 caracteres)", type="password", key="reg_pass")
        if st.button("Registrarse", use_container_width=True):
            try:
                res = supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                st.success("¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
            except Exception as e:
                st.error(f"Error al registrar: {e}")
                
    st.stop() # Detiene la ejecución aquí si no hay usuario logueado

# ──────────────────────────────────────────────
#  A PARTIR DE AQUÍ: EL USUARIO ESTÁ LOGUEADO
# ──────────────────────────────────────────────
col_titulo, col_logout = st.columns([4, 1])
with col_titulo:
    st.title("⬛ Trading Journal — Small Caps")
with col_logout:
    st.write("")
    if st.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()

# ──────────────────────────────────────────────
#  FUNCIONES DE PROCESAMIENTO
# ──────────────────────────────────────────────
def procesar_historial(texto_completo):
    ejecuciones = []
    lineas = texto_completo.splitlines()
    for linea in lineas:
        linea = linea.strip().replace('\x00', '')
        if not linea: continue
        partes = [p.strip() for p in linea.split(',')]
        p_validas = [p for p in partes if p != '']
        if len(p_validas) < 5: continue
        estado = p_validas[1].upper()
        if 'FILLED' not in estado: continue
        try:
            hora = p_validas[0]
            ticker = p_validas[2]
            lado = p_validas[3].upper()
            acciones = int(p_validas[4])
            precio_real = 0.0
            ult = p_validas[-1]
            pen = p_validas[-2]
            if ult.replace('.', '').isdigit() and pen.replace('.', '').isdigit():
                precio_real = float(f"{pen}.{ult}")
            elif ult.replace('.', '').isdigit():
                precio_real = float(ult)
            if precio_real > 0:
                ejecuciones.append({'Hora': hora, 'Ticker': ticker, 'Lado': lado, 'Acciones': acciones, 'Precio_Ejecucion': precio_real})
        except: continue
    return pd.DataFrame(ejecuciones)

def calcular_trades(df, fecha):
    trades = []
    for ticker, df_ticker in df.groupby('Ticker'):
        inventario = 0
        flujo_caja = 0.0
        acciones_totales = 0
        hora_inicio = None
        for index, row in df_ticker.iterrows():
            if inventario == 0: hora_inicio = row['Hora']
            qty = row['Acciones']
            precio = row['Precio_Ejecucion']
            if row['Lado'] in ['BUY']:
                inventario += qty
                flujo_caja -= (qty * precio)
            elif row['Lado'] in ['SELL', 'SSHRT']:
                inventario -= qty
                flujo_caja += (qty * precio)
            acciones_totales += qty
            if inventario == 0:
                pnl = round(flujo_caja, 2)
                tipo_trade = "Short" if row['Lado'] == 'BUY' else "Long"
                trades.append({
                    'Fecha': str(fecha), 'Ticker': ticker, 'Tipo': tipo_trade,
                    'Hora Inicio': hora_inicio, 'Hora Fin': row['Hora'],
                    'Volumen (Acciones)': acciones_totales // 2, 'PnL ($)': pnl,
                    'Tags': ""
                })
                flujo_caja = 0.0
                acciones_totales = 0
    return pd.DataFrame(trades).sort_values(by=['Fecha', 'Hora Inicio']).reset_index(drop=True)

# ──────────────────────────────────────────────
#  DESCARGAR DATOS DEL USUARIO DESDE SUPABASE
# ──────────────────────────────────────────────
@st.cache_data(ttl=5) # Refresca los datos cada 5 segundos
def obtener_datos_usuario():
    # RLS en Supabase garantiza que esto solo traiga los datos del usuario logueado
    res = supabase.table('historial_operaciones').select('*').execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df = df.rename(columns={
            'fecha': 'Fecha', 'ticker': 'Ticker', 'tipo': 'Tipo',
            'hora_inicio': 'Hora Inicio', 'hora_fin': 'Hora Fin',
            'volumen': 'Volumen (Acciones)', 'pnl': 'PnL ($)', 'tags': 'Tags'
        })
    return df

df_historico = obtener_datos_usuario()

# Extraer Tags Únicos
tags_unicos = []
if not df_historico.empty and 'Tags' in df_historico.columns:
    for tag_val in df_historico['Tags'].dropna():
        tag_str = str(tag_val)
        if tag_str.strip() != "" and tag_str.strip() != "None":
            tags_unicos.extend([t.strip() for t in tag_str.split(',')])
tags_unicos = sorted(list(set(tags_unicos)))

if 'mis_tags' not in st.session_state:
    st.session_state['mis_tags'] = tags_unicos

# ──────────────────────────────────────────────
#  INTERFAZ PRINCIPAL
# ──────────────────────────────────────────────
tab1, tab_filtros, tab2, tab4 = st.tabs(["  Ingreso  ", "  Filtros  ", "  Estadísticas  ", "  Historial  "])

with tab1:
    st.markdown('<span class="section-label">Nueva sesión de trading</span>', unsafe_allow_html=True)
    col_fecha, col_archivo = st.columns([1, 2])
    with col_fecha:
        fecha_operativa = st.date_input("Fecha de sesión", date.today())
    with col_archivo:
        uploaded_file = st.file_uploader("Archivo .txt de Sterling Trader Pro", type=["txt"])

    if uploaded_file is not None:
        texto = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        df_crudo = procesar_historial(texto)
        
        if df_crudo.empty:
            st.error("No se encontraron órdenes válidas.")
        else:
            df_trades_dia = calcular_trades(df_crudo, fecha_operativa)
            st.success(f"{len(df_trades_dia)} trades procesados.")
            
            # Formulario para tags
            c1, c2 = st.columns([3, 1])
            with c1: nuevo_tag = st.text_input("Crear nuevo tag:")
            with c2:
                st.write("")
                st.write("")
                if st.button("+ Añadir"):
                    if nuevo_tag and nuevo_tag not in st.session_state['mis_tags']:
                        st.session_state['mis_tags'].append(nuevo_tag)
                        st.rerun()

            edited_df = st.data_editor(
                df_trades_dia, use_container_width=True, num_rows="dynamic",
                column_config={"Tags": st.column_config.SelectboxColumn("Tags (Setups)", options=st.session_state['mis_tags'])}
            )

            if st.button(f"Guardar trades en la nube", type="primary"):
                # Preparar datos para Supabase
                df_to_upload = edited_df.rename(columns={
                    'Fecha': 'fecha', 'Ticker': 'ticker', 'Tipo': 'tipo',
                    'Hora Inicio': 'hora_inicio', 'Hora Fin': 'hora_fin',
                    'Volumen (Acciones)': 'volumen', 'PnL ($)': 'pnl', 'Tags': 'tags'
                })
                # Inyectar el ID del usuario
                df_to_upload['user_id'] = st.session_state.user.id
                datos_dict = df_to_upload.to_dict(orient='records')
                
                # Borrar datos de ese día (si existen) para evitar duplicados, luego insertar
                supabase.table('historial_operaciones').delete().eq('fecha', str(fecha_operativa)).execute()
                supabase.table('historial_operaciones').insert(datos_dict).execute()
                
                st.cache_data.clear()
                st.success("¡Operaciones guardadas de forma segura!")

with tab_filtros:
    if not df_historico.empty and st.session_state['mis_tags']:
        if 'tags_activos' not in st.session_state: st.session_state['tags_activos'] = set()
        for tag in st.session_state['mis_tags']:
            if st.checkbox(tag, value=(tag in st.session_state['tags_activos']), key=f"chk_{tag}"):
                st.session_state['tags_activos'].add(tag)
            else:
                st.session_state['tags_activos'].discard(tag)
                
        if st.session_state['tags_activos']:
            pattern = '|'.join(st.session_state['tags_activos'])
            df_historico = df_historico[df_historico['Tags'].str.contains(pattern, case=False, na=False, regex=True)]

if not df_historico.empty:
    with tab2:
        total_pnl = df_historico['PnL ($)'].sum()
        total_trades = len(df_historico)
        win_rate = (len(df_historico[df_historico['PnL ($)'] > 0]) / total_trades) * 100 if total_trades > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("PnL Histórico", f"${total_pnl:,.2f}")
        col2.metric("Total de Trades", total_trades)
        col3.metric("Win Rate", f"{win_rate:.1f}%")

        # Curva de capital básica
        df_curva = df_historico.sort_values(by=['Fecha', 'Hora Inicio']).reset_index(drop=True)
        df_curva['PnL Acumulado'] = df_curva['PnL ($)'].cumsum()
        df_curva['Trade #'] = df_curva.index + 1
        st.line_chart(df_curva.set_index('Trade #')['PnL Acumulado'])

    with tab4:
        st.markdown('<span class="section-label">Historial (Solo lectura)</span>', unsafe_allow_html=True)
        # Ocultamos la columna 'id' de la base de datos para la vista
        columnas_mostrar = [c for c in df_historico.columns if c not in ['id', 'user_id', 'created_at']]
        st.dataframe(df_historico[columnas_mostrar], use_container_width=True)
        
        with st.expander("Eliminar un día operativo"):
            fechas = sorted(df_historico['Fecha'].unique(), reverse=True)
            fecha_borrar = st.selectbox("Fecha a eliminar:", fechas)
            if st.button("Eliminar permanentemente", type="primary"):
                supabase.table('historial_operaciones').delete().eq('fecha', str(fecha_borrar)).execute()
                st.cache_data.clear()
                st.rerun()