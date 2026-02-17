import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import smtplib                         # <--- NUEVO
from email.mime.text import MIMEText    # <--- NUEVO

# --- FUNCIÓN PARA ENVIAR CORREO ---
def enviar_correo_ticket(destinatario, ticket_id, asunto_res, detalle_res):
    try:
        cuerpo = f"Desde Abelardo Yepes, queremos indicarte que hemos recibiduo tu Solicitud.\n\nTicket: {ticket_id}\nAsunto: {asunto_res}\nDetalle: {detalle_res}"
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

# --- FUNCIÓN 2: Para actualizaciones (Pégala debajo de la anterior) ---
def enviar_correo_actualizacion(destinatario, ticket_id, nuevo_estado, respuesta_admin):
    try:
        asunto_mail = f"Actualización de su Requerimiento: {ticket_id}"
        
        # Definimos el mensaje según el estado
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
        
        # AQUÍ ESTÁ EL ARREGLO: Creamos el objeto 'msg' correctamente
        msg = MIMEText(cuerpo) 
        msg['Subject'] = asunto_mail
        msg['From'] = st.secrets["emails"]["smtp_user"]
        msg['To'] = destinatario

        # Conexión y envío
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["emails"]["smtp_user"], st.secrets["emails"]["smtp_pass"])
            server.send_message(msg) # Ahora 'msg' ya existe
        return True
    except Exception as e:
        st.error(f"Error al enviar notificación: {e}")
        return False

# Configuración de marca y estilo
st.set_page_config(page_title="Tu Voz Construye a un Clic", layout="wide", page_icon="🏢")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Esto lee automáticamente tu archivo secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Leer los datos actuales del Excel
# (Asegúrate de que las pestañas se llamen 'proyectos' y 'voz')
# Esto lee de Google una vez y guarda en caché por 10 minutos
df_proyectos = conn.read(worksheet="proyectos", ttl=60)
df_voz = conn.read(worksheet="voz", ttl=60)


# --- INICIALIZAR SESSION STATE ---
if "db_proyectos" not in st.session_state:
    st.session_state.db_proyectos = df_proyectos.copy()

if "db_voz" not in st.session_state:
    st.session_state.db_voz = df_voz.copy()

if 'db_proyectos' not in st.session_state:
    st.session_state.db_proyectos = pd.DataFrame([
        {"ID": "PROJ-01", "Proyecto": "Impermeabilización Terrazas", "Progreso": 75, "Estado": "En Ejecución", "Nota": "Fase final de sellado térmico."},
        {"ID": "PROJ-02", "Proyecto": "Modernización de Ascensores", "Progreso": 20, "Estado": "Inicio", "Nota": "Pedido de repuestos internacionales realizado."}
            ])

# Estilo personalizado
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

# --- ENCABEZADO ESTRATÉGICO ---
st.title("🏢 Tu Voz Construye a un Clic")
st.info("Escucha activa, transparencia total y resultados en tiempo real.")

tabs = st.tabs(["📢 Mi Voz (Inquietudes)", "🏗️ Transformación del Entorno", "🔑 Gestión Administrativa"])

