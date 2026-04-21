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
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] { background-color: #111A24 !important; border-radius: 24px !important; border: 1px solid #1E2A38 !important; padding: 15px !important; margin-bottom: 25px !important; }
    .match-header { font-size: 0.8em; color: #8899A6; text-align: center; margin-bottom: 15px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; }
    .team-name { font-size: 1.15em; font-weight: 700; color: #FFFFFF; }
    .score-box { background: linear-gradient(145deg, #1A2433, #151E28); border: 1px solid #2C3E50; border-radius: 10px; padding: 8px 16px; font-size: 1.4em; font-weight: 900; color: #00E676; text-align: center; display: inline-block; min-width: 70px; }
    
    /* Apartado Social Mini */
    .stats-mini { background: #0D141B; border-radius: 10px; padding: 10px; margin-top: 15px; margin-bottom: 15px; border: 1px solid #1E2A38; font-size: 0.9em; text-align: center; font-weight: 600; color: #E1E8ED; }
    .flag-mini { width: 18px; border-radius: 2px; margin-right: 5px; vertical-align: middle; }
    
    div[role="radiogroup"] { display: flex !important; justify-content: center !important; gap: 15px !important; }
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button { background: linear-gradient(45deg, #00E676, #00C853) !important; color: #060D13 !important; border-radius: 30px !important; font-weight: 800 !important; border: none !important; padding: 12px !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; }
    .podium-gold { background: linear-gradient(135deg, #FFB300, #FF8F00); color: #FFF; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 15px; }
    .podium-silver { background: linear-gradient(135deg, #B0BEC5, #78909C); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; }
    .podium-bronze { background: linear-gradient(135deg, #A1887F, #6D4C41); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; }
    
    /* Transparencia en el header para que se vea el botón de menú lateral */
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
    footer, .viewerBadge_container__1QSob { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN ---
if "Id_usuario" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.5, 1])
    with col_login:
        st.markdown("<div style='text-align: center; margin-bottom: 30px;'><h1 class='text-gradient' style='font-size: 3.5em;'>FIFA 2026</h1><h3 style='color: #FFF; font-weight: 800;'>PORRA OFICIAL</h3></div>", unsafe_allow_html=True)
        with st.form("login_form", border=False):
            nombre_u = st.text_input("👤 Usuario", placeholder="Tu nombre")
            pass_u = st.text_input("🔒 Contraseña", type="password")
            submit = st.form_submit_button("ENTRAR")
        if submit:
            if nombre_u.strip() and pass_u.strip():
                res = supabase.table("Usuarios").select("*").eq("Nombre", nombre_u).execute()
                if res.data:
                    if str(res.data[0]["Password"]) == str(pass_u):
                        st.session_state.update({"Id_usuario": res.data[0]["Id"], "Nombre": res.data[0]["Nombre"], "Estado": res.data[0].get("Estado", "Pendiente")})
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta")
                else:
                    nuevo = supabase.table("Usuarios").insert({"Nombre": nombre_u, "Password": pass_u, "Puntos": 0, "Estado": "Pendiente"}).execute()
                    st.session_state.update({"Id_usuario": nuevo.data[0]["Id"], "Nombre": nombre_u, "Estado": "Pendiente"})
                    st.rerun()
    st.stop()

# --- 4. VERIFICACIÓN PAGO ---
if st.session_state.get("Estado") == "Pendiente":
    st.title("🔒 Cuenta Inactiva")
    st.warning(f"Hola {st.session_state['Nombre']}, activa tu cuenta para jugar.")
    st.info("Envía 20€ por Bizum al 6XX XXX XXX indicando tu nombre.")
    if st.button("🔄 Comprobar Pago"):
        res = supabase.table("Usuarios").select("Estado").eq("Id", st.session_state["Id_usuario"]).execute()
        st.session_state["Estado"] = res.data[0]["Estado"]; st.rerun()
    st.stop()

# --- 5. CARGA DE DATOS ---
ADMIN_NOMBRE = "AGS"
es_admin = st.session_state["Nombre"] == ADMIN_NOMBRE

partidos_db = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data

# Separación manual: Sin resultado arriba
pendientes = [p for p in partidos_db if not p.get('Resultado_real')]
finalizados = [p for p in partidos_db if p.get('Resultado_real')]
partidos_raw = pendientes + finalizados
for p in partidos_raw: p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]

todos_usuarios_raw = supabase.table("Usuarios").select("Id, Nombre, Puntos").order("Puntos", desc=True).execute().data
dict_nombres = {u['Id']: u['Nombre'] for u in todos_usuarios_raw}
usuarios_ranking = [u for u in todos_usuarios_raw if u["Nombre"] != ADMIN_NOMBRE]

hora_actual_espana = datetime.now(timezone.utc) + timedelta(hours=2) 
todas_porras = supabase.table("Porras").select("*").execute().data

with st.sidebar:
    st.markdown(f"<h2 style='text-align: center;'><span class='text-gradient'>👤 {st.session_state['Nombre']}</span></h2>", unsafe_allow_html=True)
    mi_puntos = next((u['Puntos'] for u in todos_usuarios_raw if u['Id'] == st.session_state['Id_usuario']), 0)
    st.metric("Tus Puntos", mi_puntos)
    if st.button("🚪 Cerrar Sesión"): st.session_state.clear(); st.rerun()

# --- LÓGICA DE PANTALLA DE DETALLE DE PARTIDO ---
if "view_partido" not in st.session_state:
    st.session_state["view_partido"] = None

if st.session_state["view_partido"]:
    p_id = st.session_state["view_partido"]
    p = next((x for x in partidos_db if x['Id'] == p_id), None)
    
    # Botón para volver atrás
    if st.button("⬅️ VOLVER AL CALENDARIO"):
        st.session_state["view_partido"] = None
        st.rerun()
        
    if p:
        with st.container(border=True):
            fecha_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc)
            st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha_p.strftime('%d %b %H:%M')}h</div>", unsafe_allow_html=True)
            iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
            res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
            
            st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right; padding-right: 10px;'><span class='team-name'>{p['Equipo_local']}</span><img src='https://flagcdn.com/32x24/{iso_l}.png' style='margin-left: 8px; border-radius: 4px;'></div><div style='flex-shrink: 0;'><span class='score-box'>{res_txt}</span></div><div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left; padding-left: 10px;'><img src='https://flagcdn.com/32x24/{iso_v}.png' style='margin-right: 8px; border-radius: 4px;'><span class='team-name'>{p['Equipo_visitante']}</span></div></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 15px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True)
            
            st.subheader("📊 Pronósticos de la comunidad")
            votos_p = [v for v in todas_porras if v['Id_partido'] == p['Id']]
            
            if votos_p:
                # Mostrar tabla con Nombres y Votos
                df_votos = pd.DataFrame([{"Jugador": dict_nombres.get(v['Id_usuario'], "Anon"), "Apuesta": v['Prediccion']} for v in votos_p])
                st.dataframe(df_votos, use_container_width=True, hide_index=True)
            else:
                st.info("Nadie votó en este partido.")
    
    # Detenemos la ejecución aquí para que no dibuje los TABS si estamos en la vista de detalle
    st.stop()


# --- 6. TABS (VISTA PRINCIPAL) ---
orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "3º y 4º Puesto", "Final"]
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), key=lambda x: orden_fases.index(x) if x in orden_fases else 99)

tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if es_admin else "📜 Reglas"])

with tabs[0]:
    if not partidos_raw: st.info("Cargando calendario...")
    else:
        sub_tabs = st.tabs(fases_existentes)
        votos_usuario = {v['Id_partido']: v['Prediccion'] for v in todas_porras if v['Id_usuario'] == st.session_state["Id_usuario"]}
        
        for i, fase_tab in enumerate(fases_existentes):
            with sub_tabs[i]:
                for p in [x for x in partidos_raw if x["Fase_Visual"] == fase_tab]:
                    with st.container(border=True):
                        fecha_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc)
                        st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha_p.strftime('%d %b %H:%M')}h</div>", unsafe_allow_html=True)
                        iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
                        res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
                        
                        st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right; padding-right: 10px;'><span class='team-name'>{p['Equipo_local']}</span><img src='https://flagcdn.com/32x24/{iso_l}.png' style='margin-left: 8px; border-radius: 4px;'></div><div style='flex-shrink: 0;'><span class='score-box'>{res_txt}</span></div><div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left; padding-left: 10px;'><img src='https://flagcdn.com/32x24/{iso_v}.png' style='margin-right: 8px; border-radius: 4px;'><span class='team-name'>{p['Equipo_visitante']}</span></div></div>", unsafe_allow_html=True)
                        
                        st.markdown("<hr style='margin: 15px 0px 10px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True)
                        
                        ha_votado = p['Id'] in votos_usuario

                        # ZONA DE RESULTADO O INFORMACIÓN DEL VOTO
                        if p.get('Resultado_real'):
                            if ha_votado:
                                if votos_usuario[p['Id']] == p['Resultado_real']: st.success(f"🎯 Acertaste: {votos_usuario[p['Id']]}")
                                else: st.error(f"❌ Fallaste. Apostaste: {votos_usuario[p['Id']]}")
                            else: st.info(f"Finalizado: {p['Resultado_real']}")
                        elif ha_votado:
                            st.info(f"✅ Tu voto: **{votos_usuario[p['Id']]}**")
                        elif fecha_p > hora_actual_espana:
                            pred = st.radio("Voto:", [p['Equipo_local'], 'Empate', p['Equipo_visitante']], key=f"r_{p['Id']}", horizontal=True, label_visibility="collapsed")
                            if st.button("Confirmar", key=f"b_{p['Id']}", use_container_width=True):
                                val_bd = 'X' if pred == 'Empate' else pred
                                supabase.table("Porras").upsert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": val_bd}).execute(); st.rerun()
                        else: st.warning("🔒 Cerrado.")

                        # --- ESTADÍSTICAS MINI (SOLO SI YA HA VOTADO O EL PARTIDO HA TERMINADO) ---
                        if ha_votado or p.get('Resultado_real'):
                            votos_p = [v for v in todas_porras if v['Id_partido'] == p['Id']]
                            if votos_p:
                                n_total = len(votos_p)
                                p_l = len([v for v in votos_p if v['Prediccion'] == p['Equipo_local']]) / n_total
                                p_x = len([v for v in votos_p if v['Prediccion'] == 'X']) / n_total
                                p_v = len([v for v in votos_p if v['Prediccion'] == p['Equipo_visitante']]) / n_total
                                
                                # Barra de favoritismo con porcentajes y banderas
                                st.markdown(f"""
                                <div class='stats-mini'>
                                    <span style='color:#8899A6; font-size:0.85em; font-weight:400; margin-right:10px;'>Comunidad ({n_total} votos):</span><br>
                                    <img src='https://flagcdn.com/16x12/{iso_l}.png' class='flag-mini'> {p_l:.0%} &nbsp;&nbsp;|&nbsp;&nbsp; 
                                    🤝 {p_x:.0%} &nbsp;&nbsp;|&nbsp;&nbsp; 
                                    <img src='https://flagcdn.com/16x12/{iso_v}.png' class='flag-mini'> {p_v:.0%}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Botón para ir a la vista de detalles (Solo si el partido ha comenzado)
                                if fecha_p <= hora_actual_espana:
                                    if st.button("🔍 Ver quién ha votado", key=f"btn_det_{p['Id']}", use_container_width=True):
                                        st.session_state["view_partido"] = p['Id']
                                        st.rerun()
                                else:
                                    st.markdown("<p style='font-size:0.7em; color:#8899A6; text-align:center; font-style:italic;'>La lista de votos se desbloquea al inicio del partido.</p>", unsafe_allow_html=True)
                        elif fecha_p > hora_actual_espana:
                            # Si no ha votado, invitamos a que lo haga
                            st.markdown("<p style='font-size:0.75em; color:#556677; text-align:center; margin-top:5px;'>Vota para descubrir la tendencia de la comunidad 🗳️</p>", unsafe_allow_html=True)

with tabs[1]:
    if not usuarios_ranking: st.info("Sin usuarios.")
    else:
        u_p = [u for u in usuarios_ranking if u['Puntos'] > 0]
        if u_p:
            st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'><span class='text-gradient'>🏆 LÍDERES DEL MUNDIAL</span></h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='podium-gold'>🥇<br>{u_p[0]['Nombre']}<br>{u_p[0]['Puntos']} pts</div>", unsafe_allow_html=True)
            if len(u_p) > 1:
                with c2: st.markdown(f"<div class='podium-silver'>🥈<br>{u_p[1]['Nombre']}<br>{u_p[1]['Puntos']} pts</div>", unsafe_allow_html=True)
            if len(u_p) > 2:
                with c3: st.markdown(f"<div class='podium-bronze'>🥉<br>{u_p[2]['Nombre']}<br>{u_p[2]['Puntos']} pts</div>", unsafe_allow_html=True)
            st.divider()
        st.dataframe(pd.DataFrame(usuarios_ranking)[['Nombre', 'Puntos']], use_container_width=True, hide_index=True)

if es_admin:
    with tabs[2]:
        st.subheader("🛠️ Panel Admin")
        p_admin = [p for p in partidos_db if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc) < hora_actual_espana]
        if p_admin:
            p_sel = st.selectbox("Partido finalizado:", p_admin, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            gan = st.selectbox("Resultado final:", [p_sel['Equipo_local'], 'X', p_sel['Equipo_visitante']])
            if st.button("GUARDAR Y REPARTIR PUNTOS", type="primary"):
                supabase.table("Partidos").update({"Resultado_real": gan}).eq("Id", p_sel['Id']).execute()
                votos_partido = [v for v in todas_porras if v['Id_partido'] == p_sel['Id']]
                for v in votos_partido:
                    if v['Prediccion'] == gan:
                        pts = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]['Puntos']
                        supabase.table("Usuarios").update({"Puntos": pts + 1}).eq("Id", v['Id_usuario']).execute()
                st.rerun()
        st.divider()
        u_pend = supabase.table("Usuarios").select("*").eq("Estado", "Pendiente").execute().data
        if u_pend:
            u_sel = st.selectbox("Validar pago:", u_pend, format_func=lambda x: x['Nombre'])
            if st.button("ACTIVAR USUARIO"):
                supabase.table("Usuarios").update({"Estado": "Pagado"}).eq("Id", u_sel['Id']).execute(); st.rerun()
        else: st.write("No hay pagos pendientes.")
else:
    with tabs[2]:
        st.markdown("""
        ### 📜 Reglas de la Porra Mundial 2026
        1. **Puntos:** 1 punto por acierto.
        2. **Visibilidad:** Los porcentajes de la comunidad solo se desbloquean tras realizar tu voto.
        3. **Transparencia:** Haciendo clic en "Ver quién ha votado", puedes revisar las apuestas individuales de cada jugador, pero solo una vez iniciado el partido.
        4. **Cierre:** Las apuestas se bloquean en el momento del saque inicial.
        """)
