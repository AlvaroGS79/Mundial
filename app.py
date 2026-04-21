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



# --- 2. CONFIGURACIÓN Y ESTILOS CSS PRO ---

st.set_page_config(page_title="Porra Mundial 2026", layout="centered", page_icon="⚽")



st.markdown("""

    <style>

    /* Fondo principal modo oscuro */

    .stApp { background-color: #060D13; color: #E1E8ED; font-family: 'Inter', sans-serif; }

    

    /* Gradiente de texto Pro */

    .text-gradient {

        background: -webkit-linear-gradient(45deg, #00E676, #00B0FF);

        -webkit-background-clip: text;

        -webkit-text-fill-color: transparent;

        font-weight: 900;

    }

    

    /* Estilizar Pestañas (Tabs) */

    [data-baseweb="tab-list"] { gap: 10px; }

    [data-baseweb="tab"] { background-color: transparent !important; color: #8899A6 !important; font-weight: 600 !important; }

    [data-baseweb="tab"][aria-selected="true"] { color: #00E676 !important; border-bottom: 2px solid #00E676 !important; }

    

    /* Tarjetas de Partido y Formularios */

    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {

        background-color: #111A24 !important;

        border-radius: 24px !important;

        border: 1px solid #1E2A38 !important;

        box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;

        margin-bottom: 25px !important;

        padding: 15px !important;

        transition: 0.3s ease;

    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {

        border-color: #00E67644 !important;

        box-shadow: 0 10px 30px rgba(0,230,118,0.15) !important;

    }

    

    /* Textos dentro de la tarjeta */

    .match-header { font-size: 0.8em; color: #8899A6; text-align: center; margin-bottom: 15px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; }

    .team-name { font-size: 1.15em; font-weight: 700; color: #FFFFFF; }

    .score-box { background: linear-gradient(145deg, #1A2433, #151E28); border: 1px solid #2C3E50; border-radius: 10px; padding: 8px 16px; font-size: 1.4em; font-weight: 900; color: #00E676; text-align: center; display: inline-block; min-width: 70px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);}

    

    /* RADIO BUTTONS: Centrados en cápsula deportiva */

    div[role="radiogroup"] {

        display: flex !important;

        justify-content: center !important;

        align-items: center !important;

        background-color: #1A2433;

        padding: 12px 25px;

        border-radius: 20px;

        border: 1px solid #2C3E50;

        margin: 0 auto 15px auto !important;

        width: fit-content;

        gap: 30px !important;

        box-shadow: inset 0 2px 5px rgba(0,0,0,0.3);

    }

    

    /* BOTONES GLOBALES (Confirmar y Entrar) */

    div[data-testid="stButton"], div[data-testid="stFormSubmitButton"] {

        display: flex !important;

        justify-content: center !important;

        width: 100% !important;

    }

    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button { 

        background: linear-gradient(45deg, #00E676, #00C853) !important; 

        color: #060D13 !important; 

        border-radius: 30px !important; 

        font-weight: 800 !important; 

        width: 60% !important; 

        border: none !important; 

        padding: 12px !important; 

        text-transform: uppercase !important;

        letter-spacing: 1.5px !important;

        transition: 0.3s !important; 

        box-shadow: 0 4px 10px rgba(0,230,118,0.2) !important;

    }

    div[data-testid="stButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { 

        transform: translateY(-3px) !important;

        box-shadow: 0 6px 20px rgba(0,230,118,0.5) !important; 

    }

    

    /* Podios */

    .podium-gold { background: linear-gradient(135deg, #FFB300, #FF8F00); color: #FFF; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 15px; box-shadow: 0 10px 25px rgba(255,143,0,0.3); }

    .podium-silver { background: linear-gradient(135deg, #B0BEC5, #78909C); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; }

    .podium-bronze { background: linear-gradient(135deg, #A1887F, #6D4C41); color: #FFF; padding: 15px; border-radius: 20px; text-align: center; }

    

    /* OCULTAR ELEMENTOS DE STREAMLIT (MÉTODO SEGURO) */

    #MainMenu, footer, [data-testid="stHeader"] { 

        display: none !important; 

    }

    .viewerBadge_container__1QSob, .viewerBadge_link__1S137 {

        display: none !important;

    }

    </style>

    """, unsafe_allow_html=True)



# --- 3. LÓGICA DE ACCESO (LOGIN) ---

