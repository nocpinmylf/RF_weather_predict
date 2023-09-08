import time
import joblib
import warnings
import numpy as np
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (train_test_split,
                                     learning_curve)
from sklearn.metrics import (accuracy_score,
                             classification_report,
                             mean_absolute_error,
                             mean_squared_error,
                             confusion_matrix,
                             roc_curve, roc_auc_score)

warnings.filterwarnings("ignore")

def train_model(data_path, estimators, test_rate, output_model):
  # Đọc dữ liệu từ file CSV
  data = pd.read_csv(data_path)

  # Chia thành features (X) và labels (y)
  X = data.drop('weather', axis=1)
  y = data['weather']

  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_rate, random_state=50)
  
  # Khởi tạo mô hình Random Forest
  random_forest_model = RandomForestClassifier(n_estimators=estimators, random_state=8)
  
  # Huấn luyện mô hình trên X_train và y_train
  random_forest_model.fit(X_train, y_train)

  y_pred = random_forest_model.predict(X_test)
  
  # Đánh giá mô hình
  evaluate_model(random_forest_model, X_train, y_train, X_test, y_test, y_pred)
  
  # Lưu mô hình vào file
  joblib.dump(random_forest_model, output_model)

def evaluate_model(model, X_train, y_train, X_test, y_test, y_pred):
  report = classification_report(y_test, y_pred)
  print(report)
  
  accuracy = accuracy_score(y_test, y_pred)
  mae = mean_absolute_error(y_test, y_pred)
  mse = mean_squared_error(y_test, y_pred)
  rmse = np.sqrt(mse)
  table = [
    ["Accuracy", f"{(accuracy * 100):.2f}%"], # Càng cao càng tốt.
    ["MAE", f"{mae:.2f}"],                    # Càng thấp càng tốt.
    ["MSE", f"{mse:.2f}"],                    # Càng thấp càng tốt.
    ["RMSE", f"{rmse:.2f}"]                   # Càng thấp càng tốt.
  ]
  
  print(tabulate(table, headers=["Metric", "Value"], tablefmt="grid"))
  
  # Đồ thị confusion matrix
  plot_confusion_matrix(y_test, y_pred, 1)
  
  # Đồ thị ROC Curve
  plot_roc_curve(model, X_test, y_test, 2)
  
  # Đồ thị Learning Curve
  plot_learning_curves(model, X_train, y_train, 3)
  
  plt.show()
  
def plot_confusion_matrix(y_test, y_pred, num):
  plt.figure(num=num) # Tạo một figure mới
  
  # Tính ma trận nhầm lẫn
  cm = confusion_matrix(y_test, y_pred)

  # Biểu diễn ma trận nhầm lẫn dưới dạng đồ thị
  plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
  plt.title('Confusion Matrix')
  plt.colorbar()
  plt.xticks([0, 1], ['No Rain', 'Rain'])
  plt.yticks([0, 1], ['No Rain', 'Rain'])

  # Hiển thị giá trị trên từng ô của đồ thị
  thresh = cm.max() / 2.
  for i in range(cm.shape[0]):
      for j in range(cm.shape[1]):
          plt.text(j, i, format(cm[i, j], 'd'), ha='center', va='center',
                  color='white' if cm[i, j] > thresh else 'black')

  plt.xlabel('Predicted label')
  plt.ylabel('True label')
  plt.tight_layout()
  plt.savefig('confusion_matrix.png')
  
def plot_roc_curve(model, X_test, y_test, num):
  plt.figure(num=num) # Tạo một figure mới
  
  # Dự đoán xác suất dự báo của mô hình trên tập test
  y_pred_proba = model.predict_proba(X_test)[:, 1]

  # Tính đường cong ROC và tính AUC
  fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
  auc = roc_auc_score(y_test, y_pred_proba)

  # Vẽ đồ thị ROC Curve
  plt.plot(fpr, tpr, label='ROC Curve (AUC = {:.2f})'.format(auc))
  plt.plot([0, 1], [0, 1], 'k--')  # Đường thẳng tương đương với mô hình ngẫu nhiên
  plt.xlabel('False Positive Rate')
  plt.ylabel('True Positive Rate')
  plt.title('ROC Curve')
  plt.legend(loc='lower right')
  plt.savefig('ROC_curve.png')

def plot_learning_curves(model, X_train, y_train, num):
  plt.figure(num=num)
  
  # Tính toán các giá trị train
  train_sizes, train_scores, test_scores = learning_curve(model, X_train, y_train, cv=5)

  train_mean = np.mean(train_scores, axis=1)
  train_std = np.std(train_scores, axis=1)
  test_mean = np.mean(test_scores, axis=1)
  test_std = np.std(test_scores, axis=1)

  plt.plot(train_sizes, train_mean, 'o-', color="r", label="Training score")
  plt.plot(train_sizes, test_mean, 'o-', color="g", label="Cross-validation score")
  plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="r")
  plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color="g")
  plt.xlabel("Training Samples")
  plt.ylabel("Score")
  plt.title("Learning Curve")
  plt.legend(loc="best")
  plt.savefig('learning_curve.png')
  plt.show()

if __name__ == '__main__':
  print(f'===========================================')
  print(f'===========================================')
  print(f'Start Training Model...')
  
  start_time = time.time() # Bắt đầu bộ đếm giờ
  # ======================================================================
  data_path     = 'data/processed_weather_data.csv'
  n_estimators  = 100
  test_rate     = 0.15   # 0 - 0.5
  output_model  = 'weather_model.pkl'
  
  train_model(data_path, n_estimators, test_rate, output_model)
  
  # ======================================================================
  end_time = time.time()  # Dừng bộ đếm giờ
  elapsed_time = round((end_time - start_time) / 60, 2)

  print(f'[✓] The process is completed successfully!')
  print(f'Elapsed time: {elapsed_time:.2f} minutes.')
  print(f'===========================================')
  print(f'===========================================')