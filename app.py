import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
import pandas as pd
import re

# --- CONSTANTES DE LÍNEAS DE APUESTA ---
LINEA_CORNERS = 8.5
LINEA_TARJETAS = 4.5
LINEA_FALTAS = 22.5

def check_password_strength(password):
    """
    Devuelve (True, mensaje) si cumple los requisitos:
    Mínimo 8 caracteres, al menos 1 letra y al menos 1 número.
    """
    if len(password) < 8:
        return False, "La contraseña debe tener un mínimo de 8 caracteres."
    if not re.search(r"[A-Za-z]", password):
        return False, "La contraseña debe incluir al menos una letra."
    if not re.search(r"\d", password):
        return False, "La contraseña debe incluir al menos un número."
    return True, "OK"

# --- FUNCIÓN AYUDANTE: INTERPRETAR RESULTADOS EXACTOS ---
def get_outcome(score_str):
    if not score_str or '-' not in str(score_str): return None
    try:
        l, v = map(int, str(score_str).replace(' ', '').split('-'))
        if l > v: return '1'
        if l < v: return '2'
        return 'X'
    except:
        return None

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
    .stats-mini { background: #0D141B; border-radius: 10px; padding: 10px; margin-top: 15px; margin-bottom: 15px; border: 1px solid #1E2A38; font-size: 0.9em; text-align: center; font-weight: 600; color: #E1E8ED; }
    .flag-mini { width: 18px; border-radius: 2px; margin-right: 5px; vertical-align: middle; }
    .bote-box { background: linear-gradient(135deg, #1E2A38, #111A24); border: 2px dashed #00E676; padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 25px; }
    .bote-monto { font-size: 2.2em; font-weight: 900; color: #00E676; margin-top: 5px; }
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button { background: linear-gradient(45deg, #00E676, #00C853) !important; color: #060D13 !important; border-radius: 30px !important; font-weight: 800 !important; border: none !important; padding: 12px !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; }
    .podium-gold { background: linear-gradient(135deg, #FFB300, #FF8F00); color: #FFF; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 15px; }
    .podium-silver { background: linear-gradient(135deg, #B0BEC5, #78909C); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; }
    .podium-bronze { background: linear-gradient(135deg, #A1887F, #6D4C41); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
    footer, .viewerBadge_container__1QSob { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & ACCESO ---
if "Id_usuario" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 class='text-gradient' style='font-size: 3.5em;'>FIFA 2026</h1><h3 style='color: #FFF; font-weight: 800;'>PORRA OFICIAL</h3></div>", unsafe_allow_html=True)
        tab_log, tab_reg = st.tabs(["🔐 INICIAR SESIÓN", "📝 CREAR CUENTA"])
        
        with tab_log:
            with st.form("login_form", border=False):
                apodo_login = st.text_input("👤 Usuario", placeholder="Ej: El Mosca").strip()
                pass_login = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
                submit_log = st.form_submit_button("ENTRAR")
            
            if submit_log:
                if apodo_login and pass_login:
                    res = supabase.table("Usuarios").select("*").eq("Apodo", apodo_login).execute()
                    if res.data:
                        if str(res.data[0]["Password"]) == str(pass_login):
                            st.session_state.update({
                                "Id_usuario": res.data[0]["Id"], 
                                "Apodo": res.data[0]["Apodo"], 
                                "Estado": res.data[0].get("Estado", "Pendiente")
                            })
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta")
                    else: st.error("❌ No existe ningún usuario con ese apodo")
                else: st.warning("⚠️ Rellena todos los campos para entrar.")
                
        with tab_reg:
            with st.form("register_form", border=False):
                reg_nombre = st.text_input("Nombre", placeholder="Tu nombre")
                reg_apellidos = st.text_input("Apellidos", placeholder="Tus apellidos")
                reg_apodo = st.text_input("Usuario", placeholder="Ej: El Mosca").strip()
                reg_pass = st.text_input("Contraseña", type="password", placeholder="Mín. 8 caracteres (letras y números)")
                submit_reg = st.form_submit_button("COMPLETAR REGISTRO")
                
            if submit_reg:
                if reg_nombre and reg_apellidos and reg_apodo and reg_pass:
                    is_valid_pass, error_msg = check_password_strength(reg_pass)
                    if not is_valid_pass:
                        st.error(f"❌ Contraseña insegura: {error_msg}")
                    else:
                        check_apodo = supabase.table("Usuarios").select("Id").eq("Apodo", reg_apodo).execute()
                        if check_apodo.data:
                            st.error("❌ Ese nombre de usuario ya está registrado por otro jugador. Elige otro.")
                        else:
                            try:
                                nuevo = supabase.table("Usuarios").insert({
                                    "Nombre": reg_apodo,
                                    "Nombre_Real": reg_nombre,
                                    "Apellidos": reg_apellidos,
                                    "Apodo": reg_apodo,
                                    "Password": reg_pass,
                                    "Puntos": 0,
                                    "Estado": "Pendiente"
                                }).execute()
                                
                                st.session_state.update({
                                    "Id_usuario": nuevo.data[0]["Id"], 
                                    "Apodo": reg_apodo, 
                                    "Estado": "Pendiente"
                                })
                                st.success("🎉 ¡Cuenta creada con éxito!")
                                st.rerun()
                            except Exception as e:
                                st.error("❌ Error al guardar en la base de datos. Revisa la configuración de Supabase.")
                else: st.warning("⚠️ Por favor, rellena los 4 campos del formulario para registrarte.")
    st.stop()

# --- 4. VERIFICACIÓN PAGO ---
if st.session_state.get("Estado") == "Pendiente":
    st.title("🔒 Cuenta Inactiva")
    st.warning(f"Hola {st.session_state['Apodo']}, activa tu cuenta para jugar.")
    st.info("Entrega 30€ en efectivo a cualquiera de los administradores (Kurlander, Chema o Álvaro).")
    if st.button("🔄 Comprobar Pago"):
        res = supabase.table("Usuarios").select("Estado").eq("Id", st.session_state["Id_usuario"]).execute()
        st.session_state["Estado"] = res.data[0]["Estado"]; st.rerun()
    st.stop()

# --- 5. CARGA DE DATOS Y ORDENAMIENTO ---
ADMIN_NOMBRE = "AGS"
es_admin = st.session_state["Apodo"] == ADMIN_NOMBRE

partidos_db = supabase.table("Partidos").select("*").execute().data

def sort_matches(p):
    try: dt = datetime.fromisoformat(p['Fecha_hora']).timestamp()
    except: dt = 0
    return dt

partidos_raw = sorted(partidos_db, key=sort_matches)

pendientes = [p for p in partidos_raw if not p.get('Resultado_real')]
finalizados = [p for p in partidos_raw if p.get('Resultado_real')]
partidos_raw = pendientes + finalizados

for p in partidos_raw: 
    p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]

todos_usuarios_raw = supabase.table("Usuarios").select("Id, Apodo, Puntos, Estado").order("Puntos", desc=True).execute().data
dict_nombres = {u['Id']: u['Apodo'] if u['Apodo'] else f"User_{u['Id']}" for u in todos_usuarios_raw}

usuarios_ranking = [u for u in todos_usuarios_raw if u["Apodo"] != ADMIN_NOMBRE]
usuarios_pagados = [u for u in usuarios_ranking if u.get("Estado") == "Pagado"]
bote_total = len(usuarios_pagados) * 30

hora_actual_espana = datetime.now(timezone.utc) + timedelta(hours=2) 
todas_porras = supabase.table("Porras").select("*").execute().data

# --- CARGA DEL CHAT ---
mensajes_chat = supabase.table("Chat").select("*, Usuarios(Apodo)").order("Fecha_hora", desc=True).limit(50).execute().data
mensajes_chat.reverse()  # Para que los más nuevos salgan abajo

with st.sidebar:
    st.sidebar.markdown(f"<h2 style='text-align: center;'><span class='text-gradient'>👤 {st.session_state['Apodo']}</span></h2>", unsafe_allow_html=True)
    mi_puntos = next((u['Puntos'] for u in todos_usuarios_raw if u['Id'] == st.session_state['Id_usuario']), 0)
    st.metric("Tus Puntos Totales", mi_puntos)
    if st.button("🚪 Cerrar Sesión"): 
        st.session_state.clear()
        st.rerun()

# Forzar scroll arriba
st.markdown("""
    <script>
        var body = window.parent.document.querySelector(".main");
        if (body) { body.scrollTop = 0; }
    </script>
""", unsafe_allow_html=True)

# --- 6. TABS (VISTA PRINCIPAL) ---
orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "3º y 4º Puesto", "Final"]
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), key=lambda x: orden_fases.index(x) if x in orden_fases else 99)

# MENÚ DE PESTAÑAS INTEGRANDO EL CHAT
tabs_labels = ["📅 Partidos", "🏆 Ranking", "🔍 Ver Porras", "📊 Estadísticas", "💬 Chat", "📜 Reglas"]
if es_admin: tabs_labels.append("🛠️ Admin")
tabs = st.tabs(tabs_labels)

# ================================
# TAB 1: PARTIDOS
# ================================
with tabs[0]:
    if not partidos_raw: st.info("Cargando calendario...")
    else:
        sub_tabs = st.tabs(fases_existentes)
        votos_usuario = {v['Id_partido']: v for v in todas_porras if v['Id_usuario'] == st.session_state["Id_usuario"]}
        
        for i, fase_tab in enumerate(fases_existentes):
            with sub_tabs[i]:
                for p in [x for x in partidos_raw if x["Fase_Visual"] == fase_tab]:
                    with st.container(border=True):
                        fecha_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc)
                        st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha_p.strftime('%d %b %H:%M')}h</div>", unsafe_allow_html=True)
                        iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
                        res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
                        
                        st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right; padding-right: 10px;'><span class='team-name'>{p['Equipo_local']}</span><img src='https://flagcdn.com/32x24/{iso_l}.png' style='margin-left: 8px; border-radius: 4px;'></div><div style='flex-shrink: 0;'><span class='score-box'>{res_txt}</span></div><div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left; padding-left: 10px;'><img src='https://flagcdn.com/32x24/{iso_v}.png' style='margin-right: 8px; border-radius: 4px;'><span class='team-name'>{p['Equipo_visitante']}</span></div></div>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin: 15px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True)
                        
                        ha_votado = p['Id'] in votos_usuario

                        if p.get('Resultado_real'):
                            res_real = p['Resultado_real']
                            out_real = get_outcome(res_real)
                            if ha_votado:
                                v_u = votos_usuario[p['Id']]
                                mi_voto = v_u['Prediccion']
                                out_voto = get_outcome(mi_voto)
                                
                                pts_totales_partido = 0
                                msjs_extras = []
                                
                                if mi_voto == res_real:
                                    pts_totales_partido += 20
                                    msjs_extras.append("🎯 Pleno Marcador Exacto (+20)")
                                elif out_voto == out_real and out_real is not None:
                                    pts_totales_partido += 5
                                    msjs_extras.append("✅ Ganador/Empate (+5)")
                                else:
                                    msjs_extras.append("❌ Marcador")
                                    
                                if p.get('Corners_real') is not None and v_u.get('Pred_Corners'):
                                    if (p['Corners_real'] > LINEA_CORNERS and v_u['Pred_Corners'] == 'Más') or (p['Corners_real'] < LINEA_CORNERS and v_u['Pred_Corners'] == 'Menos'):
                                        pts_totales_partido += 2
                                        msjs_extras.append("🚩 Córners (+2)")
                                    else: msjs_extras.append("❌ Córners")
                                    
                                if p.get('Tarjetas_real') is not None and v_u.get('Pred_Tarjetas'):
                                    if (p['Tarjetas_real'] > LINEA_TARJETAS and v_u['Pred_Tarjetas'] == 'Más') or (p['Tarjetas_real'] < LINEA_TARJETAS and v_u['Pred_Tarjetas'] == 'Menos'):
                                        pts_totales_partido += 2
                                        msjs_extras.append("🟨 Tarjetas (+2)")
                                    else: msjs_extras.append("❌ Tarjetas")
                                    
                                if p.get('Faltas_real') is not None and v_u.get('Pred_Faltas'):
                                    if (p['Faltas_real'] > LINEA_FALTAS and v_u['Pred_Faltas'] == 'Más') or (p['Faltas_real'] < LINEA_FALTAS and v_u['Pred_Faltas'] == 'Menos'):
                                        pts_totales_partido += 2
                                        msjs_extras.append("🩼 Faltas (+2)")
                                    else: msjs_extras.append("❌ Faltas")
                                
                                string_resumen = " | ".join(msjs_extras)
                                if pts_totales_partido > 0:
                                    st.success(f"🏆 **¡Sumaste +{pts_totales_partido} pts!** ({string_resumen})")
                                else:
                                    st.error(f"❌ **0 puntos obtenidos:** ({string_resumen})")
                            else: st.info(f"Finalizado: {res_real}")
                        
                        elif ha_votado:
                            v = votos_usuario[p['Id']]
                            st.info(f"✅ Tu pronóstico: **{v['Prediccion']}** | 🚩 {v.get('Pred_Corners','-')} | 🟨 {v.get('Pred_Tarjetas','-')} | 🩼 {v.get('Pred_Faltas','-')}")
                        
                        elif fecha_p > hora_actual_espana:
                            st.markdown("<p style='text-align:center; font-size: 0.9em; color:#8899A6; margin-bottom:5px; font-weight:bold;'>1. Marcador Exacto</p>", unsafe_allow_html=True)
                            c1, c2, c3 = st.columns([1, 1.5, 1])
                            with c2:
                                sub_c1, sub_c2, sub_c3 = st.columns([2, 1, 2])
                                with sub_c1: g_loc = st.number_input("L", min_value=0, max_value=20, step=1, key=f"gl_{p['Id']}", label_visibility="collapsed")
                                with sub_c2: st.markdown("<div style='text-align:center; padding-top:5px; font-weight:bold;'>-</div>", unsafe_allow_html=True)
                                with sub_c3: g_vis = st.number_input("V", min_value=0, max_value=20, step=1, key=f"gv_{p['Id']}", label_visibility="collapsed")
                            
                            st.markdown(f"<p style='text-align:center; font-size: 0.9em; color:#8899A6; margin-top:15px; margin-bottom:5px; font-weight:bold;'>2. Mercados Extra (+2 pts c/u)</p>", unsafe_allow_html=True)
                            ex1, ex2, ex3 = st.columns(3)
                            with ex1: pred_c = st.selectbox(f"🚩 Córners (+{LINEA_CORNERS})", ["-", "Más", "Menos"], key=f"c_{p['Id']}")
                            with ex2: pred_t = st.selectbox(f"🟨 Tarjetas (+{LINEA_TARJETAS})", ["-", "Más", "Menos"], key=f"t_{p['Id']}")
                            with ex3: pred_f = st.selectbox(f"🩼 Faltas (+{LINEA_FALTAS})", ["-", "Más", "Menos"], key=f"f_{p['Id']}")

                            if st.button("Confirmar Pronóstico", key=f"b_{p['Id']}", use_container_width=True):
                                val_bd = f"{g_loc}-{g_vis}"
                                c_bd = pred_c if pred_c != "-" else None
                                t_bd = pred_t if pred_t != "-" else None
                                f_bd = pred_f if pred_f != "-" else None
                                
                                supabase.table("Porras").upsert({
                                    "Id_usuario": st.session_state["Id_usuario"], 
                                    "Id_partido": p["Id"], 
                                    "Prediccion": val_bd,
                                    "Pred_Corners": c_bd,
                                    "Pred_Tarjetas": t_bd,
                                    "Pred_Faltas": f_bd
                                }).execute()
                                st.rerun()
                        else: st.warning("🔒 Cerrado.")

                        if ha_votado or p.get('Resultado_real'):
                            votos_p = [v for v in todas_porras if v['Id_partido'] == p['Id'] and get_outcome(v['Prediccion']) and dict_nombres.get(v['Id_usuario']) != ADMIN_NOMBRE]
                            if votos_p:
                                n_total = len(votos_p)
                                p_l = sum(1 for v in votos_p if get_outcome(v['Prediccion']) == '1') / n_total
                                p_x = sum(1 for v in votos_p if get_outcome(v['Prediccion']) == 'X') / n_total
                                p_v = sum(1 for v in votos_p if get_outcome(v['Prediccion']) == '2') / n_total
                                
                                st.markdown(f"""
                                <div class='stats-mini'>
                                    <span style='color:#8899A6; font-size:0.85em; font-weight:400; margin-right:10px;'>Tendencia Marcador ({n_total} votos):</span><br>
                                    <img src='https://flagcdn.com/16x12/{iso_l}.png' class='flag-mini'> {p_l:.0%} &nbsp;&nbsp;|&nbsp;&nbsp; 
                                    🤝 {p_x:.0%} &nbsp;&nbsp;|&nbsp;&nbsp; 
                                    <img src='https://flagcdn.com/16x12/{iso_v}.png' class='flag-mini'> {p_v:.0%}
                                </div>
                                """, unsafe_allow_html=True)
                                if fecha_p > hora_actual_espana:
                                    st.markdown("<p style='font-size:0.7em; color:#8899A6; text-align:center; font-style:italic;'>Los pronósticos completos de tus amigos se revelarán en la pestaña '🔍 Ver Porras' al empezar el partido.</p>", unsafe_allow_html=True)

# ================================
# TAB 2: RANKING DINÁMICO
# ================================
with tabs[1]:
    if not usuarios_ranking: 
        st.info("Sin usuarios para mostrar en el ranking.")
    else:
        # CÁLCULO DE PUNTOS (100% fiable)
        pts_data = {u['Id']: {"Id": u['Id'], "Jugador (Apodo)": u['Apodo'] if u['Apodo'] else "Sin Apodo", "Global": 0, "Racha_Pts": 0} for u in usuarios_ranking}
        for f in fases_existentes:
            for uid in pts_data: pts_data[uid][f] = 0
        
        partidos_con_resultado = [p for p in partidos_db if p.get('Resultado_real') and '-' in str(p['Resultado_real'])]
        try:
            partidos_con_resultado = sorted(partidos_con_resultado, key=lambda x: datetime.fromisoformat(x['Fecha_hora']).timestamp(), reverse=True)
        except:
            pass
        ultimos_3_partidos_ids = [p['Id'] for p in partidos_con_resultado[:3]]
                
        for p in partidos_db:
            res_real = p.get('Resultado_real')
            c_real = p.get('Corners_real')
            t_real = p.get('Tarjetas_real')
            f_real = p.get('Faltas_real')
            
            if res_real and '-' in str(res_real):
                out_real = get_outcome(res_real)
                fase_val = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]
                
                for v in todas_porras:
                    if v['Id_partido'] == p['Id'] and v['Id_usuario'] in pts_data:
                        pts_partido = 0
                        pred = str(v['Prediccion'])
                        if '-' in pred:
                            if pred == res_real: pts_partido += 20
                            elif get_outcome(pred) == out_real: pts_partido += 5
                        
                        if c_real is not None and v.get('Pred_Corners'):
                            if (c_real > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (c_real < LINEA_CORNERS and v['Pred_Corners'] == 'Menos'): pts_partido += 2
                        if t_real is not None and v.get('Pred_Tarjetas'):
                            if (t_real > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (t_real < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos'): pts_partido += 2
                        if f_real is not None and v.get('Pred_Faltas'):
                            if (f_real > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (f_real < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos'): pts_partido += 2
                            
                        if pts_partido > 0:
                            pts_data[v['Id_usuario']]["Global"] += pts_partido
                            if fase_val in pts_data[v['Id_usuario']]:
                                pts_data[v['Id_usuario']][fase_val] += pts_partido
                            if p['Id'] in ultimos_3_partidos_ids:
                                pts_data[v['Id_usuario']]["Racha_Pts"] += pts_partido

        max_racha = max([u["Racha_Pts"] for u in pts_data.values()]) if pts_data else 0

        # Sub-pestañas Filtro de Clasificación
        ranking_tabs_names = ["Global"] + fases_existentes
        rk_tabs = st.tabs(ranking_tabs_names)
        
        for i, rk_name in enumerate(ranking_tabs_names):
            with rk_tabs[i]:
                ranking_ordenado = sorted(pts_data.values(), key=lambda x: x[rk_name], reverse=True)
                ranking_filtrado = [u for u in ranking_ordenado if u[rk_name] > 0]
                
                if ranking_filtrado:
                    st.markdown(f"<h3 style='text-align: center; margin-bottom: 20px;'><span class='text-gradient'>🏆 CLASIFICACIÓN: {rk_name.upper()}</span></h3>", unsafe_allow_html=True)
                    
                    # 🥇 PODIO VISUAL
                    c1, c2, c3 = st.columns(3)
                    with c1: st.markdown(f"<div class='podium-gold'>🥇<br>{ranking_filtrado[0]['Jugador (Apodo)']}<br>{ranking_filtrado[0][rk_name]} pts</div>", unsafe_allow_html=True)
                    if len(ranking_filtrado) > 1:
                        with c2: st.markdown(f"<div class='podium-silver'>🥈<br>{ranking_filtrado[1]['Jugador (Apodo)']}<br>{ranking_filtrado[1][rk_name]} pts</div>", unsafe_allow_html=True)
                    if len(ranking_filtrado) > 2:
                        with c3: st.markdown(f"<div class='podium-bronze'>🥉<br>{ranking_filtrado[2]['Jugador (Apodo)']}<br>{ranking_filtrado[2][rk_name]} pts</div>", unsafe_allow_html=True)
                    
                    st.write("---")
                    
                    # 📋 TABLA DETALLADA DIRECTA (SIN GRÁFICO DE BARRAS)
                    final_rows = []
                    for u in ranking_ordenado:
                        nombre_visual = u['Jugador (Apodo)']
                        if u['Racha_Pts'] == max_racha and max_racha > 0:
                            nombre_visual = f"🔥 {nombre_visual} (En Racha)"
                        
                        final_rows.append({
                            "Jugador (Apodo)": nombre_visual,
                            "Puntos": u[rk_name],
                            "Racha (Últ. 3 part.)": f"{u['Racha_Pts']} pts"
                        })
                    st.dataframe(pd.DataFrame(final_rows), use_container_width=True, hide_index=True)
                else:
                    st.info(f"Aún no hay puntos registrados en la fase: {rk_name}")


# ================================
# TAB 3: OJO DE HALCÓN (VER PORRAS EN TIEMPO REAL)
# ================================
with tabs[2]:
    st.markdown("<h3 style='text-align: center;'><span class='text-gradient'>🔍 OJO DE HALCÓN</span></h3>", unsafe_allow_html=True)
    st.write("Selecciona un partido para ver qué ha votado absolutamente todo el grupo en tiempo real. Los partidos del futuro permanecen ocultos hasta que empiezan.")
    st.divider()

    opciones_partidos = []
    for p in partidos_raw:
        f_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc)
        if f_p <= hora_actual_espana or p.get('Resultado_real'):
            label = f"{p['Equipo_local']} vs {p['Equipo_visitante']} ({p['Fase']})"
            if p.get('Resultado_real'): label += f" [Final: {p['Resultado_real']}]"
            else: label += " [EN JUEGO / CERRADO]"
            opciones_partidos.append((p['Id'], label))
            
    if not opciones_partidos:
        st.info("Aún no ha comenzado ningún partido del torneo. Las porras se abrirán aquí automáticamente en cuanto pite el árbitro.")
    else:
        id_sel = st.selectbox("Selecciona un partido disputado o en curso:", opciones_partidos, format_func=lambda x: x[1])
        p_sel = next(x for x in partidos_raw if x['Id'] == id_sel[0])
        
        votos_p = [v for v in todas_porras if v['Id_partido'] == p_sel['Id'] and dict_nombres.get(v['Id_usuario']) != ADMIN_NOMBRE]
        
        if votos_p:
            data_list = []
            for v in votos_p:
                row = {"Jugador": dict_nombres.get(v['Id_usuario'], "Anon")}
                
                if p_sel.get('Resultado_real'):
                    r_real = p_sel['Resultado_real']
                    o_real = get_outcome(r_real)
                    o_voto = get_outcome(v['Prediccion'])
                    
                    if v['Prediccion'] == r_real: row["Resultado"] = f"{v['Prediccion']} 🎯 (+20)"
                    elif o_voto == o_real and o_real is not None: row["Resultado"] = f"{v['Prediccion']} ✅ (+5)"
                    else: row["Resultado"] = f"{v['Prediccion']} ❌"
                    
                    if p_sel.get('Corners_real') is not None and v.get('Pred_Corners'):
                        hit = (p_sel['Corners_real'] > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (p_sel['Corners_real'] < LINEA_CORNERS and v['Pred_Corners'] == 'Menos')
                        row["Córners"] = f"{v['Pred_Corners']} " + ("🟢 (+2)" if hit else "🔴")
                    else: row["Córners"] = v.get('Pred_Corners', '-')
                    
                    if p_sel.get('Tarjetas_real') is not None and v.get('Pred_Tarjetas'):
                        hit = (p_sel['Tarjetas_real'] > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (p_sel['Tarjetas_real'] < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos')
                        row["Tarjetas"] = f"{v['Pred_Tarjetas']} " + ("🟢 (+2)" if hit else "🔴")
                    else: row["Tarjetas"] = v.get('Pred_Tarjetas', '-')
                        
                    if p_sel.get('Faltas_real') is not None and v.get('Pred_Faltas'):
                        hit = (p_sel['Faltas_real'] > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (p_sel['Faltas_real'] < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos')
                        row["Faltas"] = f"{v['Pred_Faltas']} " + ("🟢 (+2)" if hit else "🔴")
                    else: row["Faltas"] = v.get('Pred_Faltas', '-')
                else:
                    row["Resultado"] = v['Prediccion']
                    row["Córners"] = v.get('Pred_Corners', '-')
                    row["Tarjetas"] = v.get('Pred_Tarjetas', '-')
                    row["Faltas"] = v.get('Pred_Faltas', '-')
                
                data_list.append(row)
                
            st.dataframe(pd.DataFrame(data_list), use_container_width=True, hide_index=True)
        else:
            st.info("Nadie envió pronósticos para este encuentro.")


# ================================
# TAB 4: ESTADÍSTICAS DEL GRUPO (ESTÉTICA DE TABLAS SEPARADAS ORIGINAL)
# ================================
with tabs[3]:
    st.markdown("<h3 style='text-align: center;'><span class='text-gradient'>📊 LÍDERES DE MERCADO</span></h3>", unsafe_allow_html=True)
    st.write("Analítica pura del torneo. Descubre quién es el que más domina cada uno de los apartados.")
    st.divider()
    
    stats_usuarios = {u['Id']: {
        "Jugador": u['Apodo'] if u['Apodo'] else "Sin Apodo", 
        "Plenos": 0, 
        "Signos": 0,
        "Corners": 0, 
        "Tarjetas": 0, 
        "Faltas": 0
    } for u in usuarios_ranking}
    
    partidos_con_resultado = [p for p in partidos_db if p.get('Resultado_real') and '-' in str(p['Resultado_real'])]
    
    for p in partidos_con_resultado:
        res_real = p['Resultado_real']
        c_real = p.get('Corners_real')
        t_real = p.get('Tarjetas_real')
        f_real = p.get('Faltas_real')
        out_real = get_outcome(res_real)
        
        for v in todas_porras:
            if v['Id_partido'] == p['Id']:
                uid = v['Id_usuario']
                if uid in stats_usuarios:
                    pred = str(v['Prediccion'])
                    if '-' in pred:
                        if pred == res_real:
                            stats_usuarios[uid]["Plenos"] += 1
                        elif get_outcome(pred) == out_real and out_real is not None:
                            stats_usuarios[uid]["Signos"] += 1
                            
                    if c_real is not None and v.get('Pred_Corners'):
                        if (c_real > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (c_real < LINEA_CORNERS and v['Pred_Corners'] == 'Menos'):
                            stats_usuarios[uid]["Corners"] += 1
                            
                    if t_real is not None and v.get('Pred_Tarjetas'):
                        if (t_real > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (t_real < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos'):
                            stats_usuarios[uid]["Tarjetas"] += 1
                            
                    if f_real is not None and v.get('Pred_Faltas'):
                        if (f_real > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (f_real < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos'):
                            stats_usuarios[uid]["Faltas"] += 1

    if not stats_usuarios or len(partidos_con_resultado) == 0:
        st.info("Las estadísticas globales se calcularán automáticamente cuando el administrador guarde el resultado del primer partido.")
    else:
        df_stats = pd.DataFrame(stats_usuarios.values())
        
        c_st1, c_st2 = st.columns(2)
        
        with c_st1:
            st.markdown("🎯 **El Gurú de los Plenos** *(Resultados Exactos)*")
            df_p = df_stats.sort_values(by="Plenos", ascending=False)[["Jugador", "Plenos"]]
            st.dataframe(df_p, use_container_width=True, hide_index=True)
            
            st.markdown("🚩 **El Rey de los Córners** *(Aciertos)*")
            df_c = df_stats.sort_values(by="Corners", ascending=False)[["Jugador", "Corners"]]
            st.dataframe(df_c, use_container_width=True, hide_index=True)
            
            st.markdown("🛑 **Especialista en Faltas** *(Aciertos)*")
            df_f = df_stats.sort_values(by="Faltas", ascending=False)[["Jugador", "Faltas"]]
            st.dataframe(df_f, use_container_width=True, hide_index=True)
            
        with c_st2:
            st.markdown("✅ **As de los Signos (1X2)** *(Ganador/Empate)*")
            df_s = df_stats.sort_values(by="Signos", ascending=False)[["Jugador", "Signos"]]
            st.dataframe(df_s, use_container_width=True, hide_index=True)

            st.markdown("🟨 **El Leñero del Grupo** *(Aciertos en Tarjetas)*")
            df_t = df_stats.sort_values(by="Tarjetas", ascending=False)[["Jugador", "Tarjetas"]]
            st.dataframe(df_t, use_container_width=True, hide_index=True)

# ================================
# TAB 5: CHAT GLOBAL DE LA COMUNIDAD
# ================================
with tabs[4]:
    st.markdown("<h3 style='text-align: center;'><span class='text-gradient'>💬 CHAT DE LA PORRA</span></h3>", unsafe_allow_html=True)
    
    # Recarga en tiempo real de los mensajes
    try:
        res_chat = supabase.table("Chat").select("*, Usuarios(Apodo)").order("Fecha_hora", desc=True).limit(40).execute()
        mensajes_chat = res_chat.data
        mensajes_chat.reverse()
    except Exception as e:
        mensajes_chat = []

    # Inicializamos el contenedor del chat
    chat_html = "<div style='background-color: #111A24; border: 1px solid #1E2A38; border-radius: 16px; padding: 15px; height: 350px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;'>"
    
    if not mensajes_chat:
        chat_html += "<p style='color: #8899A6; text-align: center; font-style: italic; margin: auto;'>¡Nadie ha hablado aún! Rompe el hielo...</p>"
    else:
        for msg in mensajes_chat:
            autor = msg.get("Usuarios", {}).get("Apodo", "Anon") if msg.get("Usuarios") else "Anon"
            texto = msg.get("Mensaje", "")
            
            try:
                dt_msg = datetime.fromisoformat(msg["Fecha_hora"].replace("Z", "+00:00")) + timedelta(hours=2)
                hora_str = dt_msg.strftime("%H:%M")
            except:
                hora_str = ""
            
            if autor == st.session_state["Apodo"]:
                chat_html += f"<div style='align-self: flex-end; background: linear-gradient(135deg, #00C853, #00E676); color: #060D13; padding: 8px 14px; border-radius: 16px 16px 2px 16px; max-width: 80%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'><div style='font-size: 0.75em; font-weight: 900; opacity: 0.8; margin-bottom: 2px;'>Tú ({hora_str})</div><div style='font-size: 0.95em; font-weight: 500;'>{texto}</div></div>"
            else:
                chat_html += f"<div style='align-self: flex-start; background-color: #1A2433; color: #E1E8ED; padding: 8px 14px; border-radius: 16px 16px 16px 2px; max-width: 80%; border: 1px solid #2C3E50;'><div style='font-size: 0.75em; font-weight: 800; color: #00E676; margin-bottom: 2px;'>{autor} <span style='color: #8899A6; font-weight: 400;'>({hora_str})</span></div><div style='font-size: 0.95em;'>{texto}</div></div>"
                
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)
    st.write("") 

    # 🎭 BARRA DE EMOTICONOS RÁPIDOS
    # Usamos st.session_state para mantener el texto escrito mientras pulsas emojis
    if "input_chat_texto" not in st.session_state:
        st.session_state["input_chat_texto"] = ""

    emojis = ["⚽", "🔥", "🏆", "🤬", "🤫", "🎉", "🤣", "❌", "👀", "🥶"]
    cols_emoji = st.columns(len(emojis) + 2) # Margen para centrar un poco
    
    for idx, emo in enumerate(emojis):
        with cols_emoji[idx]:
            if st.button(emo, key=f"emo_{idx}"):
                st.session_state["input_chat_texto"] += emo
                st.rerun()

    # Formulario de envío
    with st.form("form_enviar_chat", clear_on_submit=True, border=False):
        c_txt, c_btn = st.columns([4, 1])
        with c_txt:
            # Vinculamos el valor al session_state actualizado por los botones de arriba
            nuevo_msg = st.text_input(
                "Escribe tu mensaje...", 
                value=st.session_state["input_chat_texto"],
                placeholder="Ej: ¡Vaya robo de partido! 🤬", 
                label_visibility="collapsed"
            ).strip()
        with c_btn:
            enviar = st.form_submit_button("ENVIAR")
            
        if enviar and nuevo_msg:
            try:
                supabase.table("Chat").insert({
                    "Id_usuario": st.session_state["Id_usuario"],
                    "Mensaje": nuevo_msg
                }).execute()
                # Vaciamos el acumulador al enviar con éxito
                st.session_state["input_chat_texto"] = ""
                st.rerun()
            except Exception as e:
                st.error(f"Error al enviar: {e}")

# ================================
# TAB 6: REGLAS
# ================================
with tabs[5]:
    st.markdown(f"""
    <div class='bote-box'>
        <div style='text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.9em; color: #8899A6; font-weight: 800;'>💰 BOTE ACUMULADO ACTUAL 💰</div>
        <div class='bote-monto'>{bote_total} €</div>
        <div style='font-size: 0.8em; color: #6D7E8C; margin-top: 5px;'>Calculado en base a {len(usuarios_pagados)} jugadores validados.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    ### 📜 Reglas de la Porra Mundial 2026
    
    1. **Ganador o Empate (5 Puntos):** Recibirás **5 puntos** si logras acertar qué equipo ganará el encuentro o si el partido terminará en empate. *(Por ejemplo, si apuestas un 2-0 y el partido queda 1-0, te llevas los 5 puntos).*
       
    2. **Resultado Exacto (20 Puntos):** Recibirás **20 puntos en total** (15 del marcador exacto + 5 del ganador acumulados) si consigues acertar la cantidad exacta de goles que marcará cada equipo (ejemplo: 2-1, 0-0, 3-0).
    
    3. **Mercados Extra (+2 Puntos c/u):** Cada acierto en Más/Menos sumará 2 puntos extra (máximo 6 extra por partido).
    Las líneas oficiales son:
       * 🚩 Córners: **{LINEA_CORNERS}**
       * 🟨 Tarjetas: **{LINEA_TARJETAS}**
       * 🛑 Faltas: **{LINEA_FALTAS}**
       
    4. **Indicador de Racha (🔥):** El jugador o jugadores que hayan sumado la mayor cantidad de puntos en los **últimos 3 partidos cerrados** recibirán el distintivo especial de fuego en la tabla de clasificaciones.
    """)

# ================================
# TAB 7: ADMIN
# ================================
if es_admin:
    with tabs[6]:
        st.subheader("🛠️ Panel Admin")
        p_admin = [p for p in partidos_raw if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc) < hora_actual_espana]
        if p_admin:
            p_sel = st.selectbox("Partido finalizado:", p_admin, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            
            st.write("Marcador Final:")
            c_admin_l, c_admin_v = st.columns(2)
            gan_l = c_admin_l.number_input("Goles Local", 0, 20, 0, key="admin_l")
            gan_v = c_admin_v.number_input("Goles Visitante", 0, 20, 0, key="admin_v")
            gan_str = f"{gan_l}-{gan_v}"
            
            st.write("Estadísticas Reales:")
            c_ac, c_at, c_af = st.columns(3)
            real_c = c_ac.number_input("🚩 Córners", 0, 50, 0)
            real_t = c_at.number_input("🟨 Tarjetas", 0, 30, 0)
            real_f = c_af.number_input("🛑 Faltas", 0, 60, 0)
            
            if st.button("GUARDAR RESULTADO Y REPARTIR PUNTOS", type="primary"):
                supabase.table("Partidos").update({
                    "Resultado_real": gan_str, "Corners_real": real_c, "Tarjetas_real": real_t, "Faltas_real": real_f
                }).eq("Id", p_sel['Id']).execute()
                
                out_real = get_outcome(gan_str)
                votos_partido = [v for v in todas_porras if v['Id_partido'] == p_sel['Id']]
                
                for v in votos_partido:
                    pts_sum = 0
                    pred = str(v['Prediccion'])
                    if '-' in pred:
                        if pred == gan_str: pts_sum += 20
                        elif get_outcome(pred) == out_real: pts_sum += 5
                    
                    if v.get('Pred_Corners') and real_c is not None:
                        if (real_c > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (real_c < LINEA_CORNERS and v['Pred_Corners'] == 'Menos'): pts_sum += 2
                    if v.get('Pred_Tarjetas') and real_t is not None:
                        if (real_t > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (real_t < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos'): pts_sum += 2
                    if v.get('Pred_Faltas') and real_f is not None:
                        if (real_f > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (real_f < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos'): pts_sum += 2
                        
                    if pts_sum > 0:
                        pts_act = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]['Puntos']
                        supabase.table("Usuarios").update({"Puntos": pts_act + pts_sum}).eq("Id", v['Id_usuario']).execute()
                st.rerun()
        st.divider()
        u_pend = supabase.table("Usuarios").select("*").eq("Estado", "Pendiente").execute().data
        if u_pend:
            u_sel = st.selectbox("Validar pago de:", u_pend, format_func=lambda x: f"{x['Apodo']} ({x.get('Nombre_Real', '')})")
            if st.button("ACTIVAR USUARIO"):
                supabase.table("Usuarios").update({"Estado": "Pagado"}).eq("Id", u_sel['Id']).execute()
                st.rerun()
