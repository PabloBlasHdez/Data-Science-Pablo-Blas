import pickle

import folium
import matplotlib.pyplot as plt
import pandas as pd
from folium import TileLayer, Icon, Rectangle
import seaborn as sns

DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def limpia_lineas_codigo(lineas):
    """
    Elimina líneas con comentarios o del docstring
    :param lineas: lista de strings del código de la función
    :return: lista de strings sin los comentarios ni el docstring
    """
    resultado = []
    en_docstring = False
    for linea in lineas:
        linea_strip = linea.strip()
        # Detecta inicio o fin de docstring
        if linea_strip.startswith('"""'):
            if not en_docstring:
                en_docstring = True
            elif en_docstring:
                en_docstring = False
            continue
        if en_docstring:
            continue
        if linea_strip.startswith('#') or not linea_strip:
            continue
        resultado.append(linea)
    return resultado

def visualiza_viajes(outliers_pd: pd.DataFrame, inliers_pd: pd.DataFrame,
                     boundaries: dict) -> folium.Map:
    """
    Función para visualizar en un mapa los puntos de recogida de dos muestras distintas de viajes, una de outliers y otra de inliers,
    diferenciados por colores. Se marca el rectángulo de los límites de la ciudad de Nueva York en amarillo, los outliers con marcador rojo, y los
    inliers con marcador azul.

    :param outliers_pd: DF de Pandas con la muestra de viajes considerados outliers, que debe incluir columnas 'pickup_latitude' y 'pickup_longitude'
    :param inliers_pd: DF de Pandas con la muestra de viajes considerados inliers, que debe incluir columnas 'pickup_latitude' y 'pickup_longitude'
    :param boundaries: diccionario con las coordenadas de los límites de la ciudad de Nueva York, con claves 'min_longitude', 'max_longitude', 'min_latitude' y 'max_latitude'
    :return:
    """

    map_osm = folium.Map(location=[40.734695, -73.990372],
                         tiles='Stamen Toner',
                         attr='bla',
                         zoom_start=12
    )

    boundary_points = [
        (boundaries["min_latitude"], boundaries["min_longitude"]),
        (boundaries["min_latitude"], boundaries["max_longitude"]),
        (boundaries["max_latitude"], boundaries["max_longitude"]),
        (boundaries["max_latitude"], boundaries["min_longitude"])
    ]

    folium.PolyLine(locations=[boundary_points[0], boundary_points[1]], color='yellow', weight=4, opacity=0.8).add_to(map_osm)
    folium.PolyLine(locations=[boundary_points[1], boundary_points[2]], color='yellow', weight=4, opacity=0.8).add_to(map_osm)
    folium.PolyLine(locations=[boundary_points[2], boundary_points[3]], color='yellow', weight=4, opacity=0.8).add_to(map_osm)
    folium.PolyLine(locations=[boundary_points[3], boundary_points[0]], color='yellow', weight=4, opacity=0.8).add_to(map_osm)

    TileLayer('CartoDB positron', attr='© OpenStreetMap contributors').add_to(map_osm)

    # We will spot only the first 1000 outliers on the map. Plotting all the outliers will take more time
    for i,j in outliers_pd.iterrows():
        if int(j['pickup_latitude']) != 0:
            folium.Marker(list((j['pickup_latitude'],j['pickup_longitude'])),
                          icon=Icon(color='red', icon="map-marker")).add_to(map_osm)

    for i,j in inliers_pd.iterrows():
        if int(j['pickup_latitude']) != 0:
            folium.Marker(
                list((j['pickup_latitude'],j['pickup_longitude']))).add_to(map_osm)

    return map_osm


