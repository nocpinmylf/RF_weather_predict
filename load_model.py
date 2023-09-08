import joblib
import warnings
import pandas as pd
from datetime import datetime

def convert_time_val(time_):
  if time_.split(' ')[0].strip() == 'No':
    return 0
  hour = datetime.strptime(time_, '%I:%M %p').time().hour
  mins = datetime.strptime(time_, '%I:%M %p').time().minute
  hour = hour + 1 if mins > 30 else hour
  return hour

def get_dir_val(dir):
  direction_mapping = {
  'N': 0,
  'NNE': 22.5,
  'NE': 45,
  'ENE': 67.5,
  'E': 90,
  'ESE': 112.5,
  'SE': 135,
  'SSE': 157.5,
  'S': 180,
  'SSW': 202.5,
  'SW': 225,
  'WSW': 247.5,
  'W': 270,
  'WNW': 292.5,
  'NW': 315,
  'NNW': 337.5
  }
  return direction_mapping.get(dir)

def process_data(row):
  month         = row[0]
  min_temp      = row[1] 
  max_temp      = row[2] 
  sunrise       = row[3] 
  sunset        = row[4] 
  moonrise      = row[5] 
  moonset       = row[6] 
  wind_speed    = row[7] 
  wind_dir      = row[8] 
  rain          = row[9] 
  humidity      = row[10] 
  cloud_percent = row[11] 
  pressure      = row[12] 
  this_weather  = row[13] 
  return  [[month, min_temp, max_temp, convert_time_val(sunrise),
            convert_time_val(sunset), convert_time_val(moonrise),
            convert_time_val(moonset), wind_speed, get_dir_val(wind_dir),
            rain, humidity, cloud_percent, pressure,
            encode_weather(this_weather)]]

def encode_weather(weather_):
  list_norain = ['Clear', 'Thundery outbreaks possible', 
                 'Partly cloudy', 'Cloudy', 'Mist', 'Sunny']
  return 0 if weather_ in list_norain else 1

def predict(model_name, new_data):
  model = joblib.load(model_name) # Load mô hình
  predictions = model.predict(new_data)
  return predictions[0]

def get_labels(result):
  return 'rain' if result == 1 else 'no rain'

if __name__ == '__main__':
  warnings.filterwarnings("ignore")
  
  # wind_dir	rain(mm)	humidity(%)	cloud(%)	pressure(mb)	current_weather	weather
  model_name  = 'weather_model.pkl'
  # Saturday, 13/5/2023, overcast
  month         = 5
  min_temp      = 24          # celcius
  max_temp      = 41          # celcius
  sunrise       = '05:19 AM'
  sunset        = '06:27 PM'
  moonrise      = '02:52 AM'
  moonset       = '03:21 PM'
  wind_speed    = 11          # (km/h)
  wind_dir      = 'SSE'       # direction
  rain          = 0.1         # mm
  humidity      = 71          # %
  cloud_percent = 46          # %
  pressure      = 1004        # mb
  this_weather  = 'Mist'
  new_data      = [[month, min_temp, max_temp, convert_time_val(sunrise),
                    convert_time_val(sunset), convert_time_val(moonrise),
                    convert_time_val(moonset), wind_speed, get_dir_val(wind_dir),
                    rain, humidity, cloud_percent, pressure,
                    encode_weather(this_weather)]]
  
  # print(new_data)
  result        = predict(model_name, new_data)
  print(get_labels(result))
