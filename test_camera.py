import cv2
import mediapipe as mp

camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    if not success:
        print("Erro ao capturar imagem.")
        break

    cv2.imshow("Teste da webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
