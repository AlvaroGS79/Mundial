import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
import pandas as pd

# --- 1. CONEXIÓN ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
except:
    URL = "https://ipzbkimkrckwrxisdisr.supabase.co"
    KEY = "sb_secret_VoCodXzjNBG8nYBwMS8ZBA_IMQo--_V" 

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
    "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa",
    "Italia": "it", "Chile": "cl", "Perú": "pe", "Bolivia": "bo", "Venezuela": "ve",
    "Polonia": "pl", "Dinamarca": "dk", "Serbia": "rs", "Gales": "gb-wls", "Ucrania": "ua",
    "Nigeria": "ng", "Camerún": "cm", "Jamaica": "jm", "Costa Rica": "cr", "Grecia": "gr"
}

# --- 2. CONFIGURACIÓN Y ESTILOS CSS ---
st.set_page_config(page_title="Porra Mundial 2026", layout="centered", page_icon="⚽")

st.markdown("""
    <style>
    .stApp { background-color: #060D13; color: #E1E8ED; font-family: 'Inter', sans-serif; }
    .text-gradient { background: -webkit-linear-gradient(45deg, #00E676, #00B0FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
    [data-baseweb="tab-list"] { gap: 10px; }
    [data-baseweb="tab"] { background-color: transparent !important; color: #8899A6 !important; font-weight: 600 !important; }
    [data-baseweb="tab"][aria-selected="true"] { color: #00E676 !important; border-bottom: 2px solid #00E676 !important; }
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] { background-color: #111A24 !important; border-radius: 20px !important; border: 1px solid #1E2A38 !important; padding: 15px !important; margin-bottom: 20px !important; }
    .match-header { font-size: 0.8em; color: #8899A6; text-align: center; margin-bottom: 15px; font-weight: 800; text-transform: uppercase; }
    .team-name { font-size: 1.1em; font-weight: 700; color: #FFFFFF; }
    .score-box { background: linear-gradient(145deg, #1A2433, #151E28); border: 1px solid #2C3E50; border-radius: 10px; padding: 8px 16px; font-size: 1.3em; font-weight: 900; color: #00E676; text-align: center; min-width: 65px; }
    div[role="radiogroup"] { display: flex !important; justify-content: center !important; gap: 15px !important; }
    div[data-testid="stButton"] > button { background: linear-gradient(45deg, #00E676, #00C853) !important; color: #060D13 !important; border-radius: 30px !important; font-weight: 800 !important; width: 60% !important; margin: 0 auto !important; display: block !important; }
    #MainMenu, footer, [data-testid="stHeader"], .viewerBadge_container__1QSob { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN ---
if "Id_usuario" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<div style='text-align: center;'><h1 class='text-gradient' style='font-size: 3.5em;'>FIFA 2026</h1></div>", unsafe_allow_html=True)
        with st.form("login_form", border=False):
            nombre_u = st.text_input("👤 Usuario")
            pass_u = st.text_input("🔒 Contraseña", type="password")
            submit = st.form_submit_button("ENTRAR")
        if submit:
            res = supabase.table("Usuarios").select("*").eq("Nombre", nombre_u).execute()
            if res.data and str(res.data[0]["Password"]) == str(pass_u):
                st.session_state.update({"Id_usuario": res.data[0]["Id"], "Nombre": res.data[0]["Nombre"], "Estado": res.data[0]["Estado"]})
                st.rerun()
            elif not res.data:
                nuevo = supabase.table("Usuarios").insert({"Nombre": nombre_u, "Password": pass_u, "Puntos": 0, "Estado": "Pendiente"}).execute()
                st.session_state.update({"Id_usuario": nuevo.data[0]["Id"], "Nombre": nombre_u, "Estado": "Pendiente"})
                st.rerun()
            else: st.error("Acceso denegado")
    st.stop()

# --- 4. CARGA DE DATOS (MÉTODO SIMPLE) ---
ADMIN_NOMBRE = "AGS"
es_admin = st.session_state["Nombre"] == ADMIN_NOMBRE

# Obtenemos todos los partidos de la base de datos
partidos_all = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data

# --- LÓGICA DE FILTRADO SIMPLE ---
# 1. Los que NO tienen resultado (vacío o None)
sin_resultado = [p for p in partidos_all if not p.get('Resultado_real')]
# 2. Los que SÍ tienen resultado (cualquier contenido)
con_resultado = [p for p in partidos_all if p.get('Resultado_real')]

# Juntamos: Arriba los que faltan, abajo los terminados
partidos_finales = sin_resultado + con_resultado

# --- 5. TABS ---
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if es_admin else "📜 Reglas"])

with tabs[0]:
    fases_nombres = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "3º y 4º Puesto", "Final"]
    # Procesar fase visual
    for p in partidos_finales:
        p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]
    
    fases_ex = sorted(list(set(p["Fase_Visual"] for p in partidos_finales)), key=lambda x: fases_nombres.index(x) if x in fases_nombres else 99)
    sub_tabs = st.tabs(fases_ex)
    
    # Datos de usuario para votos
    votos_data = {v['Id_partido']: v['Prediccion'] for v in supabase.table("Porras").select("Id_partido, Prediccion").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}
    hora_actual = datetime.now(timezone.utc) + timedelta(hours=2)

    for i, fase_tab in enumerate(fases_ex):
        with sub_tabs[i]:
            # Mostramos los partidos de la fase respetando el orden simple (sin resultado primero)
            for p in [x for x in partidos_finales if x["Fase_Visual"] == fase_tab]:
                with st.container(border=True):
                    f_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc)
                    st.markdown(f"<div class='match-header'>{p['Fase']} | {f_p.strftime('%d %b %H:%M')}h</div>", unsafe_allow_html=True)
                    
                    iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
                    res_vis = p['Resultado_real'] if p['Resultado_real'] else "VS"
                    
                    st.markdown(f"""<div style='display: flex; justify-content: space-between; align-items: center; width: 100%;'>
                        <div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right;'>
                            <span class='team-name' style='margin-right: 8px;'>{p['Equipo_local']}</span>
                            <img src='https://flagcdn.com/32x24/{iso_l}.png' style='border-radius:4px; min-width: 32px;'>
                        </div>
                        <div style='text-align: center; margin: 0 10px;'><span class='score-box'>{res_vis}</span></div>
                        <div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left;'>
                            <img src='https://flagcdn.com/32x24/{iso_v}.png' style='border-radius:4px; min-width: 32px; margin-right: 8px;'>
                            <span class='team-name'>{p['Equipo_visitante']}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    st.markdown("<hr style='margin: 15px 0px 15px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True)
                    
                    if p.get('Resultado_real'):
                        # Si ya tiene resultado, mostramos cómo quedó la apuesta
                        if p['Id'] in votos_data:
                            if votos_data[p['Id']] == p['Resultado_real']: st.success(f"🎯 Acertaste: {votos_data[p['Id']]}")
                            else: st.error(f"❌ Fallaste. Apostaste: {votos_data[p['Id']]}")
                        else: st.info(f"Finalizado: {p['Resultado_real']}")
                    elif p['Id'] in votos_data:
                        st.info(f"✅ Voto registrado: **{votos_data[p['Id']]}**")
                    elif f_p > hora_actual:
                        voto = st.radio("Voto:", [p['Equipo_local'], 'Empate', p['Equipo_visitante']], key=f"r_{p['Id']}", horizontal=True, label_visibility="collapsed")
                        if st.button("Confirmar", key=f"b_{p['Id']}", use_container_width=True):
                            val = 'X' if voto == 'Empate' else voto
                            supabase.table("Porras").upsert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": val}).execute()
                            st.rerun()
                    else: st.warning("🔒 Bloqueado")
