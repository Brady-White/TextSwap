import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore
import bcrypt

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./backend/credentials/textswapfinal-firebase-adminsdk-v2sag-561a397a16.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Function to register a new user
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    university = data.get('university')

    if not email or not password or not name or not university:
        return jsonify({'error': 'All fields (name, university, email, password) are required'}), 400

    try:
        # Create a new user with email and password
        user = auth.create_user(
            email=email,
            password=password
        )
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Generate an email verification link
        verification_link = auth.generate_email_verification_link(email)

        # Send verification email
        send_verification_email(email, verification_link)

        # Save user data to Firestore
        user_data = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'university': university
        }
        db.collection('users').document(user.uid).set(user_data)

        return jsonify({"message": "Verification email sent successfully"}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    
def send_verification_email(email, verification_link):
    # SMTP server configuration (example using Gmail)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'textswap1@gmail.com'  
    smtp_password = 'nqgsvuabnzuehrho'  

    subject = "Verify your email for TextSwap"
    body = f"Hi, please verify your email by clicking the link: {verification_link} \n\nThank you, \nTextSwap Support"

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = 'TextSwap Support'
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to login a user
@app.route('/login', methods=['POST'])
def user_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        # Retrieve user by email from Firebase Auth
        user = auth.get_user_by_email(email)

        # Check if the user's email is verified
        if not user.email_verified:
            return jsonify({'error': 'Please verify your email before logging in'}), 403

        # Retrieve user data from Firestore
        user_ref = db.collection('users').document(user.uid).get()
        if not user_ref.exists:
            return jsonify({'error': 'Invalid email or password'}), 401

        user_data = user_ref.to_dict()
        hashed_password = user_data.get('password')

        # Verify the password
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Generate a custom Firebase token for the user
        token = auth.create_custom_token(user.uid)

        return jsonify({'token': token.decode('utf-8')}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
