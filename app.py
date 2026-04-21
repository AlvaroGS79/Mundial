import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
import pandas as pd

# --- 1. CONEXIÓN ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
except:
    URL = "https://tu-url.supabase.co"
    KEY = "sb_publishable_7yepF3GoDlp6yBv0w54U7g_uYpNBGF_" 

supabase: Client = create_client(URL, KEY)

BANDERAS = {
    "México": "mx", "Sudáfrica": "za", "Corea del Sur": "kr", "República Checa": "cz",
    "Canadá": "ca", "Bosnia y Herzegovina": "ba", "Catar": "qa", "Suiza": "ch",
    "Brasil": "br", "Marruecos": "ma", "Haití": "ht", "Escocia": "gb-sct",
    "Estados Unidos": "us", "Paraguay": "py", "Australia": "au", "Turquía": "tr",
    "Alemania": "de", "Curaçao": "cw", "Costa de Marfil": "ci", "Ecuador": "ec",
    "Países Bajos": "nl", "Japón": "jp", "Suecia": "se", "Túnez": "tn",
    "Bélgica": "be", "Egipto": "eg", "Irán": "ir", "Nueva Zelanda": "nz",
    "España": "es", "Cabo Verde": "cv", "Arabia Saudí": "sa", "Uruguay": "uy",
    "Francia": "fr", "Senegal": "sn", "Irak": "iq", "Noruega": "no",
    "Argentina": "ar", "Argelia": "dz", "Austria": "at", "Jordania": "jo",
    "Portugal": "pt", "RD Congo": "cd", "Uzbekistán": "uz", "Colombia": "co",
    "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa"
}

# --- 2. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Porra Mundial 2026", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #060D13; color: #E1E8ED; }
    [data-testid="stVerticalBlockBorderWrapper"] { background-color: #111A24 !important; border-radius: 20px !important; border: 1px solid #1E2A38 !important; padding: 15px !important; margin-bottom: 15px !important; }
    .match-header { font-size: 0.8em; color: #8899A6; text-align: center; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }
    .team-name { font-size: 1.1em; font-weight: 700; color: #FFFFFF; }
    .score-box { background: #1A2433; border: 1px solid #2C3E50; border-radius: 8px; padding: 5px 12px; font-size: 1.3em; font-weight: 900; color: #00E676; }
    div[role="radiogroup"] { display: flex !important; justify-content: center !important; gap: 15px !important; }
    div.stButton > button { background: linear-gradient(45deg, #00E676, #00C853) !important; color: #060D13 !important; border-radius: 20px !important; font-weight: 800 !important; width: 60% !important; display: block !important; margin: 0 auto !important; }
    #MainMenu, footer, header { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN ---
if "Id_usuario" not in st.session_state:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.title("⚽ FIFA 2026")
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("ENTRAR"):
                res = supabase.table("Usuarios").select("*").eq("Nombre", u).execute()
                if res.data and str(res.data[0]["Password"]) == str(p):
                    st.session_state.update({"Id_usuario": res.data[0]["Id"], "Nombre": res.data[0]["Nombre"], "Estado": res.data[0]["Estado"]})
                    st.rerun()
                elif not res.data:
                    nuevo = supabase.table("Usuarios").insert({"Nombre": u, "Password": p, "Puntos": 0, "Estado": "Pendiente"}).execute()
                    st.session_state.update({"Id_usuario": nuevo.data[0]["Id"], "Nombre": u, "Estado": "Pendiente"})
                    st.rerun()
    st.stop()

# --- 4. CARGA DE DATOS ---
ADMIN = "AGS"
es_admin = st.session_state["Nombre"] == ADMIN

# Obtener votos del usuario
votos = {v['Id_partido'] for v in supabase.table("Porras").select("Id_partido").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}

# Obtener todos los partidos
partidos = supabase.table("Partidos").select("*").execute().data

# --- LÓGICA DE ORDENAMIENTO DE PESOS ---
def calcular_prioridad(p):
    # Peso 2: Ya tiene resultado oficial (Al final)
    if p.get('Resultado_real'): return 2
    # Peso 1: Ya lo ha votado el usuario (Debajo de los pendientes)
    if p['Id'] in votos: return 1
    # Peso 0: Pendiente de votar (Arriba del todo)
    return 0

if partidos:
    # Ordenamos por Prioridad (0, 1, 2) y luego por Fecha
    partidos = sorted(partidos, key=lambda x: (calcular_prioridad(x), x['Fecha_hora']))

# --- 5. INTERFAZ ---
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if es_admin else "📜 Reglas"])

with tabs[0]:
    for p in partidos:
        with st.container(border=True):
            fecha = datetime.fromisoformat(p['Fecha_hora']).strftime('%d %b %H:%M')
            st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha}h</div>", unsafe_allow_html=True)
            
            # Marcador
            iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
            res_vis = p['Resultado_real'] if p['Resultado_real'] else "VS"
            st.markdown(f"""<div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='flex: 1; text-align: right;'><span class='team-name'>{p['Equipo_local']}</span> <img src='https://flagcdn.com/32x24/{iso_l}.png'></div>
                <div style='margin: 0 15px;'><span class='score-box'>{res_vis}</span></div>
                <div style='flex: 1; text-align: left;'><img src='https://flagcdn.com/32x24/{iso_v}.png'> <span class='team-name'>{p['Equipo_visitante']}</span></div>
            </div>""", unsafe_allow_html=True)
            
            st.write("---")
            
            # Lógica de botones
            if p.get('Resultado_real'):
                st.info(f"Partido Finalizado. Resultado: {p['Resultado_real']}")
            elif p['Id'] in votos:
                st.success("✅ Ya has votado este partido")
            else:
                escogido = st.radio("Tu apuesta:", [p['Equipo_local'], 'Empate', p['Equipo_visitante']], key=f"r{p['Id']}", horizontal=True, label_visibility="collapsed")
                if st.button("Confirmar Apuesta", key=f"b{p['Id']}"):
                    val = 'X' if escogido == 'Empate' else escogido
                    supabase.table("Porras").upsert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": val}).execute()
                    st.rerun()

with tabs[1]:
    u_list = supabase.table("Usuarios").select("Nombre, Puntos").order("Puntos", desc=True).execute().data
    st.table(pd.DataFrame(u_list))

if es_admin:
    with tabs[2]:
        st.subheader("Panel Admin")
        p_pend = [p for p in partidos if not p.get('Resultado_real')]
        if p_pend:
            p_sel = st.selectbox("Cerrar partido:", p_pend, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            res_adm = st.selectbox("Ganador:", [p_sel['Equipo_local'], 'X', p_sel['Equipo_visitante']])
            if st.button("GUARDAR RESULTADO"):
                supabase.table("Partidos").update({"Resultado_real": res_adm}).eq("Id", p_sel['Id']).execute()
                # Repartir puntos
                porras = supabase.table("Porras").select("*").eq("Id_partido", p_sel['Id']).execute().data
                for v in porras:
                    if v['Prediccion'] == res_adm:
                        cur_pts = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]['Puntos']
                        supabase.table("Usuarios").update({"Puntos": cur_pts + 1}).eq("Id", v['Id_usuario']).execute()
                st.rerun()
