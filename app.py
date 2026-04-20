import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# 1. CONEXIÓN (Recuerda usar st.secrets para producción)
URL = "https://ipzbkimkrckwrxisdisr.supabase.co"
KEY = "tu_clave_aqui" # USA TU KEY REAL
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
    .stApp { background-color: #0b101e; color: #ffffff; }
    .match-card { background-color: #1a233a; padding: 20px; border-radius: 15px; border: 1px solid #2d3748; margin-bottom: 15px; }
    .match-header { font-size: 0.8em; color: #a0aec0; text-align: center; margin-bottom: 10px; text-transform: uppercase; }
    .team-name { font-size: 1.1em; font-weight: bold; }
    div.stButton > button:first-child { background-color: #00e676 !important; color: #0b101e !important; border-radius: 25px; font-weight: bold; width: 100%; border: none; }
    .podium-gold { background: linear-gradient(135deg, #FFD700, #FDB931); color: #000; padding: 15px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN (Simplificado para el ejemplo)
if "Id_usuario" not in st.session_state:
    st.title("🏆 Porra Mundial 2026")
    with st.container(border=True):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("Usuarios").select("*").eq("Nombre", u).execute()
            if res.data and str(res.data[0]["Password"]) == str(p):
                st.session_state["Id_usuario"], st.session_state["Nombre"] = res.data[0]["Id"], res.data[0]["Nombre"]
                st.rerun()
            elif not res.data: # Registro automático
                nuevo = supabase.table("Usuarios").insert({"Nombre": u, "Password": p, "Puntos": 0}).execute()
                st.session_state["Id_usuario"], st.session_state["Nombre"] = nuevo.data[0]["Id"], nuevo.data[0]["Nombre"]
                st.rerun()
    st.stop()

# --- DATOS ---
partidos_raw = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data
todos_usuarios = supabase.table("Usuarios").select("Id, Nombre, Puntos").order("Puntos", desc=True).execute().data

# DETERMINAR FASES DISPONIBLES (Agrupando Grupos)
# Creamos una columna virtual para la visualización
for p in partidos_raw:
    if "Grupo" in p["Fase"]:
        p["Fase_Visual"] = "Fase de Grupos"
    else:
        p["Fase_Visual"] = p["Fase"]

# Definimos el orden de las pestañas
orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "Final"]
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), 
                          key=lambda x: orden_fases.index(x) if x in orden_fases else 99)

# --- TABS PRINCIPALES ---
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if st.session_state["Nombre"] == "AGS" else "📜 Reglas"])

with tabs[0]:
    if not partidos_raw:
        st.info("No hay partidos.")
    else:
        # Sub-pestañas para las fases agrupadas
        sub_tabs = st.tabs(fases_existentes)
        
        # Obtenemos apuestas del usuario
        votos = {v['Id_partido']: v['Prediccion'] for v in supabase.table("Porras").select("Id_partido, Prediccion").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}

        for i, fase_tab in enumerate(fases_existentes):
            with sub_tabs[i]:
                # Filtrar partidos de esta fase agrupada
                partidos_fase = [p for p in partidos_raw if p["Fase_Visual"] == fase_tab]
                
                for p in partidos_fase:
                    st.markdown("<div class='match-card'>", unsafe_allow_html=True)
                    
                    # Header: Fecha y Fase real (Ej: "Grupo A" o "Octavos")
                    fecha = datetime.fromisoformat(p['Fecha_hora'])
                    st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha.strftime('%d/%m %H:%M')}h</div>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        iso_l = BANDERAS.get(p['Equipo_local'], "un")
                        st.markdown(f"<div style='text-align: right;'><b>{p['Equipo_local']}</b> <img src='https://flagcdn.com/24x18/{iso_l}.png'></div>", unsafe_allow_html=True)
                    with col2:
                        res_display = p['Resultado_real'] if p['Resultado_real'] else "VS"
                        st.markdown(f"<div style='text-align: center; font-weight: bold; background: #2d3748; border-radius: 5px;'>{res_display}</div>", unsafe_allow_html=True)
                    with col3:
                        iso_v = BANDERAS.get(p['Equipo_visitante'], "un")
                        st.markdown(f"<div><img src='https://flagcdn.com/24x18/{iso_v}.png'> <b>{p['Equipo_visitante']}</b></div>", unsafe_allow_html=True)
                    
                    # Lógica de apuestas
                    if p.get('Resultado_real'):
                        if votos.get(p['Id']) == p['Resultado_real']: st.success(f"🎯 Acertaste: {votos[p['Id']]}")
                        elif p['Id'] in votos: st.error(f"❌ Apostaste: {votos[p['Id']]}")
                    elif p['Id'] in votos:
                        st.info(f"Tu apuesta: **{votos[p['Id']]}**")
                    elif fecha > datetime.now():
                        pred = st.radio("Resultado:", [p['Equipo_local'], 'X', p['Equipo_visitante']], key=f"p_{p['Id']}", horizontal=True, label_visibility="collapsed")
                        if st.button("Confirmar", key=f"b_{p['Id']}"):
                            supabase.table("Porras").insert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": pred}).execute()
                            st.rerun()
                    else:
                        st.warning("Cerrado.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    # RANKING (Igual al anterior, con podio visual)
    st.markdown("<div class='podium-gold'>🥇 LÍDER: " + (todos_usuarios[0]['Nombre'] if todos_usuarios else "---") + "</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(todos_usuarios)[['Nombre', 'Puntos']], use_container_width=True, hide_index=True)