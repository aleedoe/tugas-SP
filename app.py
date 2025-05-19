from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Koneksi ke database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sistem_pakar"
)
cursor = db.cursor(dictionary=True)

@app.route("/gejala", methods=["GET"])
def get_gejala():
    cursor.execute("SELECT id, kode, deskripsi FROM gejala")
    return jsonify(cursor.fetchall())

@app.route("/diagnosa", methods=["POST"])
def diagnosa():
    data = request.get_json()
    gejala_input = data.get("gejala", [])  # Expecting list of gejala IDs (int)

    # Ambil semua penyakit
    cursor.execute("SELECT * FROM penyakit")
    penyakit_list = cursor.fetchall()

    for penyakit in penyakit_list:
        cursor.execute("SELECT id_gejala FROM aturan WHERE id_penyakit = %s", (penyakit['id'],))
        rows = cursor.fetchall()
        gejala_db = [row['id_gejala'] for row in rows]

        if set(gejala_db).issubset(set(gejala_input)):
            return jsonify({
                "penyakit": penyakit["nama"],
                "solusi": penyakit["solusi"]
            })

    return jsonify({"penyakit": "Tidak diketahui", "solusi": "Silakan konsultasikan dengan pakar."})

if __name__ == "__main__":
    app.run(debug=True)