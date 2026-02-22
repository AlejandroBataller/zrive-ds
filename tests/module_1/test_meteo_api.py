from src.module_1.module_1_meteo_api import process_meteo_data
import pandas as pd


def test_process_meteo_data_columns():
    # 1. Creamos datos de prueba falsos (mock data)
    fake_raw_data = {
        "daily": {
            "time": ["2023-01-01", "2023-01-02"],
            "temperature_2m_mean": [10.5, 12.0],
            "precipitation_sum": [0.0, 5.2],
            "wind_speed_10m_max": [15.0, 20.0],
        }
    }

    # 2. Ejecutamos tu función
    df = process_meteo_data(fake_raw_data, "Madrid")

    # 3. Comprobamos que el resultado es correcto (Assertions)
    assert isinstance(df, pd.DataFrame)  # ¿Es una tabla de Pandas?
    assert "city" in df.columns  # ¿Tiene la columna 'city' que añadiste?
    assert df.shape[0] == 2  # ¿Tiene las 2 filas que le pasamos?
    assert df["city"].iloc[0] == "Madrid"  # ¿El nombre de la ciudad es correcto?
