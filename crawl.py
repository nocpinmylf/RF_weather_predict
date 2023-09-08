import csv
import time
import datetime
from datetime import date
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def GetData(dir, year, url, month=0, date=0):
  columns = ['month', 'date', 'time', 'temperature', 'rain(mm)', 'rain_percent',
             'cloud_percent','pressure(mb)', 'wind(km/h)', 'gust(km/h)', 'weather']
  # Mở File
  fileName = f'{dir}/{year}.csv'
  with open(fileName, 'a', newline = '') as file:
    writer = csv.DictWriter(file, fieldnames = columns)
    writer.writeheader()

  # khởi tạo trình duyệt Edge
  driver = webdriver.Edge()
  driver.get(url)
  year_input = driver.find_element('id', 'ctl00_MainContentHolder_txtPastDate')
  year_input.clear()
  year_input.send_keys(year)
  last_day = f'31/12/{year}'
  
  # current_date = f'31/12/{year}' if date = 0 or month = 0 else f'{date}/{month}/{year}'
  # last_day = f'12/4/{year}'
  dateFormat = '%d/%m/%Y'

  # So sánh ngày đang chọn với ngày hôm nay
  if(datetime.datetime.strptime(last_day, dateFormat).date() > datetime.datetime.now().date()):
    # Nếu ngày đang chọn lớn hơn ngày hôm nay, đặt lại ngày đang chọn thành ngày hôm nay
    last_day = datetime.datetime.now().date().strftime(dateFormat)

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

      # Tìm bảng có class 'days-details-table'
      table = soup.find('table', class_='days-details-table')

      # Tìm các dòng trong bảng
      rows = table.find_all('tr', class_='days-details-row')
      
    except:
      driver.refresh()
      time.sleep(1)
      continue
    time.sleep(1)
    
    day_, month_, year_ = map(int, last_day.split('/'))
    GetWeatherByDate(rows, month_, day_, fileName, columns)

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

def GetWeatherByDate(rows, month, date, fileName, col):
  data = []

  # Lặp qua các dòng trong bảng
  for row in rows:
    # Tìm tất cả các ô trong dòng
    cells = row.find_all('td')
    
    row_data = GetRow(cells, month, date)
    
    # Thêm dict vào danh sách dữ liệu
    data.insert(0, row_data)

  # Xoá dòng đầu tiên (vì là tiêu đề nên không cần thiết)
  data.pop(-1)

  # Lưu dữ liệu vào file csv
  with open(fileName, 'a', newline = '') as file:
    writer = csv.DictWriter(file, fieldnames = col)
    writer.writerows(data)

def GetRow(cells, month, date):
  # Tạo một dict để lưu trữ dữ liệu
  row_data = {}
  row_data['month'] = month
  row_data['date']  = date

  # Lặp qua các ô trong dòng và gán giá trị vào dict tương ứng với tên cột
  for i, cell in enumerate(cells):
    match i:
      case 0:
        # Ô thứ nhất có 2 class: 'days-comment' và 'days-temp'
        time_cell = cell.find(class_='days-comment')
        row_data['time'] = time_cell.get_text().strip() if time_cell is not None else 'N/A'
        temperature_cell = cell.find(class_='days-temp')
        row_data['temperature'] = temperature_cell.get_text().split(' ')[0].strip() if temperature_cell is not None else 'N/A'
      case 1:
        # Ô hình ảnh chính là nhãn
        img = cell.find('img')
        row_data['weather'] = img['title'] if img is not None else 'N/A'
      case 3:
        # Ô thứ ba có class 'days-rain-number'
        row_data['rain(mm)'] = cell.get_text().split('mm')[0].strip()
      case 4:
        # Ô thứ tư là 'rain_percent'
        row_data['rain_percent'] = cell.get_text().split('%')[0].strip()
      case 5:
        # Ô thứ năm là 'cloud_percent'
        row_data['cloud_percent'] = cell.get_text().split('%')[0].strip()
      case 6:
        # Ô thứ sáu là 'pressure(mb)'
        row_data['pressure(mb)'] = cell.get_text().split('mb')[0].strip()
      case 7:
        # Ô thứ bảy là 'wind(km/h)'
        row_data['wind(km/h)'] = cell.get_text().split(' ')[0].strip()
      case 8:
        # Ô thứ tám là 'gust(km/h)'
        row_data['gust(km/h)'] = cell.get_text().split(' ')[0].strip()
      case _:
        pass
  return row_data

def Start(currentYear, toYear, modeUpdate=True):
  print(f'===========================================')
  print(f'===========================================')
  print(f'Start Crawling Data')
  print(f'===========================================')
  print(f'===========================================')
  start_time = time.time() # Bắt đầu bộ đếm giờ
  # ======================================================================
  
  url = 'https://www.worldweatheronline.com/ha-noi-weather-history/vn.aspx'
  dirName = 'data'
  
  # Crawl Data
  if modeUpdate:
    GetData(dirName, currentYear, url)
  else:
    for year in range(currentYear, toYear - 1, -1):
      GetData(dirName, year, url)
  
  # ======================================================================
  end_time = time.time()  # Dừng bộ đếm giờ
  elapsed_time = round((end_time - start_time) / 60, 2)  # Tính tổng thời gian chạy script

  print(f'===========================================')
  print(f'===========================================')
  print(f'[✓] The process is completed successfully!')
  print(f'Elapsed time: {elapsed_time:.2f} minutes.')
  print(f'===========================================')
  print(f'===========================================')

if __name__ == '__main__':
  currentYear = 2023
  toYear      = 2010
  modeUpdate  = False
  Start(currentYear, toYear, modeUpdate)
