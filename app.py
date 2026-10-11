import os

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

from extension import db  # noqa: E402
from route import error_bp, home_bp, payment_bp, success_bp  # noqa: E402

app = Flask(__name__)

# Render sits behind a proxy, this makes url_for build https links
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

database_url = os.getenv("DATABASE_URL", "")
# Render gives postgres:// but SQLAlchemy wants postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(home_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(success_bp)
app.register_blueprint(error_bp)

with app.app_context():
    import model  # noqa: F401

    db.create_all()


if __name__ == "__main__":
    app.run(debug=False)
