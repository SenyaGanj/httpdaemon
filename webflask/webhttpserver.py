from flask import Flask, request, jsonify, send_file
import hashlib, os, sys, json

app = Flask(__name__)

config = {}
try:
    with open("config_server.json", 'r') as f:
        config = json.loads(f.read())
except IOError:
    config = {}


host = "0.0.0.0"
if "host" in config:
    host = config["host"]

port = "8000"
if "port" in config:
    port = config["port"]

storage_path = "store/"
if "storage_path" in config:
    storage_path = config["storage_path"]


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if not file:
        return jsonify({"error": "file was not transferred", "result": ""}), 201

    content = file.read()
    # hash content
    hash = get_hash_md5(content)
    pathDir = storage_path + hash[0] + hash[1] + "/"

    # if file exist, return this file
    if os.path.exists(pathDir + hash):
        return jsonify({"error": "", "result": hash}), 201
    # if folder not exist, create this folder
    if not os.path.exists(pathDir):
        os.makedirs(pathDir)

    # save file
    if not write_to_file(pathDir + hash, content):
        jsonify({"error": "write file error", "result": ""}), 201

    return jsonify({"error": "", "result": hash}), 201

# hash function
def get_hash_md5(data):
    hasher = hashlib.md5()
    hasher.update(data)
    return str(hasher.hexdigest())

# method for save file
def write_to_file(name, data):
    try:
        f = open(name, "wb")
        f.write(data)
        f.close()
        return True
    except IOError:
        return False


@app.route('/download/<string:hash>', methods=['GET'])
def download(hash):

    if not hash:
        return jsonify({"error": "hash was not transferred"}), 201

    hash = hash.strip()

    pathFolder = storage_path + hash[0] + hash[1] + "/"

    # if file exists, return this file
    if not os.path.exists(pathFolder + hash):
        return jsonify({"error": "file not exist"}), 201

    return send_file(pathFolder + hash)


@app.route('/delete/<string:hash>', methods=['DELETE'])
def delete(hash):

    if not hash:
        return jsonify({"error": "hash was not transferred", "status": False}), 201

    hash = hash.strip()

    pathFolder = storage_path + hash[0] + hash[1] + "/"

    # if file exists, delete this file
    if not os.path.exists(pathFolder + hash):
        return jsonify({"error": "file not exist"}), 201

    os.remove(pathFolder + hash)

    # if folder is empty, delete this folder
    if len(os.listdir(pathFolder)) == 0:
        os.rmdir(pathFolder)

    return jsonify({"error": "", "status": True}), 201

def runhttpserver():
    app.run(host=host, port=port)


'''if __name__ == '__main__':
    runhttpserver()'''