# --- TAB 1: ESCUCHA ACTIVA ---
with tabs[0]:
    st.subheader("Cuéntanos, ¿en qué podemos trabajar hoy?")
    with st.form("voz_residente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Tu Nombre")
        correo_usuario = col2.text_input("Tu Correo Electrónico") 
        
        asunto = st.selectbox("Asunto", ["Mantenimiento", "Sugerencia", "Zonas Comunes", "Seguridad"])
        detalle = st.text_area("Describe tu inquietud o propuesta:")
        
        if st.form_submit_button("Enviar a Administración"):
            if nombre and correo_usuario and detalle:
                nuevo_id = f"VOZ-{len(df_voz) + 101}"
                
                # --- AQUÍ AGREGAMOS LA COLUMNA 'Correo' ---
                nueva_voz = pd.DataFrame([{
                    "ID": nuevo_id, 
                    "Residente": nombre, 
                    "Correo": correo_usuario,  # <--- Esta es la clave
                    "Asunto": asunto, 
                    "Detalle": detalle, 
                    "Estado": "⏳ Recibido", 
                    "Respuesta_Admin": "Pendiente de revisión", 
                    "Fecha": datetime.now().strftime("%Y-%m-%d")
                }])
                
                # Concatenamos y mandamos a la nube
                df_actualizado = pd.concat([df_voz, nueva_voz], ignore_index=True)
                conn.update(worksheet="voz", data=df_actualizado)
                
                # Enviar correo (Función que ya pusimos arriba)
                enviar_correo_ticket(correo_usuario, nuevo_id, asunto, detalle)
                
                st.success(f"¡Gracias {nombre}! Ticket: **{nuevo_id}**. Guardado en Excel y notificado por correo.")
                st.rerun()

    st.markdown("---")
    st.subheader("🔍 Consulta el Respaldo de tu Solicitud")
    busqueda = st.text_input("Ingresa tu código VOZ-XXX")
    if busqueda:
        # Buscamos en el DataFrame que leímos del Excel
        res = df_voz[df_voz['ID'] == busqueda.upper()]
        if not res.empty:
            st.write(f"**Estado:** {res.iloc[0]['Estado']}")
            st.write(f"**Respuesta de la Administración:** {res.iloc[0]['Respuesta_Admin']}")
        else:
            st.error("Código no encontrado.")

# --- TAB 2: TRANSFORMACIÓN EN TIEMPO REAL ---
with tabs[1]:
    col_tit, col_ref = st.columns([4, 1])
    col_tit.subheader("Visualiza la evolución de nuestro conjunto")
    
    # Botón para refrescar datos manualmente
    if col_ref.button("🔄 Refrescar Datos"):
        st.rerun()
    
    # IMPORTANTE: Forzamos lectura fresca (ttl=0)
    # Cambia el 0 por un valor más alto, como 60 (1 minuto)
    df_p_visual = conn.read(worksheet="proyectos", ttl=60)
    
    if not df_p_visual.empty:
        for _, row in df_p_visual.iterrows():
            with st.container():
                col_a, col_b = st.columns([3, 1])
                col_a.write(f"### {row['Proyecto']}")
                
                # Convertimos progreso a entero para evitar errores en la barra
                progreso_val = int(row['Progreso'])
                col_a.progress(progreso_val)
                
                col_b.metric("Avance", f"{progreso_val}%", row['Estado'])
                st.caption(f"**Última actualización:** {row['Nota']}")
                st.divider()
    else:
        st.info("Aún no hay obras registradas por la administración.")