def aniade_capas_distritos(input_map: folium.Map, gdf):
    """
     Añade una capa de polígonos al mapa de folium a partir de un GeoDataFrame de GeoPandas, pintando cada polígono
     con un color según el valor de la propiedad `poverty_perc`, y mostrando en el tooltip las claves de `properties` de cada feature del GeoJSON.
    :param input_map: Mapa de folium existente al que se añadirá la capa de polígonos. No debe modificarse este código.
    :param gdf:  GeoDataFrame de GeoPandas con la geometría de los polígonos y sus propiedades, que debe incluir al menos la columna
                `tasa_pobreza` para pintar los polígonos según su valor, y otras columnas que se mostrarán en el tooltip al pasar el ratón por encima
    """
    # Obtener el GeoJSON como dict y extraer las claves de properties del primer feature
    import json
    geojson_dict = json.loads(gdf.to_json())
    features = geojson_dict.get('features', [])
    first_props = features[0].get('properties', {})
    tooltip_fields = list(first_props.keys())

    # Colormap lineal y rangos
    vmin = float(gdf['tasa_pobreza'].min())
    vmax = float(gdf['tasa_pobreza'].max())
    colormap = folium.LinearColormap(colors=['green', 'yellow', 'red'], vmin=vmin, vmax=vmax, caption='tasa_pobreza')

    # Función de estilo que pinta según la propiedad poverty_perc
    def style_function(feature):
        val = feature.get('properties', {}).get('tasa_pobreza')
        try:
            color = colormap(float(val))
        except Exception:
            color = '#cccccc'  # color por defecto si no hay valor
        return {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7
        }

    folium.GeoJson(
        data=geojson_dict,
        name='NYC Community Districts',
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, labels=True)
    ).add_to(input_map)
    folium.LayerControl().add_to(input_map)


def visualiza_community_districts(distritos_gdf, viajes_pd: pd.DataFrame):
    """
    Función para visualizar en un mapa de folium los distritos comunitarios de Nueva York a partir de un GeoDataFrame de GeoPandas, pintando cada distrito con un color según su tasa de pobreza, y mostrando en el tooltip las claves de `properties` de cada feature del GeoJSON.

    :param gdf: GeoDataFrame de GeoPandas con la geometría de los polígonos y sus propiedades, que debe incluir al menos la columna `tasa_pobreza` para pintar los polígonos según su valor, y otras columnas que se mostrarán en el tooltip al pasar el ratón por encima
    :return: Mapa de folium con la visualización de los distritos comunitarios
    """
    import json
    geojson_dict = json.loads(distritos_gdf.to_json())
    features = geojson_dict.get('features', [])
    first_props = features[0].get('properties', {})
    tooltip_fields = list(first_props.keys())

    map_osm = folium.Map(location=[40.734695, -73.990372],
                         tiles='Stamen Toner',
                         attr='bla',
                         zoom_start=12
    )

    TileLayer('CartoDB positron', attr='© OpenStreetMap contributors').add_to(map_osm)

    for i,j in viajes_pd.iterrows():
        if int(j['pickup_latitude']) != 0:
            folium.Marker(
                list((j['pickup_latitude'],j['pickup_longitude']))
            ).add_to(map_osm)

    folium.GeoJson(
        data=geojson_dict,
        name='NYC Community Districts',
        style_function=lambda feature: {
            'fillColor': "gray",
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.4
        },
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields, labels=True)
    ).add_to(map_osm)
    folium.LayerControl().add_to(map_osm)
    return map_osm


