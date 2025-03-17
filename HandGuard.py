import cv2
import threading
import requests
from flask import Flask, jsonify
from Manos import Detectormanos

app = Flask(__name__)
detector = Detectormanos()

cap = cv2.VideoCapture(0)

# Estado de la máquina (inicial)
estado_maquina = {"estado": "Esperando comando"}

# Área específica (Cuadro Azul)
alto_frame, ancho_frame = 480, 640
cuadro_ancho, cuadro_alto = 400, 300
cuadro_x = (ancho_frame - cuadro_ancho) // 2
cuadro_y = (alto_frame - cuadro_alto) // 2

estado_anterior = "Esperando comando"

def procesar_video():
    global estado_maquina, estado_anterior

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Voltear la imagen para mayor naturalidad y procesar la detección
        frame = cv2.flip(frame, 1)
        frame = detector.encontrarmanos(frame)
        lista, bboxs = detector.encontrarposicion(frame, dibujar=False)

        dedos_izquierda = 0
        dedos_derecha = 0
        total_dedos = 0

        if detector.resultados.multi_hand_landmarks:
            for idx, mano in enumerate(detector.resultados.multi_hand_landmarks):
                hand_type = detector.resultados.multi_handedness[idx].classification[0].label
                dedos = detector.dedosarriba()

                # Coordenadas de la mano
                mano_x = int(mano.landmark[0].x * frame.shape[1])
                mano_y = int(mano.landmark[0].y * frame.shape[0])

                # Verificar si la mano está dentro del área específica (cuadro azul)
                if cuadro_x <= mano_x <= cuadro_x + cuadro_ancho and cuadro_y <= mano_y <= cuadro_y + cuadro_alto:
                    if hand_type == "Left":
                        dedos_izquierda += dedos[idx]
                    elif hand_type == "Right":
                        dedos_derecha += dedos[idx]

            total_dedos = dedos_izquierda + dedos_derecha

            # Lógica de detección basada en el número de dedos
            if total_dedos == 10:
                nuevo_estado = "Encendido"
            elif total_dedos == 5:
                nuevo_estado = "Paro"
            elif total_dedos == 2:
                nuevo_estado = "Paro de emergencia"
            else:
                nuevo_estado = estado_anterior
        else:
            nuevo_estado = estado_anterior  # Si no hay detección, se mantiene el estado anterior

        # Si el estado actual es "Paro de emergencia", solo se permite cambiar a "Encendido"
        if estado_anterior == "Paro de emergencia" and nuevo_estado != "Encendido":
            nuevo_estado = "Paro de emergencia"

        estado_anterior = nuevo_estado
        estado_maquina = {"estado": estado_anterior}

        # Enviar el estado actualizado al servidor en la Raspberry Pi
        try:
            requests.post("http://192.168.0.100:5000/actualizar_estado", json={"estado": estado_anterior})
        except Exception as e:
            print("Error al enviar el estado:", e)

        # Dibujar el cuadro azul y el estado en el frame
        cv2.rectangle(frame, (cuadro_x, cuadro_y), (cuadro_x + cuadro_ancho, cuadro_y + cuadro_alto), (255, 0, 0), 2)
        cv2.putText(frame, f'Stado: {estado_anterior}', (cuadro_x + 10, cuadro_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        print(f'Estado actual de la máquina: {estado_anterior}')
        cv2.imshow('Conteo de Dedos', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/estado', methods=['GET'])
def obtener_estado():
    return jsonify(estado_maquina)

# Iniciar el procesamiento de video en un hilo separado
threading.Thread(target=procesar_video, daemon=True).start()

if __name__ == '__main__':
    print("Iniciando Flask...")
    app.run(host='0.0.0.0', port=5001, debug=True)
