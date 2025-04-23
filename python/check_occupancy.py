import cv2
from ultralytics import solutions

# Đường dẫn tới video và model
video_path = "./videos/yt1s.com - BLKHDPTZ12 Security Camera Parkng Lot Surveillance Video_360P.mp4"
model_path = "./best.pt"  # Model YOLO bạn đã train
json_path = "./parking_boxes.json"  # File chứa các bounding box của vị trí đỗ xe

# Mở video
cap = cv2.VideoCapture(video_path)
assert cap.isOpened(), "Không thể mở video."

# Lấy thông tin video để ghi output
w, h, fps = (int(cap.get(x)) for x in (
    cv2.CAP_PROP_FRAME_WIDTH,
    cv2.CAP_PROP_FRAME_HEIGHT,
    cv2.CAP_PROP_FPS
))
out = cv2.VideoWriter("output_parking_management.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Tạo đối tượng quản lý bãi đỗ xe
parkingmanager = solutions.ParkingManagement(
    model=model_path,
    json_file=json_path
)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Xử lý frame bằng parking manager
    results = parkingmanager(frame)

    # Frame sau khi được xử lý đã có overlay trạng thái occupancy
    processed_frame = results.plot_im

    # Hiển thị
    cv2.imshow("Parking Status", processed_frame)

    # Ghi ra video
    out.write(processed_frame)

    # Nhấn Q để thoát sớm
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Dọn dẹp
cap.release()
out.release()
cv2.destroyAllWindows()
