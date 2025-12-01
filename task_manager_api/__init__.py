from flask_sqlalchemy import SQLAlchemy
from task_manager_api.config import get_config
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
import logging.config
from .logging_config import setup_logging
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()


def create_app(config_class=None, verbose=False, quiet=False, log_to_file=True):
    app = Flask(__name__)
    # here we are creating dynamic attribute
    app.config.from_object(get_config())

    setup_logging(
        verbose=app.config.get("LOGGING_VERBOSE"),
        quiet=app.config.get("LOGGING_QUIET"),
        log_to_file=log_to_file,
    )

    logger = logging.getLogger(__name__)
    logger.info("Flask app created and logging initialized")

    db.init_app(
        app
    )  # this will create the instance to use the flask app outside the main run
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Root route (it wont come inside the api module , cause it is not api related route )

    @app.route("/")
    def root():
        return jsonify(
            {
                "service": "Task Manager API",
                "status": "healthy",
                "version": "v1",
                "description": "Backend service for managing tasks and authentication.",
            }
        )

    # Mail Service :
    if app.config.get("USE_FAKE_MAIL", False):
        from task_manager_api.mail_service.fake_service import FakeMailService

        app.mail_service = FakeMailService(app)

    else:
        from task_manager_api.mail_service.real_service import RealMailService

        app.mail_service = RealMailService(app)

    # Blueprints
    from task_manager_api.api.v1.auth.routes import auth
    from task_manager_api.api.v1.tasks.routes import tasks
    from task_manager_api.api.v1.docs.routes import docs

    # Registering  the blueprint
    app.register_blueprint(auth)
    app.register_blueprint(tasks)
    app.register_blueprint(docs)

    # Max_content_request_length (MEaning a request throught wont be greater than 2MB , cause for the safety)
    app.config["Max_Content_Length"] = 2 * 1024 * 1024

    from .error_handler import register_payload_error_handler

    register_payload_error_handler(app)

    return app
