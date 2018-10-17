from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import urllib
import re
import json
import hashlib
import os
import json

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

class RestHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if None != re.search('/upload*', self.path):

            result = {"result": "", "error": ""}
            length = int(self.headers.get('content-length'))

            data = self.rfile.read(length)

            if data:
                # hash content
                hash = self.get_hash_md5(data)

                pathDir = storage_path + hash[0] + hash[1] + "/"

                # if file exist, return this file
                if os.path.exists(pathDir + hash):
                    result["result"] = hash
                    self.wfile.write(json.dumps(result).encode())
                    return

                # if folder not exist, create this folder
                if not os.path.exists(pathDir):
                    os.makedirs(pathDir)

                # save file
                if not self.write_to_file(pathDir + hash, data):
                    result["error"] = "write file error"
                    self.wfile.write(json.dumps(result).encode())
                    return


                result["result"] = hash
                self.wfile.write(json.dumps(result).encode())
                return
            else:
                result["error"] = "data file not found"
                self.wfile.write(json.dumps(result).encode())
                return

    # hash function
    def get_hash_md5(self, data):
        hasher = hashlib.md5()
        hasher.update(data)
        return str(hasher.hexdigest())

    # method for save file
    def write_to_file(self, name, data):
        try:
            f = open(name, "wb")
            f.write(data)
            f.close()
            return True
        except IOError:
            return False

    def do_GET(self):
        result = {"error": ""}
        if None != re.search('/download*', self.path):
            # get hash from address
            hashFile = self.path.split('/')[-1]
            if hashFile == "download" or hashFile == "":
                result["error"] = "not found hash file parameter"
                self.wfile.write(json.dumps(result).encode())
                return

            # if file exists, open file and return data
            path = storage_path + hashFile[0] + hashFile[1] + "/" + hashFile
            if not os.path.exists(path):
                result["error"] = "file not found"
                self.wfile.write(json.dumps(result).encode())
                return

            self.send_response(200)
            self.send_header('Content-Disposition', 'attachment; filename="' + hashFile + '"')
            self.end_headers()

            try:
                filecontent = open(path, 'rb').read()
                self.wfile.write(filecontent)
                return
            except IOError:
                result["error"] = "read file error"
                self.wfile.write(json.dumps(result).encode())
                return

        else:
            result["error"] = "method not found"
            self.wfile.write(json.dumps(result).encode())
            return


    def do_DELETE(self):
        result = {"error": "", "result": False}
        if None != re.search('/delete*', self.path):
            # get hash from address
            hashFile = self.path.split('/')[-1]

            if hashFile == "delete" or hashFile == "":
                result["error"] = "not found hash file parameter"
                self.wfile.write(json.dumps(result).encode())
                return

            path = storage_path + hashFile[0] + hashFile[1] + "/"

            # if file exists, delete file
            if not os.path.exists(path + hashFile):
                result["error"] = "file not found"
                self.wfile.write(json.dumps(result).encode())
                return

            self.send_response(200)
            self.end_headers()

            os.remove(path + hashFile)

            # if folder is empty, delete folder
            if len(os.listdir(path)) == 0:
                os.rmdir(path)

            result["result"] = True
            self.wfile.write(json.dumps(result).encode())
            return

        else:
            result["error"] = "method not found"
            self.wfile.write(json.dumps(result).encode())
            return


'''if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 6000), RestHTTPRequestHandler)
    while True:
        httpd.handle_request()'''
def runserver():
    httpd = HTTPServer((host, port), RestHTTPRequestHandler)
    while True:
        httpd.handle_request()