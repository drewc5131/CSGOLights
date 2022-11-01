import json

from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods = ["POST"])
def main():
    with open('csgo.json', 'w') as f:
        f.write(str(json.dumps(json.loads(request.data))))
        print(request.data)
    return ''


if __name__ == "__main__":
    app.run(port = 8080, debug = True)
