from flask import Flask, jsonify, request
from threading import Lock
from datetime import datetime, timedelta
import celery
import time
app = Flask(__name__)
store = {}
expiry_store = {}
lock = Lock()


def key_valid(key):
    if key not in store:
        return False
    if store[key]['expiry'] and time.time() > store[key]['expiry']:
        del store[key]
        return False
    return True


def set_value(key, value, expiry=None, condition=None):
    with lock:
        if condition == "NX" and key in store:
            return False
        if condition == "XX" and key not in store:
            return False
        store[key] = value
        if expiry:
            expiry_time = datetime.now() + timedelta(seconds=expiry)
            expiry_store[key] = expiry_time
        return True


def get_value(key):
    with lock:
        if key not in store:
            return None
        if key in expiry_store and expiry_store[key] < datetime.now():
            del store[key]
            del expiry_store[key]
            return None
        return store[key]


def push_value(key, values):
    with lock:
        if key not in store:
            store[key] = []
        store[key].extend(values)
        return len(store[key])


def pop_value(key):
    with lock:
        if key not in store:
            return None
        if not isinstance(store[key], list):
            return None
        if not store[key]:
            return None
        return store[key].pop()


def blocking_pop_value(key, timeout):
    start_time = time.time()
    while True:
        with lock:
            if key not in store:
                return None
            if not isinstance(store[key], list):
                return None
            if store[key]:
                return store[key].pop()
        time.sleep(0.1)
        if time.time() - start_time > timeout:
            break
    return None


@app.route("/qpop", methods=["GET"])
def qpop_handler():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "Missing key"}), 400
    value = pop_value(key)
    if value is None:
        return jsonify({"error": "Key not found or not a list"}), 404
    return jsonify({"result": value}), 200


@app.route("/bqpop", methods=["GET"])
def bqpop_handler():
    key = request.args.get("key")
    timeout = float(request.args.get("timeout", 0))
    if not key:
        return jsonify({"error": "Missing key"}), 400
    value = blocking_pop_value(key, timeout)
    if value is None:
        return jsonify({"error": "Key not found or not a list or timed out"}), 404
    return jsonify({"result": value}), 200


@app.route('/set', methods=['POST'])
def set_key():
    key = request.json['key']
    value = request.json['value']
    expiry = request.json.get('expiry', None)
    condition = request.json.get('condition', None)

    task = celery.send_task('tasks.set_key', args=[
                            key, value, expiry, condition])
    task.wait()

    response = task.result
    return jsonify(response)


@celery.task(name='tasks.set_key')
def set_key_task(key, value, expiry, condition):
    with app.app_context():
        with app.test_request_context():
            with lock:
                if condition == 'NX' and key_valid(key):
                    return {'success': False, 'message': 'Key already exists.'}, 409
                elif condition == 'XX' and not key_valid(key):
                    return {'success': False, 'message': 'Key does not exist.'}, 404
                else:
                    store[key] = {'value': value,
                                  'expiry': time.time() + expiry if expiry else None}
                    return {'success': True, 'message': 'Key set successfully.'}, 200


@app.route("/get", methods=["GET"])
def get_handler():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "Missing key"}), 400
    value = get_value(key)
    if value is None:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"result": value}), 200


@app.route("/qpush", methods=["POST"])
def qpush_handler():
    data = request.get_json()
    key = data.get("key")
    values = data.get("values")
    if not key or not values:
        return jsonify({"error": "Missing key or values"}), 400
    result = push_value(key, values)
    return jsonify({"result": result}), 200


if __name__ == "__main__":
    app.run(debug=True)
