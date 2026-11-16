import cv2
import mediapipe as mp
import time
import pyautogui

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from features import MouseMove, PinchClick, Scroll

# Configurações

PROJECT_DIR = Path(__file__).resolve().parent

MODEL_PATH = PROJECT_DIR / "models" / "hand_landmarker.task"

CAMERA_ID = 0
MAX_HANDS = 2

# Conexões entre os 21 pontos da mão

CONNECTIONS = [
        (0, 1), (1, 2), (1, 5), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
        ]

# inicializar o detector

def create_landmarker():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
                f"Modelo não encontrado: {MODEL_PATH}"
                )
    base_options = python.BaseOptions(
            model_asset_path=str(MODEL_PATH)
            )

    options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=MAX_HANDS
            )
    detector = vision.HandLandmarker.create_from_options(
            options
            )
    return detector

# processar a imagem

def detect_hands(frame, detector, timestamp_ms):
    #OpenCV utiliza BGR; MediaPipe recebe RGB.

    rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
            )
    
    # Converter para o formato de imagem do MediaPipe.
    mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
            )
    # executar a detecção
    result = detector.detect_for_video(
            mp_image,
            timestamp_ms
            )

    return result

# Desenha os landmarks

def draw_landmarks(frame, result):

    height, width, _ = frame.shape

    for hand in result.hand_landmarks:

        # Converter coordenadas normalizadas em pixels.
        points = []

        for landmark in hand:
    
            x = int(landmark.x * width)
            y = int(landmark.y * height)

            points.append((x, y))

        # Desenhar as conexões.
        for start, end in CONNECTIONS:

            cv2.line(frame, points[start], points[end], (0, 255, 0), 2)

        # Desenhar os pontos.
        for point in points:

            cv2.circle(frame, point, 5, (0, 0, 255), -1)

    return frame

def main():

    detector = create_landmarker()

    # Configurações das funcionalidades.

    ENABLE_MOUSE_MOVE = True
    ENABLE_CLICK = True
    ENABLE_SCROLL = True

    features = []

    if ENABLE_MOUSE_MOVE:
        features.append(MouseMove(smoothing=0.30))

    if ENABLE_CLICK:
        features.append(PinchClick())

    if ENABLE_SCROLL:
        features.append(Scroll())

    camera = cv2.VideoCapture(CAMERA_ID)

    try:
        if not camera.isOpened():
            raise RuntimeError("Não foi possivel abrir a câmera.")

        while True:
            # Capturar um frame.
            sucess, frame = camera.read()

            if not sucess:
                break

            # espelhar a imagem
            frame = cv2.flip(frame, 1)

            # Timestamp em milisegundos.
            timestamp_ms = time.monotonic_ns() // 1_000_000

            # detectar as mãos.
            result = detect_hands(
                frame,
                detector,
                timestamp_ms
                )
            
            if result.hand_landmarks:

                # Utilizar a primeira mão detectada.
                hand = result.hand_landmarks[0]

                # Executar cada funcionalidade.
                for feature in features:

                    feature.update(hand)

            else:

                # Limpar os estados quando a mão desaparecer.
                for feature in features:

                    feature.reset()

            # Desenhar os pontos encontrados.
            frame = draw_landmarks( frame, result )

            # Mostrar a quantidade de mãos.
            cv2.putText( frame, f"Maos: {len(result.hand_landmarks)}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("MediaPipe - Hand Landmarker", frame)

            # Precionar Q para sair
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        detector.close()

if __name__ == "__main__":
    main()



# hand = result.hand_landmarks[0]
#
# wrist = hand[0]
# thumb_tip = hand[4]
# index_tip = hand[8]
# middle_tip = hand[12]
# ring_tip = hand[16]
# pinky_tip = hand[26]
#
# print(index_tip.x, index_tip.y, index_tip.z)
