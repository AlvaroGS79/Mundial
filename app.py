import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# 1. CONEXIÓN
URL = "https://ipzbkimkrckwrxisdisr.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlwemJraW1rcmNrd3J4aXNkaXNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4MzEyNjAsImV4cCI6MjA4OTQwNzI2MH0.4P7vwWBnX6sr5rxI7iixArK0FshGOfH9KKLnVCEubhY"
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

# 2. CONFIG Y CSS
st.set_page_config(page_title="Porra Mundial 2026", layout="centered", page_icon="🏆")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div { background-color: transparent !important; border: none !important; }
    div.stButton > button:first-child { background-color: #2e7d32 !important; color: white !important; border-radius: 10px; font-weight: bold; width: 100%; }
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) { border: 1px solid rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 12px; }
    [data-testid="stDataFrameToolbar"], #MainMenu, footer { display: none !important; }
    [data-testid="stMetricValue"] { color: #ffd700 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN
if "Id_usuario" not in st.session_state:
    st.title("🏆 Porra Mundial 2026")
    with st.container(border=True):
        nombre_usuario = st.text_input("Usuario:")
        pass_usuario = st.text_input("Contraseña:", type="password")
        if st.button("ENTRAR", type="primary"):
            if nombre_usuario.strip() and pass_usuario.strip():
                res = supabase.table("Usuarios").select("*").eq("Nombre", nombre_usuario).execute()
                if len(res.data) > 0:
                    if str(res.data[0].get("Password")) == str(pass_usuario):
                        st.session_state["Id_usuario"], st.session_state["Nombre"] = res.data[0]["Id"], res.data[0]["Nombre"]
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta.")
                else:
                    nuevo = supabase.table("Usuarios").insert({"Nombre": nombre_usuario, "Password": pass_usuario, "Puntos": 0}).execute()
                    st.session_state["Id_usuario"], st.session_state["Nombre"] = nuevo.data[0]["Id"], nuevo.data[0]["Nombre"]
                    st.rerun()
    st.stop()

# --- DATOS ---
todos_usuarios = supabase.table("Usuarios").select("Id, Nombre, Puntos").order("Puntos", desc=True).execute().data
mis_puntos, mi_posicion = 0, 1
for i, u in enumerate(todos_usuarios):
    if u["Id"] == st.session_state["Id_usuario"]:
        mis_puntos, mi_posicion = u["Puntos"], i + 1
        break

with st.sidebar:
    st.markdown(f"## ⚽ Mi Perfil")
    st.markdown(f"**Jugador:** {st.session_state['Nombre']}")
    c1, c2 = st.columns(2)
    c1.metric("Puntos", mis_puntos)
    c2.metric("Posición", f"{mi_posicion}º")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- CONTENIDO ---
st.title("🏆 Porra Mundial 2026")
# Obtenemos los partidos y las fases disponibles
partidos_raw = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data
df_p = pd.DataFrame(partidos_raw)
fases_disponibles = df_p['Fase'].unique().tolist() if not df_p.empty else []

ADMIN_NOMBRE = "AGS"
es_admin = st.session_state['Nombre'] == ADMIN_NOMBRE
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "📜 Reglas"] + (["⚙️ Admin"] if es_admin else []))

# --- TAB 1: PARTIDOS CON SUBMENÚS ---
with tabs[0]:
    if not partidos_raw:
        st.info("No hay partidos cargados.")
    else:
        # ✅ MEJORA: SUBMENÚ DE FASES
        fase_elegida = st.selectbox("📍 Selecciona Fase/Grupo:", fases_disponibles)
        
        votos = {v['Id_partido']: v['Prediccion'] for v in supabase.table("Porras").select("Id_partido, Prediccion").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}
        
        partidos_filtrados = [p for p in partidos_raw if p['Fase'] == fase_elegida]
        
        for p in partidos_filtrados:
            with st.container(border=True):
                iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
                st.markdown(f"#### <img src='https://flagcdn.com/24x18/{iso_l}.png'> {p['Equipo_local']} vs {p['Equipo_visitante']} <img src='https://flagcdn.com/24x18/{iso_v}.png'>", unsafe_allow_html=True)
                
                fecha = datetime.fromisoformat(p['Fecha_hora'])
                st.caption(f"⏰ {fecha.strftime('%d/%m/%Y - %H:%M')}h")
                
                if p.get('Resultado_real'):
                    st.info(f"Finalizado: **{p['Resultado_real']}**")
                    if p['Id'] in votos:
                        if votos[p['Id']] == p['Resultado_real']: st.success("🎯 ¡Acertaste!")
                        else: st.error(f"❌ Tu apuesta: {votos[p['Id']]}")
                elif p['Id'] in votos:
                    st.success(f"Apostaste por: **{votos[p['Id']]}**")
                elif fecha > datetime.now():
                    pred = st.radio("¿Pronóstico?", [p['Equipo_local'], 'X', p['Equipo_visitante']], key=f"r_{p['Id']}", horizontal=True)
                    if st.button("Confirmar", key=f"b_{p['Id']}"):
                        supabase.table("Porras").insert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": pred}).execute()
                        st.rerun()
                else: st.warning("🔒 Cerrado.")

# --- TAB 2: RANKING ---
with tabs[1]:
    st.subheader("📊 Clasificación")
    if todos_usuarios:
        df = pd.DataFrame(todos_usuarios)
        def medalla(i): return "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        df['Pos'] = [medalla(i) for i in range(len(df))]
        df['Jugador'] = df['Pos'] + " " + df['Nombre']
        max_p = int(df['Puntos'].max()) if df['Puntos'].max() > 0 else 10
        def style_row(row):
            return ['background-color: #ffd700; color: #0e1117; font-weight: bold;'] * len(row) if row['Nombre'] == st.session_state['Nombre'] else [''] * len(row)
        st.dataframe(df[['Jugador', 'Puntos', 'Nombre']].style.apply(style_row, axis=1), use_container_width=True, hide_index=True,
                     column_config={"Jugador": "Jugador", "Puntos": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max_p), "Nombre": None})

# --- REGLAS ---
with tabs[2]:
    st.info("Acierto: 1 pto | X: Empate | Vota antes del pitido inicial.")

# --- ADMIN ---
if es_admin:
    with tabs[3]:
        # Filtramos partidos pasados sin resultado
        pendientes = [p for p in partidos_raw if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']) < datetime.now()]
        if pendientes:
            p_sel = st.selectbox("Cerrar:", pendientes, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            ganador = st.selectbox("Ganador:", [p_sel['Equipo_local'], 'X', p_sel['Equipo_visitante']])
            if st.button("GUARDAR RESULTADO"):
                supabase.table("Partidos").update({"Resultado_real": ganador}).eq("Id", p_sel['Id']).execute()
                p_votos = supabase.table("Porras").select("*").eq("Id_partido", p_sel['Id']).execute().data
                for v in p_votos:
                    if v['Prediccion'] == ganador:
                        u = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]
                        supabase.table("Usuarios").update({"Puntos": u['Puntos'] + 1}).eq("Id", v['Id_usuario']).execute()
                st.rerun()