if "Id_usuario" not in st.session_state:

    st.markdown("<br><br>", unsafe_allow_html=True)

    _, col_login, _ = st.columns([1, 1.5, 1])

    

    with col_login:

        st.markdown("""

        <div style="text-align: center; margin-bottom: 30px;">

            <h1 class="text-gradient" style="font-size: 3.5em; margin-bottom: 0;">FIFA 2026</h1>

            <h3 style="color: #FFF; font-weight: 800; letter-spacing: 2px; margin-top: 5px;">PORRA OFICIAL</h3>

            <p style="color: #8899A6; font-size: 0.95em;">Inicia sesión o regístrate para jugar</p>

        </div>

        """, unsafe_allow_html=True)

        

        with st.form("login_form", border=False):

            nombre_u = st.text_input("👤 Usuario", placeholder="Tu nombre")

            pass_u = st.text_input("🔒 Contraseña", type="password", placeholder="Mínimo 1 carácter")

            st.write("") 

            submit = st.form_submit_button("ENTRAR AL TORNEO")



        if submit:

            if nombre_u.strip() and pass_u.strip():

                res = supabase.table("Usuarios").select("*").eq("Nombre", nombre_u).execute()

                if res.data:

                    if str(res.data[0]["Password"]) == str(pass_u):

                        st.session_state["Id_usuario"] = res.data[0]["Id"]

                        st.session_state["Nombre"] = res.data[0]["Nombre"]

                        st.session_state["Estado"] = res.data[0].get("Estado", "Pendiente")

                        st.rerun()

                    else: 

                        st.error("❌ Contraseña incorrecta")

                else:

                    nuevo = supabase.table("Usuarios").insert({"Nombre": nombre_u, "Password": pass_u, "Puntos": 0, "Estado": "Pendiente"}).execute()

                    st.session_state["Id_usuario"] = nuevo.data[0]["Id"]

                    st.session_state["Nombre"] = nuevo.data[0]["Nombre"]

                    st.session_state["Estado"] = "Pendiente"

                    st.rerun()

            else:

                st.warning("⚠️ Rellena ambos campos")

    st.stop()



# --- 4. VERIFICACIÓN DE PAGO ---

if st.session_state.get("Estado") == "Pendiente":

    st.title("🔒 Cuenta Inactiva")

    st.warning(f"Hola {st.session_state['Nombre']}, necesitas activar tu cuenta para jugar.")

    st.info("Envía tu inscripción de **20€ por Bizum al 6XX XXX XXX** indicando tu nombre. El administrador validará tu pago al instante.")

    if st.button("🔄 Comprobar Pago"):

        res = supabase.table("Usuarios").select("Estado").eq("Id", st.session_state["Id_usuario"]).execute()

        st.session_state["Estado"] = res.data[0]["Estado"]

        st.rerun()

    st.stop()



# --- 5. CARGA DE DATOS ---

ADMIN_NOMBRE = "AGS"

es_admin = st.session_state["Nombre"] == ADMIN_NOMBRE



partidos_raw = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data

todos_usuarios_raw = supabase.table("Usuarios").select("Id, Nombre, Puntos").order("Puntos", desc=True).execute().data

todos_usuarios = [u for u in todos_usuarios_raw if u["Nombre"] != ADMIN_NOMBRE]



for p in partidos_raw:

    p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]



orden_fases = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "3º y 4º Puesto", "Final"]

fases_existentes = sorted(list(set(p["Fase_Visual"] for p in partidos_raw)), 

                          key=lambda x: orden_fases.index(x) if x in orden_fases else 99)



with st.sidebar:

    st.markdown(f"<h2 style='text-align: center;'><span class='text-gradient'>👤 {st.session_state['Nombre']}</span></h2>", unsafe_allow_html=True)

    res_yo = [u for u in todos_usuarios_raw if u['Id'] == st.session_state['Id_usuario']]

    puntos_yo = res_yo[0]['Puntos'] if res_yo else 0

    pos_display = "Admin" if es_admin else f"{next((i + 1 for i, u in enumerate(todos_usuarios) if u['Id'] == st.session_state['Id_usuario']), '-')}º"

    

    c1, c2 = st.columns(2)

    c1.metric("Tus Puntos", puntos_yo)

    c2.metric("Posición", pos_display)

    st.divider()

    if st.button("🚪 Cerrar Sesión"):

        st.session_state.clear()

        st.rerun()



hora_actual_espana = datetime.now(timezone.utc) + timedelta(hours=2) 



# --- 6. TABS PRINCIPALES ---

tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if es_admin else "📜 Reglas"])



