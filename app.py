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
        return False, "La contraseña debe tener un mínimo de 8 caracteres." [cite: 112]
    if not re.search(r"[A-Za-z]", password):
        return False, "La contraseña debe incluir al menos una letra." [cite: 113]
    if not re.search(r"\d", password):
        return False, "La contraseña debe incluir al menos un número." [cite: 114]
    return True, "OK" [cite: 115]

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
    KEY = st.secrets["SUPABASE_KEY"] [cite: 116]
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
    "Bélgica": "be", "Egipto": "eg", "Irán": "ir", "Nueva Zelanda": "nz", [cite: 117]
    "España": "es", "Cabo Verde": "cv", "Arabia Saudí": "sa", "Uruguay": "uy",
    "Francia": "fr", "Senegal": "sn", "Irak": "iq", "Noruega": "no",
    "Argentina": "ar", "Argelia": "dz", "Austria": "at", "Jordania": "jo",
    "Portugal": "pt", "RD Congo": "cd", "Uzbekistán": "uz", "Colombia": "co",
    "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa",
    "Italia": "it", "Chile": "cl", "Perú": "pe", "Bolivia": "bo", "Venezuela": "ve",
    "Polonia": "pl", "Dinamarca": "dk", "Serbia": "rs", "Gales": "gb-wls", "Ucrania": "ua",
    "Nigeria": "ng", "Camerún": "cm", "Jamaica": "jm", "Costa Rica": "cr", "Grecia": "gr" [cite: 118]
}

# --- 2. CONFIGURACIÓN Y ESTILOS CSS ---
st.set_page_config(page_title="Porra Mundial 2026", layout="centered", page_icon="⚽")

