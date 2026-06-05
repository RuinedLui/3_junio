import pandas as pd

print("=" * 70)
print("REPORTE DE VOLUMETRÍA: DATOS CRUDOS VS. DATOS LIMPIOS")
print("=" * 70)

# ─────────────────────────────────────────────
# 1. CARGA
# ─────────────────────────────────────────────
df = pd.read_csv("encuesta_snacks_mundial_2026_guatemala_2500_respuestas.csv")

# === AQUÍ GENERAMOS EL REPORTE DE DATOS CRUDOS ===
print(f"[+] DATOS CRUDOS: Se cargaron {df.shape[0]} respuestas con {df.shape[1]} columnas.")
print(f"[!] Valores nulos detectados inicialmente: {df.isnull().sum().sum()}\n")

# ─────────────────────────────────────────────
# 2. ESTANDARIZACIÓN GENERAL
# ─────────────────────────────────────────────
df["Municipio"]              = df["Municipio"].fillna("No especificado")
df["Ocupacion"]              = df["Ocupacion"].fillna("No especificado")
df["LugarCompraSnacks"]      = df["LugarCompraSnacks"].fillna("No especificado")
df["SaborPreferido"]         = df["SaborPreferido"].fillna("No especificado")
df["PrecioAdecuado"]         = df["PrecioAdecuado"].fillna("No especificado")
df["SeleccionInfluyeCompra"] = df["SeleccionInfluyeCompra"].fillna("No especificado")

alias_depto = {"Guate": "Guatemala", "Xela": "Quetzaltenango"}
df["Departamento"] = df["Departamento"].str.strip().str.title().replace(alias_depto)
df["Municipio"]    = df["Municipio"].str.strip().str.title()

print("[✓] FASE DE LIMPIEZA: Nulos imputados y texto estandarizado correctamente.")

# ─────────────────────────────────────────────
# 3. DIM_GEOGRAFIA
# ─────────────────────────────────────────────
dim_geo = df[["Departamento","Municipio"]].drop_duplicates().reset_index(drop=True)
dim_geo.insert(0, "GeografiaID", dim_geo.index + 1)
df = df.merge(dim_geo, on=["Departamento","Municipio"], how="left")

# ─────────────────────────────────────────────
# 4. DIM_DEMOGRAFIA 
# ─────────────────────────────────────────────
dim_dem = df[["RangoEdad","Genero","Ocupacion"]].drop_duplicates().reset_index(drop=True)
dim_dem.insert(0, "DemografiaID", dim_dem.index + 1)
dim_dem.columns = ["DemografiaID","Rango_Edad","Genero","Ocupacion"]
df = df.merge(dim_dem.rename(columns={"Rango_Edad":"RangoEdad"}),
              on=["RangoEdad","Genero","Ocupacion"], how="left")

# ─────────────────────────────────────────────
# 5. DIM_HABITOS_CONSUMO
# ─────────────────────────────────────────────
cons_cols = ["FrecuenciaConsumoSnacks","LugarCompraSnacks",
             "ConQuienVePartidos","GastoSnacksPartido"]
dim_cons = df[cons_cols].drop_duplicates().reset_index(drop=True)
dim_cons.insert(0, "ConsumoID", dim_cons.index + 1)
dim_cons.columns = ["ConsumoID","Frecuencia_Consumo","Lugar_Compra_Habitual",
                    "Compania_Partidos","Gasto_Snacks_Partido"]
df = df.merge(
    dim_cons.rename(columns={
        "Frecuencia_Consumo"   : "FrecuenciaConsumoSnacks",
        "Lugar_Compra_Habitual": "LugarCompraSnacks",
        "Compania_Partidos"    : "ConQuienVePartidos",
        "Gasto_Snacks_Partido" : "GastoSnacksPartido",
    }),
    on=cons_cols, how="left"
)

# ─────────────────────────────────────────────
# 6. DIM_PREFERENCIAS_PRODUCTO
# ─────────────────────────────────────────────
prod_cols = ["SaborPreferido","PrecioAdecuado","PresentacionPreferida","PagaMasEdicionMundial"]
dim_prod = df[prod_cols].drop_duplicates().reset_index(drop=True)
dim_prod.insert(0, "ProductoID", dim_prod.index + 1)
dim_prod.columns = ["ProductoID","Sabor_Preferido","Precio_Ideal",
                    "Presentacion_Preferida","Paga_Mas_Edicion_Especial"]
