from flask import Flask, render_template, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import pickle
import csv
import os

app = Flask(__name__)

# تحميل نموذج التنبؤ بالكلمة
model = load_model('next_word_model.h5')
with open('tokenizer.pickle', 'rb') as f:
    tokenizer = pickle.load(f)

# دالة التنبؤ بالكلمة التالية
def predict_next_words(input_text, num_words=3):
    sequence = tokenizer.texts_to_sequences([input_text])
    padded = tf.keras.preprocessing.sequence.pad_sequences(sequence, maxlen=10)
    predictions = model.predict(padded, verbose=0)[0]
    top_indices = predictions.argsort()[-num_words:][::-1]
    return [tokenizer.index_word.get(i, '') for i in top_indices]

# دالة لقراءة الكتب من CSV
def read_books():
    books = []
    file_path = 'dataset/books.csv'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود.")
        return books

    try:
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader):
                if i >= 50:  # تحديد عدد الكتب المسترجعة
                    break
                books.append({
                    'isbn': row.get('ISBN', 'N/A'),
                    'title': row.get('Book-Title', 'No Title'),
                    'author': row.get('Book-Author', 'Unknown'),
                    'year': row.get('Year-Of-Publication', 'N/A'),
                    'publisher': row.get('Publisher', 'N/A'),
                    'image_url': row.get('Image-URL-M', '')
                })
    except Exception as e:
        print(f"حدث خطأ أثناء قراءة الملف: {e}")
    
    return books

@app.route("/")
def home():
    return render_template("word-prediction.html")

# مسار التنبؤ بالكلمة
@app.route("/predict_next_word", methods=["GET"])
def predict_next_word():
    input_text = request.args.get("text")
    if input_text:
        predictions = predict_next_words(input_text)
        return jsonify(predicted_text=predictions)
    else:
        return jsonify(predicted_text=[])

# عرض الكتب
@app.route("/books")
def books():
    book_list = read_books()
    return render_template("articles.html", books=book_list)

# البحث في الكتب
@app.route("/search_books", methods=["GET"])
def search_books():
    query = request.args.get("q", "").lower()
    books = read_books()
    matched = []
    if query:
        for book in books:
            if query in book['title'].lower():
                matched.append({
                    'title': book['title'],
                    'author': book['author'],
                    'year': book['year'],
                    'publisher': book['publisher'],
                    'image_url': book['image_url']
                })
    return jsonify(results=matched)

if __name__ == "__main__":
    app.run(debug=True)
