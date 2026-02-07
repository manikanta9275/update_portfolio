from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import secrets
import time
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:64978", "http://localhost:3000"]}})

# ---------------- CONFIG ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update with your SMTP server details
app.config['MAIL_PORT'] = 587  # Update with the port number of your SMTP server
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USERNAME'] = 'abhiproject9275@gmail.com'  # Update with your email address
app.config['MAIL_PASSWORD'] = 'kvna acie pjzh kleq'  # Update with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'abhiproject9275@gmail.com'  # Update with your email address
mail = Mail(app)

# OTP storage (use DB in production)
otp_store = {}

# ---------------- OTP GENERATOR ----------------
def generate_otp():
    return str(secrets.randbelow(10000)).zfill(4)

# ---------------- SEND OTP ----------------
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    print("EMAIL RECEIVED:", email)

    if not email:
        return jsonify({"error": "Email is required"}), 400

    otp = generate_otp()

    otp_store[email] = {
        "otp": otp,
        "time": time.time()
    }

    msg = Message(
        "Your OTP Verification",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f"Your OTP is: {otp}. Valid for 5 minutes."

    mail.send(msg)
    return jsonify({"status": "OTP sent"})


# ---------------- VERIFY OTP ----------------
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.json.get('email')
    user_otp = request.json.get('otp')

    record = otp_store.get(email)

    if not record:
        return jsonify({"verified": False})

    # OTP expiry (5 minutes)
    if time.time() - record['time'] > 300:
        return jsonify({"verified": False})

    if record['otp'] == user_otp:
        otp_store.pop(email)
        return jsonify({"verified": True})

    return jsonify({"verified": False})

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run()
