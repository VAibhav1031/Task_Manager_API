from flask import (
    Blueprint,
    send_from_directory,
    render_template,
)

docs = Blueprint("docs", __name__, url_prefix="/api/")


@docs.route("/openapi.yaml")
def openapi_spec():
    return send_from_directory(".", "openapi.yaml")


@docs.route("/docs")
def swagger_ui():
    return render_template("docs.html")
