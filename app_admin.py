import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from streamlit_option_menu import option_menu
import base64

# --- FUNCIÓN PARA ENVIAR CORREO ---
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
    except Exception as e:
        st.error(f"Error al enviar correo: {e}")
        return False

# --- FUNCIÓN 2: Para actualizaciones ---
def enviar_correo_actualizacion(destinatario, ticket_id, nuevo_estado, respuesta_admin):
    try:
        asunto_mail = f"Actualización de su Requerimiento: {ticket_id}"
        mensaje_cierre = "✅ Su requerimiento ha sido finalizado." if "Resultado" in nuevo_estado else "🚧 Su requerimiento tiene una nueva actualización."
        
        cuerpo = f"""
        Hola,
        
        {mensaje_cierre}
        
        DETALLES DE LA ACTUALIZACIÓN:
        - Ticket: {ticket_id}
        - Nuevo Estado: {nuevo_estado}
        - Respuesta de Administración: {respuesta_admin}
        
        Atentamente,
        Administración del Conjunto.
        """
        
        msg = MIMEText(cuerpo) 
        msg['Subject'] = asunto_mail
        msg['From'] = st.secrets["emails"]["smtp_user"]
        msg['To'] = destinatario

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["emails"]["smtp_user"], st.secrets["emails"]["smtp_pass"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error al enviar notificación: {e}")
        return False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Abelardo Yepes - Gestión", 
    layout="wide", 
    page_icon="🏢"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        [data-testid="stSidebarNav"] { display: none; }
        .stButton>button { border-radius: 20px; transition: all 0.3s ease; }
        .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LÓGICA PARA LOGO CLICKEABLE ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- SIDEBAR: LOGO Y MENÚ ---
with st.sidebar:
    try:
        bin_str = get_base64_of_bin_file('Logo.png')
        logo_url = "https://abelardoyepes.com/"
        html_code = f'''
            <a href="{logo_url}" target="_blank">
                <img src="data:image/png;base64,{bin_str}" style="width:100%;">
            </a>
        '''
        st.markdown(html_code, unsafe_allow_html=True)
    except:
        st.markdown("[🏢 Abelardo Yepes S.A.S](https://abelardoyepes.com/)")
    
    st.markdown("---")
    selected = option_menu(
        menu_title="Menú Principal",
        options=["Mi Voz", "Transformación", "Gestión"],
        icons=["megaphone", "building-up", "person-fill-lock"],
        menu_icon="cast",
        default_index=0,
        styles={"nav-link-selected": {"background-color": "#2c3e50"}}
    )

# --- SECCIÓN 1: MI VOZ ---
if selected == "Mi Voz":
    st.title("📢 Mi Voz (Inquietudes)")
    opcion_voz = st.radio("Acción", ["Nueva Solicitud", "Consultar mi Ticket"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")
    df_voz = conn.read(worksheet="voz", ttl=0)

    if opcion_voz == "Nueva Solicitud":
        with st.form("form_voz", clear_on_submit=True):
            col1, col2 = st.columns(2)
            nombre = col1.text_input("Tu Nombre")
            correo_usuario = col2.text_input("Tu Correo")
            asunto = st.selectbox("Asunto", ["Mantenimiento", "Sugerencia", "Zonas Comunes", "Seguridad"])
            detalle = st.text_area("Describe tu propuesta:")
            
            if st.form_submit_button("Enviar a Administración"):
    # Añadimos una validación simple de "@"
    if nombre and correo_usuario and detalle:
        if "@" in correo_usuario:
            # ... resto de tu código para guardar en Sheets ...
            enviar_correo_ticket(correo_usuario, nuevo_id, asunto, detalle)
            st.success(f"Ticket {nuevo_id} enviado.")
        else:
            st.error("⚠️ Por favor, ingresa un correo electrónico válido (debe incluir @).")
    else:
        st.warning("⚠️ Completa todos los campos.")
    else:
        busqueda = st.text_input("Ingresa tu código (Ejemplo: VOZ-101)")
        if busqueda:
            res = df_voz[df_voz['ID'] == busqueda.upper().strip()]
            if not res.empty:
                st.info(f"**Estado:** {res.iloc[0]['Estado']}")
                st.write(f"**Respuesta:** {res.iloc[0]['Respuesta_Admin']}")

# --- SECCIÓN 2: TRANSFORMACIÓN ---
elif selected == "Transformación":
    st.title("🏗️ Transformación del Entorno")
    df_p = conn.read(worksheet="proyectos", ttl=0)
    if not df_p.empty:
        for _, row in df_p.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                c1.subheader(row['Proyecto'])
                c1.progress(int(row['Progreso']))
                c2.metric("Avance", f"{row['Progreso']}%", row['Estado'])
                st.write(f"**Nota:** {row['Nota']}")

# --- SECCIÓN 3: GESTIÓN ---
elif selected == "Gestión":
    st.title("🔑 Panel Administrativo")
    password = st.sidebar.text_input("Clave de acceso", type="password")
    
    if password == "admin123":
        tab1, tab2 = st.tabs(["📩 Gestión de Inquietudes", "🚧 Control de Obras"])
        
        with tab1:
            st.markdown("### 📢 Gestión de Inquietudes")
            df_voz = conn.read(worksheet="voz", ttl=0) 
            if not df_voz.empty:
                sel_id = st.selectbox("Seleccionar VOZ-ID", df_voz["ID"])
                idx_voz = df_voz[df_voz["ID"] == sel_id].index[0]
                
                st.info(f"**Residente:** {df_voz.at[idx_voz, 'Residente']} | **Asunto:** {df_voz.at[idx_voz, 'Asunto']}")
                st.write(f"**Detalle:** {df_voz.at[idx_voz, 'Detalle']}")
                
                col_v1, col_v2 = st.columns(2)
                opciones_estado = ["⏳ Recibido", "🛠️ En Gestión", "✅ Resultado Garantizado"]
                
                try:
                    indice_estado = opciones_estado.index(df_voz.at[idx_voz, "Estado"])
                except:
                    indice_estado = 0

                new_status = col_v1.selectbox("Actualizar Estado", opciones_estado, index=indice_estado)
                new_resp = col_v2.text_area("Respuesta:", value=df_voz.at[idx_voz, "Respuesta_Admin"])
                
                if st.button("Actualizar y Notificar"):
                    df_voz.at[idx_voz, "Estado"] = new_status
                    df_voz.at[idx_voz, "Respuesta_Admin"] = new_resp
                    conn.update(worksheet="voz", data=df_voz)
                    
                    if enviar_correo_actualizacion(df_voz.at[idx_voz, "Correo"], sel_id, new_status, new_resp):
                        st.success(f"✅ Notificación enviada a {df_voz.at[idx_voz, 'Correo']}")
                    else:
                        st.warning("⚠️ Guardado, pero el correo falló.")
                    
                    if st.button("Entendido / Cerrar"):
                        st.rerun()
                
                st.dataframe(df_voz)
        
        with tab2:
            st.subheader("Actualizar Obras")
            df_admin_p = conn.read(worksheet="proyectos", ttl=0)
            if not df_admin_p.empty:
                proy_sel = st.selectbox("Proyecto", df_admin_p['Proyecto'].tolist())
                pidx = df_admin_p[df_admin_p['Proyecto'] == proy_sel].index[0]
                
                col_a, col_b = st.columns(2)
                p_prog = col_a.slider("Progreso %", 0, 100, int(df_admin_p.at[pidx, 'Progreso']))
                p_est = col_b.selectbox("Fase", ["Planeación", "Ejecución", "Finalizado"], index=0)
                p_nota = st.text_input("Nota", value=df_admin_p.at[pidx, 'Nota'])
                
                if st.button("Actualizar Proyecto"):
                    df_admin_p.at[pidx, 'Progreso'] = p_prog
                    df_admin_p.at[pidx, 'Estado'] = p_est
                    df_admin_p.at[pidx, 'Nota'] = p_nota
                    conn.update(worksheet="proyectos", data=df_admin_p)
                    st.success("Avance guardado.")
                    st.rerun()
                st.table(df_admin_p)
    else:
        st.warning("Ingrese la clave correcta.")

