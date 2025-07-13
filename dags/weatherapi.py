from airflow import DAG
from datetime import timedelta, datetime
from airflow.providers.http.sensors.http import HttpSensor
from config import FULL_WEATHER_URL,S3_BUCKET_NAME
import json
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.standard.operators.python import PythonOperator
import boto3



def kelvin_to_fahrenheit(temp_in_kelvin):
    import pandas as pd
    import numpy as np
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32
    return temp_in_fahrenheit


def transform_load_data(task_instance):
    import pandas as pd
    import numpy as np
    data = task_instance.xcom_pull(task_ids="extract_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_farenheit = kelvin_to_fahrenheit(data["main"]["temp"])
    feels_like_farenheit= kelvin_to_fahrenheit(data["main"]["feels_like"])
    min_temp_farenheit = kelvin_to_fahrenheit(data["main"]["temp_min"])
    max_temp_farenheit = kelvin_to_fahrenheit(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    transformed_data = {"City": city,
                        "Description": weather_description,
                        "Temperature (F)": temp_farenheit,
                        "Feels Like (F)": feels_like_farenheit,
                        "Minimun Temp (F)":min_temp_farenheit,
                        "Maximum Temp (F)": max_temp_farenheit,
                        "Pressure": pressure,
                        "Humidty": humidity,
                        "Wind Speed": wind_speed,
                        "Time of Record": time_of_record,
                        "Sunrise (Local Time)":sunrise_time,
                        "Sunset (Local Time)": sunset_time                        
                        }
    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)
    
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = 'current_weather_data_madgaon_' + dt_string
    df_data.to_csv(f"s3://{S3_BUCKET_NAME}/{dt_string}.csv", index=False)


default_args = {  
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 29),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    'weather_dag',
    default_args=default_args,  
    schedule='@daily',
    catchup=False
) as dag:

    is_weather_api_ready = HttpSensor(
        task_id='is_weather_api_ready',
        http_conn_id='weathermap_api',  
        endpoint=FULL_WEATHER_URL
    )

    extract_weather_data = HttpOperator(
        task_id = 'extract_weather_data',
        http_conn_id = 'weathermap_api',
        endpoint=FULL_WEATHER_URL,
        method = 'GET',
        response_filter= lambda r: json.loads(r.text),
        log_response=True
    )

    transform_load_weather_data = PythonOperator(   
        task_id= 'transform_load_weather_data',
        python_callable=transform_load_data
    )

    is_weather_api_ready >> extract_weather_data >> transform_load_weather_data