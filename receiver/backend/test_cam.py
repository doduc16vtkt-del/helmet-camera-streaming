import cv2

# Mở camera mặc định (ID 0) với backend MSMF (Windows)
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

if not cap.isOpened():
    print("❌ Không mở được camera")
    exit()

print("✅ Camera đã mở")
print("Nhấn phím Q để thoát")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Không đọc được frame")
        break

    cv2.imshow("Camera", frame)

    # Nhấn Q hoặc q để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("👋 Đã thoát camera")
