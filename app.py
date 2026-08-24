from flask import Flask, request, jsonify

app = Flask(__name__)

tasks = [
    {
        "id": 1,
        "title": "Learn AWS",
        "description": "Revise AWS fundamentals",
        "completed": False
    },
    {
        "id": 2,
        "title": "Learn Docker",
        "description": "Dockerize Flask application",
        "completed": False
    }
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):

    for task in tasks:
        if task["id"] == task_id:
            return jsonify(task)

    return jsonify({
        "error": "Task not found"
    }), 404


@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "description": data.get("description", ""),
        "completed": False
    }

    tasks.append(new_task)

    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):

    data = request.get_json()

    for task in tasks:

        if task["id"] == task_id:

            task["title"] = data.get("title", task["title"])
            task["description"] = data.get(
                "description",
                task["description"]
            )
            task["completed"] = data.get(
                "completed",
                task["completed"]
            )

            return jsonify(task)

    return jsonify({
        "error": "Task not found"
    }), 404


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    for task in tasks:

        if task["id"] == task_id:

            tasks.remove(task)

            return jsonify({
                "message": "Task deleted"
            })

    return jsonify({
        "error": "Task not found"
    }), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)