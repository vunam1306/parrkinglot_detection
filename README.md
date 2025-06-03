sử dụng dataset đã được dán nhãn bằng roboflow 


re-trainning YOLOv8 với dataset và google colab, 


download file best.pt để sử dụng model mới 



https://github.com/user-attachments/assets/d2bbfadd-571f-4d75-a57c-dfeb7e71a3e3


đánh dấu các vị trí đỗ xe bằng file label_parking.py.


file parking_boxes.json là nơi chứa các điểm đã được đánh dấu từ file label_parking.py.


khởi chạy main bằng lệnh 
"python -m uvicorn main:app --reload"