with tabs[0]:

    if not partidos_raw:

        st.info("Cargando calendario oficial...")

    else:

        sub_tabs = st.tabs(fases_existentes)

        votos = {v['Id_partido']: v['Prediccion'] for v in supabase.table("Porras").select("Id_partido, Prediccion").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}



        for i, fase_tab in enumerate(fases_existentes):

            with sub_tabs[i]:

                partidos_fase = [p for p in partidos_raw if p["Fase_Visual"] == fase_tab]

                for p in partidos_fase:

                    

                    with st.container(border=True):

                        fecha_partido = datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc)

                        

                        st.markdown(f"<div class='match-header'>{p['Fase']} &nbsp;|&nbsp; {fecha_partido.strftime('%d %b %Y - %H:%M')}h</div>", unsafe_allow_html=True)

                        

                        # --- SOLUCIÓN RESPONSIVE PARA MÓVILES (FLEXBOX SIN SANGRÍA) ---

                        iso_l = BANDERAS.get(p['Equipo_local'], "un")

                        iso_v = BANDERAS.get(p['Equipo_visitante'], "un")

                        res_txt = p['Resultado_real'] if p['Resultado_real'] else "VS"

                        

                        # Al quitar las sangrías e hilarlo así, Streamlit se ve obligado a renderizar el HTML

                        html_marcador = (

                            f"<div style='display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 10px;'>"

                            f"<div style='display: flex; align-items: center; justify-content: flex-end; flex: 1; text-align: right; padding-right: 10px;'>"

                            f"<span class='team-name' style='margin-right: 8px; font-size: clamp(0.85em, 2.5vw, 1.15em); line-height: 1.2;'>{p['Equipo_local']}</span>"

                            f"<img src='https://flagcdn.com/32x24/{iso_l}.png' style='border-radius:4px; box-shadow:0 2px 4px rgba(0,0,0,0.5); min-width: 32px;'>"

                            f"</div>"

                            f"<div style='flex-shrink: 0; text-align: center;'>"

                            f"<span class='score-box' style='font-size: clamp(1em, 3vw, 1.4em); padding: 6px 10px;'>{res_txt}</span>"

                            f"</div>"

                            f"<div style='display: flex; align-items: center; justify-content: flex-start; flex: 1; text-align: left; padding-left: 10px;'>"

                            f"<img src='https://flagcdn.com/32x24/{iso_v}.png' style='border-radius:4px; box-shadow:0 2px 4px rgba(0,0,0,0.5); min-width: 32px; margin-right: 8px;'>"

                            f"<span class='team-name' style='font-size: clamp(0.85em, 2.5vw, 1.15em); line-height: 1.2;'>{p['Equipo_visitante']}</span>"

                            f"</div>"

                            f"</div>"

                        )

                        st.markdown(html_marcador, unsafe_allow_html=True)

                        # ----------------------------------------------------------------

                        

                        st.markdown("<hr style='margin: 10px 0px 15px 0px; border: none; border-top: 1px solid #1E2A38;'>", unsafe_allow_html=True)

                        

                        # ZONA DE APUESTAS

                        if p.get('Resultado_real'):

                            _, col_res, _ = st.columns([1, 4, 1])

                            with col_res:

                                if p['Id'] in votos:

                                    if votos[p['Id']] == p['Resultado_real']: st.success(f"🎯 Acertaste: {votos[p['Id']]}")

                                    else: st.error(f"❌ Fallaste. Tu apuesta fue: {votos[p['Id']]}")

                                else:

                                    st.info("Partido cerrado sin pronóstico")

                                    

                        elif p['Id'] in votos:

                            _, col_res, _ = st.columns([1, 4, 1])

                            with col_res:

                                st.info(f"✅ Voto registrado: **{votos[p['Id']]}**")

                                    

                        elif fecha_partido > hora_actual_espana:

                            # COLUMNAS PARA CENTRAR OPCIONES (RADIO)

                            _, col_radio, _ = st.columns([1, 5, 1])

                            with col_radio:

                                pred = st.radio("Voto:", [p['Equipo_local'], 'Empate', p['Equipo_visitante']], key=f"r_{p['Id']}", horizontal=True, label_visibility="collapsed")

                                valor_bd = 'X' if pred == 'Empate' else pred 

                            

                            st.write("") 

                            

                            # COLUMNAS PARA EL BOTÓN

                            _, col_btn, _ = st.columns([1, 2, 1])

                            with col_btn:

                                if st.button("Confirmar", key=f"b_{p['Id']}", use_container_width=True):

                                    supabase.table("Porras").upsert({"Id_usuario": st.session_state["Id_usuario"], "Id_partido": p["Id"], "Prediccion": valor_bd}).execute()

                                    st.rerun()

                        else: 

                            st.warning("🔒 Partido en juego / Finalizado. Esperando resultado.")

