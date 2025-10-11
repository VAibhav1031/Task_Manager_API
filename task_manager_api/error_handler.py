from flask import jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
import uuid

central_registry = {
    "USER_ALREADY_EXISTS": "User already exists, Try different",
    "UNAUTHORIZED": "Unauthorized access",
    "INVALID_INPUT": "Invalid input data",
    "NOT_FOUND": "Resource not found",
    "INTERNAL_ERROR": "Internal server error",
}


def _make_instance():
    return f"{request.path}#{uuid.uuid4()}"


def error_response(
    code, status, error_type=None, message=None, reason=None, details=None
):
    return (
        jsonify(
            {
                "errors": {
                    "code": code,
                    # machine-readable , maybe in future i will add something in here like url or something URL+code.lower()
                    "type": error_type or code.lower(),
                    "status": status,
                    "message": message or central_registry.get(code, "Unknown error"),
                    "reason": reason,
                    "details": details,
                    "instance": _make_instance(),
                }
            }
        ),
        status,
    )


# bad request means something you have done which is not intended to happen


def bad_request(error_type=None, msg=None, details=None, reason=None):
    return error_response(
        code="BAD_REQUEST",
        error_type=error_type,
        status=400,
        message=msg,
        reason=reason,
        details=details,
    )


def handle_marshmallow_error(err, msg=None):
    return bad_request(msg=msg or "Invalid input", details=err.messages)


def not_found(msg=None):
    return error_response(code="NOT_FOUND", status=404, message=msg)


def user_already_exists(msg=None):
    return error_response(code="USER_ALREADY_EXISTS", status=409, message=msg)


def unauthorized_error(msg=None, reason=None):
    return error_response(
        code="UNAUTHORIZED",
        status=401,
        message=msg,
        reason=reason,  # could be used  for the token errors
    )  #


def forbidden_access(msg=None):
    return error_response(code="FORBIDDEN_ACCESS", status=403, message=msg)


def internal_server_error(msg=None):
    return error_response(code="INTERNAL_ERROR", status=500, message=msg)


def too_many_requests(msg=None, reason=None):
    return error_response(
        code="TOO_MANY_REQUEST", status=429, message=msg, reason=reason
    )


def register_payload_error_handler(app):
    @app.errorhandler(RequestEntityTooLarge)
    def handle_payload_too_large():
        return bad_request(
            error_type="PayloadTooLarge",
            msg="Request payload exceeds maximum allowed size (2 MB)",
        )
