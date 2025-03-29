from flask import Flask, request, jsonify, render_template
import RPi.GPIO as gpio
import sqlite3
from datetime import datetime

# Configuración de los pines GPIO
gpio.setmode(gpio.BCM)

verde_encendido = 4
amarillo_paro = 18
rojo_emergencia = 23

gpio.setup(verde_encendido, gpio.OUT)
gpio.setup(amarillo_paro, gpio.OUT)
gpio.setup(rojo_emergencia, gpio.OUT)

app = Flask(__name__)

# Variable global para almacenar el último estado recibido
ultimo_estado = "Esperando comando"

# Función para actualizar los LEDs según el estado
def actualizar_leds(estado):
    estado = estado.lower()  # Convertir a minúsculas para evitar errores

    if estado == "encendido":
        gpio.output(verde_encendido, gpio.HIGH)
        gpio.output(amarillo_paro, gpio.LOW)
        gpio.output(rojo_emergencia, gpio.LOW)

    elif estado == "paro":
        gpio.output(verde_encendido, gpio.LOW)
        gpio.output(amarillo_paro, gpio.HIGH)
        gpio.output(rojo_emergencia, gpio.LOW)

    elif estado == "paro de emergencia":
        gpio.output(verde_encendido, gpio.LOW)
        gpio.output(amarillo_paro, gpio.LOW)
        gpio.output(rojo_emergencia, gpio.HIGH)

    elif estado == "esperando comando":
        gpio.output(verde_encendido, gpio.LOW)
        gpio.output(amarillo_paro, gpio.LOW)
        gpio.output(rojo_emergencia, gpio.LOW)

    else:
        print("⚠ Estado no reconocido. Activando paro de emergencia por seguridad.")
        gpio.output(verde_encendido, gpio.LOW)
        gpio.output(amarillo_paro, gpio.LOW)
        gpio.output(rojo_emergencia, gpio.HIGH)

# Conexión a la base de datos
def conectar_db():
    conn = sqlite3.connect('registro_estados.db')
    return conn

# Crear tabla de comandos si no existe
def crear_tabla():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS comandos
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       estado TEXT,
                       fecha_hora TEXT)''')
    conn.commit()
    conn.close()

crear_tabla()

# Ruta para recibir el estado de la máquina
@app.route('/actualizar_estado', methods=['POST'])
def recibir_estado():
    global ultimo_estado
    if request.method == 'POST':
        datos = request.json
        nuevo_estado = datos.get('estado', "Esperando comando")  # Valor por defecto

        # Verificar si el estado es válido antes de actualizar
        estados_validos = ["encendido", "paro", "paro de emergencia", "esperando comando"]
        if nuevo_estado.lower() not in estados_validos:
            nuevo_estado = "paro de emergencia"  # Fallback de seguridad

        ultimo_estado = nuevo_estado
        actualizar_leds(ultimo_estado)  # Controla los LEDs

        # Registrar en la base de datos
        conn = conectar_db()
        cursor = conn.cursor()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO comandos (estado, fecha_hora) VALUES (?, ?)", (ultimo_estado, fecha_hora))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "nuevo_estado": ultimo_estado}), 200

# Ruta para obtener el estado actual en JSON
@app.route('/estado_actual')
def estado_actual():
    return jsonify({'estado': ultimo_estado})

# Ruta para obtener los registros de comandos
@app.route('/registros')
def registros():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, estado, fecha_hora FROM comandos")
    registros = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "estado": r[1], "fecha_hora": r[2]} for r in registros])

# Nueva ruta para filtrar registros según el estado seleccionado
@app.route('/filtrar_registros')
def filtrar_registros():
    estado_filtro = request.args.get('estado', '')

    conn = conectar_db()
    cursor = conn.cursor()

    if estado_filtro:
        cursor.execute("SELECT id, estado, fecha_hora FROM comandos WHERE estado = ?", (estado_filtro,))
    else:
        cursor.execute("SELECT id, estado, fecha_hora FROM comandos")

    registros = cursor.fetchall()
    conn.close()

    return jsonify([{"id": r[0], "estado": r[1], "fecha_hora": r[2]} for r in registros])

# Página HTML principal
@app.route('/')
def index():
    return render_template('index.html', ultimo_estado=ultimo_estado)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Apagando LEDs y cerrando servidor...")
        gpio.cleanup()  # Apagar los LEDs al salir