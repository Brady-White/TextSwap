import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from firebase_admin import credentials, auth, firestore, initialize_app
import bcrypt

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./credentials/textswapfinal-firebase-adminsdk-v2sag-561a397a16.json')
initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Pydantic models for data validation
class UserRegistration(BaseModel):
    email: str
    password: str
    name: str
    university: str

class UserLogin(BaseModel):
    email: str
    password: str

class Listing(BaseModel):
    title: str
    author: str
    course_number: str
    condition: str
    price: str
    other_desired_titles: str = None
    user_email: str

# Helper function to send verification email
def send_verification_email(email: str, verification_link: str):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

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
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Verification email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Route to register a new user
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration):
    try:
        # Create a new user with email and password
        firebase_user = auth.create_user(email=user.email, password=user.password)
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # Generate an email verification link and send email
        verification_link = auth.generate_email_verification_link(user.email)
        send_verification_email(user.email, verification_link)

        # Save user data to Firestore
        user_data = {
            'email': user.email,
            'password': hashed_password.decode('utf-8'),
            'name': user.name,
            'university': user.university
        }
        db.collection('users').document(firebase_user.uid).set(user_data)

        return {"message": "Verification email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route to login a user
@app.post("/login")
async def user_login(login_data: UserLogin):
    try:
        # Retrieve user by email from Firebase Auth
        firebase_user = auth.get_user_by_email(login_data.email)

        # Check if the user's email is verified
        if not firebase_user.email_verified:
            raise HTTPException(status_code=403, detail="Please verify your email before logging in")

        # Retrieve user data from Firestore
        user_ref = db.collection('users').document(firebase_user.uid).get()
        if not user_ref.exists:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_data = user_ref.to_dict()
        hashed_password = user_data.get('password').encode('utf-8')

        # Verify the password
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate a custom Firebase token for the user
        token = auth.create_custom_token(firebase_user.uid)

        return {"token": token}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to create a new listing
@app.post("/create_listing", status_code=status.HTTP_201_CREATED)
async def create_listing(listing: Listing):
    try:
        # Prepare listing data
        listing_data = listing.dict()

        # Add the listing to Firestore
        db.collection('listings').add(listing_data)

        return {"message": "Listing created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
