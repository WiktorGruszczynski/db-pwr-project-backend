import uuid
import secrets
import string
import smtplib
import os
from datetime import datetime, timedelta
from email.message import EmailMessage
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.database import get_db_connection
from app.users.schemas import UserRegister, UserLogin, UserVerify2FA

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_session_id() -> str:
    return str(uuid.uuid4())

def get_session_expiration() -> datetime:
    return datetime.now() + timedelta(days=7)

def generate_code() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def send_2fa_email(to_email: str, code: str) -> None:
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    sender_email = os.getenv("SMTP_USERNAME")
    sender_password = os.getenv("SMTP_PASSWORD")

    msg = EmailMessage()
    msg['Subject'] = 'Potwierdź swój adres e-mail'
    msg['From'] = sender_email
    msg['To'] = to_email
    
    msg.set_content(f"Witaj!\n\nTwój kod weryfikacyjny to: {code}\n\nKod wygaśnie za 10 minut.")

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Sukces! Wysłano maila do {to_email}")
    except Exception as e:
        print(f"Błąd wysyłania maila: {e}")

def create_and_send_2fa_code(user_id: str, user_email: str, code_type: str = 'EMAIL_VERIFICATION') -> None:
    code = generate_code()
    expires_at = datetime.now() + timedelta(minutes=10)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO verification_code (user_id, code, code_type, expires_at) 
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, code, code_type, expires_at)
            )
            conn.commit()
    finally:
        conn.close()
        
    send_2fa_email(to_email=user_email, code=code)


def register_new_user(user: UserRegister) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, is_enabled FROM users_user WHERE email = %s OR username = %s", (user.email, user.username))
            existing_user = cursor.fetchone()

            if existing_user:
                if existing_user["is_enabled"]:
                    raise HTTPException(status_code=400, detail="Użytkownik już istnieje")
                else:
                    create_and_send_2fa_code(existing_user["id"], user.email, 'EMAIL_VERIFICATION')
                    return

            hashed_password = get_password_hash(user.password)

            cursor.execute(
                """
                INSERT INTO users_user (username, email, password, is_enabled) 
                VALUES (%s, %s, %s, FALSE) RETURNING id
               """,
               (user.username, user.email, hashed_password)
            )

            new_user_id = cursor.fetchone()["id"]

            conn.commit()
            create_and_send_2fa_code(new_user_id, user.email, 'EMAIL_VERIFICATION')
    finally:
        conn.close()


def verify_user_registration(data: UserVerify2FA) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, is_enabled FROM users_user WHERE email = %s", (data.email,))
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=400, detail="Błędne dane")
            if user["is_enabled"]:
                raise HTTPException(status_code=400, detail="Użytkownik jest już aktywny")

            cursor.execute(
                """
                SELECT id FROM verification_code 
                WHERE user_id = %s AND code = %s AND code_type = 'EMAIL_VERIFICATION' AND expires_at > CURRENT_TIMESTAMP
                """, 
                (user["id"], data.code)
            )
            valid_code = cursor.fetchone()

            if not valid_code:
                raise HTTPException(status_code=400, detail="Nieprawidłowy kod")

            cursor.execute("UPDATE users_user SET is_enabled = TRUE WHERE id = %s", (user["id"],))
            cursor.execute("DELETE FROM verification_code WHERE id = %s", (valid_code["id"],))
            conn.commit()
    finally:
        conn.close()

def authenticate_user(user: UserLogin)-> str:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password, is_enabled FROM users_user WHERE email = %s", (user.email,))
            db_user =  cursor.fetchone()

            if not db_user or not verify_password(user.password, db_user["password"]):
                raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")
            
            if not db_user["is_enabled"]:
                raise HTTPException(status_code=403, detail="Najpierw potwierdź swój adres e-mail (skorzystaj ponownie z formularza rejestracji by wymusić nowy kod).")
            
            session_id = generate_session_id()
            expires_at = get_session_expiration()

            cursor.execute(
                "INSERT INTO session (id, user_id, expires_at) VALUES (%s, %s, %s)",
                (session_id, db_user["id"], expires_at),
            )
            conn.commit()
            return session_id

    finally:
        conn.close()        
    


def remove_session(session_id: str) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM session WHERE id = %s", (session_id,))
            conn.commit()
    finally:
        conn.close()

def get_user_by_session(session_id: str) -> dict | None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.username, u.email
                FROM session s
                JOIN users_user u ON s.user_id = u.id
                WHERE s.id = %s AND s.expires_at > CURRENT_TIMESTAMP
            """, (session_id,)
            )
            return cursor.fetchone()
    finally:
        conn.close()


def send_password_reset_code(email: str) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users_user WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                return 
            
            create_and_send_2fa_code(user["id"], email, 'PASSWORD_RESET')
    finally:
        conn.close()


def verify_and_reset_password(email: str, code: str, new_password: str) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users_user WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                raise HTTPException(status_code=400, detail="Błędne dane")

            cursor.execute(
                """
                SELECT id FROM verification_code 
                WHERE user_id = %s AND code = %s AND code_type = 'PASSWORD_RESET' AND expires_at > CURRENT_TIMESTAMP
                """, 
                (user["id"], code)
            )
            valid_code = cursor.fetchone()

            if not valid_code:
                raise HTTPException(status_code=400, detail="Nieprawidłowy lub wygasły kod")

            hashed_password = get_password_hash(new_password)

            cursor.execute("UPDATE users_user SET password = %s WHERE id = %s", (hashed_password, user["id"]))
            cursor.execute("DELETE FROM verification_code WHERE id = %s", (valid_code["id"],))
            conn.commit()
    finally:
        conn.close()