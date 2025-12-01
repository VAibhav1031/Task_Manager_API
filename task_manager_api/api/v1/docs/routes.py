from flask import Blueprint, send_from_directory, render_template, current_app

docs = Blueprint("docs", __name__, url_prefix="/api/v1")


@docs.route("/openapi")
def openapi_spec():
    folder = current_app.static_folder
    return send_from_directory(folder, "openapi.yaml", mimetype="text/yaml")


@docs.route("/docs")
def swagger_ui():
    return render_template("docs.html")
