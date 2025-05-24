from flask import Flask, request, jsonify
from flask import send_from_directory
import os
import uuid
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging

app = Flask(__name__)

# Crear carpeta de uploads/audios si no existe.
UPLOAD_AUDIOS_FOLDER = './uploads/audios'
os.makedirs(UPLOAD_AUDIOS_FOLDER, exist_ok=True)

app.config['UPLOAD_AUDIOS_FOLDER'] = UPLOAD_AUDIOS_FOLDER

# Crear carpeta de logs si no existe
LOG_FOLDER = './logs'
os.makedirs(LOG_FOLDER, exist_ok=True)


# Configurar logging
logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, 'app.log'),
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Conexion a la base de datos (ajusta los valores a tu entorno)
def get_db_connection():
    return mysql.connector.connect(
        host='mysql',
        user='root',
        password='admin',
        database='latidoapp',
        port=3306
    )

@app.route("/")
def helloworld():
    return "Hola Mundo!"

@app.route('/api/mediciones', methods=['POST'])
def registrar_medicion():
    if 'audio' not in request.files or 'nombres' not in request.form:

        return jsonify({"error": "Faltan campos obligatorios."}), 400

    archivo_audio = request.files['audio']
    nombres = request.form['nombres']

    if archivo_audio.filename == '':
        return jsonify({"error": "Nombre de audio vacío es requerido"}), 400

    # Guardar archivo audio
    nombre_audio = f"{uuid.uuid4().hex}_{archivo_audio.filename}"
    ruta_archivo_audio = os.path.join(app.config['UPLOAD_AUDIOS_FOLDER'], nombre_audio)
    archivo_audio.save(ruta_archivo_audio)

    # Insertar en tabla 'mediciones'
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO mediciones (nombres, fecha, audio_nombre)
            VALUES (%s, %s, %s)
        """, (nombres, fecha_actual, nombre_audio))
        conn.commit()
        id_medicion = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            "status": "recibido",
            "mensaje": "Medición registrada correctamente.",
            "id_medicion": id_medicion,
            "audio": nombre_audio,
            "success": True
        }), 202


    except Error as e:
        # Guardar error en el archivo de logs
        logging.error(f"Ocurrió un error al registrar la medición a la base de datos:  (Error): {str(e)}")

        # Eliminar el audio.
        if os.path.exists(ruta_archivo_audio):
            os.remove(ruta_archivo_audio)
        else:
            logging.error(f"No se encontró el archivo para eliminar: {ruta_archivo_audio}")

        return jsonify({
            "error": "Ocurrió un error al hacer el registro en la base de datos."
        }), 500

    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass  # en caso de que no se hayan creado correctamente

# Este metodo 'servir_archivo' es necesario para poder visualizar las imagenes o escuchar los audios.
@app.route('/api/uploads/<tipo>/<filename>')
def servir_archivo(tipo, filename):
    if tipo == 'audios':
        carpeta = app.config['UPLOAD_AUDIOS_FOLDER']
    else:
        return jsonify({"error": "Tipo de archivo no permitido"}), 400

    return send_from_directory(carpeta, filename)


@app.route('/api/mediciones', methods=['GET'])
def obtener_mediciones():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT m.nombres, m.fecha, m.audio_nombre
            FROM mediciones m
            ORDER BY m.fecha DESC
            LIMIT 20
        """)

        resultados = cursor.fetchall()

        # Agregar URL de los archivos
        for r in resultados:
            r['url_audio'] = f"/uploads/audios/{r['audio_nombre']}"

        return jsonify({
            "result": resultados,
            "total": len(resultados)
        })

    except Error as e:
        # Log opcional: print(f"Error en la base de datos: {e}")

        # Guardar error en el archivo de logs
        logging.error(f"Ocurrió un error al consultar la base de datos:  (Error): {str(e)}")

        return jsonify({
            "error": "Ocurrió un error al consultar la base de datos."
        }), 500

    finally:
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except:
            pass  # en caso de que no se hayan creado correctamente

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
