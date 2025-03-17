# HandGuard
Descripción

Este proyecto utiliza OpenCV, Flask y la librería Mediapipe para detectar gestos con las manos y controlar el estado de una máquina en función del número de dedos levantados dentro de un área específica de la cámara.

Requisitos

Python 3.x

OpenCV (cv2)

Flask

Requests

Mediapipe (para la detección de manos)

Instalación de Dependencias

Ejecuta el siguiente comando para instalar las dependencias necesarias:

pip install opencv-python flask requests mediapipe

Archivos Principales

app.py: Script principal que maneja la detección de manos y el servidor Flask.

manos.py: Contiene la clase Detectormanos para el procesamiento de imágenes y detección de manos.

Funcionamiento

Se inicia la cámara y se detectan las manos usando Mediapipe.

Se cuenta el número de dedos levantados dentro de un área específica (cuadro azul).

Se asigna un estado a la máquina según la cantidad de dedos detectados:

10 dedos → Encendido

5 dedos → Paro

2 dedos → Paro de emergencia

Si el estado es "Paro de emergencia", solo puede cambiar a "Encendido".

El estado se envía a un servidor Flask en la Raspberry Pi mediante requests.post().

Se muestra el video con anotaciones y el estado actual.

Un servidor Flask permite consultar el estado a través de http://<IP>:5001/estado.

Ejecución

Ejecuta el siguiente comando en la terminal:

python app.py

API

GET /estado: Retorna el estado actual de la máquina en formato JSON.

Detener el Programa

Presiona la tecla q en la ventana de OpenCV para cerrar el programa.

Notas

Asegúrate de cambiar la dirección IP 192.168.0.100:5000 en el código para que coincida con la de tu Raspberry Pi.

La cámara debe estar bien posicionada para detectar correctamente los gestos.

Autor

Proyecto desarrollado para control de máquinas con visión artificial y detección de gestos.

