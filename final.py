import warnings
import numpy as np
import pandas as pd
import streamlit as st
import crawl2 as crawl
from PIL import Image
import load_model as load
from tabulate import tabulate

warnings.filterwarnings("ignore")
model_name      = 'weather_model.pkl'
columns         = ['Month', 'Date', 'Minimum Temperature', 'Maximum Temperature',
                  'Sunrise Time', 'Sunset Time','Moonrise Time', 'Moonset Time',
                  'Wind Speed(km/h)', 'Wind Direction', 'Rain(mm)',
                  'Humidity(%)', 'Cloud(%)', 'Pressure(mb)', 'This Weather']

data            = crawl.Start(modeUpdate=True, currentYear=crawl.GetLatestYear())
table_data      = list(zip(columns, data))
filtered_data   = [value for column, value in table_data if column != 'Date']
processed_data  = load.process_data(filtered_data)
result          = load.predict(model_name, processed_data)

# ===========================================
# === Deployment
# ===========================================
st.set_page_config(
  page_title=" Live Weather Forecast",
  page_icon="🌦️",
  layout="wide",
  initial_sidebar_state="expanded",
)

# --- CSS ----------------------------------- 
style = '''
  <style>
    .page-title {
      text-align: center;
      color: #72ed86;
      text-transform: uppercase;
    }
    
    h2.header {
      text-transform: capitalize;
    }
    
    .header:hover {
      color: #72ed86;
      transition: .3s;
    }
    
    .predict-value {
      color: #7c07b3;
      padding: 4px 7px;
      border-radius: 3px;
      background-color: #282629;
      text-transform: uppercase;
    }
    
    .center {
      text-align: center;
    }
    
    footer {
      visibility: hidden;
      display: none;
    }
  </style>
'''
st.markdown(style, unsafe_allow_html=True)

# --- Components ----------------------------
st.markdown(f'''
<h1 class='page-title'>🌦️ Weather Forecast 🌦️</h1>
<h2 class='header'>Today's forecast (24 hours): <span class='predict-value'>{load.get_labels(result)}</span></h2>


<h2 class='header center'>Yesterday's Data</h2>
      
''', unsafe_allow_html=True)
st.table(pd.DataFrame(table_data, columns=('Attribute', 'Value')))

st.image(Image.open('confusion_matrix.png'), caption='confusion_matrix')
st.image(Image.open('learning_curve.png'), caption='learning_curve')
st.image(Image.open('ROC_curve.png'), caption='ROC_curve')