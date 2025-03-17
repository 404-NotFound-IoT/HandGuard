import math
import cv2
import mediapipe as mp
import time

class Detectormanos:
    def __init__(self, mode=False, maxManos=2, Confdeteccion=0.5, Confsegui=0.5):
        self.mode = mode
        self.maxManos = maxManos
        self.Confdeteccion = float(Confdeteccion)
        self.Confsegui = float(Confsegui)

        self.mpmanos = mp.solutions.hands
        self.manos = self.mpmanos.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxManos,
            min_detection_confidence=self.Confdeteccion,
            min_tracking_confidence=self.Confsegui
        )
        self.dibujo = mp.solutions.drawing_utils
        self.tip = [4, 8, 12, 16, 20]
        self.resultados = None
        self.lista = []  # Inicializar lista aquí

    def encontrarmanos(self, frame, dibujar=True):
        imgcolor = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.resultados = self.manos.process(imgcolor)

        if self.resultados.multi_hand_landmarks:
            for mano in self.resultados.multi_hand_landmarks:
                if dibujar:
                    self.dibujo.draw_landmarks(frame, mano, self.mpmanos.HAND_CONNECTIONS)
        return frame

    def encontrarposicion(self, frame, dibujar=True):
        xlista = []
        ylista = []
        bboxs = []
        self.lista = []  # Asegúrate de reiniciar la lista cada vez que llames a esta función
        if self.resultados and self.resultados.multi_hand_landmarks:  # Verificar si self.resultados no es None
            for mano in self.resultados.multi_hand_landmarks:
                xlista.clear()
                ylista.clear()
                mano_lista = []
                for id, lm in enumerate(mano.landmark):
                    alto, ancho, c = frame.shape
                    cx, cy = int(lm.x * ancho), int(lm.y * alto)
                    xlista.append(cx)
                    ylista.append(cy)
                    mano_lista.append([id, cx, cy])
                    if dibujar:
                        cv2.circle(frame, (cx, cy), 5, (0, 0, 0), cv2.FILLED)

                if dibujar:
                    xmin, xmax = min(xlista), max(xlista)
                    ymin, ymax = min(ylista), max(ylista)
                    bbox = xmin, ymin, xmax, ymax
                    cv2.rectangle(frame, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)
                    bboxs.append(bbox)
                self.lista.append(mano_lista)

        return self.lista, bboxs

    def dedosarriba(self):
        dedos = []
        if len(self.lista) > 0:
            for mano in self.lista:
                mano_dedos = 0
                if len(mano) > max(self.tip):
                    # Verificamos si el dedo pulgar está levantado
                    if mano[self.tip[0]][2] < mano[self.tip[0] - 1][2]:
                        mano_dedos += 1

                    # Verificamos si los dedos índice, medio, anular y meñique están levantados
                    for id in range(1, 5):
                        if len(mano) > self.tip[id]:
                            if mano[self.tip[id]][2] < mano[self.tip[id] - 2][2]:
                                mano_dedos += 1
                dedos.append(mano_dedos)
        return dedos

    def manejar_dedos(self, total_dedos):
        # Simulación de comandos y velocidad en la consola
        if total_dedos == 0:
            print("No se detectaron dedos levantados.")
            print("Paro de emergencia activado.")
        else:
            velocidad = min(total_dedos, 10)  # Limitar la velocidad a un máximo de 10
            print(f"Velocidad de la banda al {velocidad}")
            if total_dedos == 5:
                print("Comando: Motor encendido.")
            elif total_dedos < 5:
                print("Comando: Velocidad media activada.")
            else:
                print("Comando desconocido.")


def main():
    ptiempo = 0
    ctiempo = 0
    detectando_manos = False  # Inicializar variable para controlar la detección de manos

    cap = cv2.VideoCapture(0)
    detector = Detectormanos()

    while True:
        ret, frame = cap.read()

        if not detectando_manos:
            # Llamar a encontrarposicion para inicializar lista
            detector.encontrarmanos(frame)
            lista, bboxs = detector.encontrarposicion(frame)  # Inicializar lista aquí

            dedos = detector.dedosarriba()
            total_dedos = sum(dedos)

            if total_dedos > 0:  # Si se detecta al menos un dedo, activar la detección de manos
                detectando_manos = True
                print("Detección de manos activada.")

        if detectando_manos:
            frame = detector.encontrarmanos(frame)
            lista, bboxs = detector.encontrarposicion(frame)

            # Contar dedos levantados
            dedos = detector.dedosarriba()
            total_dedos = sum(dedos)

            # Simular el comando basado en el total de dedos levantados
            detector.manejar_dedos(total_dedos)

        ctiempo = time.time()
        fps = 1 / (ctiempo - ptiempo)
        ptiempo = ctiempo

        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("MANOS", frame)
        k = cv2.waitKey(1)

        if k == 27:  # Presionar Esc para salir
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()