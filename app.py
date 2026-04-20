import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# --- 1. CONEXIÓN (Configura esto en Streamlit Cloud Secrets) ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
except:
    # Para pruebas locales si no tienes secretos configurados
    URL = "https://ipzbkimkrckwrxisdisr.supabase.co"
    KEY = "TU_KEY_AQUI" 

supabase: Client = create_client(URL, KEY)

BANDERAS = {
    "México": "mx", "Sudáfrica": "za", "Corea del Sur": "kr", "Canadá": "ca",
    "Estados Unidos": "us", "Paraguay": "py", "Catar": "qa", "Suiza": "ch",
    "Brasil": "br", "Marruecos": "ma", "Haití": "ht", "Escocia": "gb-sct",
    "Australia": "au", "Alemania": "de", "Curazao": "cw", "Países Bajos": "nl",
    "Japón": "jp", "Costa de Marfil": "ci", "Ecuador": "ec", "Túnez": "tn",
    "España": "es", "Cabo Verde": "cv", "Bélgica": "be", "Egipto": "eg",
    "Arabia Saudí": "sa", "Uruguay": "uy", "Irán": "ir", "Nueva Zelanda": "nz",
    "Francia": "fr", "Senegal": "sn", "Noruega": "no", "Argentina": "ar",
    "Argelia": "dz", "Austria": "at", "Jordania": "jo", "Portugal": "pt",
    "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa",
    "Uzbekistán": "uz", "Colombia": "co"
}

# --- 2. CONFIGURACIÓN Y ESTILOS CSS ---
st.set_page_config(page_title="Porra Mundial 2026", layout="centered", page_icon="🏆")

