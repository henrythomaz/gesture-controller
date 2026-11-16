import math
import time
import pyautogui


# Configurações de segurança e desempenho
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0


# Verifica se um dedo está levantado.
def is_finger_up(hand, tip, pip):

    return hand[tip].y < hand[pip].y


# Calcula a distância entre dois landmarks.
def calculate_distance(point_a, point_b):

    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y

    return math.hypot(dx, dy)


# Limita um valor entre mínimo e máximo.
def clamp(value, minimum, maximum):

    return max(minimum, min(value, maximum))


class MouseMove:

    def __init__(self, smoothing=0.30):

        self.screen_width, self.screen_height = pyautogui.size()

        self.smoothing = smoothing

        self.previous_x = None
        self.previous_y = None

    def update(self, hand):

        index_up = is_finger_up(hand, 8, 6)
        middle_up = is_finger_up(hand, 12, 10)
        ring_up = is_finger_up(hand, 16, 14)
        pinky_up = is_finger_up(hand, 20, 18)

        # Gesto: somente o indicador levantado.
        pointing = (
            index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        )

        if not pointing:
            return

        # Posição atual da ponta do indicador.
        index = hand[8]

        # Criar uma margem para facilitar o controle.
        margin = 0.08

        normalized_x = clamp(
            (index.x - margin) / (1 - 2 * margin),
            0,
            1
        )

        normalized_y = clamp(
            (index.y - margin) / (1 - 2 * margin),
            0,
            1
        )

        # Converter coordenadas normalizadas em pixels da tela.
        target_x = normalized_x * (self.screen_width - 1)
        target_y = normalized_y * (self.screen_height - 1)

        # Inicializar a posição suavizada.
        if self.previous_x is None:

            self.previous_x = target_x
            self.previous_y = target_y

        else:

            self.previous_x += (
                target_x - self.previous_x
            ) * self.smoothing

            self.previous_y += (
                target_y - self.previous_y
            ) * self.smoothing

        # Movimentar o cursor.
        pyautogui.moveTo(
            int(self.previous_x),
            int(self.previous_y)
        )

    def reset(self):

        self.previous_x = None
        self.previous_y = None


class PinchClick:

    def __init__(self, threshold=0.045, cooldown=0.35):

        self.threshold = threshold
        self.cooldown = cooldown

        self.left_was_pinched = False
        self.right_was_pinched = False

        self.last_left_click = 0
        self.last_right_click = 0

    def update(self, hand):

        thumb = hand[4]
        index = hand[8]
        middle = hand[12]

        # Identificar as pinças.
        left_pinched = (
            calculate_distance(thumb, index)
            < self.threshold
        )

        right_pinched = (
            calculate_distance(thumb, middle)
            < self.threshold
            and not left_pinched
        )

        now = time.monotonic()

        # Clique esquerdo: somente quando a pinça começa.
        if (
            left_pinched
            and not self.left_was_pinched
            and now - self.last_left_click >= self.cooldown
        ):

            pyautogui.click()

            self.last_left_click = now

        # Clique direito.
        if (
            right_pinched
            and not self.right_was_pinched
            and now - self.last_right_click >= self.cooldown
        ):

            pyautogui.click(button="right")

            self.last_right_click = now

        # Guardar o estado atual.
        self.left_was_pinched = left_pinched
        self.right_was_pinched = right_pinched

    def reset(self):

        self.left_was_pinched = False
        self.right_was_pinched = False

class Scroll:

    def __init__(self, sensitivity=150):

        self.sensitivity = sensitivity

        self.previous_y = None
        self.accumulator = 0

    def update(self, hand):

        # Verificar os dedos levantados.
        index_up = is_finger_up(hand, 8, 6)
        middle_up = is_finger_up(hand, 12, 10)
        ring_up = is_finger_up(hand, 16, 14)
        pinky_up = is_finger_up(hand, 20, 18)

        # Gesto que ativa o scroll.
        scrolling = (
            index_up
            and middle_up
            and not ring_up
            and not pinky_up
        )

        # Se o gesto não estiver ativo, reiniciar.
        if not scrolling:

            self.reset()
            return

        # Calcular a posição vertical média dos dedos.
        current_y = (
            hand[8].y + hand[12].y
        ) / 2

        # Na primeira leitura, apenas registrar a posição.
        if self.previous_y is None:

            self.previous_y = current_y
            return

        # Calcular a diferença entre os frames.
        delta = self.previous_y - current_y

        # Acumular o movimento.
        self.accumulator += delta * self.sensitivity

        # Converter para um número inteiro.
        amount = int(self.accumulator)

        # Executar o scroll.
        if amount != 0:

            pyautogui.scroll(amount)

            # Remover do acumulador o movimento consumido.
            self.accumulator -= amount

        # Atualizar a posição anterior.
        self.previous_y = current_y

    def reset(self):

        self.previous_y = None
        self.accumulator = 0

