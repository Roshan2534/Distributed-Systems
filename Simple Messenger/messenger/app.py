from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
import pymongo

app = Flask(__name__)
api = Api(app)


client = pymongo.MongoClient(host='test_mongodb',
                         port=27017,
                         username='root',
                         password='pass',
                        authSource="admin")
db = client["SentencesDatabase"]
users = db["Users"]

# A decorator used to tell the application
# which URL is associated function

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/view', methods=["GET", "POST"])
def view_message():
    sentence = users.find({}, {
                "message": 1
    })
    messages = []
    for i in sentence:
        messages.append(i["message"])
    return render_template("messages.html",data = list(enumerate(messages)))


@app.route('/submitdata', methods=["POST"])
def insert_message():
    message = request.form.get("message")
    users.insert_one({
                    "message": message,
    })
    return render_template("form.html", data = "Your Message has been submitted")

@app.route('/', methods=["GET"])
def main_page():
    return render_template("form.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4500)
