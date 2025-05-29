import cv2
import os

# Mở video
video_path = "./videos/videoplayback.mp4"
cap = cv2.VideoCapture(video_path)

# Thư mục lưu ảnh
output_folder = "./sample_frames"
os.makedirs(output_folder, exist_ok=True)

fps = int(cap.get(cv2.CAP_PROP_FPS))  # Frame per second
print("FPS:", fps)

for second in range(10):  # 10 giây đầu
    frame_number = second * fps
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)  # Di chuyển tới frame ở giây tương ứng
    ret, frame = cap.read()
    if not ret:
        print(f"Không đọc được frame tại giây {second}")
        continue

    resized_frame = cv2.resize(frame, (854, 480))  # resize chuẩn 640x360
    filename = os.path.join(output_folder, f"frame_{second:02d}.jpg")
    cv2.imwrite(filename, resized_frame)
    print(f"Saved: {filename}")

cap.release()
print("Done!")
