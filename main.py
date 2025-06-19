from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import uuid
import os

app = Flask(__name__)

# Load Firebase credentials and initialize app
cred = credentials.Certificate("firebase_config/firebase_credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://patanjali-slic-25-26-default-rtdb.firebaseio.com/'  # replace with your actual Firebase Realtime DB URL
})

# Home page
@app.route('/')
def home():
    return render_template("index.html")

# Chat selection page: choose new/existing
@app.route('/chat')
def chat_select():
    return render_template("chat_select.html")

# Generate 8-digit UUID for new user
@app.route('/new_user')
def new_user():
    new_id = str(uuid.uuid4().int)[:8]
    return redirect(url_for('chat_user', user_id=new_id))

# Login for existing user using UUID
@app.route('/existing_user', methods=['POST'])
def existing_user():
    user_id = request.form['user_id']
    return redirect(url_for('chat_user', user_id=user_id))

# User chat interface
@app.route('/chat/<user_id>', methods=['GET', 'POST'])
def chat_user(user_id):
    ref = db.reference(f"/chats/{user_id}")
    if request.method == 'POST':
        message = request.form['message']
        ref.push({"from": "user", "text": message})
    messages = ref.get() or {}
    return render_template("chat_user.html", user_id=user_id, messages=messages)

# Admin chat interface to reply to users (secured view - simple version)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user_id = request.form['user_id']
        message = request.form['message']
        db.reference(f"/chats/{user_id}").push({"from": "admin", "text": message})
    users = db.reference("/chats").get() or {}
    return render_template("chat_admin.html", users=users)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
