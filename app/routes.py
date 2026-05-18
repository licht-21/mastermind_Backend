from flask import current_app as app, request, jsonify
import mysql.connector 

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="Leomorddyroth5121",        
        database="saving_db"
    )

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Checks if account details already conflict with existing rows
        cursor.execute("SELECT * FROM users WHERE email = %s OR name = %s", (email, username))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"status": "error", "message": "Username or Email already registered"}), 400

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        
        user_id = cursor.lastrowid

        return jsonify({
            "status": "success",
            "message": "Registration successful!",
            "user": {
                "id": user_id,
                "username": username,
                "email": email
            }
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username') # This variable contains whatever string they typed in the box
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # CHANGED: This query now searches BOTH columns for a match using OR logic
        cursor.execute(
            "SELECT * FROM users WHERE (name = %s OR email = %s) AND password = %s", 
            (username, username, password)
        )
        user = cursor.fetchone()

        if user:
            return jsonify({
                "status": "success",
                "message": "Login successful!",
                "user": {
                    "id": user['id'],
                    "username": user['name'], 
                    "email": user['email']
                }
            }), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()