st.markdown("""
    <style>
    .stApp { background-color: #060D13; color: #E1E8ED; font-family: 'Inter', sans-serif; } [cite: 119]
    .text-gradient { background: -webkit-linear-gradient(45deg, #00E676, #00B0FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; } [cite: 120]
    [data-baseweb="tab-list"] { gap: 10px; }
    [data-baseweb="tab"] { background-color: transparent !important; color: #8899A6 !important; font-weight: 600 !important; } [cite: 121]
    [data-baseweb="tab"][aria-selected="true"] { color: #00E676 !important; border-bottom: 2px solid #00E676 !important; } [cite: 122]
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] { background-color: #111A24 !important; border-radius: 24px !important; border: 1px solid #1E2A38 !important; padding: 15px !important; margin-bottom: 25px !important; } [cite: 123]
    .match-header { font-size: 0.8em; color: #8899A6; text-align: center; margin-bottom: 15px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; } [cite: 124]
    .team-name { font-size: 1.15em; font-weight: 700; color: #FFFFFF; } [cite: 125]
    .score-box { background: linear-gradient(145deg, #1A2433, #151E28); border: 1px solid #2C3E50; border-radius: 10px; padding: 8px 16px; font-size: 1.4em; font-weight: 900; color: #00E676; text-align: center; display: inline-block; min-width: 70px; } [cite: 126]
    .stats-mini { background: #0D141B; border-radius: 10px; padding: 10px; margin-top: 15px; margin-bottom: 15px; border: 1px solid #1E2A38; font-size: 0.9em; text-align: center; font-weight: 600; color: #E1E8ED; } [cite: 127, 128]
    .flag-mini { width: 18px; border-radius: 2px; margin-right: 5px; vertical-align: middle; } [cite: 129]
    
    .bote-box { background: linear-gradient(135deg, #1E2A38, #111A24); border: 2px dashed #00E676; padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 25px; } [cite: 130]
    .bote-monto { font-size: 2.2em; font-weight: 900; color: #00E676; margin-top: 5px; } [cite: 131]
    
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button { background: linear-gradient(45deg, #00E676, #00C853) !important; color: #060D13 !important; border-radius: 30px !important; font-weight: 800 !important; border: none !important; padding: 12px !important; text-transform: uppercase !important; letter-spacing: 1.5px !important; } [cite: 132, 133]
    .podium-gold { background: linear-gradient(135deg, #FFB300, #FF8F00); color: #FFF; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 15px; } [cite: 134]
    .podium-silver { background: linear-gradient(135deg, #B0BEC5, #78909C); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; } [cite: 135]
    .podium-bronze { background: linear-gradient(135deg, #A1887F, #6D4C41); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; } [cite: 136]
    [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
    footer, .viewerBadge_container__1QSob { display: none !important; } [cite: 137]
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
            with st.form("login_form", border=False): [cite: 138]
                apodo_login = st.text_input("👤 Usuario", placeholder="Ej: El Mosca").strip()
                pass_login = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
                submit_log = st.form_submit_button("ENTRAR")
            
            if submit_log:
                if apodo_login and pass_login: [cite: 139]
                    res = supabase.table("Usuarios").select("*").eq("Apodo", apodo_login).execute()
                    if res.data:
                        if str(res.data[0]["Password"]) == str(pass_login):
                            st.session_state.update({ [cite: 140]
                                "Id_usuario": res.data[0]["Id"], 
                                "Apodo": res.data[0]["Apodo"], 
                                "Estado": res.data[0].get("Estado", "Pendiente") [cite: 141]
                            })
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta")
                    else: st.error("❌ No existe ningún usuario con ese apodo") [cite: 142]
                else: st.warning("⚠️ Rellena todos los campos para entrar.")
                
        with tab_reg:
            with st.form("register_form", border=False):
                reg_nombre = st.text_input("Nombre", placeholder="Tu nombre") [cite: 143]
                reg_apellidos = st.text_input("Apellidos", placeholder="Tus apellidos")
                reg_apodo = st.text_input("Usuario", placeholder="Ej: El Mosca").strip()
                reg_pass = st.text_input("Contraseña", type="password", placeholder="Mín. 8 caracteres (letras y números)") [cite: 144]
                submit_reg = st.form_submit_button("COMPLETAR REGISTRO")
                
            if submit_reg:
                if reg_nombre and reg_apellidos and reg_apodo and reg_pass:
                    is_valid_pass, error_msg = check_password_strength(reg_pass)
                    if not is_valid_pass: [cite: 145]
                        st.error(f"❌ Contraseña insegura: {error_msg}")
                    else:
                        check_apodo = supabase.table("Usuarios").select("Id").eq("Apodo", reg_apodo).execute()
                        if check_apodo.data: [cite: 146]
                            st.error("❌ Ese nombre de usuario ya está registrado por otro jugador. Elige otro.")
                        else:
                            try: [cite: 147]
                                nuevo = supabase.table("Usuarios").insert({
                                    "Nombre": reg_apodo,
                                    "Nombre_Real": reg_nombre, [cite: 148]
                                    "Apellidos": reg_apellidos,
                                    "Apodo": reg_apodo,
                                    "Password": reg_pass, [cite: 149]
                                    "Puntos": 0,
                                    "Estado": "Pendiente" [cite: 150]
                                }).execute()
                                
                                st.session_state.update({ [cite: 151]
                                    "Id_usuario": nuevo.data[0]["Id"], 
                                    "Apodo": reg_apodo, 
                                    "Estado": "Pendiente" [cite: 152]
                                })
                                st.success("🎉 ¡Cuenta creada con éxito!")
                                st.rerun() [cite: 153]
                            except Exception as e:
                                st.error("❌ Error al guardar en la base de datos. Revisa la configuración de Supabase.") [cite: 154]
                else: st.warning("⚠️ Por favor, rellena los 4 campos del formulario para registrarte.")
    st.stop()

# --- 4. VERIFICACIÓN PAGO ---
if st.session_state.get("Estado") == "Pendiente":
    st.title("🔒 Cuenta Inactiva")
    st.warning(f"Hola {st.session_state['Apodo']}, activa tu cuenta para jugar.")
    st.info("Entrega 30€ en efectivo a cualquiera de los administradores (Kurlander, Chema o Álvaro).")
    if st.button("🔄 Comprobar Pago"):
        res = supabase.table("Usuarios").select("Estado").eq("Id", st.session_state["Id_usuario"]).execute()
        st.session_state["Estado"] = res.data[0]["Estado"]; st.rerun() [cite: 155]
    st.stop()

# --- 5. CARGA DE DATOS Y ORDENAMIENTO ---
ADMIN_NOMBRE = "AGS"
es_admin = st.session_state["Apodo"] == ADMIN_NOMBRE

partidos_db = supabase.table("Partidos").select("*").execute().data

def sort_matches(p):
    try: 
        dt = datetime.fromisoformat(p['Fecha_hora']).timestamp()
    except: 
        dt = 0
    return dt

partidos_raw = sorted(partidos_db, key=sort_matches)

pendientes = [p for p in partidos_raw if not p.get('Resultado_real')]
finalizados = [p for p in partidos_raw if p.get('Resultado_real')]
partidos_raw = pendientes + finalizados

for p in partidos_raw: 
    p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"] [cite: 156]

todos_usuarios_raw = supabase.table("Usuarios").select("Id, Apodo, Puntos, Estado").order("Puntos", desc=True).execute().data
dict_nombres = {u['Id']: u['Apodo'] if u['Apodo'] else f"User_{u['Id']}" for u in todos_usuarios_raw}

usuarios_ranking = [u for u in todos_usuarios_raw if u["Apodo"] != ADMIN_NOMBRE]
usuarios_pagados = [u for u in usuarios_ranking if u.get("Estado") == "Pagado"]
bote_total = len(usuarios_pagados) * 30

hora_actual_espana = datetime.now(timezone.utc) + timedelta(hours=2) 
todas_porras = supabase.table("Porras").select("*").execute().data

# --- PROCESAMIENTO GLOBAL DINÁMICO DE PUNTOS ---
# Calculamos las clasificaciones en una única pasada para que la barra lateral y el ranking vayan a la par
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), key=lambda x: orden_fases.index(x) if x in orden_fases else 99) if 'orden_fases' in locals() else ["Fase de Grupos"]

pts_data = {u['Id']: {"Id": u['Id'], "Jugador (Apodo)": u['Apodo'] if u['Apodo'] else "Sin Apodo", "Global": 0, "Racha_Pts": 0} for u in todos_usuarios_raw}
# Inicializar todas las fases para cada usuario
for p in partidos_raw:
    f_vis = p["Fase_Visual"]
    for uid in pts_data:
        if f_vis not in pts_data[uid]:
            pts_data[uid][f_vis] = 0

partidos_con_resultado = [p for p in partidos_db if p.get('Resultado_real') and '-' in str(p['Resultado_real'])]
try:
    partidos_con_resultado = sorted(partidos_con_resultado, key=lambda x: datetime.fromisoformat(x['Fecha_hora']).timestamp(), reverse=True) [cite: 220]
except:
    pass
ultimos_3_partidos_ids = [p['Id'] for p in partidos_con_resultado[:3]]

for p in partidos_db:
    res_real = p.get('Resultado_real')
    c_real = p.get('Corners_real')
    t_real = p.get('Tarjetas_real')
    f_real = p.get('Faltas_real') [cite: 222]
    
    if res_real and '-' in str(res_real):
        out_real = get_outcome(res_real)
        fase_val = p["Fase_Visual"]
        
        for v in todas_porras: [cite: 223]
            if v['Id_partido'] == p['Id'] and v['Id_usuario'] in pts_data:
                pts_partido = 0
                pred = str(v['Prediccion'])
                if '-' in pred: [cite: 224]
                    if pred == res_real: pts_partido += 20
                    elif get_outcome(pred) == out_real: pts_partido += 5
                
                if c_real is not None and v.get('Pred_Corners'): [cite: 225]
                    if (c_real > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (c_real < LINEA_CORNERS and v['Pred_Corners'] == 'Menos'): pts_partido += 2
                if t_real is not None and v.get('Pred_Tarjetas'): [cite: 226]
                    if (t_real > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (t_real < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos'): pts_partido += 2
                if f_real is not None and v.get('Pred_Faltas'): [cite: 227]
                    if (f_real > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (f_real < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos'): pts_partido += 2
                    
                if pts_partido > 0:
                    pts_data[v['Id_usuario']]["Global"] += pts_partido [cite: 228]
                    pts_data[v['Id_usuario']][fase_val] += pts_partido
                    
                    if p['Id'] in ultimos_3_partidos_ids:
                        pts_data[v['Id_usuario']]["Racha_Pts"] += pts_partido [cite: 229]

with st.sidebar:
    st.sidebar.markdown(f"<h2 style='text-align: center;'><span class='text-gradient'>👤 {st.session_state['Apodo']}</span></h2>", unsafe_allow_html=True) [cite: 156, 157]
    # MODIFICACIÓN CLAVE: Ahora lee los puntos reales dinámicos calculados del historial en vez de la columna fija
    mi_puntos_dinamicos = pts_data.get(st.session_state['Id_usuario'], {}).get("Global", 0)
    st.metric("Tus Puntos Totales", mi_puntos_dinamicos)
    if st.button("🚪 Cerrar Sesión"): st.session_state.clear(); st.rerun() [cite: 158]

# --- LÓGICA DE PANTALLA DE DETALLE DE PARTIDO ---
if "view_partido" not in st.session_state: st.session_state["view_partido"] = None

if st.session_state["view_partido"]:
    p_id = st.session_state["view_partido"]
    p = next((x for x in partidos_raw if x['Id'] == p_id), None)
    
    if st.button("⬅️ VOLVER AL CALENDARIO"):
        st.session_state["view_partido"] = None
        st.rerun()
        
    if p:
        with st.container(border=True):
            fecha_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc) [cite: 159]
            st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha_p.strftime('%d %b %H:%M')}h</div>", unsafe_allow_html=True)
            iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
            res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
            
            st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right; padding-right: 10px;'><span class='team-name'>{p['Equipo_local']}</span><img src='https://flagcdn.com/32x24/{iso_l}.png' style='margin-left: 8px; border-radius: 4px;'></div><div style='flex-shrink: 0;'><span class='score-box'>{res_txt}</span></div><div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left; padding-left: 10px;'><img src='https://flagcdn.com/32x24/{iso_v}.png' style='margin-right: 8px; border-radius: 4px;'><span class='team-name'>{p['Equipo_visitante']}</span></div></div>", unsafe_allow_html=True) [cite: 160, 161, 162]
            st.markdown("<hr style='margin: 15px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True)
            
            if p.get("Corners_real") is not None:
                st.markdown(f"<p style='text-align:center; color:#8899A6;'>Estadísticas Finales: 🚩 {p['Corners_real']} | 🟨 {p['Tarjetas_real']} | 🩼 {p['Faltas_real']}</p>", unsafe_allow_html=True)
            
            st.subheader("📊 Pronósticos de la comunidad") [cite: 163]
            votos_p = [v for v in todas_porras if v['Id_partido'] == p['Id'] and dict_nombres.get(v['Id_usuario']) != ADMIN_NOMBRE]
            
            if votos_p: [cite: 164]
                data_list = []
                for v in votos_p:
                    row = {"Jugador (Apodo)": dict_nombres.get(v['Id_usuario'], "Anon")}
                    
                    if p.get('Resultado_real'): [cite: 165]
                        r_real = p['Resultado_real']
                        o_real = get_outcome(r_real)
                        o_voto = get_outcome(v['Prediccion'])
                        
                        if v['Prediccion'] == r_real:
                            row["Resultado"] = f"{v['Prediccion']} 🎯 (+20)"
                        elif o_voto == o_real and o_real is not None:
                            row["Resultado"] = f"{v['Prediccion']} ✅ (+5)" [cite: 167]
                        else:
                            row["Resultado"] = f"{v['Prediccion']} ❌"
                        
                        if p.get('Corners_real') is not None and v.get('Pred_Corners'): [cite: 168]
                            hit = (p['Corners_real'] > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (p['Corners_real'] < LINEA_CORNERS and v['Pred_Corners'] == 'Menos')
                            row["Córners"] = f"{v['Pred_Corners']} " + ("🟢 (+2)" if hit else "🔴") [cite: 169]
                        else: row["Córners"] = v.get('Pred_Corners', '-')
                        
                        if p.get('Tarjetas_real') is not None and v.get('Pred_Tarjetas'): [cite: 170]
                            hit = (p['Tarjetas_real'] > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (p['Tarjetas_real'] < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos')
                            row["Tarjetas"] = f"{v['Pred_Tarjetas']} " + ("🟢 (+2)" if hit else "🔴")
                        else: row["Tarjetas"] = v.get('Pred_Tarjetas', '-') [cite: 171]
                            
                        if p.get('Faltas_real') is not None and v.get('Pred_Faltas'):
                            hit = (p['Faltas_real'] > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (p['Faltas_real'] < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos') [cite: 172]
                            row["Faltas"] = f"{v['Pred_Faltas']} " + ("🟢 (+2)" if hit else "🔴")
                        else: row["Faltas"] = v.get('Pred_Faltas', '-')
                    else: [cite: 173]
                        row["Resultado"] = v['Prediccion']
                        row["Córners"] = v.get('Pred_Corners', '-')
                        row["Tarjetas"] = v.get('Pred_Tarjetas', '-')
                        row["Faltas"] = v.get('Pred_Faltas', '-') [cite: 174]
                    data_list.append(row)
                    
                df_votos = pd.DataFrame(data_list)
                st.dataframe(df_votos, use_container_width=True, hide_index=True)
            else:
                st.info("Nadie votó en este partido.") [cite: 175]
    st.stop()

# --- 6. TABS (VISTA PRINCIPAL) ---
orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "3º y 4º Puesto", "Final"]
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), key=lambda x: orden_fases.index(x) if x in orden_fases else 99)

tabs_labels = ["📅 Partidos", "🏆 Ranking", "📜 Reglas"]
if es_admin: tabs_labels.append("🛠️ Admin")
tabs = st.tabs(tabs_labels)

# ================================
# TAB 1: PARTIDOS
# ================================
with tabs[0]:
    if not partidos_raw: st.info("Cargando calendario...")
    else:
        sub_tabs = st.tabs(fases_existentes)
        votos_usuario = {v['Id_partido']: v for v in todas_porras if v['Id_usuario'] == st.session_state["Id_usuario"]} [cite: 176]
        
        for i, fase_tab in enumerate(fases_existentes):
            with sub_tabs[i]:
                for p in [x for x in partidos_raw if x["Fase_Visual"] == fase_tab]:
                    with st.container(border=True):
                        fecha_p = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc) [cite: 177]
                        st.markdown(f"<div class='match-header'>{p['Fase']} | {fecha_p.strftime('%d %b %H:%M')}h</div>", unsafe_allow_html=True) [cite: 178]
                        iso_l, iso_v = BANDERAS.get(p['Equipo_local'], "un"), BANDERAS.get(p['Equipo_visitante'], "un")
                        res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
                        
                        st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center;'><div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right; padding-right: 10px;'><span class='team-name'>{p['Equipo_local']}</span><img src='https://flagcdn.com/32x24/{iso_l}.png' style='margin-left: 8px; border-radius: 4px;'></div><div style='flex-shrink: 0;'><span class='score-box'>{res_txt}</span></div><div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left; padding-left: 10px;'><img src='https://flagcdn.com/32x24/{iso_v}.png' style='margin-right: 8px; border-radius: 4px;'><span class='team-name'>{p['Equipo_visitante']}</span></div></div>", unsafe_allow_html=True) [cite: 179]
                        st.markdown("<hr style='margin: 15px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True) [cite: 180]
                        
                        ha_votado = p['Id'] in votos_usuario

                        if p.get('Resultado_real'):
                            res_real = p['Resultado_real'] [cite: 181]
                            out_real = get_outcome(res_real)
                            if ha_votado:
                                v_u = votos_usuario[p['Id']] [cite: 182]
                                mi_voto = v_u['Prediccion']
                                out_voto = get_outcome(mi_voto)
                                
                                pts_totales_partido = 0
                                msjs_extras = []
                                
                                if mi_voto == res_real:
                                    pts_totales_partido += 20
                                    msjs_extras.append("🎯 Pleno Marcador Exacto (+20)") [cite: 185]
                                elif out_voto == out_real and out_real is not None:
                                    pts_totales_partido += 5
                                    msjs_extras.append("✅ Ganador/Empate (+5)") [cite: 186]
                                else:
                                    msjs_extras.append("❌ Marcador") [cite: 187]
                                    
                                if p.get('Corners_real') is not None and v_u.get('Pred_Corners'):
                                    if (p['Corners_real'] > LINEA_CORNERS and v_u['Pred_Corners'] == 'Más') or (p['Corners_real'] < LINEA_CORNERS and v_u['Pred_Corners'] == 'Menos'): [cite: 188]
                                        pts_totales_partido += 2
                                        msjs_extras.append("🚩 Córners (+2)") [cite: 189]
                                    else: msjs_extras.append("❌ Córners")
                                    
                                if p.get('Tarjetas_real') is not None and v_u.get('Pred_Tarjetas'): [cite: 190]
                                    if (p['Tarjetas_real'] > LINEA_TARJETAS and v_u['Pred_Tarjetas'] == 'Más') or (p['Tarjetas_real'] < LINEA_TARJETAS and v_u['Pred_Tarjetas'] == 'Menos'):
                                        pts_totales_partido += 2 [cite: 191]
                                        msjs_extras.append("🟨 Tarjetas (+2)")
                                    else: msjs_extras.append("❌ Tarjetas")
                                    
                                if p.get('Faltas_real') is not None and v_u.get('Pred_Faltas'): [cite: 192]
                                    if (p['Faltas_real'] > LINEA_FALTAS and v_u['Pred_Faltas'] == 'Más') or (p['Faltas_real'] < LINEA_FALTAS and v_u['Pred_Faltas'] == 'Menos'): [cite: 193]
                                        pts_totales_partido += 2
                                        msjs_extras.append("🩼 Faltas (+2)") [cite: 194]
                                    else: msjs_extras.append("❌ Faltas")
                                
                                string_resumen = " | ".join(msjs_extras) [cite: 195, 196]
                                if pts_totales_partido > 0:
                                    st.success(f"🏆 **¡Sumaste +{pts_totales_partido} pts!** ({string_resumen})")
                                else:
                                    st.error(f"❌ **0 puntos obtenidos:** ({string_resumen})") [cite: 197]
                            else: st.info(f"Finalizado: {res_real}")
                        
                        elif ha_votado:
                            v = votos_usuario[p['Id']]
                            st.info(f"✅ Tu pronóstico: **{v['Prediccion']}** | 🚩 {v.get('Pred_Corners','-')} | 🟨 {v.get('Pred_Tarjetas','-')} | 🩼 {v.get('Pred_Faltas','-')}")
                        
                        elif fecha_p > hora_actual_espana: [cite: 199]
                            st.markdown("<p style='text-align:center; font-size: 0.9em; color:#8899A6; margin-bottom:5px; font-weight:bold;'>1. Marcador Exacto</p>", unsafe_allow_html=True)
                            c1, c2, c3 = st.columns([1, 1.5, 1]) [cite: 200]
                            with c2:
                                sub_c1, sub_c2, sub_c3 = st.columns([2, 1, 2])
                                with sub_c1: g_loc = st.number_input("L", min_value=0, max_value=20, step=1, key=f"gl_{p['Id']}", label_visibility="collapsed") [cite: 201]
                                with sub_c2: st.markdown("<div style='text-align:center; padding-top:5px; font-weight:bold;'>-</div>", unsafe_allow_html=True) [cite: 202]
                                with sub_c3: g_vis = st.number_input("V", min_value=0, max_value=20, step=1, key=f"gv_{p['Id']}", label_visibility="collapsed")
                            
                            st.markdown(f"<p style='text-align:center; font-size: 0.9em; color:#8899A6; margin-top:15px; margin-bottom:5px; font-weight:bold;'>2. Mercados Extra (+2 pts c/u)</p>", unsafe_allow_html=True) [cite: 203]
                            ex1, ex2, ex3 = st.columns(3)
                            with ex1: pred_c = st.selectbox(f"🚩 Córners (+{LINEA_CORNERS})", ["-", "Más", "Menos"], key=f"c_{p['Id']}")
                            with ex2: pred_t = st.selectbox(f"🟨 Tarjetas (+{LINEA_TARJETAS})", ["-", "Más", "Menos"], key=f"t_{p['Id']}") [cite: 204]
                            with ex3: pred_f = st.selectbox(f"🩼 Faltas (+{LINEA_FALTAS})", ["-", "Más", "Menos"], key=f"f_{p['Id']}")

                            if st.button("Confirmar Pronóstico", key=f"b_{p['Id']}", use_container_width=True):
                                val_bd = f"{g_loc}-{g_vis}" [cite: 205]
                                c_bd = pred_c if pred_c != "-" else None
                                t_bd = pred_t if pred_t != "-" else None [cite: 206]
                                f_bd = pred_f if pred_f != "-" else None
                                
                                supabase.table("Porras").upsert({ [cite: 207]
                                    "Id_usuario": st.session_state["Id_usuario"], 
                                    "Id_partido": p["Id"], 
                                    "Prediccion": val_bd, [cite: 208]
                                    "Pred_Corners": c_bd,
                                    "Pred_Tarjetas": t_bd,
                                    "Pred_Faltas": f_bd [cite: 209]
                                }).execute()
                                st.rerun()
                        else: st.warning("🔒 Cerrado.") [cite: 210]

                        if ha_votado or p.get('Resultado_real'):
                            votos_p = [v for v in todas_porras if v['Id_partido'] == p['Id'] and get_outcome(v['Prediccion']) and dict_nombres.get(v['Id_usuario']) != ADMIN_NOMBRE] [cite: 211]
                            if votos_p:
                                n_total = len(votos_p) [cite: 212]
                                p_l = sum(1 for v in votos_p if get_outcome(v['Prediccion']) == '1') / n_total
                                p_x = sum(1 for v in votos_p if get_outcome(v['Prediccion']) == 'X') / n_total
                                p_v = sum(1 for v in votos_p if get_outcome(v['Prediccion']) == '2') / n_total [cite: 213]
                                
                                st.markdown(f""" [cite: 214]
                                <div class='stats-mini'>
                                    <span style='color:#8899A6; font-size:0.85em; font-weight:400; margin-right:10px;'>Tendencia Marcador ({n_total} votos):</span><br> [cite: 215]
                                    <img src='https://flagcdn.com/16x12/{iso_l}.png' class='flag-mini'> {p_l:.0%} &nbsp;&nbsp;|&nbsp;&nbsp; 
                                    🤝 {p_x:.0%} &nbsp;&nbsp;|&nbsp;&nbsp; [cite: 216]
                                    <img src='https://flagcdn.com/16x12/{iso_v}.png' class='flag-mini'> {p_v:.0%}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if fecha_p <= hora_actual_espana:
                                    if st.button("🔍 Ver detalles y mercados extra", key=f"btn_det_{p['Id']}", use_container_width=True):
                                        st.session_state["view_partido"] = p['Id'] [cite: 218]
                                        st.rerun()
                                else:
                                    st.markdown("<p style='font-size:0.7em; color:#8899A6; text-align:center; font-style:italic;'>Los pronósticos completos se revelan al inicio.</p>", unsafe_allow_html=True) [cite: 219]

# ================================
# TAB 2: RANKING DINÁMICO POR FASES Y RACHAS
# ================================
with tabs[1]:
    if not usuarios_ranking: 
        st.info("Sin usuarios.")
    else:
        # Se preparan las pestañas de rankings usando el filtro exclusivo sin Admin que ya se calculó en el bloque 5
        ranking_tabs_names = ["Global"] + fases_existentes [cite: 230]
        rk_tabs = st.tabs(ranking_tabs_names)
        
        # Filtrar el pts_data general para excluir al admin
        ranking_usuarios_filtrado = {uid: datos for uid, datos in pts_data.items() if datos["Jugador (Apodo)"] != ADMIN_NOMBRE}
        max_racha = max([u["Racha_Pts"] for u in ranking_usuarios_filtrado.values()]) if ranking_usuarios_filtrado else 0 [cite: 229]
        
        for i, rk_name in enumerate(ranking_tabs_names):
            with rk_tabs[i]:
                ranking_ordenado = sorted(ranking_usuarios_filtrado.values(), key=lambda x: x[rk_name], reverse=True)
                ranking_filtrado = [u for u in ranking_ordenado if u[rk_name] > 0] [cite: 231]
                
                if ranking_filtrado:
                    st.markdown(f"<h3 style='text-align: center; margin-bottom: 30px;'><span class='text-gradient'>🏆 LÍDERES: {rk_name.upper()}</span></h3>", unsafe_allow_html=True) [cite: 232]
                    c1, c2, c3 = st.columns(3)
                    with c1: st.markdown(f"<div class='podium-gold'>🥇<br>{ranking_filtrado[0]['Jugador (Apodo)']}<br>{ranking_filtrado[0][rk_name]} pts</div>", unsafe_allow_html=True)
                    if len(ranking_filtrado) > 1:
                        with c2: st.markdown(f"<div class='podium-silver'>🥈<br>{ranking_filtrado[1]['Jugador (Apodo)']}<br>{ranking_filtrado[1][rk_name]} pts</div>", unsafe_allow_html=True) [cite: 233]
                    if len(ranking_filtrado) > 2:
                        with c3: st.markdown(f"<div class='podium-bronze'>🥉<br>{ranking_filtrado[2]['Jugador (Apodo)']}<br>{ranking_filtrado[2][rk_name]} pts</div>", unsafe_allow_html=True)
                    st.divider()
                    
                    final_rows = []
                    for u in ranking_ordenado:
                        nombre_visual = u['Jugador (Apodo)']
                        if u['Racha_Pts'] == max_racha and max_racha > 0: [cite: 235]
                            nombre_visual = f"🔥 {nombre_visual} (En Racha)"
                        
                        final_rows.append({
                            "Jugador (Apodo)": nombre_visual, [cite: 236]
                            "Puntos": u[rk_name],
                            "Racha (Últ. 3 partidos)": f"{u['Racha_Pts']} pts" [cite: 237]
                        })
                    
                    st.dataframe(pd.DataFrame(final_rows), use_container_width=True, hide_index=True)
                else:
                    st.info(f"Aún no hay puntos repartidos en: {rk_name}") [cite: 238]

# ================================
# TAB 3: REGLAS
# ================================
with tabs[2]:
    st.markdown(f"""
    <div class='bote-box'>
        <div style='text-transform: uppercase; letter-spacing: 1.5px; font-size: 0.9em; color: #8899A6; font-weight: 800;'>💰 BOTE ACUMULADO ACTUAL 💰</div>
        <div class='bote-monto'>{bote_total} €</div>
        <div style='font-size: 0.8em; color: #6D7E8C; margin-top: 5px;'>Calculado en base a {len(usuarios_pagados)} jugadores validados.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    ### 📜 Reglas de la Porra Mundial 2026 [cite: 239]
    
    1. **Ganador o Empate (5 Puntos):** Recibirás **5 puntos** si logras acertar qué equipo ganará el encuentro o si el partido terminará en empate. [cite: 239]
    *(Por ejemplo, si apuestas un 2-0 y el partido queda 1-0, te llevas los 5 puntos).* [cite: 240]
       
    2. **Resultado Exacto (20 Puntos):** Recibirás **20 puntos en total** (15 del marcador exacto + 5 del ganador acumulados) si consigues acertar la cantidad exacta de goles que marcará cada equipo (ejemplo: 2-1, 0-0, 3-0).
    
    3. **Mercados Extra (+2 Puntos c/u):** Cada acierto en Más/Menos sumará 2 puntos extra (máximo 6 extra por partido). [cite: 241]
    Las líneas oficiales son: [cite: 242]
       * 🚩 Córners: **{LINEA_CORNERS}**
       * 🟨 Tarjetas: **{LINEA_TARJETAS}**
       * 🛑 Faltas: **{LINEA_FALTAS}**
       
    4. **Indicador de Racha (🔥):** El jugador o jugadores que hayan sumado la mayor cantidad de puntos en los **últimos 3 partidos cerrados** recibirán el distintivo especial de fuego en la tabla de clasificaciones.
    """) [cite: 243]

# ================================
# TAB 4: ADMIN
# ================================
if es_admin:
    with tabs[3]:
        st.subheader("🛠️ Panel Admin")
        p_admin = [p for p in partidos_raw if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc) < hora_actual_espana]
        if p_admin:
            p_sel = st.selectbox("Partido finalizado:", p_admin, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            
            st.write("Marcador Final:")
            c_admin_l, c_admin_v = st.columns(2) [cite: 244]
            gan_l = c_admin_l.number_input("Goles Local", 0, 20, 0, key="admin_l")
            gan_v = c_admin_v.number_input("Goles Visitante", 0, 20, 0, key="admin_v")
            gan_str = f"{gan_l}-{gan_v}"
            
            st.write("Estadísticas Reales:")
            c_ac, c_at, c_af = st.columns(3) [cite: 245]
            real_c = c_ac.number_input("🚩 Córners", 0, 50, 0)
            real_t = c_at.number_input("🟨 Tarjetas", 0, 30, 0)
            real_f = c_af.number_input("🛑 Faltas", 0, 60, 0)
            
            if st.button("GUARDAR RESULTADO Y REPARTIR PUNTOS", type="primary"):
                supabase.table("Partidos").update({ [cite: 246]
                    "Resultado_real": gan_str, "Corners_real": real_c, "Tarjetas_real": real_t, "Faltas_real": real_f
                }).eq("Id", p_sel['Id']).execute()
                
                out_real = get_outcome(gan_str)
                votos_partido = [v for v in todas_porras if v['Id_partido'] == p_sel['Id']] [cite: 247]
                
                for v in votos_partido:
                    pts_sum = 0
                    pred = str(v['Prediccion'])
                    if '-' in pred: [cite: 248]
                        if pred == gan_str: pts_sum += 20
                        elif get_outcome(pred) == out_real: pts_sum += 5
                    
                    if v.get('Pred_Corners') and real_c is not None: [cite: 249]
                        if (real_c > LINEA_CORNERS and v['Pred_Corners'] == 'Más') or (real_c < LINEA_CORNERS and v['Pred_Corners'] == 'Menos'): pts_sum += 2
                    if v.get('Pred_Tarjetas') and real_t is not None:
                        if (real_t > LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Más') or (real_t < LINEA_TARJETAS and v['Pred_Tarjetas'] == 'Menos'): pts_sum += 2 [cite: 250]
                    if v.get('Pred_Faltas') and real_f is not None:
                        if (real_f > LINEA_FALTAS and v['Pred_Faltas'] == 'Más') or (real_f < LINEA_FALTAS and v['Pred_Faltas'] == 'Menos'): pts_sum += 2
                    
                    if pts_sum > 0:
                        pts_act = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]['Puntos']
                        supabase.table("Usuarios").update({"Puntos": pts_act + pts_sum}).eq("Id", v['Id_usuario']).execute()
                st.rerun() [cite: 252]
        st.divider()
        u_pend = supabase.table("Usuarios").select("*").eq("Estado", "Pendiente").execute().data
        if u_pend:
            u_sel = st.selectbox("Validar pago de:", u_pend, format_func=lambda x: f"{x['Apodo']} ({x.get('Nombre_Real', '')})")
            if st.button("ACTIVAR USUARIO"):
                supabase.table("Usuarios").update({"Estado": "Pagado"}).eq("Id", u_sel['Id']).execute(); st.rerun() [cite: 253]
