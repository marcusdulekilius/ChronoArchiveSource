from flask import Flask, render_template, request
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# SQLite database
def initialize_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )''')
    conn.commit()
    conn.close()

initialize_database()

# API ve CSE
API_KEY = 'your-api-key'
CSE_ID = 'your-cse-id'

def internet_cevap(soru):
    try:
        # Google Custom Search API isteği
        params = {
            'key': API_KEY,
            'cx': CSE_ID,
            'q': soru,
            'num': 1  # 1 in 14.000.605
        }
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            # İlk sonucu al
            first_result = data['items'][0]
            title = first_result.get('title', 'Başlık bulunamadı')
            snippet = first_result.get('snippet', 'Açıklama bulunamadı')
            link = first_result.get('link', '#')
            return f"\n\n{snippet}\n\nDetaylı bilgi için: {link}"
        else:
            return "Üzgünüm, bu konuda bilgim yok."
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return "Üzgünüm, bu konuda bilgim yok."

def insert_question_answer(question, answer):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        soru = request.form['soru']
        cevap = internet_cevap(soru)
        insert_question_answer(soru, cevap)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT question, answer FROM questions ORDER BY id DESC")
    sorular_cevaplar = c.fetchall()
    conn.close()

    return render_template('index.html', sorular_cevaplar=sorular_cevaplar)

if __name__ == '__main__':
    app.run(debug=True)