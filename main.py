from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import uuid
import os

app = Flask(__name__)

# Load Firebase credentials (from secret environment variable path in production)
cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'firebase_credentials.json')
cred = credentials.Certificate(cred_path)

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://patanjali-slic-25-26-default-rtdb.firebaseio.com/'  # Replace with your own
})

# Home Page
@app.route('/')
def home():
    return render_template("index.html")

# Chat Option Page (New/Existing)
@app.route('/chat')
def chat_select():
    return render_template("chat_select.html")

# New User - Generate 8-digit UUID
@app.route('/new_user')
def new_user():
    while True:
        new_id = str(uuid.uuid4().int)[:8]
        # Avoid accidental UUID collision
        if not db.reference(f"/chats/{new_id}").get():
            break
    return redirect(url_for('chat_user', user_id=new_id))

# Existing User Login
@app.route('/existing_user', methods=['POST'])
def existing_user():
    user_id = request.form['user_id']
    if not db.reference(f"/chats/{user_id}").get():
        return "Invalid ID. Please try again.", 404
    return redirect(url_for('chat_user', user_id=user_id))

# User Chat Page
@app.route('/chat/<user_id>', methods=['GET', 'POST'])
def chat_user(user_id):
    ref = db.reference(f"/chats/{user_id}")
    if request.method == 'POST':
        message = request.form['message']
        ref.push({"from": "user", "text": message})
    messages = ref.get() or {}
    return render_template("chat_user.html", user_id=user_id, messages=messages)

# Admin Interface (developer-only view)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user_id = request.form['user_id']
        message = request.form['message']
        db.reference(f"/chats/{user_id}").push({"from": "admin", "text": message})
    users = db.reference("/chats").get() or {}
    return render_template("chat_admin.html", users=users)

# Run Flask server
if __name__ == '__main__':
    app.run(debug=True)
