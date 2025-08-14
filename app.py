from __future__ import annotations
from typing import Optional
from flask import Flask, render_template, request, redirect, url_for, flash
import db as dbmod


def create_app(test_db_path: Optional[str] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(SECRET_KEY="dev-key-change-this")

    if test_db_path:
        app.config["DATABASE"] = test_db_path
    else:
        app.config["DATABASE"] = "todo.sqlite3"

    @app.cli.command("db-init")
    def db_init_cmd():
        seed = "--seed" in request.environ.get("flask.cli.command_line", "")
        dbmod.init_db(app.config["DATABASE"], seed=seed)
        print("Initialized DB", "(with seed)" if seed else "")

    @app.get("/")
    def index():
        conn = dbmod.get_db(app.config["DATABASE"])  
        tasks = dbmod.list_tasks(conn)
        return render_template("index.html", tasks=tasks)

    @app.post("/add")
    def add():
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "warning")
            return redirect(url_for("index"))
        conn = dbmod.get_db(app.config["DATABASE"])
        dbmod.add_task(conn, title)
        flash("Task added.", "success")
        return redirect(url_for("index"))

    @app.post("/toggle/<int:task_id>")
    def toggle(task_id: int):
        conn = dbmod.get_db(app.config["DATABASE"])
        if not dbmod.toggle_done(conn, task_id):
            flash("Task not found.", "danger")
        return redirect(url_for("index"))

    @app.get("/edit/<int:task_id>")
    def edit_get(task_id: int):
        conn = dbmod.get_db(app.config["DATABASE"])
        task = dbmod.get_task(conn, task_id)
        if not task:
            flash("Task not found.", "danger")
            return redirect(url_for("index"))
        return render_template("edit.html", task=task)

    @app.post("/edit/<int:task_id>")
    def edit_post(task_id: int):
        title = request.form.get("title", "")
        conn = dbmod.get_db(app.config["DATABASE"])
        if not dbmod.update_title(conn, task_id, title.strip()):
            flash("Task not found.", "danger")
        else:
            flash("Updated.", "success")
        return redirect(url_for("index"))

    @app.post("/delete/<int:task_id>")
    def delete(task_id: int):
        conn = dbmod.get_db(app.config["DATABASE"])
        if not dbmod.delete_task(conn, task_id):
            flash("Task not found.", "danger")
        else:
            flash("Deleted.", "info")
        return redirect(url_for("index"))

    @app.post("/clear-completed")
    def clear_completed():
        conn = dbmod.get_db(app.config["DATABASE"])
        dbmod.clear_completed(conn)
        flash("Cleared completed tasks.", "info")
        return redirect(url_for("index"))

    return app

app = create_app()