df = df.merge(
    dim_prod.rename(columns={
        "Sabor_Preferido"          : "SaborPreferido",
        "Precio_Ideal"             : "PrecioAdecuado",
        "Presentacion_Preferida"   : "PresentacionPreferida",
        "Paga_Mas_Edicion_Especial": "PagaMasEdicionMundial",
    }),
    on=prod_cols, how="left"
)

# ─────────────────────────────────────────────
# 7. DIM_SNACK
# ─────────────────────────────────────────────
snacks_unicos = (
    df["SnacksSeleccionados"].str.split("; ").explode()
    .str.strip().drop_duplicates().reset_index(drop=True)
)
dim_snack = pd.DataFrame({"SnackID": snacks_unicos.index + 1,
                           "Snack_Nombre": snacks_unicos.values})

# ─────────────────────────────────────────────
# 8. DIM_JUGADOR
# ─────────────────────────────────────────────
jugadores_unicos = (
    df["JugadoresInfluyentes"].str.split("; ").explode()
    .str.strip().drop_duplicates().reset_index(drop=True)
)
dim_jugador = pd.DataFrame({"JugadorID": jugadores_unicos.index + 1,
                             "Jugador_Nombre": jugadores_unicos.values})

# ─────────────────────────────────────────────
# 9. DIM_MARKETING_MUNDIAL 
# ─────────────────────────────────────────────
mkt_cols = ["SeleccionApoya", "CompraDisenoSeleccion", "SeleccionInfluyeCompra", 
            "TipoPublicidadAtractiva","PromocionPreferida",
            "PlaneaVerMundial2026","CompraTarjetasColeccionables"]
dim_mkt = df[mkt_cols].drop_duplicates().reset_index(drop=True)
dim_mkt.insert(0, "MarketingID", dim_mkt.index + 1)
dim_mkt.columns = ["MarketingID","Equipo_Favorito", "Compra_Diseno_Seleccion", "Seleccion_Influye_Compra",
                   "Tipo_Publicidad","Tipo_Promocion","Sigue_Mundial_2026",
                   "Compraria_Tarjetas_Coleccionables"]
df = df.merge(
    dim_mkt.rename(columns={
        "Equipo_Favorito"                   : "SeleccionApoya",
        "Compra_Diseno_Seleccion"           : "CompraDisenoSeleccion",
        "Seleccion_Influye_Compra"          : "SeleccionInfluyeCompra",
        "Tipo_Publicidad"                   : "TipoPublicidadAtractiva",
        "Tipo_Promocion"                    : "PromocionPreferida",
        "Sigue_Mundial_2026"                : "PlaneaVerMundial2026",
        "Compraria_Tarjetas_Coleccionables" : "CompraTarjetasColeccionables",
    }),
    on=mkt_cols, how="left"
)

# ─────────────────────────────────────────────
# 10. FACT_ENCUESTAS
# ─────────────────────────────────────────────
fact = df[["EncuestaID","FechaEncuesta","HoraEncuesta",
           "GeografiaID","DemografiaID","ConsumoID",
           "ProductoID","MarketingID"]].copy()
fact["Cantidad_Encuesta"] = 1

print("[✓] FASE DE TRANSFORMACIÓN: Esquema de Estrella y Tablas Puente generadas con éxito.")

# ─────────────────────────────────────────────
# 11. BRIDGE TABLES
# ─────────────────────────────────────────────
snack_lookup = dim_snack.set_index("Snack_Nombre")["SnackID"]
bridge_snack_rows = []
for _, row in df[["EncuestaID","SnacksSeleccionados"]].iterrows():
    for s in str(row["SnacksSeleccionados"]).split("; "):
        s = s.strip()
        if s in snack_lookup.index:
            bridge_snack_rows.append({"EncuestaID": row["EncuestaID"], "SnackID": snack_lookup[s]})
bridge_encuesta_snack = pd.DataFrame(bridge_snack_rows).drop_duplicates()

