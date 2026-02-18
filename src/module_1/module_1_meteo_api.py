import requests  # Necesaria para conectarte a la API
import time
import pandas as pd

API_URL = "https://archive-api.open-meteo.com/v1/archive?"

COORDINATES = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}
VARIABLES = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]

def get_data_meteo_api(city_name):
    # Aquí es donde usarás requests para llamar a la API
    #primero sacamos las coordenadas 
    lat=COORDINATES[city_name]["latitude"]
    lon=COORDINATES[city_name]["longitude"]

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2010-01-01",
        "end_date": "2020-12-31",
        "daily": ",".join(VARIABLES),
        "timezone": "auto"
    }
    r=requests.get(API_URL, params=params)

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
    df=pd.DataFrame(daily_data)
    # Convertimos la columna time a formato fecha real
    df["time"] = pd.to_datetime(df["time"])
    #Añadir una columna con el nombre de la ciudad
    df["city"] = city_name

    return df
def resample_to_monthly(df):
    # Ponemos la fecha como índice para poder agrupar el tiempo
    df=df.set_index("time")

    # Agrupamos por mes y calculamos la media
    # 'numeric_only=True' asegura que no intenta hacer medias de la columna city
    monthly_df = dfresample("mes").mean(numeric_only=True)

    return monthly_df

def main():
    # Probamos con Madrid
    print("--- Probando descarga de Madrid ---")
    datos_madrid = get_data_meteo_api("Madrid")
    
    if datos_madrid:
        # Imprimimos solo las llaves para ver qué contiene el paquete
        print("Estructura recibida:", datos_madrid.keys())
        # Vemos los primeros 5 días de temperaturas para confirmar
        print("Primeras temperaturas:", datos_madrid["daily"]["temperature_2m_mean"][:5])
    else:
        print("No se pudieron obtener los datos.")

if __name__ == "__main__":
    main()
