import pandas as pd
import numpy as np

# Configuración visual para la consola
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("=" * 70)
print("   ETL - ENCUESTA SNACKS MUNDIAL 2026 (FASE 1: INGESTA Y LIMPIEZA)")
print("=" * 70)

# ==========================================
# Paso 1. Carga del Dataset Original
# ==========================================
# Leemos el archivo CSV esta en src/
df_crudo = pd.read_csv("encuesta_snacks_mundial_2026_guatemala_2500_respuestas.csv")

print("\n>>> PASO 1: LECTURA DEL ARCHIVO CSV")
print("-" * 70)
print(f"Total de Encuestas Recibidas: {df_crudo.shape[0]} filas")
print(f"Total de Variables (Preguntas): {df_crudo.shape[1]} columnas")

# ==========================================
# Paso 2. Estandarización de Texto y Limpieza Básica
# ==========================================
# Al ser un formulario, la gente suele dejar espacios al inicio o final.
# Vamos a limpiar todas las columnas de texto (object)

# Seleccionamos solo las columnas que son texto
columnas_texto = df_crudo.select_dtypes(include=['object']).columns

# Aplicamos .str.strip() para quitar espacios y .str.title() para estandarizar formato
for col in columnas_texto:
    df_crudo[col] = df_crudo[col].str.strip().str.title()

print("\n>>> PASO 2: LIMPIEZA DE ESPACIOS Y FORMATO DE TEXTO APLICADA")
print("-" * 70)

# ==========================================
# Paso 3. Tratamiento de Valores Nulos
# ==========================================
print("\n>>> PASO 3: REPORTE DE VALORES NULOS")
print("-" * 70)
nulos_por_columna = df_crudo.isnull().sum()
print(nulos_por_columna[nulos_por_columna > 0]) # Solo mostramos si hay errores

# Llenamos los posibles nulos con "No Indicado" para no perder la encuesta
df_crudo.fillna("No Indicado", inplace=True)

print("\n(✓) Valores nulos reemplazados por 'No Indicado' exitosamente.")

#ESTO POSTERIORMERTE SE QUITARÁ, SOLO ES PARA VER LA MUESTRA DE DATOS LIMPIOS EN LA CONSOLA
# Mostramos una vista previa rápida de las primeras 3 encuestas
print("\n>>> VISTA PREVIA DE DATOS LIMPIOS (MUESTRA)")
print("-" * 70)

# Usamos .T (Transponer) para que las 26 columnas se vean hacia abajo 
# y sea muy fácil leer el perfil de las primeras 3 personas.
print(df_crudo.head(3).T.to_string())

# ==========================================
# FASE 2: CREACIÓN DEL ESQUEMA DE ESTRELLA (STAR SCHEMA)
# Extraemos valores únicos para crear las Tablas de Dimensiones
# ==========================================
print("\n>>> FASE 2: CONSTRUCCIÓN DE LAS TABLAS DE DIMENSIONES")
print("-" * 70)

# 1. Dimensión Geografía
dim_geografia = df_crudo[['Departamento', 'Municipio']].drop_duplicates().reset_index(drop=True)
dim_geografia.insert(0, 'GeografiaID', range(1, len(dim_geografia) + 1))
print(f"✓ dim_geografia creada con {len(dim_geografia)} ubicaciones únicas.")

# 2. Dimensión Demografía
dim_demografia = df_crudo[['RangoEdad', 'Genero', 'Ocupacion']].drop_duplicates().reset_index(drop=True)
dim_demografia.insert(0, 'DemografiaID', range(1, len(dim_demografia) + 1))
print(f"✓ dim_demografia creada con {len(dim_demografia)} perfiles únicos.")

# 3. Dimensión Hábitos de Consumo
dim_consumo = df_crudo[['FrecuenciaConsumoSnacks', 'LugarCompraSnacks', 'ConQuienVePartidos', 'GastoSnacksPartido']].drop_duplicates().reset_index(drop=True)
dim_consumo.insert(0, 'ConsumoID', range(1, len(dim_consumo) + 1))
print(f"✓ dim_consumo creada con {len(dim_consumo)} patrones únicos.")

# 4. Dimensión Preferencias de Producto
dim_producto = df_crudo[['SnacksSeleccionados', 'SaborPreferido', 'PresentacionPreferida', 'PrecioAdecuado', 'PagaMasEdicionMundial']].drop_duplicates().reset_index(drop=True)
dim_producto.insert(0, 'ProductoID', range(1, len(dim_producto) + 1))
print(f"✓ dim_producto creada con {len(dim_producto)} combinaciones de producto únicas.")

# 5. Dimensión Marketing
dim_marketing = df_crudo[['PlaneaVerMundial2026', 'SeleccionApoya', 'JugadoresInfluyentes', 'TipoPublicidadAtractiva', 'PromocionPreferida']].drop_duplicates().reset_index(drop=True)
dim_marketing.insert(0, 'MarketingID', range(1, len(dim_marketing) + 1))
print(f"✓ dim_marketing creada con {len(dim_marketing)} perfiles de marketing únicos.")


# ==========================================
# FASE 3: CONSTRUCCIÓN DE LA TABLA DE HECHOS (FACT TABLE)
# ==========================================
print("\n>>> FASE 3: CONSTRUCCIÓN DE LA TABLA DE HECHOS")
print("-" * 70)

# Unimos (Merge) el dataframe original con las dimensiones para traernos los nuevos IDs
df_temporal = df_crudo.copy()
df_temporal = df_temporal.merge(dim_geografia, on=['Departamento', 'Municipio'], how='left')
df_temporal = df_temporal.merge(dim_demografia, on=['RangoEdad', 'Genero', 'Ocupacion'], how='left')
df_temporal = df_temporal.merge(dim_consumo, on=['FrecuenciaConsumoSnacks', 'LugarCompraSnacks', 'ConQuienVePartidos', 'GastoSnacksPartido'], how='left')
df_temporal = df_temporal.merge(dim_producto, on=['SnacksSeleccionados', 'SaborPreferido', 'PresentacionPreferida', 'PrecioAdecuado', 'PagaMasEdicionMundial'], how='left')
df_temporal = df_temporal.merge(dim_marketing, on=['PlaneaVerMundial2026', 'SeleccionApoya', 'JugadoresInfluyentes', 'TipoPublicidadAtractiva', 'PromocionPreferida'], how='left')

# Seleccionamos solo las columnas que van en la tabla de hechos
fact_encuestas = df_temporal[['EncuestaID', 'FechaEncuesta', 'HoraEncuesta', 'GeografiaID', 'DemografiaID', 'ConsumoID', 'ProductoID', 'MarketingID']].copy()

# Agregamos una métrica de conteo base para Power BI
fact_encuestas['Cantidad_Encuesta'] = 1 

print(f"✓ fact_encuestas creada con {len(fact_encuestas)} registros y conectada a todos los IDs.")
print("\nVista previa de la Tabla de Hechos (Muestra):")
print(fact_encuestas.head(3))

# ==========================================