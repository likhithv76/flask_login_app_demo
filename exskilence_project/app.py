from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "secret_key_123"

def get_db_connection():
    """Get database connection"""
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "flask_login")
        )
        return db
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def get_cursor(db):
    """Get cursor with dictionary results"""
    if db:
        return db.cursor(dictionary=True)
    return None

def init_db():
    """Initialize database with users table"""
    db = get_db_connection()
    if not db:
        print("Failed to connect to database. Please check your MySQL configuration.")
        return
    
    cursor = get_cursor(db)
    if not cursor:
        db.close()
        return
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        
        # Check if admin user exists, if not insert it
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE username = %s', ('admin',))
        result = cursor.fetchone()
        if result and result['count'] == 0:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', ('admin', 'admin123'))
        
        db.commit()
    except mysql.connector.Error as err:
        print(f"Database initialization error: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db_connection()
        if not db:
            return render_template("login.html", error="Database connection failed. Please check your MySQL configuration.")
        
        cursor = get_cursor(db)
        if not cursor:
            db.close()
            return render_template("login.html", error="Database connection failed.")
        
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
        except mysql.connector.Error as err:
            return render_template("login.html", error=f"Database error: {err}")
        finally:
            cursor.close()
            db.close()

        if user:
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=4000)
