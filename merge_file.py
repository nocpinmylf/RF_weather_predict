import os
import csv

def reverse_data_in_file(file_path, save_path):
  # Đọc toàn bộ nội dung của file
  with open(file_path, "r") as file:
    lines = file.readlines()

  # Đảo ngược thứ tự các dòng
  reversed_lines = reversed(lines[1:]) # Xoá dòng header

  # Ghi nội dung đã đảo ngược vào file
  with open(save_path, "w") as file:
    file.writelines(reversed_lines) 

def merge_files(directory, output_file, header):
  # Kiểm tra xem thư mục tồn tại hay không
  if not os.path.exists(directory):
    print(f"Thư mục '{directory}' không tồn tại.")
    return
  
  # Mở file đầu ra để ghi dữ liệu trộn
  with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    
    # Ghi dòng header vào file xử lý
    outfile.writelines(header + '\n')
    
    files = os.listdir(directory)
    # files_sorted = sorted(files, reverse=True)  # Sắp xếp các file theo thứ tự ngược lại
    
    # Lặp qua tất cả các file trong thư mục
    for file, filename in enumerate(files):
      # if not filename.split('.')[0].isdigit():
      if not filename.startswith('_'):
        print("Skipping file:", filename)
        continue
      
      filepath = os.path.join(directory, filename)
      
      # Kiểm tra xem tập tin có phải là file CSV hay không
      if os.path.isfile(filepath) and filename.lower().endswith('.csv'):
        # Đọc dữ liệu từ file hiện tại và ghi vào file đầu ra
        with open(filepath, 'r') as csvfile:
          reader = csv.reader(csvfile)
          for i, row in enumerate(reader):
            writer.writerow(row)

if __name__ == '__main__':
  print(f'===========================================')
  print(f'===========================================')
  print(f'Start Merging...')
  # ======================================================================
  
  # header = 'month,date,time,temperature,rain(mm),rain_percent,cloud_percent,pressure(mb),wind(km/h),gust(km/h),weather'
  header = 'month,date,min_temp,max_temp,sunrise,sunset,moonrise,moonset,wind_speed(km/h),wind_dir,rain(mm),humidity(%),cloud(%),pressure(mb),weather'
  directory = 'data'  # Thay đổi thành đường dẫn thư mục chứa các file CSV của bạn
  
  for year in range(2009, 2024):
    file_name = f'{year}.csv'
    reverse_file = f'_{year}.csv' # Tên file
    
    file_path = os.path.join(directory, file_name)
    
    save_path = os.path.join(directory, reverse_file)
    reverse_data_in_file(file_path, save_path)
  
  # Merge files
  outfile_file = 'weather_data.csv'
  output_path = os.path.join(directory, outfile_file)
  merge_files(directory, output_path, header)
  
  # ======================================================================
  print(f'Done.')
  print(f'===========================================')
  print(f'===========================================')
  
  
