from datetime import date

from flask import current_app as app, request, jsonify
import mysql.connector


def get_user_id_from_request():
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return None
    try:
        return int(user_id)
    except (TypeError, ValueError):
        return None


def goal_to_json(row):
    target = float(row["target_amount"])
    current = float(row["current_amount"])
    if target > 0:
        percent = min(100, int((current / target) * 100))
    else:
        percent = 0

    due_date = row.get("due_date")
    archived_at = row.get("archived_at")
    is_archived = bool(row.get("is_archived", 0))
    is_overdue = False
    if due_date and not is_archived and percent < 100:
        due_value = due_date.date() if hasattr(due_date, "date") else due_date
        if due_value < date.today():
            is_overdue = True

    return {
        "id": row["id"],
        "name": row["name"],
        "targetAmount": target,
        "currentAmount": current,
        "progressPercent": percent,
        "dueDate": due_date.isoformat() if due_date else None,
        "isArchived": is_archived,
        "archivedAt": archived_at.strftime("%Y-%m-%d %H:%M:%S") if archived_at else None,
        "isOverdue": is_overdue,
    }


def deposit_to_json(row):
    created = row.get("created_at")
    return {
        "id": row["id"],
        "goalId": row["goal_id"],
        "amount": float(row["amount"]),
        "note": row.get("note"),
        "createdAt": created.strftime("%Y-%m-%d %H:%M:%S") if created else None,
    }


def record_deposit(cursor, goal_id, amount, note=None):
    cursor.execute(
        "INSERT INTO deposits (goal_id, amount, note) VALUES (%s, %s, %s)",
        (goal_id, amount, note),
    )


def savings_order_clause(sort_key):
    mapping = {
        "name": "name ASC",
        "due_date": "due_date IS NULL, due_date ASC",
        "progress": "(current_amount / NULLIF(target_amount, 0)) DESC",
        "newest": "id DESC",
    }
    return mapping.get(sort_key, "id DESC")


def ensure_user_settings(cursor, user_id):
    cursor.execute("SELECT user_id FROM user_settings WHERE user_id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO user_settings (user_id, dark_mode, date_format) VALUES (%s, 0, 'DD/MM/YYYY')",
            (user_id,),
        )


