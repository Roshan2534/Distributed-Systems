from flask import Flask, request, render_template
import flask
from flask_restful import Api
import pymongo, requests
import os


app = Flask(__name__)
api = Api(app)

IS_LEADER = os.environ['IS_LEADER']
IS_Node1 = os.environ['IS_Node1']
IS_Node2 = os.environ['IS_Node2']


if (IS_LEADER=="true"):
    client = pymongo.MongoClient(host='test_mongodb',
                                 port=27017,
                                 authSource="admin")
    db = client["SentencesDatabase"]
    users = db["Users"]

elif (IS_Node1=="true"):
    client = pymongo.MongoClient(host='test_mongodb1',
                                 port=27017,
                                 authSource="admin")
    db = client["SentencesDatabase"]
    users = db["Users"]

elif (IS_Node2=="true"):
    client = pymongo.MongoClient(host='test_mongodb2',
                                 port=27017,
                                 authSource="admin")
    db = client["SentencesDatabase"]
    users = db["Users"]


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/view', methods=["GET", "POST"])
def view_message():
    if IS_LEADER=="true":
        ip_address = flask.request.remote_addr
        address = []
        address1 = []
        ip = ""
        ip1 = ""
        for i in str(ip_address):
            address.append(i)
            address1.append(i)

        temp = int(address[-1])
        temp += 5
        address[-1] = str(temp)
        for i in address:
            ip += str(i)
        x = requests.get(f"http://{ip}:4600/view")
        node1ID = x.text.split()

        temp1 = int(address1[-1])
        temp1 += 6
        address1[-1] = str(temp1)
        for i in address1:
            ip1 += str(i)
        y = requests.get(f"http://{ip1}:4700/view")
        node2ID = y.text.split()

        sentence = users.find({}, {
            "_id": 1
        })

        message = users.find({}, {
            "message": 1
        })

        LID = ""
        for i in sentence:
            LID += (f"{i['_id']} ")
        IDLeader = LID.split()

        messages = []
        for i in message:
            messages.append(i["message"])

        return render_template("messages.html", messages=messages, LID=IDLeader, Node1=node1ID, Node2=node2ID, zip=zip)
    else:
        IDS = users.find({}, {
            "_id": 1
        })
        ID = ""
        for i in IDS:
            ID += (f"{i['_id']} ")
        return str(ID)


@app.route('/submitdata', methods=["POST"])
def insert_message():
    message = request.form.get("message")
    if IS_LEADER=="true":
        ip_address = flask.request.remote_addr

        address = []
        address1 = []
        ip = ""
        ip1 = ""
        for i in str(ip_address):
            address.append(i)
            address1.append(i)
        temp = int(address[-1])
        temp += 5
        address[-1] = str(temp)
        for i in address:
            ip += str(i)
        x = requests.post(f"http://{ip}:4600/nodes_insert", json={"message": message})

        temp1 = int(address1[-1])
        temp1 += 6
        address1[-1] = str(temp1)
        for i in address1:
            ip1 += str(i)
        y = requests.post(f"http://{ip1}:4700/nodes_insert", json={"message": message})
        users.insert_one({
            "message": message,
        })
        z = users.find_one({"message": message})
        ID = str(z.get("_id"))

        return render_template("form.html", data=f"The leader node has stored the message with ID: {ID} \n The First Node has stored the message with ID: {x.text} \n The Second Node has stored the message with ID: {y.text}")


@app.route('/nodes_insert', methods=["POST"])
def nodes_insert():
    message1 = request.json['message']
    users.insert_one({
        "message": message1,
    })
    x = users.find_one({"message": message1})
    return str(x.get("_id"))

@app.route('/', methods=["GET"])
def main_page():
    if IS_LEADER=="true":
        return render_template("form.html")
    elif IS_Node1=="true":
        return "You are not Allowed to access this page"
    elif IS_Node2=="true":
        return "You are not Allowed to access this page"



if __name__ == '__main__':
    if IS_LEADER=="true":
        app.run(host="0.0.0.0", port=4500)
    elif IS_Node1 =="true":
        app.run(host="0.0.0.0", port=4600)
    elif IS_Node2 =="true":
        app.run(host="0.0.0.0", port=4700)