st.markdown("""
    <style>
    .stApp { background-color: #0b101e; color: #ffffff; }
    .match-card { background-color: #1a233a; padding: 20px; border-radius: 15px; border: 1px solid #2d3748; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .match-header { font-size: 0.75em; color: #a0aec0; text-align: center; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .team-name { font-size: 1.1em; font-weight: bold; }
    div.stButton > button:first-child { background-color: #00e676 !important; color: #0b101e !important; border-radius: 25px; font-weight: bold; width: 100%; border: none; padding: 10px; }
    .podium-gold { background: linear-gradient(135deg, #FFD700, #FDB931); color: #000; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .podium-silver { background: linear-gradient(135deg, #C0C0C0, #8E8E8E); color: #000; padding: 10px; border-radius: 15px; text-align: center; }
    .podium-bronze { background: linear-gradient(135deg, #CD7F32, #8B4513); color: #fff; padding: 10px; border-radius: 15px; text-align: center; }
    /* Estilo login */
    .login-container { background-color: #161e31; padding: 40px; border-radius: 20px; text-align: center; border: 1px solid #2d3748; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE ACCESO (LOGIN + ESTADO) ---
if "Id_usuario" not in st.session_state:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.title("🏆 Porra Mundial 2026")
    nombre_u = st.text_input("Usuario", placeholder="Tu nombre")
    pass_u = st.text_input("Contraseña", type="password", placeholder="Mínimo 1 carácter")
    
    if st.button("ENTRAR / REGISTRARSE"):
        if nombre_u.strip() and pass_u.strip():
            res = supabase.table("Usuarios").select("*").eq("Nombre", nombre_u).execute()
            if res.data:
                if str(res.data[0]["Password"]) == str(pass_u):
                    st.session_state["Id_usuario"] = res.data[0]["Id"]
                    st.session_state["Nombre"] = res.data[0]["Nombre"]
                    st.session_state["Estado"] = res.data[0].get("Estado", "Pendiente")
                    st.rerun()
                else: st.error("Contraseña incorrecta")
            else:
                nuevo = supabase.table("Usuarios").insert({"Nombre": nombre_u, "Password": pass_u, "Puntos": 0, "Estado": "Pendiente"}).execute()
                st.session_state["Id_usuario"] = nuevo.data[0]["Id"]
                st.session_state["Nombre"] = nuevo.data[0]["Nombre"]
                st.session_state["Estado"] = "Pendiente"
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. VERIFICACIÓN DE PAGO ---
if st.session_state.get("Estado") == "Pendiente":
    st.title("⚽ Cuenta Pendiente")
    st.warning(f"Hola {st.session_state['Nombre']}, tu cuenta aún no ha sido activada.")
    st.info("Envía un Bizum de 5€ al número **6XX XXX XXX** para participar. Una vez enviado, el administrador te dará acceso.")
    if st.button("🔄 Ya he pagado, actualizar"):
        res = supabase.table("Usuarios").select("Estado").eq("Id", st.session_state["Id_usuario"]).execute()
        st.session_state["Estado"] = res.data[0]["Estado"]
        st.rerun()
    st.stop()

# --- 5. CARGA DE DATOS ---
partidos_raw = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data
todos_usuarios = supabase.table("Usuarios").select("Id, Nombre, Puntos").order("Puntos", desc=True).execute().data

# Agrupar fases
for p in partidos_raw:
    p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]

orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "Final"]
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), 
                          key=lambda x: orden_fases.index(x) if x in orden_fases else 99)

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['Nombre']}")
    res_yo = [u for u in todos_usuarios if u['Id'] == st.session_state['Id_usuario']]
    puntos_yo = res_yo[0]['Puntos'] if res_yo else 0
    st.metric("Tus Puntos", puntos_yo)
    if st.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 6. TABS PRINCIPALES ---
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if st.session_state["Nombre"] == "AGS" else "📜 Reglas"])

with tabs[0]:
    if not partidos_raw:
        st.info("Cargando partidos...")
    else:
        sub_tabs = st.tabs(fases_existentes)
        votos = {v['Id_partido']: v['Prediccion'] for v in supabase.table("Porras").select("Id_partido, Prediccion").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}

        for i, fase_tab in enumerate(fases_existentes):
            with sub_tabs[i]:
                partidos_fase = [p for p in partidos_raw if p["Fase_Visual"] == fase_tab]
                for p in partidos_fase:
                    st.markdown("<div class='match-card'>", unsafe_allow_html=True)
                    fecha = datetime.fromisoformat(p['Fecha_hora'])
                    st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha.strftime('%d/%m %H:%M')}h</div>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([2, 1, 2])
                    with c1:
                        iso_l = BANDERAS.get(p['Equipo_local'], "un")
                        st.markdown(f"<div style='text-align: right;'><b>{p['Equipo_local']}</b> <img src='https://flagcdn.com/24x18/{iso_l}.png'></div>", unsafe_allow_html=True)
                    with c2:
                        res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
                        st.markdown(f"<div style='text-align: center; font-weight: bold; background: #2d3748; border-radius: 5px;'>{res_txt}</div>", unsafe_allow_html=True)
                    with c3:
                        iso_v = BANDERAS.get(p['Equipo_visitante'], "un")
                        st.markdown(f"<div><img src='https://flagcdn.com/24x18/{iso_v}.png'> <b>{p['Equipo_visitante']}</b></div>", unsafe_allow_html=True)
                    
                    # Lógica apuesta
                    if p.get('Resultado_real'):
                        if votos.get(p['Id']) == p['Resultado_real']: st.success(f"🎯 Acertaste: {votos[p['Id']]}")
                        elif p['Id'] in votos: st.error(f"❌ Fallaste: {votos[p['Id']]}")
                    elif p['Id'] in votos:
                        st.info(f"Pronóstico: **{votos[p['Id']]}**")
                    elif fecha > datetime.now():
                        pred = st.radio("Voto:", [p['Equipo_local'], 'X', p['Equipo_visitante']], key=f"p_{p['Id']}", horizontal=True, label_visibility="collapsed")
                        if st.button("Confirmar", key=f"b_{p['Id']}"):
                            supabase.table("Porras").upsert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": pred}).execute()
                            st.rerun()
                    else: st.warning("🔒 Cerrado")
                    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    if todos_usuarios:
        st.markdown("<div class='podium-gold'>🥇 1º " + todos_usuarios[0]['Nombre'] + f" ({todos_usuarios[0]['Puntos']} pts)</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if len(todos_usuarios) > 1: c1.markdown("<div class='podium-silver'>🥈 2º " + todos_usuarios[1]['Nombre'] + "</div>", unsafe_allow_html=True)
        if len(todos_usuarios) > 2: c2.markdown("<div class='podium-bronze'>🥉 3º " + todos_usuarios[2]['Nombre'] + "</div>", unsafe_allow_html=True)
        st.divider()
        st.dataframe(pd.DataFrame(todos_usuarios)[['Nombre', 'Puntos']], use_container_width=True, hide_index=True)

if st.session_state["Nombre"] == "AGS":
    with tabs[2]:
        st.subheader("Panel Admin")
        p_pend = [p for p in partidos_raw if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']) < datetime.now()]
        if p_pend:
            p_sel = st.selectbox("Cerrar partido:", p_pend, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            gan = st.selectbox("Resultado real:", [p_sel['Equipo_local'], 'X', p_sel['Equipo_visitante']])
            if st.button("GUARDAR Y REPARTIR"):
                supabase.table("Partidos").update({"Resultado_real": gan}).eq("Id", p_sel['Id']).execute()
                votos_p = supabase.table("Porras").select("*").eq("Id_partido", p_sel['Id']).execute().data
                for v in votos_p:
                    if v['Prediccion'] == gan:
                        u_pts = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]['Puntos']
                        supabase.table("Usuarios").update({"Puntos": u_pts + 1}).eq("Id", v['Id_usuario']).execute()
                st.rerun()
        
        st.divider()
        st.subheader("Activar Usuarios")
        u_pend = supabase.table("Usuarios").select("*").eq("Estado", "Pendiente").execute().data
        if u_pend:
            u_sel = st.selectbox("Usuario a activar:", u_pend, format_func=lambda x: x['Nombre'])
            if st.button("MARCAR COMO PAGADO"):
                supabase.table("Usuarios").update({"Estado": "Pagado"}).eq("Id", u_sel['Id']).execute()
                st.rerun()
        else: st.write("No hay pagos pendientes.")
else:
    with tabs[2]:
        st.info("Reglas: Acierto = 1 punto. Vota antes del inicio.")