def maybe_auto_archive(cursor, conn, goal_id, user_id):
    cursor.execute(
        "SELECT target_amount, current_amount FROM savings_goals WHERE id = %s AND user_id = %s",
        (goal_id, user_id),
    )
    row = cursor.fetchone()
    if not row:
        return
    target = float(row["target_amount"])
    current = float(row["current_amount"])
    if target > 0 and current >= target:
        cursor.execute(
            "UPDATE savings_goals SET is_archived = 1, archived_at = CURRENT_TIMESTAMP "
            "WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        conn.commit()


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="passwordito",        
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


@app.route("/api/savings", methods=["GET"])
def list_savings():
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    archived_param = request.args.get("archived", "0")
    is_archived = 1 if archived_param in ("1", "true", "True") else 0
    sort_key = request.args.get("sort", "newest")
    order_by = savings_order_clause(sort_key)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"SELECT * FROM savings_goals WHERE user_id = %s AND is_archived = %s ORDER BY {order_by}",
            (user_id, is_archived),
        )
        rows = cursor.fetchall()
        return jsonify([goal_to_json(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings", methods=["POST"])
def create_savings_goal():
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    target_amount = data.get("targetAmount")
    current_amount = data.get("currentAmount", 0)
    due_date = data.get("dueDate") or None

    if not name or target_amount is None:
        return jsonify({"status": "error", "message": "Name and target amount are required"}), 400

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount or 0)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid amount"}), 400

    if target_amount <= 0:
        return jsonify({"status": "error", "message": "Target amount must be greater than zero"}), 400
    if current_amount < 0:
        return jsonify({"status": "error", "message": "Current amount cannot be negative"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        is_archived = 1 if target_amount > 0 and current_amount >= target_amount else 0
        cursor.execute(
            "INSERT INTO savings_goals (user_id, name, target_amount, current_amount, due_date, is_archived, archived_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, CASE WHEN %s = 1 THEN CURRENT_TIMESTAMP ELSE NULL END)",
            (user_id, name, target_amount, current_amount, due_date, is_archived, is_archived),
        )
        conn.commit()
        goal_id = cursor.lastrowid
        if current_amount > 0:
            record_deposit(cursor, goal_id, current_amount, "Initial savings")
            conn.commit()
        cursor.execute("SELECT * FROM savings_goals WHERE id = %s", (goal_id,))
        row = cursor.fetchone()
        return jsonify(goal_to_json(row)), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/summary", methods=["GET"])
def savings_summary():
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS active_goal_count,
                COALESCE(SUM(current_amount), 0) AS total_saved,
                COALESCE(SUM(target_amount), 0) AS total_target,
                SUM(
                    CASE
                        WHEN due_date IS NOT NULL
                             AND due_date < CURDATE()
                             AND current_amount < target_amount
                        THEN 1 ELSE 0
                    END
                ) AS overdue_count
            FROM savings_goals
            WHERE user_id = %s AND is_archived = 0
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        return jsonify({
            "activeGoalCount": int(row["active_goal_count"] or 0),
            "totalSaved": float(row["total_saved"] or 0),
            "totalTarget": float(row["total_target"] or 0),
            "overdueCount": int(row["overdue_count"] or 0),
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/<int:goal_id>/deposits", methods=["GET"])
def list_deposits(goal_id):
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id FROM savings_goals WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Goal not found"}), 404

        cursor.execute(
            "SELECT * FROM deposits WHERE goal_id = %s ORDER BY created_at DESC",
            (goal_id,),
        )
        rows = cursor.fetchall()
        return jsonify([deposit_to_json(row) for row in rows]), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/<int:goal_id>/duplicate", methods=["POST"])
def duplicate_savings_goal(goal_id):
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM savings_goals WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        source = cursor.fetchone()
        if not source:
            return jsonify({"status": "error", "message": "Goal not found"}), 404

        new_name = f"{source['name']} (copy)"
        cursor.execute(
            "INSERT INTO savings_goals (user_id, name, target_amount, current_amount, due_date, is_archived) "
            "VALUES (%s, %s, %s, 0, %s, 0)",
            (user_id, new_name, source["target_amount"], source.get("due_date")),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM savings_goals WHERE id = %s", (new_id,))
        row = cursor.fetchone()
        return jsonify(goal_to_json(row)), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/<int:goal_id>", methods=["PUT"])
def update_savings_goal(goal_id):
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    target_amount = data.get("targetAmount")
    current_amount = data.get("currentAmount")
    due_date = data.get("dueDate")

    if not name or target_amount is None or current_amount is None:
        return jsonify({"status": "error", "message": "Name, target, and current amount are required"}), 400

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid amount"}), 400

    if target_amount <= 0:
        return jsonify({"status": "error", "message": "Target amount must be greater than zero"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id FROM savings_goals WHERE id = %s AND user_id = %s AND is_archived = 0",
            (goal_id, user_id),
        )
        if not cursor.fetchone():
            return jsonify({"status": "error", "message": "Goal not found"}), 404

        cursor.execute(
            "UPDATE savings_goals SET name = %s, target_amount = %s, current_amount = %s, due_date = %s "
            "WHERE id = %s AND user_id = %s",
            (name, target_amount, current_amount, due_date, goal_id, user_id),
        )
        conn.commit()
        maybe_auto_archive(cursor, conn, goal_id, user_id)
        cursor.execute("SELECT * FROM savings_goals WHERE id = %s", (goal_id,))
        row = cursor.fetchone()
        return jsonify(goal_to_json(row)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/<int:goal_id>", methods=["DELETE"])
def delete_savings_goal(goal_id):
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "DELETE FROM savings_goals WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Goal not found"}), 404
        return jsonify({"status": "success", "message": "Goal deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/<int:goal_id>/archive", methods=["POST"])
def archive_savings_goal(goal_id):
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM savings_goals WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "Goal not found"}), 404

        cursor.execute(
            "UPDATE savings_goals SET is_archived = 1, archived_at = CURRENT_TIMESTAMP "
            "WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        conn.commit()
        cursor.execute("SELECT * FROM savings_goals WHERE id = %s", (goal_id,))
        updated = cursor.fetchone()
        return jsonify(goal_to_json(updated)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/savings/<int:goal_id>/deposit", methods=["POST"])
def deposit_to_goal(goal_id):
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    data = request.get_json() or {}
    amount = data.get("amount")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid deposit amount"}), 400

    if amount <= 0:
        return jsonify({"status": "error", "message": "Deposit must be greater than zero"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM savings_goals WHERE id = %s AND user_id = %s",
            (goal_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "Goal not found"}), 404

        new_current = float(row["current_amount"]) + amount
        cursor.execute(
            "UPDATE savings_goals SET current_amount = %s WHERE id = %s AND user_id = %s AND is_archived = 0",
            (new_current, goal_id, user_id),
        )
        record_deposit(cursor, goal_id, amount, data.get("note"))
        conn.commit()
        maybe_auto_archive(cursor, conn, goal_id, user_id)
        cursor.execute("SELECT * FROM savings_goals WHERE id = %s", (goal_id,))
        updated = cursor.fetchone()
        if not updated:
            return jsonify({"status": "error", "message": "Goal not found"}), 404
        return jsonify(goal_to_json(updated)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/settings", methods=["GET"])
def get_settings():
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        ensure_user_settings(cursor, user_id)
        conn.commit()
        cursor.execute("SELECT * FROM user_settings WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        return jsonify({
            "darkMode": bool(row["dark_mode"]),
            "dateFormat": row["date_format"],
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/settings", methods=["PUT"])
def update_settings():
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing X-User-Id header"}), 401

    data = request.get_json() or {}
    dark_mode = data.get("darkMode", False)
    date_format = data.get("dateFormat", "DD/MM/YYYY")
    if date_format not in ("DD/MM/YYYY", "YYYY-MM-DD"):
        return jsonify({"status": "error", "message": "Invalid date format"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        ensure_user_settings(cursor, user_id)
        cursor.execute(
            "UPDATE user_settings SET dark_mode = %s, date_format = %s WHERE user_id = %s",
            (1 if dark_mode else 0, date_format, user_id),
        )
        conn.commit()
        return jsonify({
            "darkMode": bool(dark_mode),
            "dateFormat": date_format,
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()