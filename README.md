📦 Project Components
Apache Airflow: Orchestrates and schedules the data extraction and loading tasks.
AWS EC2: Hosts the Airflow environment and runs the pipeline.
Amazon S3: Stores the weather data as JSON files.
OpenWeather API: Provides real-time weather data.


🚀 Features
✅ Extract current weather data from OpenWeather API.
✅ Store the data in S3 as structured JSON files.
✅ Run on a scalable EC2 instance.
✅ Configurable city and API keys.
✅ Easy to extend for multiple cities or data types.


⚙️ Prerequisites
AWS Account with:
S3 bucket created (e.g., airflowweatherapibucket)
IAM Role/Access Key with S3 permissions
EC2 instance (Ubuntu recommended)
Python 3.8+ installed
Airflow installed and configured on EC2
OpenWeather API Key

