from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import uuid
import os

app = Flask(__name__)

# Use environment variable if available (for deployment)
cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'firebase_credentials.json')
cred = credentials.Certificate(cred_path)

# Initialize Firebase app
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://patanjali-slic-25-26-default-rtdb.firebaseio.com/'
})

# Home page
@app.route('/')
def home():
    return render_template("index.html")

# Chat selection page
@app.route('/chat')
def chat_select():
    return render_template("chat_select.html")

# New user: generate unique 8-digit UUID
@app.route('/new_user')
def new_user():
    while True:
        new_id = str(uuid.uuid4().int)[:8]
        if not db.reference(f"/chats/{new_id}").get():
            break
    return redirect(url_for('chat_user', user_id=new_id))

# Existing user login
@app.route('/existing_user', methods=['POST'])
def existing_user():
    user_id = request.form['user_id']
    if not db.reference(f"/chats/{user_id}").get():
        return "Invalid ID. Please try again.", 404
    return redirect(url_for('chat_user', user_id=user_id))

# User chat page
@app.route('/chat/<user_id>', methods=['GET', 'POST'])
def chat_user(user_id):
    ref = db.reference(f"/chats/{user_id}")
    if request.method == 'POST':
        message = request.form['message']
        ref.push({"from": "user", "text": message})
        return redirect(url_for('chat_user', user_id=user_id))  # Prevents duplicates on refresh
    messages = ref.get() or {}
    return render_template("chat_user.html", user_id=user_id, messages=messages)

# Admin chat interface
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        user_id = request.form['user_id']
        message = request.form['message']
        db.reference(f"/chats/{user_id}").push({"from": "admin", "text": message})
        return redirect(url_for('admin'))  # Prevents duplicates on refresh
    users = db.reference("/chats").get() or {}
    return render_template("chat_admin.html", users=users)

# Run app locally
if __name__ == '__main__':
    app.run(debug=True)

