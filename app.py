# --- 4. CARGA DE DATOS (ESTRUCTURA BINARIA) ---
ADMIN_NOMBRE = "AGS"
es_admin = st.session_state["Nombre"] == ADMIN_NOMBRE

# 1. Traemos todos los partidos ordenados por fecha
partidos_raw = supabase.table("Partidos").select("*").order("Fecha_hora").execute().data

# 2. Clasificación infalible para campos NULL o vacíos
pendientes = []
finalizados = []

for p in partidos_raw:
    res = p.get('Resultado_real')
    # Esta condición detecta NULL (None), strings vacíos o la palabra "None"
    if res is None or str(res).strip().lower() in ["", "none", "null"]:
        pendientes.append(p)
    else:
        finalizados.append(p)

# Unimos poniendo los NULL arriba
partidos_finales = pendientes + finalizados

# --- 5. TABS ---
tabs = st.tabs(["📅 Partidos", "🏆 Ranking", "⚙️ Admin" if es_admin else "📜 Reglas"])

with tabs[0]:
    fases_nombres = ["Fase de Grupos", "Dieciseisavos", "Octavos", "Cuartos", "Semifinales", "3º y 4º Puesto", "Final"]
    for p in partidos_finales:
        p["Fase_Visual"] = "Fase de Grupos" if "Grupo" in p["Fase"] else p["Fase"]
    
    fases_ex = sorted(list(set(p["Fase_Visual"] for p in partidos_finales)), key=lambda x: fases_nombres.index(x) if x in fases_nombres else 99)
    sub_tabs = st.tabs(fases_ex)
    
    votos_data = {v['Id_partido']: v['Prediccion'] for v in supabase.table("Porras").select("Id_partido, Prediccion").eq("Id_usuario", st.session_state["Id_usuario"]).execute().data}
    hora_actual = datetime.now(timezone.utc) + timedelta(hours=2)

    for i, fase_tab in enumerate(fases_ex):
        with sub_tabs[i]:
            # FILTRAR PARTIDOS DE ESTA PESTAÑA
            partidos_fase = [x for x in partidos_finales if x["Fase_Visual"] == fase_tab]
            
            # SEPARACIÓN POR SEGURIDAD: Primero los que no tienen resultado
            for p in partidos_fase:
                res_val = p.get('Resultado_real')
                es_finalizado = not (res_val is None or str(res_val).strip().lower() in ["", "none", "null"])
                
                # Solo dibujamos si NO es finalizado en esta primera pasada
                if not es_finalizado:
                    with st.container(border=True):
                        # ... (Aquí va el código del diseño del partido que ya tienes) ...
                        dibujar_partido(p, votos_data, hora_actual) # Función simplificada para el ejemplo

            # SEGUNDA PASADA: Los finalizados (si existen)
            finalizados_fase = [x for x in partidos_fase if not (x.get('Resultado_real') is None or str(x.get('Resultado_real')).strip().lower() in ["", "none", "null"])]
            
            if finalizados_fase:
                st.markdown("<br><h4 style='text-align:center; color:#8899A6;'>RESULTADOS</h4>", unsafe_allow_html=True)
                for p in finalizados_fase:
                    with st.container(border=True):
                         # ... (Diseño del partido finalizado) ...
                         dibujar_partido(p, votos_data, hora_actual)