def plot_boxplot_facets(stats_df, variable: str) -> None:
    """
    Genera un gráfico facetado de boxplots a partir del DataFrame pivotado
    devuelto por compute_boxplot_stats().

    Formato esperado del DataFrame de entrada (pivotado):
        - Una fila por hora del día (columna 'hour_of_day', valores 0-23).
        - Para cada día de la semana d (0=lunes … 6=domingo), cinco columnas:
              {d}_q1, {d}_median, {d}_q3, {d}_whisker_low, {d}_whisker_high
          Ejemplo: '0_q1', '0_median', '0_q3', '0_whisker_low', '0_whisker_high',
                   '1_q1', ..., '6_whisker_high'

    Layout del gráfico:
        - Filas de facetas    → horas del día (0-23)
        - Columnas de facetas → días de la semana (0=lunes … 6=domingo)

    Cada subgráfico contiene un único boxplot construido con ax.bxp() usando
    los estadísticos precalculados.
    """
    # Convertir a Pandas para iterar cómodamente
    # Acepta tanto Spark DataFrame como Pandas DataFrame
    if hasattr(stats_df, 'toPandas'):
        pdf: pd.DataFrame = stats_df.toPandas()
    else:
        pdf = stats_df.copy()

    # Detectar los días de la semana presentes a partir de los prefijos de columna
    # Las columnas tienen el formato '{day}_{stat}'
    days = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    hours = sorted(pdf['pickup_hour'].unique())  # 0-23

    n_rows = len(hours)   # hasta 24
    n_cols = len(days)    # hasta 7

    fig, axes = plt.subplots(
        nrows=n_rows,
        ncols=n_cols,
        figsize=(n_cols * 1.6, n_rows * 1.2),
        sharex=False,
        sharey=True,          # mismo eje Y para comparar entre celdas
        squeeze=False,
    )

    for row_idx, h in enumerate(hours):
        # Fila del DataFrame pivotado correspondiente a esta hora
        hour_row = pdf[pdf['pickup_hour'] == h]

        for col_idx, d in enumerate(days):
            ax = axes[row_idx][col_idx]

            if hour_row.empty:
                ax.set_visible(False)
                continue

            r = hour_row.iloc[0]

            # Nombres de columna con prefijo del día
            prefix = f'{d}_'
            q1_val  = r.get(f'{prefix}q1',          r.get(f'{d}_q1',          None))
            med_val = r.get(f'{prefix}median',       r.get(f'{d}_median',       None))
            q3_val  = r.get(f'{prefix}q3',           r.get(f'{d}_q3',           None))
            wlo_val = r.get(f'{prefix}whisker_low',  r.get(f'{d}_whisker_low',  None))
            whi_val = r.get(f'{prefix}whisker_high', r.get(f'{d}_whisker_high', None))

            # Si algún valor esencial es nulo, ocultar el subgráfico
            if any(v is None or (isinstance(v, float) and pd.isna(v))
                   for v in [q1_val, med_val, q3_val]):
                ax.set_visible(False)
                continue

            bxp_stats = [{
                'med':    float(med_val),
                'q1':     float(q1_val),
                'q3':     float(q3_val),
                'whislo': float(wlo_val) if wlo_val is not None and not pd.isna(wlo_val) else float(q1_val),
                'whishi': float(whi_val) if whi_val is not None and not pd.isna(whi_val) else float(q3_val),
                'fliers': [],
            }]

            ax.bxp(bxp_stats, showfliers=False, widths=0.5,
                   boxprops=dict(color='steelblue'),
                   medianprops=dict(color='tomato', linewidth=1.5),
                   whiskerprops=dict(color='steelblue'),
                   capprops=dict(color='steelblue'))

            ax.set_xticks([])
            ax.tick_params(axis='y', labelsize=5)

            # Etiquetas de fila (hora) en el eje izquierdo
            if col_idx == 0:
                ax.set_ylabel(f'{h:02d} h', fontsize=10, rotation=0, labelpad=18, va='center')

            # Etiquetas de columna (día) en la fila superior
            if row_idx == 0:
                day_label = d
                ax.set_title(day_label, fontsize=10, pad=3)

    fig.suptitle(f"Boxplot de {variable} por hora del día × día de la semana", fontsize=12, y=1.002)
    plt.tight_layout()
    plt.show()


def plot_week_hour_heatmap(df_pd: pd.DataFrame, title="Heatmap by Day of Week and Hour of Day", cbar_label="Value"):
    """
    Dibuja un heatmap rectangular de seaborn con filas = días de la semana
    y columnas = horas del día.

    Parámetros:
        df_pd      : DataFrame de Pandas con 7 filas (días) y 24 columnas (horas).
                     Las columnas deben ser strings o enteros "0".."23" / 0..23.
        title      : Título del gráfico.
        cbar_label : Etiqueta de la barra de color.
    """
    heatmap_data = df_pd.copy()
    heatmap_data.set_index("day_of_week", drop=True, inplace=True)
    heatmap_data.columns = [int(c) for c in heatmap_data.columns]  # "0".."23" → 0..23

    fig, ax = plt.subplots(figsize=(14, 4))

    sns.heatmap(
        heatmap_data,
        ax=ax,
        cmap="RdBu_r",          # azul oscuro → blanco → rojo
        linewidths=0.5,
        linecolor="white",
        annot=True,             # muestra el valor en cada celda
        fmt=".1f",              # redondeado a 1 decimal
        annot_kws={"size": 7},  # tamaño de fuente para que quepan los números
        cbar_kws={"label": cbar_label},
    )

    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("Hour of Day", fontsize=11)
    ax.set_ylabel("Day of Week", fontsize=11)
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()
    plt.show()