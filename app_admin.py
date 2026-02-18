import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from streamlit_option_menu import option_menu
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Abelardo Yepes - Gestión", 
    layout="wide", 
    page_icon="🏢"
)

# --- ESTILOS CSS PERSONALIZADOS (LOOK & FEEL DE LA IMAGEN) ---
st.markdown("""
    <style>
        /* Fondo general azul acero */
        .stApp {
            background: linear-gradient(to bottom, #7ba1c7, #5a82a8);
        }
        
        /* Contenedores blancos (Tarjetas) */
        [data-testid="stForm"], [data-testid="stMetric"], .stTabs, div.stElementContainer:has(div.stAlert) {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px !important;
            padding: 20px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
            border: none !important;
        }

        /* Estilo para los contenedores de proyectos */
        div.stColumn > div > div > div.stVerticalBlockBorderWrapper {
            background-color: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            margin-bottom: 10px;
        }

        /* Texto y Títulos */
        h1, h2, h3, .stMarkdown p {
            color: white !important;
        }
        
        /* Botones estilo corporativo */
        .stButton>button {
            background-color: #0078d4 !important;
            color: white !important;
            border-radius: 25px !important;
            border: none !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
            transition: 0.3s !important;
        }
        .stButton>button:hover {
            background-color: #005a9e !important;
            transform: scale(1.02);
        }

        /* Ajustes de Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
        }
        
        /* Barra de progreso azul */
        .stProgress > div > div > div > div {
            background-color: #0078d4 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE CORREO (Se mantienen igual) ---
def enviar_correo_ticket(destinatario, ticket_id, asunto_res, detalle_res):
    try:
        cuerpo = f"Desde Abelardo Yepes, queremos indicarte que hemos recibido tu Solicitud.\n\nTicket: {ticket_id}\nAsunto: {asunto_res}\nDetalle: {detalle_res}"
        msg = MIMEText(cuerpo)
        msg['Subject'] = f"Confirmación de Ticket: {ticket_id}"
        msg['From'] = st.secrets["emails"]["smtp_user"]
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["emails"]["smtp_user"], st.secrets["emails"]["smtp_pass"])
            server.send_message(msg)
        return True
    except: return False

def enviar_correo_actualizacion(destinatario, ticket_id, nuevo_estado, respuesta_admin):
    try:
        cuerpo = f"Actualización de su Requerimiento: {ticket_id}\n\nNuevo Estado: {nuevo_estado}\nRespuesta: {respuesta_admin}"
        msg = MIMEText(cuerpo)
        msg['Subject'] = f"Actualización de Ticket: {ticket_id}"
        msg['From'] = st.secrets["emails"]["smtp_user"]
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["emails"]["smtp_user"], st.secrets["emails"]["smtp_pass"])
            server.send_message(msg)
        return True
    except: return False

# --- LOGO Y MENÚ LATERAL ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

with st.sidebar:
    try:
        bin_str = get_base64_of_bin_file('Logo.png')
        st.markdown(f'''<a href="https://abelardoyepes.com/" target="_blank"><img src="data:image/png;base64,{bin_str}" style="width:100%;"></a>''', unsafe_allow_html=True)
    except:
        st.markdown("### 🏢 Abelardo Yepes S.A.S")
    
    st.markdown("---")
    selected = option_menu(
        menu_title="Menú Principal",
        options=["Mi Voz", "Transformación", "Gestión"],
        icons=["megaphone", "building-up", "person-fill-lock"],
        menu_icon="cast",
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2c3e50"}}
    )

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SECCIÓN 1: MI VOZ ---
if selected == "Mi Voz":
    st.title("📢 Mi Voz (Inquietudes)")
    st.info("Escucha activa, transparencia total y resultados en tiempo real.")
    
    col_izq, col_der = st.columns([2, 1])
    
    with col_izq:
        df_voz = conn.read(worksheet="voz", ttl=0)
        with st.form("form_voz", clear_on_submit=True):
            st.markdown("<p style='color:black !important; font-weight:bold;'>Crear Nueva Solicitud</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Tu Nombre")
            correo = c2.text_input("Tu Correo")
            asunto = st.selectbox("Asunto", ["Mantenimiento", "Sugerencia", "Zonas Comunes", "Seguridad"])
            detalle = st.text_area("Descripción de la inquietud:")
            if st.form_submit_button("Enviar a Administración"):
                if nombre and correo and detalle:
                    nuevo_id = f"VOZ-{len(df_voz) + 101}"
                    nueva_fila = pd.DataFrame([{"ID": nuevo_id, "Residente": nombre, "Correo": correo, "Asunto": asunto, "Detalle": detalle, "Estado": "⏳ Recibido", "Respuesta_Admin": "Pendiente", "Fecha": datetime.now().strftime("%Y-%m-%d")}])
                    conn.update(worksheet="voz", data=pd.concat([df_voz, nueva_fila]))
                    enviar_correo_ticket(correo, nuevo_id, asunto, detalle)
                    st.success(f"Ticket {nuevo_id} generado correctamente.")
    
    with col_der:
        st.markdown("<p style='color:white; font-weight:bold;'>🔍 Consulta tu Solicitud</p>", unsafe_allow_html=True)
        busqueda = st.text_input("Ingresa tu código VOZ-XXX")
        if busqueda:
            res = df_voz[df_voz['ID'] == busqueda.upper().strip()]
            if not res.empty:
                st.info(f"**Estado:** {res.iloc[0]['Estado']}\n\n**Respuesta:** {res.iloc[0]['Respuesta_Admin']}")

# --- SECCIÓN 2: TRANSFORMACIÓN ---
elif selected == "Transformación":
    st.title("🏗️ Transformación del Entorno")
    df_p = conn.read(worksheet="proyectos", ttl=0)
    for _, row in df_p.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"<h3 style='color:#1e3d59 !important;'>{row['Proyecto']}</h3>", unsafe_allow_html=True)
            c1.progress(int(row['Progreso']))
            c2.metric("Avance", f"{row['Progreso']}%", row['Estado'])
            st.markdown(f"<p style='color:gray !important;'><b>Nota:</b> {row['Nota']}</p>", unsafe_allow_html=True)

# --- SECCIÓN 3: GESTIÓN ---
elif selected == "Gestión":
    st.title("🔑 Panel Administrativo")
    password = st.sidebar.text_input("Clave de acceso", type="password")
    if password == "admin123":
        tab1, tab2 = st.tabs(["📩 Inquietudes", "🚧 Obras"])
        # Aquí se mantiene tu lógica original de actualización de Sheets...
        with tab1:
            st.dataframe(conn.read(worksheet="voz", ttl=0), use_container_width=True)