# --- TAB 3: GESTIÓN INTERNA ---
with tabs[2]:
    st.subheader("Panel de Respaldo y Resultados")
    password = st.text_input("Clave de acceso", type="password")
    
    if password == "admin123":


        # --- SUB-SECCIÓN B: GESTIÓN DE INQUIETUDES (Lectura Real) ---
        st.markdown("### 📢 Gestión de Inquietudes (Residentes)")
        
        # Volvemos a leer para asegurar que tenemos lo último de Google
        df_voz = conn.read(worksheet="voz", ttl=0) 

        if not df_voz.empty:
            sel_id = st.selectbox("Seleccionar VOZ-ID para responder", df_voz["ID"])
            idx_voz = df_voz[df_voz["ID"] == sel_id].index[0]
            
            col_v1, col_v2 = st.columns(2)
            # Mostramos lo que ya hay en el Excel para editarlo
            new_status = col_v1.selectbox("Estado", ["⏳ Recibido", "🛠️ En Gestión", "✅ Resultado Garantizado"], 
                                         index=["⏳ Recibido", "🛠️ En Gestión", "✅ Resultado Garantizado"].index(df_voz.at[idx_voz, "Estado"]))
            new_resp = col_v2.text_area("Respuesta al residente:", value=df_voz.at[idx_voz, "Respuesta_Admin"])
            
            if st.button("Actualizar Inquietud"):
                # Actualizamos los datos en el DataFrame
                df_voz.at[idx_voz, "Estado"] = new_status
                df_voz.at[idx_voz, "Respuesta_Admin"] = new_resp
                
                # Obtener el correo del residente para notificarle
                # (Asegúrate de que la columna se llame 'Correo')
                correo_destinatario = df_voz.at[idx_voz, "Correo"]
                ticket_id = df_voz.at[idx_voz, "ID"]
                
                # GUARDAR EN GOOGLE SHEETS
                conn.update(worksheet="voz", data=df_voz)
                
                # --- NUEVO: ENVIAR NOTIFICACIÓN DE ACTUALIZACIÓN ---
                if correo_destinatario:
                    enviar_correo_actualizacion(correo_destinatario, ticket_id, new_status, new_resp)
                    st.success(f"Inquietud actualizada y notificación enviada a {correo_destinatario}")
                else:
                    st.warning("Inquietud actualizada, pero no se encontró correo para notificar.")
                
                st.rerun()

        # --- SUB-SECCIÓN B: GESTIÓN DE PROYECTOS ---
        st.markdown("### 🏗️ Registro y Control de Obras")
        
        # Leemos los datos más recientes de la nube para el desprendible
        # Usa un tiempo de vida razonable
        df_proyectos = conn.read(worksheet="proyectos", ttl=60)

        # --- Desprendible de Proyectos en Curso ---
        st.markdown("#### 📝 Actualizar Avance de Obra")
        
        if not df_proyectos.empty:
            # Lista de proyectos para el selectbox
            lista_proyectos = df_proyectos["Proyecto"].tolist()
            
            proyecto_a_editar = st.selectbox(
                "¿Qué avance quiere registrar? Seleccione el proyecto:", 
                lista_proyectos
            )
            
            # Buscamos la fila del proyecto seleccionado
            idx_proj = df_proyectos[df_proyectos["Proyecto"] == proyecto_a_editar].index[0]
            
            # --- FORMULARIO CON LIMPIEZA AUTOMÁTICA ---
            # 'clear_on_submit=True' hace que al dar clic en el botón, los campos se reseteen
            with st.form("form_actualizar_avance", clear_on_submit=True):
                col_p1, col_p2 = st.columns(2)
                
                # Valores actuales traídos del Excel
                progreso_actual = int(df_proyectos.at[idx_proj, "Progreso"])
                estado_actual = df_proyectos.at[idx_proj, "Estado"]
                
                nuevo_progreso = col_p1.slider("Nuevo Porcentaje de Avance", 0, 100, progreso_actual)
                nuevo_estado_p = col_p2.selectbox(
                    "Nuevo Estado de Obra", 
                    ["Inicio", "En Ejecución", "Finalizado", "Suspendido"],
                    index=["Inicio", "En Ejecución", "Finalizado", "Suspendido"].index(estado_actual)
                )
                nueva_nota_p = st.text_input("Nota de esta actualización (ej: Fase de pintura)", value=df_proyectos.at[idx_proj, "Nota"])

                # Botón de publicación que también limpia el formulario
                if st.form_submit_button("Publicar y Limpiar para nueva entrada"):
                    # Actualizamos el DataFrame localmente
                    df_proyectos.at[idx_proj, "Progreso"] = nuevo_progreso
                    df_proyectos.at[idx_proj, "Estado"] = nuevo_estado_p
                    df_proyectos.at[idx_proj, "Nota"] = nueva_nota_p
                    
                    # Guardamos los cambios en Google Sheets
                    conn.update(worksheet="proyectos", data=df_proyectos)
                    st.success(f"✅ ¡Actualizado! Datos de '{proyecto_a_editar}' guardados y formulario listo para otro proyecto.")
                    st.rerun()
                    
            st.caption("💡 Al hacer clic en publicar, los campos se reiniciarán automáticamente para que puedas actualizar otro proyecto.")
        else:
            st.info("Aún no hay proyectos en curso. Registre uno nuevo arriba.")
        
        st.divider()
        st.write("### 📊 Vista General de Datos (Solo Admin)")
        st.dataframe(df_voz)