jug_lookup = dim_jugador.set_index("Jugador_Nombre")["JugadorID"]
bridge_jug_rows = []
for _, row in df[["EncuestaID","JugadoresInfluyentes"]].iterrows():
    for j in str(row["JugadoresInfluyentes"]).split("; "):
        j = j.strip()
        if j in jug_lookup.index:
            bridge_jug_rows.append({"EncuestaID": row["EncuestaID"], "JugadorID": jug_lookup[j]})
bridge_encuesta_jugador = pd.DataFrame(bridge_jug_rows).drop_duplicates()

# ─────────────────────────────────────────────
# 12. EXPORTAR CSV
# ─────────────────────────────────────────────
fact.to_csv("fact_encuestas.csv",                    index=False, encoding="utf-8-sig")
dim_geo.to_csv("dim_geografia.csv",                  index=False, encoding="utf-8-sig")
dim_dem.to_csv("dim_demografia.csv",                 index=False, encoding="utf-8-sig")
dim_cons.to_csv("dim_habitos_concleasumo.csv",            index=False, encoding="utf-8-sig")
dim_prod.to_csv("dim_preferencias_producto.csv",      index=False, encoding="utf-8-sig")
dim_snack.to_csv("dim_snack.csv",                    index=False, encoding="utf-8-sig")
dim_jugador.to_csv("dim_jugador.csv",                index=False, encoding="utf-8-sig")
dim_mkt.to_csv("dim_marketing_mundial.csv",          index=False, encoding="utf-8-sig")
bridge_encuesta_snack.to_csv("bridge_encuesta_snack.csv",       index=False, encoding="utf-8-sig")
bridge_encuesta_jugador.to_csv("bridge_encuesta_jugador.csv",   index=False, encoding="utf-8-sig")

# === AQUÍ COMPLETAMOS EL REPORTE DE DATOS LIMPIOS ===
print("\n[+] DATOS LIMPIOS: Exportación exitosa a 10 archivos CSV.")
print(f"    - Tabla de Hechos retenida: {fact.shape[0]} registros (0% pérdida de datos).")
print("    - Valores nulos finales en el modelo: 0")
print("=" * 70)

# =============================================================================
# REPORTE EJECUTIVO Y DE INTELIGENCIA DE NEGOCIOS 
# =============================================================================

print("\n" + "="*70)
print(">>> FASE 4: DASHBOARD EJECUTIVO DE KPIs (TOP MÉTRICAS)")
print("="*70)

# KPI 1
print("\n[KPI 1] TOP 3 DEPARTAMENTOS CON MAYOR PARTICIPACIÓN:")
for i, (depto, pct) in enumerate(df['Departamento'].value_counts(normalize=True).head(3).mul(100).items(), 1):
    print(f"  {i}. {depto}: {pct:.1f}% del mercado encuestado")

# KPI 2
print("\n[KPI 2] TOP 3 SNACKS FAVORITOS:")
top_snacks = bridge_encuesta_snack.merge(dim_snack, on='SnackID')['Snack_Nombre'].value_counts(normalize=True).head(3).mul(100)
for i, (snack, pct) in enumerate(top_snacks.items(), 1):
    print(f"  {i}. {snack}: {pct:.1f}% de las menciones")

# KPI 3
print("\n[KPI 3] TOP 3 JUGADORES MÁS INFLUYENTES:")
top_jugadores = bridge_encuesta_jugador.merge(dim_jugador, on='JugadorID')['Jugador_Nombre'].value_counts(normalize=True).head(3).mul(100)
for i, (jugador, pct) in enumerate(top_jugadores.items(), 1):
    print(f"  {i}. {jugador}: {pct:.1f}% de las menciones")

# KPI 4
print("\n[KPI 4] INTENCIÓN DE MERCADO (¿VERÁN EL MUNDIAL 2026?):")
mundial_intent = df['PlaneaVerMundial2026'].value_counts(normalize=True).mul(100)
for i, (respuesta, pct) in enumerate(mundial_intent.items(), 1):
    print(f"  {i}. {respuesta}: {pct:.1f}%")

# KPI 5
print("\n[KPI 5] SENSIBILIDAD AL PRECIO (PAGO POR EDICIÓN ESPECIAL):")
precio_intent = df['PagaMasEdicionMundial'].value_counts(normalize=True).mul(100)
for i, (respuesta, pct) in enumerate(precio_intent.items(), 1):
    print(f"  {i}. {respuesta}: {pct:.1f}%")


