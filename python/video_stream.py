from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from ultralytics import solutions
import cv2

app = FastAPI()

# Đường dẫn video, model YOLO và file JSON vùng đỗ xe
video_path = "D:/spacedetection/space_detection/videos/yt1s.com - BLKHDPTZ12 Security Camera Parkng Lot Surveillance Video_360P.mp4"
model_path = "D:/spacedetection/space_detection/best.pt"
json_path = "D:/spacedetection/space_detection/parking_boxes.json"

streaming = True
cap = cv2.VideoCapture(video_path)
assert cap.isOpened(), "Không thể mở video."

parkingmanager = solutions.ParkingManagement(
    model=model_path,
    json_file=json_path
)

def reset_video():
    global cap
    cap.release()
    cap = cv2.VideoCapture(video_path)

def gen_frames():
    global streaming
    while streaming:
        success, frame = cap.read()
        if not success:
            break
        results = parkingmanager(frame)
        processed_frame = results.plot_im
        _, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>Quản lý Bãi đỗ xe</title>
            <style>
                body {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    background-color: #f4f4f4;
                    font-family: Arial, sans-serif;
                }
                img {
                    border: 2px solid #444;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
                form {
                    display: inline-block;
                    margin: 0 10px;
                }
                button {
                    padding: 10px 20px;
                    font-size: 16px;
                    border: none;
                    border-radius: 5px;
                    background-color: #007bff;
                    color: white;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>📹 Giám sát Bãi đỗ xe</h1>
            <img src="/video_feed" width="720" height="480" />
            <div>
                <form action="/stop_stream" method="post">
                    <button type="submit">⏹ Dừng video</button>
                </form>
                <form action="/restart_stream" method="post">
                    <button type="submit">▶️ Phát lại</button>
                </form>
            </div>
        </body>
    </html>
    """

@app.get("/video_feed")
def video_feed():
    global streaming
    streaming = True
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/stop_stream")
def stop_stream():
    global streaming
    streaming = False
    return {"message": "Video đã dừng."}

@app.post("/restart_stream")
def restart_stream():
    global streaming
    reset_video()
    streaming = True
    return {"message": "Video đã phát lại."}
