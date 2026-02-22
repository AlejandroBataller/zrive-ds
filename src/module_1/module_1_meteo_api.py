import requests  # Necesaria para conectarte a la API
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://archive-api.open-meteo.com/v1/archive?"

COORDINATES = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}
VARIABLES = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]


def get_data_meteo_api(city_name):
    # Aquí es donde usarás requests para llamar a la API

    lat = COORDINATES[city_name]["latitude"]
    lon = COORDINATES[city_name]["longitude"]

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2010-01-01",
        "end_date": "2020-12-31",
        "daily": ",".join(VARIABLES),
        "timezone": "auto",
    }
    r = requests.get(API_URL, params=params)
    if r.status_code == 200:
        print(f"Datos de {city_name} descargados con éxito")
        return r.json()
    else:
        print(f"Error en {city_name}: {r.status_code}")
        return None


def process_meteo_data(raw_data, city_name):
    # Extraemos la parte daily que es la que tiene los datos climaticos
    daily_data = raw_data["daily"]

    # Creamos el DataFrame de Pandas
    df = pd.DataFrame(daily_data)

    # Convertimos la columna time a formato fecha real
    df["time"] = pd.to_datetime(df["time"])

    # Añadir una columna con el nombre de la ciudad
    df["city"] = city_name

    return df


def resample_to_monthly(df):
    # Ponemos la fecha como índice para poder agrupar el tiempo
    df = df.set_index("time")

    # Agrupamos por mes y calculamos la media
    # 'numeric_only=True' asegura que no intenta hacer medias de la columna city
    # "MS" = Month Start y es para que pandas entienda que es mensual
    monthly_df = df.resample("MS").mean(numeric_only=True)

    return monthly_df


def plot_meteo_data(dfs_dict):
    """
        Recibe un diccionario con los DataFrames de cada ciudad y genera gráficos.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
    
    variables = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]
    titles = ["Temperatura Media (ºC)", "Precipitación Total (mm)", "Velocidad Máxima Viento (km/h)"]

    for i, var in enumerate(variables):
        for city, df in dfs_dict.items():
            axes[i].plot(df.index, df[var], label=city)
        axes[i].set_title(titles[i]) # pone el nombre que le correspone a cada panel
        axes[i].legend() # Muestra el cuadradito donde pone el color y la ciudad a la que corresponde (gracias al label = city)
        axes[i].grid(True) # Muestra la cuadrícula de fondo

    plt.xlabel("Fecha") # Pone la etiqueta "Fecha" en el eje de las X
    plt.tight_layout() # Ajusto los titulos 
    
    # Guardamos el resultado como pide el PDF
    plt.savefig("weather_comparison.png")
    print("📊 Gráfico comparativo guardado como 'weather_comparison.png'")
    plt.show()

def main():
    # Diccionario para guardar los resultados finales de cada ciudad
    all_cities_data = {}
    
    # Iteramos sobre las ciudades que definimos en COORDINATES
    for city in COORDINATES.keys():
        print(f"\n--- Iniciando proceso para: {city} ---")
        
        # Llamada a la API 
        raw_data = get_data_meteo_api(city)
        
        if raw_data:
            # Procesamiento inicial a DataFrame 
            df_daily = process_meteo_data(raw_data, city)
            
            # Reducción de resolución a mensual
            df_monthly = resample_to_monthly(df_daily)
            
            # Guardamos el DataFrame en nuestro diccionario
            all_cities_data[city] = df_monthly
            print(f"Datos de {city} listos para graficar.")
        else:
            print(f"Saltando {city} debido a un error en la descarga.")

    # Si logramos obtener datos, generamos el gráfico
    if all_cities_data:
        print("\nGenerando gráficos comparativos...")
        plot_meteo_data(all_cities_data)
    else:
        print("No se obtuvieron datos de ninguna ciudad. Revisa la conexión.")

if __name__ == "__main__":
    main()