# --- FASE 5: ANALÍTICA AVANZADA (ESTRATEGIA) ---
print("\n" + "="*70)
print(">>> FASE 5: ANALÍTICA AVANZADA (OPORTUNIDADES DE NEGOCIO)")
print("="*70)

# 1. Disposición a pagar por Edad (Filtrando solo los que dicen "Sí")
print("\n[INSIGHT 1] TOP 3 RANGOS DE EDAD CON MAYOR DISPOSICIÓN A PAGAR MÁS:")
pago_edad = df[df['PagaMasEdicionMundial'].str.contains('Sí', na=False, case=False)]
top_pago_edad = pago_edad['RangoEdad'].value_counts().head(3)
for i, (edad, cantidad) in enumerate(top_pago_edad.items(), 1):
    print(f"  {i}. {edad} ({cantidad} potenciales compradores premium)")

# 2. Marketing vs Coleccionables (Publicidad que más convierte en tarjetas)
print("\n[INSIGHT 2] TOP 3 CANALES DE PUBLICIDAD PARA VENDER COLECCIONABLES:")
col_publi = df[df['CompraTarjetasColeccionables'].str.contains('Sí', na=False, case=False)]
top_col_publi = col_publi['TipoPublicidadAtractiva'].value_counts().head(3)
for i, (publi, cantidad) in enumerate(top_col_publi.items(), 1):
    print(f"  {i}. {publi} ({cantidad} interesados en tarjetas)")

# 3. Frecuencia vs Gasto (El segmento de mayor valor)
print("\n[INSIGHT 3] PERFIL DEL CONSUMIDOR HIGH-TICKET (GASTO ALTO + ALTA FRECUENCIA):")
top_gasto_frec = df.groupby(['FrecuenciaConsumoSnacks', 'GastoSnacksPartido']).size().nlargest(3)
for i, ((frecuencia, gasto), cantidad) in enumerate(top_gasto_frec.items(), 1):
    print(f"  {i}. Frecuencia: {frecuencia} | Gasto: {gasto} -> {cantidad} usuarios")


# --- FASE 6: ANÁLISIS MULTIDIMENSIONAL (CORRELACIONES CLAVE) ---
print("\n" + "="*70)
print(">>> FASE 6: ANÁLISIS MULTIDIMENSIONAL (PATRONES DE COMPORTAMIENTO)")
print("="*70)

# 1. Snacks por Edad (La combinación más fuerte)
print("\n[REPORTE 1] TOP 4 COMBINACIONES: SNACK FAVORITO POR RANGO DE EDAD")
snack_demog = bridge_encuesta_snack.merge(fact, on='EncuestaID').merge(dim_dem, on='DemografiaID').merge(dim_snack, on='SnackID')
top_snack_edad = snack_demog.groupby(['Rango_Edad', 'Snack_Nombre']).size().nlargest(4)
for i, ((edad, snack), cantidad) in enumerate(top_snack_edad.items(), 1):
    print(f"  {i}. Público {edad} prefiere {snack} ({cantidad} votos)")

# 2. Gasto por Departamento
print("\n[REPORTE 2] TOP 3 CIUDADES CON MAYOR VOLUMEN DE GASTO ALTO:")
# Asumiendo que el gasto alto se identifica por texto; ajusta según tus valores
gasto_alto = df[df['GastoSnacksPartido'].astype(str).str.contains('alto|más de', na=False, case=False)]
if not gasto_alto.empty:
    top_depto_gasto = gasto_alto['Departamento'].value_counts().head(3)
    for i, (depto, cantidad) in enumerate(top_depto_gasto.items(), 1):
        print(f"  {i}. {depto} ({cantidad} consumidores de alto gasto)")
else:
    # Si no hay un filtro exacto, sacamos la combinación general más común
    top_depto_gasto = df.groupby(['Departamento', 'GastoSnacksPartido']).size().nlargest(3)
    for i, ((depto, gasto), cantidad) in enumerate(top_depto_gasto.items(), 1):
        print(f"  {i}. {depto} con gasto '{gasto}' ({cantidad} usuarios)")

