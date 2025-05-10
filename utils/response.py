from flask import jsonify

def success(data=None, message=None, status=200):
    response = {}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), status

def error(message="Something went wrong", status=400):
    return jsonify({
        "error": message
        }), status
