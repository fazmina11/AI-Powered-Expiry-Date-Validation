
"""
Simple webcam test to verify OpenCV GUI works
"""
import cv2

print("Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam!")
    exit(1)

print("Webcam opened! Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Could not read frame!")
        break
    
    cv2.imshow("Webcam Test", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
for _ in range(5):
    cv2.waitKey(1)

print("Done!")
