from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from ultralytics import YOLO
import cv2
import numpy as np
import json
from fastapi.responses import RedirectResponse


app = FastAPI()

class ParkingLot:
    
# load model và video    
    def __init__(self, video_path, model_path, json_path):
        self.video_path = video_path
        self.model_path = model_path
        self.json_path = json_path
        self.cap = cv2.VideoCapture(video_path)
        assert self.cap.isOpened(), f"Không thể mở video: {video_path}"
        self.model = YOLO(model_path)
        self.parking_zones = self.load_zones(json_path)
        self.streaming = False

# đọc danh sách các vùng đỗ xe từ file JSON
    def load_zones(self, path):
        with open(path, "r") as f:
            data = json.load(f)
            return [zone["points"] for zone in data]

# reset video capture để bắt đầu lại từ đầu
    def reset(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.video_path)

# hàm kiểm tra xem xe có nằm trong vùng đỗ hay không
    def is_car_in_zone(self, detection_box, zone_polygon):
        x1, y1, x2, y2 = detection_box
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        result = cv2.pointPolygonTest(np.array(zone_polygon, np.int32), (center_x, center_y), False)
        return result >= 0

# xử lý từng frame của video, phát hiện xe và vẽ vùng đỗ
    def process_frame(self, frame):
        results = self.model(frame)
        detections = results[0].boxes.xyxy.cpu().numpy()

        occupied_count = 0
        empty_count = 0

# kiểm tra từng vùng đỗ xe với các phát hiện
        for zone in self.parking_zones:
            is_occupied = False
            for det in detections:
                if self.is_car_in_zone(det, zone):
                    is_occupied = True
                    break

# vẽ vùng đỗ xe trên frame, xanh là trống, đỏ là có xe, và đếm số lượng
            color = (0, 0, 255) if is_occupied else (0, 255, 0)
            if is_occupied:
                occupied_count += 1
            else:
                empty_count += 1

            pts = np.array(zone, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=2)

# hiển thị số lượng vị trí trống và có xe trong bãi đỗ
        cv2.putText(frame, f"Empty: {empty_count} | Occupied: {occupied_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
        return frame

# cấu hình video, model và file Json vị trí đỗ 
lots = {
    "lot1": ParkingLot(
        "D:/spacedetection/space_detection/videos/yt1s.com - BLKHDPTZ12 Security Camera Parkng Lot Surveillance Video_360P.mp4",
        "D:/spacedetection/space_detection/best.pt",
        "D:/spacedetection/space_detection/parking_boxes.json"
    ),
    "lot2": ParkingLot(
        "D:/spacedetection/space_detection/videos/videoplayback.mp4",
        "D:/spacedetection/space_detection/best2.pt",
        "D:/spacedetection/space_detection/parking_boxes2.json"
    )
}

current_lot = "lot1"

@app.get("/", response_class=HTMLResponse)
def index():
    return """
 <html>
        <head>
            <title>Giám sát bãi đỗ xe</title>
            <style>
                body { text-align: center; font-family: sans-serif; padding: 20px; }
                .button-container {
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                button {
                    padding: 10px 20px;
                    font-size: 16px;
                    border-radius: 5px;
                    border: none;
                    background-color: #3498db;
                    color: white;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
                button:hover {
                    background-color: #2980b9;
                }
                img {
                    border: 2px solid black;
                    border-radius: 10px;
                    margin-top: 20px;
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <h1>🚗 Hệ thống Giám sát Bãi đỗ xe</h1>
            <div class="button-container">
                <form action="/switch_lot/lot1" method="post">
                    <button type="submit">Bãi số 1</button>
                </form>
                <form action="/switch_lot/lot2" method="post">
                    <button type="submit">Bãi số 2</button>
                </form>
                <form action="/stop_stream" method="post">
                    <button type="submit">⏹ Dừng</button>
                </form>
            </div>
            <img src="/video_feed" width="720" height="480" />
        </body>
    </html>
    """

@app.get("/video_feed")
def video_feed():
    def gen_frames(lot):
        frame_id = 0
        while lot.streaming:
            success, frame = lot.cap.read()
            if not success:
                break
            frame_id += 1
            if frame_id % 3 != 0:
                continue
            frame = lot.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

    lots[current_lot].streaming = True
    return StreamingResponse(
        gen_frames(lots[current_lot]),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/switch_lot/{lot_id}")
def switch_lot(lot_id: str):
    global current_lot
    if lot_id not in lots:
        return {"error": "Bãi không tồn tại."}
    
    lots[current_lot].streaming = False
    current_lot = lot_id
    lots[current_lot].reset()
    lots[current_lot].streaming = True
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop_stream")
def stop_stream():
    lots[current_lot].streaming = False
    return {"message": "Đã dừng stream."}