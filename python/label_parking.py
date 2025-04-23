import cv2
import json
import numpy as np

points = []
boxes = []

def click_event(event, x, y, flags, param):
    global points, boxes

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

        if len(points) == 4:
            boxes.append(points.copy())
            points = []

def draw_boxes(img):
    temp_img = img.copy()
    for box in boxes:
        for i in range(4):
            cv2.line(temp_img, box[i], box[(i+1)%4], (0,255,0), 2)
    return temp_img

def save_to_json(filename="parking_boxes.json"):
    converted_data = [{"id": i, "points": box} for i, box in enumerate(boxes)]
    with open(filename, 'w') as f:
        json.dump(converted_data, f, indent=2)
    print(f"Saved {len(boxes)} boxes to {filename}")

# Load ảnh nền
image = cv2.imread("./sample_frames/frame_00.jpg")  # Thay tên ảnh của bạn
clone = image.copy()

cv2.namedWindow("Parking Label Tool")
cv2.setMouseCallback("Parking Label Tool", click_event)

while True:
    temp = draw_boxes(clone)
    cv2.imshow("Parking Label Tool", temp)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break
    elif key == ord('z'):
        if boxes:
            boxes.pop()
            print("Đã xóa bounding box trước đó")
    elif key == ord('s'):
        save_to_json()

""" Click chuột trái: chọn điểm
Nhấn z: xóa bounding box cuối
Nhấn s: lưu file JSON (format chuẩn cho ultralytics)
Nhấn q: thoát """

cv2.destroyAllWindows()
