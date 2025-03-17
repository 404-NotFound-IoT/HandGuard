# HandGuard

# Descripción

HandGuard es un proyecto que utiliza OpenCV, Flask y MediaPipe para la detección de gestos con las manos. Con base en el número de dedos levantados dentro de un área específica de la cámara, se controla el estado de una máquina y se envía la información a un servidor Flask en una Raspberry Pi.

# Requisitos

Python 3.x

OpenCV (cv2)

Flask

Requests

MediaPipe

# Instalación de Dependencias

Ejecuta el siguiente comando para instalar las dependencias necesarias:

pip install opencv-python flask requests mediapipe

Archivos Principales

app.py: Script principal que maneja la detección de manos y el servidor Flask.

manos.py: Contiene la clase Detectormanos para el procesamiento de imágenes y detección de manos.

# Funcionamiento

Se activa la cámara y se detectan las manos en tiempo real con MediaPipe.

Se cuentan los dedos levantados dentro de un área delimitada (cuadro azul).

Se asigna un estado a la máquina según la cantidad de dedos detectados:

0 dedos: Paro de emergencia.

1-4 dedos: Velocidad media activada.

5 dedos: Motor encendido.

Más de 5 dedos: Comando desconocido.

Si el estado es "Paro de emergencia", solo puede cambiar a "Encendido".

El estado se envía a un servidor Flask en la Raspberry Pi mediante requests.post().

Se muestra el video con anotaciones y el estado actual.

Un servidor Flask permite consultar el estado a través de http://<IP>:5001/estado.

El programa muestra los FPS (fotogramas por segundo) en la esquina superior izquierda para monitorear el rendimiento.

# Estructura del Proyecto

El script principal consta de las siguientes secciones:

1. Importación de Bibliotecas

Se importan las bibliotecas necesarias para el procesamiento de imágenes, detección de manos y control del tiempo.

2. Clase Detectormanos

Esta clase encapsula toda la funcionalidad de detección y procesamiento de manos. Contiene los siguientes métodos:

__init__(): Inicializa los parámetros de detección de manos y configuración de MediaPipe.

encontrarmanos(): Detecta las manos en el cuadro de imagen y dibuja los puntos clave.

encontrarposicion(): Encuentra la posición de cada punto clave de la mano y calcula el área delimitadora.

dedosarriba(): Determina cuántos dedos están levantados.

manejar_dedos(): Simula comandos basados en el número de dedos levantados.

3. Función Principal main()

Captura el video en tiempo real desde la cámara y utiliza los métodos de la clase para realizar la detección y simulación de comandos. Muestra la velocidad estimada y permite salir con la tecla Esc.

# Ejecución

Para iniciar el sistema, ejecuta en la terminal:

python app.py

API

GET /estado: Retorna el estado actual de la máquina en formato JSON.

Detener el Programa

Presiona la tecla q en la ventana de OpenCV o Esc para cerrar el programa.

# Notas

Asegúrate de cambiar la dirección IP 192.168.0.100:5000 en el código para que coincida con la de tu Raspberry Pi.

La cámara debe estar bien posicionada para detectar correctamente los gestos.

# Contribuciones

Si deseas contribuir, puedes abrir un Pull Request o reportar problemas en el repositorio.

# Licencia

Este proyecto está bajo la Licencia MIT.

# Autor

Proyecto desarrollado para control de máquinas con visión artificial y detección de gestos.


