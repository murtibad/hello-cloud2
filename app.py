from flask import Flask, render_template_string, request
import os, psycopg2

app = Flask(__name__)  # <- DÜZELTİLDİ

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://murat:yE9n7WzbEIA3aVR3M1U5yvJ6ED6DfcWo@dpg-d3tjfl2li9vc73befqjg-a.oregon-postgres.render.com/hello_cloud2_db_qtdv")

HTML = """
<!doctype html>
<html>
<head>
<title>Buluttan Selam</title>
<style>
    body {font-family: Arial; text-align: center; padding: 50px; background: #eef2f3;}
    h1 { color: #333; }
    form { margin: 20px auto; }
    input { margin: 10px; font-size: 16px; }
    button { padding:10px 15px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; }
    ul { list-style: none; padding: 0; }
    li { background: white; margin: 5px auto; width: 200px; padding:8px; border-radius: 5px; }
</style>
</head>
<body>
    <h1>Buluttan Selam</h1>
    <p>adını yaz , selamını bırak</p>
    <form method="POST">
        <input type="text" name="isim" placeholder="Adını yaz" required>
        <button type="submit">Gönder</button>
    </form>
    <h3>Ziyaretçiler</h3>
    <ul>
        {% for ad in isimler %}
            <li>{{ ad }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

def connect_db():
    if not DATABASE_URL:
        # Render’da ortam değişkeni yoksa 500 yerine açık hata döndürelim
        raise RuntimeError("DATABASE_URL tanımlı değil.")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS ziyaretciler (id SERIAL PRIMARY KEY, isim TEXT NOT NULL)")

# 🔒 gunicorn’da __main__ çalışmadığı için tabloyu ilk istekten önce oluştur
@app.before_first_request
def _ensure_db():
    init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    with connect_db() as conn:
        with conn.cursor() as cur:
            if request.method == "POST":
                isim = (request.form.get("isim") or "").strip()
                if isim:
                    cur.execute("INSERT INTO ziyaretciler (isim) VALUES (%s)", (isim,))
            cur.execute("SELECT isim FROM ziyaretciler ORDER BY id DESC LIMIT 10")
            isimler = [row[0] for row in cur.fetchall()]
    return render_template_string(HTML, isimler=isimler)

if __name__ == "__main__":  # <- DÜZELTİLDİ
    app.run(host="0.0.0.0", port=5000)
