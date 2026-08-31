from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT DEFAULT '',
            completed BOOLEAN DEFAULT FALSE
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "version": "v3",
        "deployment": "terraform-github-actions"
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, completed
        FROM tasks
        ORDER BY id
    """)

    tasks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(tasks)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, title, completed
        FROM tasks
        WHERE id = %s
        """,
        (task_id,)
    )

    task = cur.fetchone()

    cur.close()
    conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({
            "error": "title is required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks (title, description, completed)
        VALUES (%s, %s, %s)
        RETURNING *;
    """, (
        data["title"],
        data.get("description", ""),
        data.get("completed", False)
    ))

    new_task = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET title = %s,
            completed = %s
        WHERE id = %s
        RETURNING id, title, completed
        """,
        (
            data.get("title"),
            data.get("completed", False),
            task_id
        )
    )

    task = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task)


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM tasks
        WHERE id = %s
        RETURNING id
        """,
        (task_id,)
    )

    deleted_task = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if deleted_task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted"})




if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)