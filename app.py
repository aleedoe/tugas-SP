from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)  # Perbaikan dari 'name' ke '__name__'
CORS(app)

# Konfigurasi koneksi database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'sistem_pakar'
}

# Fungsi untuk mendapatkan koneksi database
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Endpoint untuk mendapatkan data gejala
@app.route('/gejala', methods=['GET'])
def get_gejala():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, kode, deskripsi FROM gejala")
    result = cursor.fetchall()
    conn.close()
    return jsonify(result)

# Endpoint untuk proses diagnosa
@app.route('/diagnosa', methods=['POST'])
def diagnosa():
    data = request.json
    selected_gejala_ids = data.get('gejala', [])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.kode AS kode_aturan, a.id_penyakit, p.kode AS kode_penyakit, p.nama, a.id_gejala
        FROM aturan a
        JOIN penyakit p ON a.id_penyakit = p.id
    """)
    aturan = cursor.fetchall()
    conn.close()

    # Memetakan aturan berdasarkan kode aturan
    aturan_map = {}
    for row in aturan:
        kode = row['kode_aturan']
        if kode not in aturan_map:
            aturan_map[kode] = {
                'penyakit': row['nama'],
                'kode_penyakit': row['kode_penyakit'],
                'gejala': set()
            }
        aturan_map[kode]['gejala'].add(row['id_gejala'])

    # Mencari hasil diagnosa yang cocok
    hasil = None
    input_set = set(selected_gejala_ids)
    for rule in aturan_map.values():
        if rule['gejala'] == input_set:
            hasil = rule
            break

    if hasil:
        return jsonify({
            'penyakit': f"{hasil['kode_penyakit']} - {hasil['penyakit']}",
            'solusi': 'Silakan lakukan tindakan pengendalian.'
        })
    else:
        return jsonify({
            'penyakit': 'Tidak Diketahui',
            'solusi': 'Data tidak cocok dengan basis pengetahuan.'
        })

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)