with tabs[1]:

    if not todos_usuarios:

        st.info("Aún no hay usuarios en el ranking.")

    else:

        usuarios_con_puntos = [u for u in todos_usuarios if u['Puntos'] > 0]

        

        if usuarios_con_puntos:

            st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'><span class='text-gradient'>🏆 LÍDERES DEL MUNDIAL</span></h3>", unsafe_allow_html=True)

            col_oro, col_plata, col_bronce = st.columns(3)

            if len(usuarios_con_puntos) > 0:

                with col_oro: st.markdown(f"<div class='podium-gold'><h1 style='margin:0;'>🥇</h1><h3 style='margin:5px 0;'>{usuarios_con_puntos[0]['Nombre']}</h3><h4 style='margin:0;'>{usuarios_con_puntos[0]['Puntos']} pts</h4></div>", unsafe_allow_html=True)

            if len(usuarios_con_puntos) > 1:

                with col_plata: st.markdown(f"<div class='podium-silver'><h2 style='margin:0;'>🥈</h2><h4 style='margin:5px 0;'>{usuarios_con_puntos[1]['Nombre']}</h4><h5 style='margin:0;'>{usuarios_con_puntos[1]['Puntos']} pts</h5></div>", unsafe_allow_html=True)

            if len(usuarios_con_puntos) > 2:

                with col_bronce: st.markdown(f"<div class='podium-bronze'><h2 style='margin:0;'>🥉</h2><h4 style='margin:5px 0;'>{usuarios_con_puntos[2]['Nombre']}</h4><h5 style='margin:0;'>{usuarios_con_puntos[2]['Puntos']} pts</h5></div>", unsafe_allow_html=True)

            st.divider()

        else:

            st.markdown("<div style='text-align: center; color: #8899A6; margin-bottom: 20px; font-style: italic;'>El podio aparecerá en cuanto comiencen a repartirse los primeros puntos. ¡Suerte a todos!</div>", unsafe_allow_html=True)



        st.markdown("<h4 style='color:#FFF;'>Clasificación Completa</h4>", unsafe_allow_html=True)

        

        df = pd.DataFrame(todos_usuarios)

        def medalla(i): return "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."

        

        df['Pos'] = [medalla(i) if u['Puntos'] > 0 else f"{i+1}." for i, u in enumerate(todos_usuarios)]

        df['Jugador'] = df['Pos'] + " " + df['Nombre']

        max_p = int(df['Puntos'].max()) if df['Puntos'].max() > 0 else 10

        

        def style_row(row):

            return ['background-color: #1E2A38; color: #00E676; font-weight: 800;'] * len(row) if row['Nombre'] == st.session_state['Nombre'] else [''] * len(row)

        

        st.dataframe(df[['Jugador', 'Puntos', 'Nombre']].style.apply(style_row, axis=1), use_container_width=True, hide_index=True,

                     column_config={"Jugador": "Jugador", "Puntos": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max_p), "Nombre": None})



if es_admin:

    with tabs[2]:

        st.subheader("🛠️ Panel de Control")

        

        p_pend = [p for p in partidos_raw if not p.get('Resultado_real') and datetime.fromisoformat(p['Fecha_hora']).replace(tzinfo=timezone.utc) < hora_actual_espana]

        

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

        u_pend = supabase.table("Usuarios").select("*").eq("Estado", "Pendiente").execute().data

        if u_pend:

            u_sel = st.selectbox("Usuario que ha pagado:", u_pend, format_func=lambda x: x['Nombre'])

            if st.button("MARCAR COMO PAGADO"):

                supabase.table("Usuarios").update({"Estado": "Pagado"}).eq("Id", u_sel['Id']).execute()

                st.success(f"¡Usuario {u_sel['Nombre']} activado!")

                st.rerun()

        else: 

            st.write("No hay pagos pendientes.")

else:

    with tabs[2]:

        st.markdown("""

        ### 📜 Reglas de la Porra Oficial

        * **Puntuación:** Recibes **1 punto** por cada pronóstico correcto (1, X, 2).

        * **Cierre Automático:** Las apuestas se bloquean en el instante exacto en que arranca el partido (Hora Peninsular de España). No se admiten votos de última hora.

        * **Actualizaciones:** Los cruces de eliminatorias (Octavos, etc.) se irán actualizando automáticamente en la app según avancen los equipos en la realidad.

        """)
