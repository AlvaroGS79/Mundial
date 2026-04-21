import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone
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
st.set_page_config(page_title="Porra Mundial 2026", layout="centered", page_icon="🏆")

st.markdown("""
    <style>
    .stApp { background-color: #0b101e; color: #ffffff; }
    .match-card { background-color: #1a233a; padding: 20px; border-radius: 15px; border: 1px solid #2d3748; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .match-header { font-size: 0.75em; color: #a0aec0; text-align: center; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .team-name { font-size: 1.1em; font-weight: bold; }
    
    div.stButton > button:first-child { background-color: #00e676 !important; color: #0b101e !important; border-radius: 25px; font-weight: bold; width: 100%; border: none; padding: 10px; transition: 0.3s; }
    div.stButton > button:first-child:hover { background-color: #00c853 !important; transform: scale(1.02); }
    
    [data-testid="stRadio"] > div { justify-content: center !important; }
    
    .podium-gold { background: linear-gradient(135deg, #FFD700, #FDB931); color: #000; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .podium-silver { background: linear-gradient(135deg, #C0C0C0, #8E8E8E); color: #000; padding: 10px; border-radius: 15px; text-align: center; }
    .podium-bronze { background: linear-gradient(135deg, #CD7F32, #8B4513); color: #fff; padding: 10px; border-radius: 15px; text-align: center; }
    .login-container { background-color: #161e31; padding: 40px; border-radius: 20px; text-align: center; border: 1px solid #2d3748; }
    [data-testid="stDataFrameToolbar"], #MainMenu, footer { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE ACCESO (LOGIN + ESTADO) ---
if "Id_usuario" not in st.session_state:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 4em; margin-bottom: 0;'>🏆</h1>", unsafe_allow_html=True)
        st.markdown("<h2>Porra Mundial 2026</h2>", unsafe_allow_html=True)
        
        nombre_u = st.text_input("Usuario", placeholder="Tu nombre", label_visibility="collapsed")
        pass_u = st.text_input("Contraseña", type="password", placeholder="Contraseña", label_visibility="collapsed")
        st.write("")
        
        if st.button("ENTRAR / REGISTRARSE"):
            if nombre_u.strip() and pass_u.strip():
                res = supabase.table("Usuarios").select("*").eq("Nombre", nombre_u).execute()
                if res.data:
                    if str(res.data[0]["Password"]) == str(pass_u):
                        st.session_state["Id_usuario"] = res.data[0]["Id"]
                        st.session_state["Nombre"] = res.data[0]["Nombre"]
                        st.session_state["Estado"] = res.data[0].get("Estado", "Pendiente")
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta")
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
    st.info("Para participar en la porra, envía tu aportación de 20€ por Bizum al 6XX XXX XXX indicando tu nombre. Una vez enviado, el administrador te dará acceso.")
    if st.button("🔄 Ya he pagado, comprobar acceso"):
        res = supabase.table("Usuarios").select("Estado").eq("Id", st.session_state["Id_usuario"]).execute()
        st.session_state["Estado"] = res.data[0]["Estado"]
        st.rerun()
    st.stop()

# --- 5. CARGA DE DATOS Y FILTROS ---
ADMIN_NOMBRE = "AGS"
es_admin = st.session_state["Nombre"] == ADMIN_NOMBRE

partidos_raw = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data
# Traemos a todos los usuarios de la base de datos
todos_usuarios_raw = supabase.table("Usuarios").select("Id, Nombre, Puntos").order("Puntos", desc=True).execute().data

# 🔥 Filtramos al administrador para que no aparezca en ningún ranking 🔥
todos_usuarios = [u for u in todos_usuarios_raw if u["Nombre"] != ADMIN_NOMBRE]

for p in partidos_raw:
    p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]

orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "Final"]
fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), 
                          key=lambda x: orden_fases.index(x) if x in orden_fases else 99)

with st.sidebar:
    st.markdown(f"<h2 style='text-align: center;'>👤 {st.session_state['Nombre']}</h2>", unsafe_allow_html=True)
    
    # Usamos la lista "raw" (sin filtrar) solo para buscar tus propios puntos en el menú lateral
    res_yo = [u for u in todos_usuarios_raw if u['Id'] == st.session_state['Id_usuario']]
    puntos_yo = res_yo[0]['Puntos'] if res_yo else 0
    
    if es_admin:
        pos_display = "Admin"
    else:
        num_pos = next((i + 1 for i, u in enumerate(todos_usuarios) if u['Id'] == st.session_state['Id_usuario']), "-")
        pos_display = f"{num_pos}º"
    
    c1, c2 = st.columns(2)
    c1.metric("Tus Puntos", puntos_yo)
    c2.metric("Posición", pos_display)
    st.divider()
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

# --- 6. TABS PRINCIPALES ---
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if es_admin else "📜 Reglas"])

with tabs[0]:
    if not partidos_raw:
        st.info("No hay partidos cargados en la base de datos.")
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
                        st.markdown(f"<div style='text-align: right;'><span class='team-name'>{p['Equipo_local']}</span> <img src='https://flagcdn.com/32x24/{iso_l}.png' style='border-radius:3px;'></div>", unsafe_allow_html=True)
                    with c2:
                        res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"
                        st.markdown(f"<div style='text-align: center; font-size:1.2em; font-weight: bold; background: #2d3748; border-radius: 5px; padding: 2px;'>{res_txt}</div>", unsafe_allow_html=True)
                    with c3:
                        iso_v = BANDERAS.get(p['Equipo_visitante'], "un")
                        st.markdown(f"<div style='text-align: left;'><img src='https://flagcdn.com/32x24/{iso_v}.png' style='border-radius:3px;'> <span class='team-name'>{p['Equipo_visitante']}</span></div>", unsafe_allow_html=True)
                    
                    st.markdown("<hr style='margin: 15px 0px 15px 0px; border: none; border-top: 1px solid #2d3748;'>", unsafe_allow_html=True)
                    
                    if p.get('Resultado_real'):
                        st.write("")
                        _, col_res, _ = st.columns([1, 4, 1])
                        with col_res:
                            if p['Id'] in votos:
                                if votos[p['Id']] == p['Resultado_real']: st.success(f"🎯 Acertaste el resultado: {votos[p['Id']]}")
                                else: st.error(f"❌ Fallaste. Tu apuesta: {votos[p['Id']]}")
                            else:
                                st.markdown("<div style='text-align: center; color: gray;'>No apostaste a este partido</div>", unsafe_allow_html=True)
                                
                    elif p['Id'] in votos:
                        st.write("")
                        _, col_res, _ = st.columns([1, 4, 1])
                        with col_res:
                            st.info(f"✅ Tu pronóstico guardado: **{votos[p['Id']]}**")
                            
                    elif fecha > datetime.now(timezone.utc):
                        col_r_izq, col_r_cen, col_r_der = st.columns([1, 6, 1])
                        with col_r_cen:
                            pred = st.radio("Voto:", [p['Equipo_local'], 'Empate', p['Equipo_visitante']], key=f"r_{p['Id']}", horizontal=True, label_visibility="collapsed")
                            valor_bd = 'X' if pred == 'Empate' else pred 
                            
                        st.write("") 
                        
                        col_b_izq, col_b_cen, col_b_der = st.columns([1, 2, 1])
                        with col_b_cen:
                            if st.button("Confirmar", key=f"b_{p['Id']}"):
                                supabase.table("Porras").upsert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": valor_bd}).execute()
                                st.rerun()
                    else: 
                        st.warning("🔒 Partido cerrado. Esperando resultado.")
                        
                    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    if not todos_usuarios:
        st.info("Aún no hay usuarios registrados participando.")
    else:
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>👑 Top 3 Mundial</h3>", unsafe_allow_html=True)
        col_oro, col_plata, col_bronce = st.columns(3)
        if len(todos_usuarios) > 0:
            with col_oro: st.markdown(f"<div class='podium-gold'><h1>🥇</h1><h2>{todos_usuarios[0]['Nombre']}</h2><h3>{todos_usuarios[0]['Puntos']} pts</h3></div>", unsafe_allow_html=True)
        if len(todos_usuarios) > 1:
            with col_plata: st.markdown(f"<div class='podium-silver'><h2>🥈</h2><h3>{todos_usuarios[1]['Nombre']}</h3><h4>{todos_usuarios[1]['Puntos']} pts</h4></div>", unsafe_allow_html=True)
        if len(todos_usuarios) > 2:
            with col_bronce: st.markdown(f"<div class='podium-bronze'><h2>🥉</h2><h3>{todos_usuarios[2]['Nombre']}</h3><h4>{todos_usuarios[2]['Puntos']} pts</h4></div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("#### Clasificación General")
        
        df = pd.DataFrame(todos_usuarios)
        def medalla(i): return "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        df['Pos'] = [medalla(i) for i in range(len(df))]
        df['Jugador'] = df['Pos'] + " " + df['Nombre']
        max_p = int(df['Puntos'].max()) if df['Puntos'].max() > 0 else 10
        
        def style_row(row):
            return ['background-color: #00e676; color: #0b101e; font-weight: bold;'] * len(row) if row['Nombre'] == st.session_state['Nombre'] else [''] * len(row)
        
        st.dataframe(df[['Jugador', 'Puntos', 'Nombre']].style.apply(style_row, axis=1), use_container_width=True, hide_index=True,
                     column_config={"Jugador": "Jugador", "Puntos": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max_p), "Nombre": None})

if es_admin:
    with tabs[2]:
        st.subheader("🛠️ Panel de Control")
        
        st.markdown("#### ⚽ Actualizar Resultados")
        p_pend = [p for p in partidos_raw if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']) < datetime.now(timezone.utc)]
        if p_pend:
            st.info(f"Hay {len(p_pend)} partidos finalizados sin resultado cargado.")
            p_sel = st.selectbox("Selecciona un partido:", p_pend, format_func=lambda x: f"{x['Equipo_local']} vs {x['Equipo_visitante']}")
            gan = st.selectbox("Resultado final (Ganador/Empate):", [p_sel['Equipo_local'], 'X', p_sel['Equipo_visitante']])
            if st.button("GUARDAR RESULTADO Y REPARTIR PUNTOS", type="primary"):
                supabase.table("Partidos").update({"Resultado_real": gan}).eq("Id", p_sel['Id']).execute()
                votos_p = supabase.table("Porras").select("*").eq("Id_partido", p_sel['Id']).execute().data
                for v in votos_p:
                    if v['Prediccion'] == gan:
                        u_pts = supabase.table("Usuarios").select("Puntos").eq("Id", v['Id_usuario']).execute().data[0]['Puntos']
                        supabase.table("Usuarios").update({"Puntos": u_pts + 1}).eq("Id", v['Id_usuario']).execute()
                st.success("¡Resultado actualizado y ranking recalculado!")
                st.rerun()
        else:
            st.success("No hay partidos pendientes de cerrar.")
        
        st.divider()
        
        st.markdown("#### 💰 Activar Usuarios (Pagos)")
        u_pend = supabase.table("Usuarios").select("*").eq("Estado", "Pendiente").execute().data
        if u_pend:
            u_sel = st.selectbox("Usuario que ha pagado la cuota:", u_pend, format_func=lambda x: x['Nombre'])
            if st.button("MARCAR COMO PAGADO"):
                supabase.table("Usuarios").update({"Estado": "Pagado"}).eq("Id", u_sel['Id']).execute()
                st.success(f"¡Usuario {u_sel['Nombre']} activado correctamente!")
                st.rerun()
        else: 
            st.write("No hay pagos pendientes por revisar.")
else:
    with tabs[2]:
        st.markdown("""
        ### 📜 Reglas de la Porra
        * **Puntuación:** Recibes **1 punto** por cada resultado acertado (Ganador Local, Empate o Ganador Visitante).
        * **Límite de tiempo:** Las apuestas se bloquean automáticamente en la fecha y hora de inicio de cada partido.
        * **Fases Eliminatorias:** Cuando no se conozcan los cruces de Octavos, Cuartos, etc., aparecerán textos como "Ganador Grupo A". Los equipos reales se irán actualizando a medida que avance el torneo.
        """)
