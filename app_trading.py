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

if 'access_token' in st.session_state and 'refresh_token' in st.session_state:
    try:
        supabase.auth.set_session(st.session_state['access_token'], st.session_state['refresh_token'])
    except:
        st.session_state.user = None

# ──────────────────────────────────────────────
#  TEMA OSCURO PROFESIONAL - CSS GLOBAL
# ──────────────────────────────────────────────
dark_theme_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background-color: #0a0e1a !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] { background-color: #0d1120 !important; border-right: 1px solid #1e2740 !important; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

h1 { font-family: 'IBM Plex Mono', monospace !important; font-size: 1.6rem !important; font-weight: 600 !important; color: #f8fafc !important; letter-spacing: -0.02em !important; padding-bottom: 0.25rem !important; border-bottom: 2px solid #1e40af !important; margin-bottom: 1.5rem !important; }
h2, h3 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; color: #e2e8f0 !important; letter-spacing: -0.01em !important; }

[data-testid="stTabs"] [role="tablist"] { background: #0d1120 !important; border-bottom: 1px solid #1e2740 !important; gap: 4px !important; padding: 4px 4px 0 !important; border-radius: 8px 8px 0 0 !important; }
[data-testid="stTabs"] button[role="tab"] { background: transparent !important; color: #64748b !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 0.85rem !important; border-radius: 6px 6px 0 0 !important; border: 1px solid transparent !important; padding: 8px 16px !important; transition: all 0.2s ease !important; }
[data-testid="stTabs"] button[role="tab"]:hover { color: #94a3b8 !important; background: #1e2740 !important; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { background: #1e2740 !important; color: #60a5fa !important; border-color: #1e2740 !important; border-bottom-color: transparent !important; font-weight: 600 !important; }

[data-testid="stTextInput"] input, [data-testid="stDateInput"] input, [data-baseweb="select"] div, [data-baseweb="input"] input { background-color: #111827 !important; color: #e2e8f0 !important; border: 1px solid #1e2740 !important; border-radius: 6px !important; font-family: 'Inter', sans-serif !important; }
[data-baseweb="select"] div:hover, [data-testid="stTextInput"] input:focus { border-color: #3b82f6 !important; }

[data-testid="stButton"] > button { background: #1e40af !important; color: #f8fafc !important; border: none !important; border-radius: 6px !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 0.85rem !important; padding: 8px 18px !important; transition: all 0.2s ease !important; }
[data-testid="stButton"] > button:hover { background: #2563eb !important; box-shadow: 0 0 18px rgba(59,130,246,0.35) !important; }
[data-testid="stButton"] > button[kind="primary"] { background: linear-gradient(135deg, #1d4ed8, #1e40af) !important; box-shadow: 0 2px 12px rgba(29,78,216,0.4) !important; }

[data-testid="metric-container"] { background: #0d1120 !important; border: 1px solid #1e2740 !important; border-radius: 10px !important; padding: 16px 20px !important; transition: border-color 0.2s ease !important; }
[data-testid="metric-container"]:hover { border-color: #3b82f6 !important; }
[data-testid="metric-container"] [data-testid="stMetricLabel"] { font-family: 'Inter', sans-serif !important; font-size: 0.75rem !important; text-transform: uppercase !important; color: #64748b !important; font-weight: 500 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace !important; font-size: 1.6rem !important; font-weight: 600 !important; color: #f8fafc !important; }

[data-testid="stDataFrame"], iframe { border: 1px solid #1e2740 !important; border-radius: 8px !important; overflow: hidden !important; }
[data-testid="stAlert"] { border-radius: 8px !important; border-left-width: 3px !important; font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important; }
[data-testid="stFileUploader"] { border: 1px dashed #1e2740 !important; border-radius: 8px !important; background: #0d1120 !important; padding: 8px !important; }
[data-testid="stExpander"] { background: #0d1120 !important; border: 1px solid #1e2740 !important; border-radius: 8px !important; }
hr { border-color: #1e2740 !important; }

.cal-grid { display: grid; grid-template-columns: repeat(5, 1fr) 1.2fr; gap: 7px; margin-bottom: 8px; }
.cal-header { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.72rem; text-align: center; color: #475569; padding-bottom: 6px; border-bottom: 1px solid #1e2740; text-transform: uppercase; }
.cal-day { border-radius: 7px; padding: 10px; min-height: 82px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.15s ease; }
.cal-day:hover { transform: scale(1.02); }
.cal-date { font-size: 0.78rem; font-weight: 600; align-self: flex-start; opacity: 0.85; font-family: 'Inter', sans-serif; }
.cal-pnl { font-size: 1.05rem; font-weight: 700; text-align: center; margin: auto 0; font-family: 'IBM Plex Mono', monospace; }
.cal-trades { font-size: 0.68rem; font-weight: 500; text-align: center; opacity: 0.65; font-family: 'Inter', sans-serif; margin-top: 2px; }
.day-green { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.35); color: #34d399; }
.day-red { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.35); color: #f87171; }
.day-gray { background: #0d1120; border: 1px solid #1e2740; color: #334155; }
.day-blank { background: transparent; border: none; }
.cal-week-total { border-radius: 7px; padding: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
.week-title { font-size: 0.68rem; text-transform: uppercase; font-weight: 700; opacity: 0.75; font-family: 'Inter', sans-serif; }

.section-label { font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #3b82f6; margin-bottom: 8px; display: block; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 900px !important; padding-left: 3rem !important; padding-right: 3rem !important; padding-top: 2rem !important; }
[data-testid="stSidebar"] { display: none !important; }
label, [data-testid="stWidgetLabel"] { color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important; letter-spacing: 0.02em !important; }
</style>
"""
st.markdown("<div id='inicio'></div>", unsafe_allow_html=True)
st.markdown(dark_theme_css, unsafe_allow_html=True)

# ──────────────────────────────────────────────
#  SISTEMA DE AUTENTICACIÓN
# ──────────────────────────────────────────────
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center;'>🔐 Trading Journal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Inicia sesión para acceder a tu historial privado</p>", unsafe_allow_html=True)
    
    tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
    with tab_login:
        with st.form("login_form"):
            email_login = st.text_input("Correo electrónico", key="login_email", autocomplete="email")
            pass_login = st.text_input("Contraseña", type="password", key="login_pass", autocomplete="current-password")
            submit_login = st.form_submit_button("Entrar", type="primary", use_container_width=True)
            if submit_login:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_login, "password": pass_login})
                    st.session_state.user = res.user
                    st.session_state['access_token'] = res.session.access_token
                    st.session_state['refresh_token'] = res.session.refresh_token
                    st.rerun()
                except Exception as e:
                    st.error("Error al iniciar sesión. Verifica tus credenciales.")
                
    with tab_registro:
        with st.form("registro_form"):
            email_reg = st.text_input("Nuevo Correo electrónico", key="reg_email", autocomplete="email")
            pass_reg = st.text_input("Nueva Contraseña (mínimo 6 caracteres)", type="password", key="reg_pass", autocomplete="new-password")
            submit_reg = st.form_submit_button("Registrarse", use_container_width=True)
            if submit_reg:
                try:
                    res = supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                    st.success("¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
    st.stop()

# ──────────────────────────────────────────────
#  CARGA GLOBAL DE DATOS
# ──────────────────────────────────────────────
@st.cache_data(ttl=5)
def obtener_datos_usuario():
    res = supabase.table('historial_operaciones').select('*').execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df = df.rename(columns={
            'fecha': 'Fecha', 'ticker': 'Ticker', 'tipo': 'Tipo',
            'hora_inicio': 'Hora Inicio', 'hora_fin': 'Hora Fin',
            'volumen': 'Volumen (Acciones)', 'pnl': 'PnL ($)', 'tags': 'Tags',
            'perfil': 'Perfil'
        })
        if 'Perfil' not in df.columns: df['Perfil'] = 'Mi Cuenta'
        df['Perfil'] = df['Perfil'].fillna('Mi Cuenta')
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%Y-%m-%d')
        df['Tags'] = df['Tags'].fillna("")
        df['DateTime_Real'] = pd.to_datetime(df['Fecha'].astype(str) + ' ' + df['Hora Inicio'].astype(str), errors='coerce')
        df = df.sort_values(by='DateTime_Real').reset_index(drop=True)
        df = df.drop(columns=['DateTime_Real'])
    return df

df_historico_global = obtener_datos_usuario()

tags_unicos = []
if not df_historico_global.empty and 'Tags' in df_historico_global.columns:
    for tag_val in df_historico_global['Tags'].dropna():
        tag_str = str(tag_val)
        if tag_str.strip() != "" and tag_str.strip() != "None":
            tags_unicos.extend([t.strip() for t in tag_str.split(',')])
tags_unicos = sorted(list(set(tags_unicos)))

if 'mis_tags' not in st.session_state:
    st.session_state['mis_tags'] = tags_unicos

# Obtener lista de perfiles únicos desde la base de datos sin forzar ninguno
perfiles_db = df_historico_global['Perfil'].unique().tolist() if not df_historico_global.empty else []

if 'lista_perfiles' not in st.session_state:
    st.session_state['lista_perfiles'] = perfiles_db if perfiles_db else ['Mi Cuenta']
else:
    for p in perfiles_db:
        if p not in st.session_state['lista_perfiles']: 
            st.session_state['lista_perfiles'].append(p)

# Validar que el perfil activo exista en la lista actual
if 'perfil_activo' not in st.session_state or st.session_state['perfil_activo'] not in st.session_state['lista_perfiles']:
    st.session_state['perfil_activo'] = st.session_state['lista_perfiles'][0]

# ──────────────────────────────────────────────
#  FILTRADO POR PERFIL Y RESETEO DE ÍNDICE
# ──────────────────────────────────────────────
# Filtramos la data para que toda la app solo vea el perfil activo y reseteamos el conteo
if not df_historico_global.empty:
    df_perfil = df_historico_global[df_historico_global['Perfil'] == st.session_state['perfil_activo']].copy()
    # ESTA ES LA CORRECCIÓN: Reseteamos el índice y le sumamos 1 para que empiece desde 1 sin saltos
    df_perfil.reset_index(drop=True, inplace=True)
    df_perfil.index = df_perfil.index + 1
else:
    df_perfil = pd.DataFrame()

# ──────────────────────────────────────────────
#  HEADER, PERFIL ACTIVO Y CIERRE DE SESIÓN
# ──────────────────────────────────────────────
col_titulo, col_perfil, col_logout = st.columns([3, 1, 1])
with col_titulo:
    st.title("⬛ Trading Journal")
with col_perfil:
    st.markdown(f"<div style='text-align:right; padding-top:15px; color:#64748b; font-size:0.75rem;'>PERFIL ACTIVO<br><b style='color:#60a5fa; font-size:0.9rem;'>{st.session_state['perfil_activo']}</b></div>", unsafe_allow_html=True)
with col_logout:
    st.write("")
    if st.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()

# ──────────────────────────────────────────────
#  LÓGICA DE PROCESAMIENTO
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
            hora = p_validas[0]; ticker = p_validas[2]; lado = p_validas[3].upper(); acciones = int(p_validas[4])
            precio_real = 0.0; ult = p_validas[-1]; pen = p_validas[-2]
            if ult.replace('.', '').isdigit() and pen.replace('.', '').isdigit(): precio_real = float(f"{pen}.{ult}")
            elif ult.replace('.', '').isdigit(): precio_real = float(ult)
            if precio_real > 0: ejecuciones.append({'Hora': hora, 'Ticker': ticker, 'Lado': lado, 'Acciones': acciones, 'Precio_Ejecucion': precio_real})
        except: continue
    return pd.DataFrame(ejecuciones)

def calcular_trades(df, fecha):
    trades = []
    for ticker, df_ticker in df.groupby('Ticker'):
        inventario = 0; flujo_caja = 0.0; acciones_totales = 0; hora_inicio = None
        for index, row in df_ticker.iterrows():
            if inventario == 0: hora_inicio = row['Hora']
            qty = row['Acciones']; precio = row['Precio_Ejecucion']
            if row['Lado'] in ['BUY']: inventario += qty; flujo_caja -= (qty * precio)
            elif row['Lado'] in ['SELL', 'SSHRT']: inventario -= qty; flujo_caja += (qty * precio)
            acciones_totales += qty
            if inventario == 0:
                trades.append({ 'Fecha': str(fecha), 'Ticker': ticker, 'Tipo': "Short" if row['Lado'] == 'BUY' else "Long", 'Hora Inicio': hora_inicio, 'Hora Fin': row['Hora'], 'Volumen (Acciones)': acciones_totales // 2, 'PnL ($)': round(flujo_caja, 2), 'Tags': "" })
                flujo_caja = 0.0; acciones_totales = 0
    return pd.DataFrame(trades).sort_values(by=['Fecha', 'Hora Inicio']).reset_index(drop=True)

# ──────────────────────────────────────────────
#  INTERFAZ PRINCIPAL TABS
# ──────────────────────────────────────────────
tab1, tab_filtros, tab2, tab3, tab4, tab_perfiles = st.tabs([
    "  Ingreso  ", "  Filtros  ", "  Estadísticas  ", "  Calendario  ", "  Historial  ", "  Perfiles  "
])

# ── PESTAÑA PERFILES (Gestión) ──
with tab_perfiles:
    st.markdown('<span class="section-label">Selección de Cuenta</span>', unsafe_allow_html=True)
    
    idx_activo = st.session_state['lista_perfiles'].index(st.session_state['perfil_activo']) if st.session_state['perfil_activo'] in st.session_state['lista_perfiles'] else 0
    perfil_seleccionado = st.radio("Elige el perfil con el que deseas trabajar:", st.session_state['lista_perfiles'], index=idx_activo, horizontal=True)
    
    if perfil_seleccionado != st.session_state['perfil_activo']:
        st.session_state['perfil_activo'] = perfil_seleccionado
        st.rerun()
        
    st.markdown("---")
    st.markdown('<span class="section-label">Gestión de Perfiles</span>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.expander("➕ Crear Nuevo Perfil"):
            nuevo_perfil = st.text_input("Nombre del perfil:", placeholder="Ej: Cuenta Fondeo")
            if st.button("Crear", use_container_width=True):
                if nuevo_perfil and nuevo_perfil not in st.session_state['lista_perfiles']:
                    st.session_state['lista_perfiles'].append(nuevo_perfil)
                    st.session_state['perfil_activo'] = nuevo_perfil
                    st.rerun()
                    
    with c2:
        with st.expander("✏️ Renombrar Perfil"):
            perfil_a_renombrar = st.selectbox("Perfil actual:", st.session_state['lista_perfiles'], key="ren_sel")
            nuevo_nombre = st.text_input("Nuevo nombre:", key="ren_txt")
            if st.button("Actualizar", use_container_width=True):
                if nuevo_nombre and nuevo_nombre != perfil_a_renombrar and nuevo_nombre not in st.session_state['lista_perfiles']:
                    supabase.table('historial_operaciones').update({'perfil': nuevo_nombre}).eq('perfil', perfil_a_renombrar).eq('user_id', st.session_state.user.id).execute()
                    
                    st.session_state['lista_perfiles'].remove(perfil_a_renombrar)
                    st.session_state['lista_perfiles'].append(nuevo_nombre)
                    if st.session_state['perfil_activo'] == perfil_a_renombrar:
                        st.session_state['perfil_activo'] = nuevo_nombre
                        
                    st.cache_data.clear()
                    st.success("Perfil actualizado.")
                    st.rerun()

    with c3:
        with st.expander("🗑️ Eliminar Perfil"):
            st.warning("Se borrarán todos sus trades.")
            perfil_a_borrar = st.selectbox("Perfil a eliminar:", st.session_state['lista_perfiles'], key="del_sel")
            if st.button("Eliminar permanentemente", type="primary", use_container_width=True):
                if len(st.session_state['lista_perfiles']) > 1:
                    supabase.table('historial_operaciones').delete().eq('perfil', perfil_a_borrar).eq('user_id', st.session_state.user.id).execute()
                    st.session_state['lista_perfiles'].remove(perfil_a_borrar)
                    if st.session_state['perfil_activo'] == perfil_a_borrar:
                        st.session_state['perfil_activo'] = st.session_state['lista_perfiles'][0]
                        
                    st.cache_data.clear()
                    st.success("Perfil eliminado.")
                    st.rerun()
                else:
                    st.error("Debes tener al menos un perfil en tu cuenta.")

# ── PESTAÑA INGRESO ──
with tab1:
    st.markdown('<span class="section-label">Nueva sesión de trading</span>', unsafe_allow_html=True)
    st.info(f"Los datos que subas se guardarán en el perfil: **{st.session_state['perfil_activo']}**")
    col_fecha, col_archivo = st.columns([1, 2])
    with col_fecha: fecha_operativa = st.date_input("Fecha de sesión", date.today())
    with col_archivo: uploaded_file = st.file_uploader("Archivo .txt de Sterling Trader Pro", type=["txt"], label_visibility="visible")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue(); texto = ""
        for encoding in ['utf-8', 'latin-1', 'utf-16', 'cp1252']:
            try:
                temp_text = bytes_data.decode(encoding)
                if 'Filled' in temp_text or 'FILLED' in temp_text.upper(): texto = temp_text; break
            except: continue
        if not texto: texto = bytes_data.decode('utf-8', errors='ignore')

        df_crudo = procesar_historial(texto)
        if df_crudo.empty: st.error("No se encontraron órdenes 'Filled' válidas en el archivo.")
        else:
            df_trades_dia = calcular_trades(df_crudo, fecha_operativa)
            if not df_trades_dia.empty:
                st.success(f"{len(df_trades_dia)} trades procesados correctamente.")
                st.markdown("---")
                st.markdown('<span class="section-label">Asignación de Setups</span>', unsafe_allow_html=True)

                c1, c2 = st.columns([3, 1])
                with c1: nuevo_tag = st.text_input("Crear nuevo tag:", placeholder="Ej: Scalping, Gap & Go...")
                with c2:
                    st.write(""); st.write("")
                    if st.button("+ Añadir"):
                        if nuevo_tag and nuevo_tag not in st.session_state['mis_tags']:
                            st.session_state['mis_tags'].append(nuevo_tag); st.rerun()

                st.caption("Doble clic en la columna **Tags** para asignar el setup a cada trade.")
                edited_df = st.data_editor(
                    df_trades_dia, use_container_width=True, num_rows="dynamic",
                    column_config={ "Tags": st.column_config.SelectboxColumn("Tags (Setups)", options=st.session_state['mis_tags'], required=False) }
                )

                if st.button(f"Guardar trades en {st.session_state['perfil_activo']}", type="primary"):
                    df_to_upload = edited_df.rename(columns={
                        'Fecha': 'fecha', 'Ticker': 'ticker', 'Tipo': 'tipo',
                        'Hora Inicio': 'hora_inicio', 'Hora Fin': 'hora_fin',
                        'Volumen (Acciones)': 'volumen', 'PnL ($)': 'pnl', 'Tags': 'tags'
                    })
                    df_to_upload['user_id'] = st.session_state.user.id
                    df_to_upload['perfil'] = st.session_state['perfil_activo']
                    datos_dict = df_to_upload.to_dict(orient='records')
                    
                    supabase.table('historial_operaciones').delete().eq('fecha', str(fecha_operativa)).eq('user_id', st.session_state.user.id).eq('perfil', st.session_state['perfil_activo']).execute()
                    supabase.table('historial_operaciones').insert(datos_dict).execute()
                    st.cache_data.clear(); st.success(f"¡Operaciones guardadas en {st.session_state['perfil_activo']}!")

# ── PESTAÑA FILTROS ──
with tab_filtros:
    st.markdown('<span class="section-label">Filtrar estadísticas por Setup / Tag</span>', unsafe_allow_html=True)
    if not df_perfil.empty and st.session_state['mis_tags']:
        if 'tags_activos' not in st.session_state: st.session_state['tags_activos'] = set()
        st.caption("Activa o desactiva los tags para filtrar las estadísticas de este perfil.")
        for tag in st.session_state['mis_tags']:
            if st.checkbox(tag, value=(tag in st.session_state['tags_activos']), key=f"chk_{tag}"): st.session_state['tags_activos'].add(tag)
            else: st.session_state['tags_activos'].discard(tag)
        st.markdown("---")
        if st.session_state['tags_activos']:
            pattern = '|'.join(st.session_state['tags_activos'])
            df_perfil = df_perfil[df_perfil['Tags'].str.contains(pattern, case=False, na=False, regex=True)]
            st.success(f"Filtrando por: {', '.join(sorted(st.session_state['tags_activos']))}")
        else: st.info("Mostrando todos los datos de este perfil.")
    elif df_perfil.empty: st.info(f"Aún no hay datos guardados en el perfil '{st.session_state['perfil_activo']}'.")

# ── PESTAÑAS DE VISUALIZACIÓN ──
if not df_perfil.empty:
    with tab2:
        total_pnl = df_perfil['PnL ($)'].sum()
        total_trades = len(df_perfil)
        win_rate = (len(df_perfil[df_perfil['PnL ($)'] > 0]) / total_trades) * 100 if total_trades > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("PnL Histórico Total", f"${total_pnl:,.2f}")
        col2.metric("Total de Trades", total_trades)
        col3.metric("Win Rate Global", f"{win_rate:.1f}%")
        st.markdown("---")
        st.markdown('<span class="section-label">Curva de Capital</span>', unsafe_allow_html=True)

        df_curva = df_perfil.copy()
        df_curva['PnL Acumulado'] = df_curva['PnL ($)'].cumsum()
        df_curva['Trade #'] = df_curva.index # Usamos directamente el índice porque ya empieza en 1

        grafico_curva = alt.Chart(df_curva).mark_area(
            line={'color': '#3b82f6', 'strokeWidth': 2}, color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='rgba(59,130,246,0.35)', offset=0), alt.GradientStop(color='rgba(59,130,246,0.0)', offset=1)], x1=0, x2=0, y1=0, y2=1)
        ).encode(
            x=alt.X('Trade #:Q', title='Número de Trade', axis=alt.Axis(labelColor='#64748b', titleColor='#64748b', gridColor='#1e2740')),
            y=alt.Y('PnL Acumulado:Q', title='Capital Acumulado ($)', axis=alt.Axis(labelColor='#64748b', titleColor='#64748b', gridColor='#1e2740')),
            tooltip=[alt.Tooltip('Fecha:N'), alt.Tooltip('Ticker:N'), alt.Tooltip('PnL ($):Q', format='$.2f'), alt.Tooltip('PnL Acumulado:Q', format='$.2f')]
        ).properties(height=320, background='#0d1120').configure_view(strokeWidth=0)
        st.altair_chart(grafico_curva, use_container_width=True)

        st.markdown("---")
        st.markdown('<span class="section-label">Rendimiento Diario</span>', unsafe_allow_html=True)
        rendimiento_diario = df_perfil.groupby('Fecha')['PnL ($)'].sum().reset_index()
        rendimiento_diario['Color'] = rendimiento_diario['PnL ($)'].apply(lambda x: '#10b981' if x >= 0 else '#ef4444')

        grafico_base = alt.Chart(rendimiento_diario).mark_bar(size=40, cornerRadiusTopLeft=4, cornerRadiusTopRight=4) if len(rendimiento_diario) < 7 else alt.Chart(rendimiento_diario).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        grafico = grafico_base.encode(
            x=alt.X('Fecha:O', title='Día Operativo', axis=alt.Axis(labelColor='#64748b', titleColor='#64748b', gridColor='#1e2740')),
            y=alt.Y('PnL ($):Q', title='PnL Neto ($)', axis=alt.Axis(labelColor='#64748b', titleColor='#64748b', gridColor='#1e2740')),
            color=alt.Color('Color:N', scale=None), tooltip=[alt.Tooltip('Fecha:O'), alt.Tooltip('PnL ($):Q', format='$.2f')]
        ).properties(height=280, background='#0d1120').configure_view(strokeWidth=0)
        st.altair_chart(grafico, use_container_width=True)

        if 'Tags' in df_perfil.columns:
            df_perfil['Tags_Calc'] = df_perfil['Tags'].astype(str)
            df_tags = df_perfil.assign(Tag_Ind=df_perfil['Tags_Calc'].str.split(',')).explode('Tag_Ind')
            df_tags['Tag_Ind'] = df_tags['Tag_Ind'].str.strip()
            df_tags = df_tags[df_tags['Tag_Ind'] != ""]
            if not df_tags.empty:
                st.markdown("---")
                st.markdown('<span class="section-label">Rendimiento por Setup</span>', unsafe_allow_html=True)
                pnl_por_tag = df_tags.groupby('Tag_Ind')['PnL ($)'].sum().reset_index()
                pnl_por_tag['Color'] = pnl_por_tag['PnL ($)'].apply(lambda x: '#10b981' if x >= 0 else '#ef4444')
                grafico_tags = alt.Chart(pnl_por_tag).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                    y=alt.Y('Tag_Ind:N', title='Setup', sort='-x', axis=alt.Axis(labelColor='#64748b', titleColor='#64748b')),
                    x=alt.X('PnL ($):Q', title='PnL Generado ($)', axis=alt.Axis(labelColor='#64748b', titleColor='#64748b', gridColor='#1e2740')),
                    color=alt.Color('Color:N', scale=None), tooltip=[alt.Tooltip('Tag_Ind:N'), alt.Tooltip('PnL ($):Q', format='$.2f')]
                ).properties(height=230, background='#0d1120').configure_view(strokeWidth=0)
                st.altair_chart(grafico_tags, use_container_width=True)

    with tab3:
        df_perfil['Fecha_DT'] = pd.to_datetime(df_perfil['Fecha'])
        df_perfil['Mes_Año'] = df_perfil['Fecha_DT'].dt.strftime('%Y-%m')
        años_disponibles = sorted(df_perfil['Fecha_DT'].dt.year.unique(), reverse=True)
        meses_por_año = {año: sorted(df_perfil[df_perfil['Fecha_DT'].dt.year == año]['Fecha_DT'].dt.month.unique()) for año in años_disponibles}
        NOMBRES_MESES = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}

        if 'cal_año' not in st.session_state or st.session_state['cal_año'] not in años_disponibles: st.session_state['cal_año'] = años_disponibles[0]
        if 'cal_mes' not in st.session_state or st.session_state['cal_mes'] not in meses_por_año[st.session_state['cal_año']]: st.session_state['cal_mes'] = meses_por_año[st.session_state['cal_año']][-1]

        st.markdown('<span class="section-label">Año</span>', unsafe_allow_html=True)
        cols_años = st.columns([1]*len(años_disponibles) + [6])
        for i, año in enumerate(años_disponibles):
            with cols_años[i]:
                activo = año == st.session_state['cal_año']
                estilo = "background:#0f2460 !important; color:#93c5fd !important; border:1px solid #1e40af !important; font-weight:700 !important;" if activo else "background:#0d1120 !important; color:#475569 !important; border:1px solid #1e2740 !important; font-weight:500 !important;"
                if st.button(str(año), key=f"año_{año}", use_container_width=True):
                    st.session_state['cal_año'] = año; st.session_state['cal_mes'] = meses_por_año[año][-1]; st.rerun()
                st.markdown(f"""<style>div[data-testid="column"]:nth-child({i+1}) div[data-testid="stButton"] > button {{ {estilo} border-radius: 6px !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.85rem !important; }}</style>""", unsafe_allow_html=True)

        st.markdown('<span class="section-label">Mes</span>', unsafe_allow_html=True)
        meses_del_año = meses_por_año[st.session_state['cal_año']]
        cols_meses = st.columns([1]*len(meses_del_año) + [6])
        for i, mes in enumerate(meses_del_año):
            with cols_meses[i]:
                activo = mes == st.session_state['cal_mes']
                estilo_m = "background:#0f2460 !important; color:#93c5fd !important; border:1px solid #1e40af !important; font-weight:700 !important;" if activo else "background:#0d1120 !important; color:#475569 !important; border:1px solid #1e2740 !important; font-weight:500 !important;"
                if st.button(NOMBRES_MESES[mes], key=f"mes_{mes}", use_container_width=True):
                    st.session_state['cal_mes'] = mes; st.rerun()
                st.markdown(f"""<style>div[data-testid="column"]:nth-child({i+1}) div[data-testid="stButton"] > button {{ {estilo_m} border-radius: 6px !important; font-family: 'Inter', sans-serif !important; font-size: 0.82rem !important; }}</style>""", unsafe_allow_html=True)

        st.markdown("---")
        año_sel = st.session_state['cal_año']; mes_sel = st.session_state['cal_mes']
        mes_año_str = f"{año_sel}-{mes_sel:02d}"
        df_mes = df_perfil[df_perfil['Mes_Año'] == mes_año_str]

        pnl_mes_total = df_mes['PnL ($)'].sum()
        color_mes = "#10b981" if pnl_mes_total >= 0 else "#ef4444"
        st.markdown(f"<div style='text-align:right; margin-bottom:16px;'><span style='font-size:0.75rem; font-weight:600; color:#475569; text-transform:uppercase;'>PnL del mes — {NOMBRES_MESES[mes_sel]} {año_sel}</span><br><span style='font-size:1.9rem; font-weight:700; color:{color_mes}; font-family:\"IBM Plex Mono\",monospace;'>{('+' if pnl_mes_total>=0 else '')}${pnl_mes_total:,.2f}</span></div>", unsafe_allow_html=True)

        pnl_por_dia = df_mes.groupby(df_mes['Fecha_DT'].dt.day)['PnL ($)'].sum().to_dict()
        trades_por_dia = df_mes.groupby(df_mes['Fecha_DT'].dt.day).size().to_dict()
        trades_mes_total = len(df_mes)

        html_cal = '<div class="cal-grid">' + ''.join([f'<div class="cal-header">{d}</div>' for d in ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Semana']]) + '</div>'
        for semana in calendar.monthcalendar(año_sel, mes_sel):
            dias_habiles = semana[0:5]
            if all(dia == 0 for dia in dias_habiles): continue
            html_cal += '<div class="cal-grid">'
            pnl_semana = 0.0; trades_semana = 0; dias_con_trade = 0
            for dia in dias_habiles:
                if dia == 0: html_cal += '<div class="cal-day day-blank"></div>'
                elif dia in pnl_por_dia:
                    pnl = pnl_por_dia[dia]; n_trades = trades_por_dia.get(dia, 0); pnl_semana += pnl; trades_semana += n_trades; dias_con_trade += 1
                    clase = "day-green" if pnl >= 0 else "day-red"
                    html_cal += f'<div class="cal-day {clase}"><div class="cal-date">{dia}</div><div class="cal-pnl">{("+" if pnl>=0 else "")}${pnl:,.2f}</div><div class="cal-trades">{n_trades} trades</div></div>'
                else: html_cal += f'<div class="cal-day day-gray"><div class="cal-date">{dia}</div><div class="cal-pnl">—</div></div>'

            if dias_con_trade > 0: html_cal += f'<div class="cal-week-total {"day-green" if pnl_semana>=0 else "day-red"}"><div class="week-title">Sem.</div><div class="cal-pnl">{("+" if pnl_semana>=0 else "")}${pnl_semana:,.2f}</div><div class="cal-trades">{trades_semana} trades</div></div>'
            else: html_cal += '<div class="cal-week-total day-gray"><div class="week-title">Sem.</div><div class="cal-pnl">—</div></div>'
            html_cal += '</div>'

        color_hex = "#34d399" if pnl_mes_total >= 0 else "#f87171"
        bg_mes = "rgba(16, 185, 129, 0.1)" if pnl_mes_total >= 0 else "rgba(239, 68, 68, 0.1)"
        border_mes = "rgba(16, 185, 129, 0.35)" if pnl_mes_total >= 0 else "rgba(239, 68, 68, 0.35)"
        html_cal += f"""<div style='display:flex; justify-content:flex-end; margin-top:10px;'><div style='background:{bg_mes}; border:1px solid {border_mes}; border-radius:8px; padding:10px 18px; text-align:right; min-width:200px;'><span style='font-size:0.68rem; font-weight:700; text-transform:uppercase; color:{color_hex}; opacity:0.75; font-family:Inter,sans-serif;'>Total del mes</span><br><span style='font-size:1.1rem; font-weight:700; color:{color_hex}; font-family:"IBM Plex Mono",monospace;'>{('+' if pnl_mes_total>=0 else '')}${pnl_mes_total:,.2f}</span><span style='font-size:0.78rem; color:{color_hex}; opacity:0.65; margin-left:10px;'>{trades_mes_total} trades</span></div></div>"""
        st.markdown(html_cal, unsafe_allow_html=True)

    with tab4:
        with st.expander(f"Gestor de Datos — Eliminar de '{st.session_state['perfil_activo']}'"):
            fechas_guardadas = sorted(df_perfil['Fecha'].unique(), reverse=True)
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1: fecha_a_borrar = st.selectbox("Fecha a eliminar:", fechas_guardadas)
            with col_d2:
                st.write(""); st.write("")
                if st.button("Eliminar permanentemente", type="primary"):
                    supabase.table('historial_operaciones').delete().eq('fecha', str(fecha_a_borrar)).eq('user_id', st.session_state.user.id).eq('perfil', st.session_state['perfil_activo']).execute()
                    st.cache_data.clear(); st.success(f"Datos del {fecha_a_borrar} eliminados de {st.session_state['perfil_activo']}."); st.rerun()

        st.markdown(f'<span class="section-label">Historial de {st.session_state["perfil_activo"]}</span>', unsafe_allow_html=True)
        
        c1_hist, c2_hist = st.columns([3, 1])
        with c1_hist: nuevo_tag_hist = st.text_input("Crear nuevo Tag para la lista:", placeholder="Ej: Breakout...", key="tag_tab4")
        with c2_hist:
            st.write(""); st.write("")
            if st.button("+ Añadir a la lista", key="btn_tab4"):
                if nuevo_tag_hist and nuevo_tag_hist not in st.session_state['mis_tags']:
                    st.session_state['mis_tags'].append(nuevo_tag_hist); st.rerun()

        st.caption("Doble clic en la columna **Tags** para editar.")

        columnas_ocultas = ['user_id', 'created_at', 'Fecha_DT', 'Mes_Año', 'Tags_Calc', 'Perfil']
        columnas_mostrar = [c for c in df_perfil.columns if c not in columnas_ocultas]
        df_editable = df_perfil[columnas_mostrar].copy()

        edited_historial = st.data_editor(
            df_editable, use_container_width=True, num_rows="fixed",
            column_config={
                "id": None,
                "Tags": st.column_config.SelectboxColumn("Tags (Setups)", options=st.session_state['mis_tags'], required=False),
                "Volumen (Acciones)": st.column_config.NumberColumn("Qty"),
            }
        )

        if st.button("Guardar cambios en el historial", type="primary"):
            for index, row in edited_historial.iterrows():
                tag_original = df_perfil.loc[index, 'Tags']
                tag_nuevo = row['Tags']
                if tag_original != tag_nuevo:
                    supabase.table('historial_operaciones').update({'tags': tag_nuevo}).eq('id', row['id']).execute()
            st.cache_data.clear(); st.success("Cambios sincronizados en la nube."); st.rerun()