"""
Application entry point.

Run locally with:
    python app.py

Or with a production server:
    gunicorn "app:create_app()"
"""
import os
from flask import Flask, render_template
from config import config_map


def create_app(env=None):
    app = Flask(__name__)
    env = env or os.environ.get("FLASK_ENV", "default")
    app.config.from_object(config_map.get(env, config_map["default"]))

    # ---- Blueprints ----
    from routes.auth import auth_bp
    from routes.portfolio import portfolio_bp
    from routes.admin import admin_bp

    app.register_blueprint(portfolio_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # ---- Error handlers ----
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("404.html", server_error=True), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True), host="0.0.0.0", port=5000)
