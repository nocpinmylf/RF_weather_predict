import os
import csv
import time
import requests
import datetime
from datetime import date, datetime, timedelta
import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.edge.options import Options

def GetLatestDate():
  now       = datetime.now()
  yesterday = now - timedelta(days=1)
  day       = yesterday.day
  month     = yesterday.month
  year      = yesterday.year
  return f'{day}/{month}/{year}'

def GetLatestYear():
  now       = datetime.now()
  yesterday = now - timedelta(days=1)
  year      = yesterday.year
  return year

def GetFileDirectory(dir, year):
  columns = ['month', 'date', 'min_temp', 'max_temp', 'sunrise',
             'sunset','moonrise', 'moonset', 'wind_speed(km/h)', 'wind_dir',
             'rain(mm)', 'humidity(%)', 'cloud(%)', 'pressure(mb)', 'weather']
  # Mở File
  fileName = f'{dir}/{year}.csv'
  if os.path.getsize(fileName) == 0: # Nếu file chưa có dữ liệu thì ghi header vào
    with open(fileName, 'a', newline = '') as file:
      writer = csv.DictWriter(file, fieldnames = columns)
      writer.writeheader()
  return fileName

def GetLatestData(dir, year, url):
  # Lấy đường dẫn file lưu
  fileName = GetFileDirectory(dir, year)
  last_day = GetLatestDate()

  while True:
    try:
      response = requests.get(url)
      soup = BeautifulSoup(response.content, 'html.parser')
      date_, month_, year_ = map(int, last_day.split('/'))
      data = GetWeatherByDate(soup, date_, month_, year_, fileName)
      if data is not None:
        return data
    except Exception as e:
      traceback.print_tb(e.__traceback__)
      continue

def GetData(dir, year, url):
  # Lấy đường dẫn file lưu
  fileName = GetFileDirectory(year)

  # khởi tạo trình duyệt Edge
  driver = webdriver.Edge()
  driver.get(url)
  year_input = driver.find_element('id', 'ctl00_MainContentHolder_txtPastDate')
  year_input.clear()
  year_input.send_keys(year)
  last_day = f'31/12/{year}'

  # last_day = f'01/03/{year}'
  dateFormat = '%d/%m/%Y'

  # So sánh ngày đang chọn với ngày hôm nay
  if(datetime.datetime.strptime(last_day, dateFormat).date() > datetime.datetime.now().date()):
    # Nếu ngày đang chọn lớn hơn ngày hôm nay, đặt lại ngày đang chọn thành ngày hôm nay
    last_day = GetLatestDate()

  while True:
    try:
      # Nhập ngày cần tìm kiếm
      date_input = driver.find_element('id', 'ctl00_MainContentHolder_txtPastDate')
      date_input.clear()
      date_input.send_keys(last_day)
      
      # Click nút "Show past weather"
      show_weather_button = driver.find_element('id', 'ctl00_MainContentHolder_butShowPastWeather')
      show_weather_button.click()
      
      soup = BeautifulSoup(driver.page_source, 'html.parser')
      
      date_, month_, year_ = map(int, last_day.split('/'))
      GetWeatherByDate(soup, date_, month_, year_, fileName)
      
    except Exception as e:
      traceback.print_tb(e.__traceback__)
      driver.refresh()
      time.sleep(1)
      continue
    time.sleep(1)
    
    # Kiểm tra nếu đã lấy hết thông tin thì dừng vòng lặp
    if last_day == f'01/01/{year}':
      driver.quit()
      break

    # Cập nhật ngày tiếp theo
    last_day_obj = datetime.datetime.strptime(last_day, dateFormat)
    # Chuyển đổi chuỗi ngày sang đối tượng datetime
    last_day_obj = datetime.datetime.strptime(last_day, dateFormat)

    # Giảm ngày đi một đơn vị
    last_day_obj -= datetime.timedelta(days = 1)

    # Chuyển đổi đối tượng datetime về định dạng chuỗi ngày
    last_day = last_day_obj.strftime(dateFormat)

def GetWeatherByDate(soup, date, month, year, fileName):
  
  # Thời tiết
  weather = soup.find('div', class_='days-collapse-forecast').text
  
  # Tìm tag
  sunrise_div   = soup.find_all('div', class_='days-rise')[1]
  sunset_div    = soup.find_all('div', class_='days-set')[1]
  moonrise_div  = soup.find('div', class_='days-rise')
  moonset_div   = soup.find('div', class_='days-set')
  
  # Trích xuất
  sunrise   = sunrise_div.span.text
  sunset    = sunset_div.span.text
  moonrise  = moonrise_div.span.text
  moonset   = moonset_div.span.text

  # Tìm bảng có class 'days-details-table'
  table   = soup.find('div', class_='wwo-tabular')

  # Tìm các dòng trong bảng
  rows    = table.find_all('div', class_='mr-1')
  enable  = False
  detail  = []
  
  for item in rows:
    tag_value = item.text
    if tag_value.isdigit():
      if tag_value == str(year):
        enable = True
      else:
        enable = False
    if enable:
      detail.append(tag_value)
  
  max_temp  = detail[2].split(' ')[0]
  min_temp  = detail[3].split(' ')[0]
  wind      = detail[4].split('km/h')[0].strip()
  wind_dir  = detail[4].split('km/h')[1]
  rain      = detail[5].split(' ')[0]
  humidity  = detail[6].split('%')[0]
  cloud     = detail[7].split('%')[0]
  pressure  = detail[8].split(' ')[0]

  row_data = [month, date, min_temp, max_temp,
              sunrise, sunset, moonrise, moonset,
              wind, wind_dir, rain, humidity, cloud, pressure, weather]
  data = ','.join(map(str, row_data))
  if data is None:
    raise Exception
   
  return row_data
    
def Start(modeUpdate, currentYear, toYear=2009):
  print(f'===========================================')
  print(f'===========================================')
  print(f'Start Crawling Data')

  start_time = time.time() # Bắt đầu bộ đếm giờ
  # ======================================================================
  
  url = 'https://www.worldweatheronline.com/ha-noi-weather-history/vn.aspx'
  dirName = 'data'
  
  # Crawl Data
  if modeUpdate:
    return GetLatestData(dirName, GetLatestYear(), url)
  else:
    for year in range(currentYear, toYear - 1, -1):
      GetData(dirName, year, url)
      
  # ======================================================================
  end_time = time.time()  # Dừng bộ đếm giờ
  elapsed_time = round((end_time - start_time) / 60, 2)  # Tính tổng thời gian chạy script

  print(f'[✓] The process is completed successfully!')
  print(f'Elapsed time: {elapsed_time:.2f} minutes.')
  print(f'===========================================')
  print(f'===========================================')

if __name__ == '__main__':
  currentYear = GetLatestYear()
  toYear      = 2009
  modeUpdate  = True
  Start(modeUpdate, currentYear, toYear)