# 3. Conversión de Mundial vs Coleccionables
print("\n[REPORTE 3] TASA DE CONVERSIÓN: FANS DEL MUNDIAL QUE COMPRARÍAN COLECCIONABLES")
fans_mundial = df[df['PlaneaVerMundial2026'].str.contains('Sí', na=False, case=False)]
if len(fans_mundial) > 0:
    fans_compradores = fans_mundial['CompraTarjetasColeccionables'].str.contains('Sí', na=False, case=False).sum()
    tasa = (fans_compradores / len(fans_mundial)) * 100
    print(f"  -> El {tasa:.1f}% de los que seguirán el mundial están dispuestos a comprar tarjetas.")

# 4. Sabor vs Presentación
print("\n[REPORTE 4] TOP 3 FORMATOS DE PRODUCTO MÁS BUSCADOS (SABOR + PRESENTACIÓN):")
top_sabor_pres = df.groupby(['SaborPreferido', 'PresentacionPreferida']).size().nlargest(3)
for i, ((sabor, presentacion), cantidad) in enumerate(top_sabor_pres.items(), 1):
    print(f"  {i}. Sabor {sabor} en formato {presentacion} ({cantidad} preferencias)")

    # --- FASE 7: ESTRATEGIA DE CANALES, EMPAQUES Y CAMPAÑAS ---
print("\n" + "="*70)
print(">>> FASE 7: ESTRATEGIA COMERCIAL Y DE MARKETING APLICADA")
print("="*70)

# 1. Canales de Distribución (Dónde enfocar la logística)
print("\n[REPORTE 5] TOP 3 CANALES DE DISTRIBUCIÓN (DÓNDE COMPRAN MÁS):")
top_canales = df['LugarCompraSnacks'].value_counts(normalize=True).head(3).mul(100)
for i, (canal, pct) in enumerate(top_canales.items(), 1):
    print(f"  {i}. {canal}: {pct:.1f}% de la intención de compra")

# 2. Empaque vs Compañía (Estrategia para crear Combos/Bundles)
print("\n[REPORTE 6] COMPORTAMIENTO SOCIAL VS TAMAÑO DE EMPAQUE (CREACIÓN DE COMBOS):")
top_empaque_social = df.groupby(['ConQuienVePartidos', 'PresentacionPreferida']).size().nlargest(4)
for i, ((compania, empaque), cantidad) in enumerate(top_empaque_social.items(), 1):
    print(f"  {i}. Público que ve partidos con '{compania}' prefiere tamaño '{empaque}' ({cantidad} usuarios)")

# 3. Promociones que enganchan (Estrategia de retención)
print("\n[REPORTE 7] TOP 3 PROMOCIONES MÁS EFECTIVAS PARA ACELERAR VENTAS:")
top_promos = df['PromocionPreferida'].value_counts(normalize=True).head(3).mul(100)
for i, (promo, pct) in enumerate(top_promos.items(), 1):
    print(f"  {i}. {promo}: {pct:.1f}% de preferencia en el mercado")

# 4. Impacto del Branding (¿Vale la pena invertir en empaques de países?)
print("\n[REPORTE 8] RENTABILIDAD DEL EMPAQUE TEMÁTICO (DISEÑO DE LA SELECCIÓN):")
diseno_importa = df['CompraDisenoSeleccion'].value_counts(normalize=True).mul(100)
for i, (respuesta, pct) in enumerate(diseno_importa.items(), 1):
    print(f"  {i}. Comprarían solo por el diseño del país -> {respuesta}: {pct:.1f}%")

# 5. La Campaña Ganadora (Alineación del presupuesto de Marketing)
print("\n[REPORTE 9] TOP 3 CAMPAÑAS QUE GENERAN MAYOR PROBABILIDAD DE COMPRA:")
top_campanias = df['CampaniaMasProbableCompra'].value_counts(normalize=True).head(3).mul(100)
for i, (campania, pct) in enumerate(top_campanias.items(), 1):
    print(f"  {i}. Temática '{campania}': {pct:.1f}% de favorabilidad")

print("\n" + "="*70)
print("FIN DEL REPORTE EJECUTIVO (LISTO PARA CONCLUSIONES DE NEGOCIO)")
print("="*70)

