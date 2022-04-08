import socket
import time
import threading
import json
import traceback
import os
from random import uniform

IS_LEADER = os.environ['IS_LEADER']
IS_Follower = os.environ['IS_Follower']
IS_Candidate = os.environ['IS_Candidate']

IS_Node1 = os.environ['IS_Node1']
IS_Node2 = os.environ['IS_Node2']
IS_Node3 = os.environ['IS_Node3']
IS_Node4 = os.environ['IS_Node4']
IS_Node5 = os.environ['IS_Node5']

Sender = ''
if IS_Node1 == "true":
    Sender = "Node1"
elif IS_Node2 == "true":
    Sender = "Node2"
elif IS_Node3 == "true":
    Sender = "Node3"
elif IS_Node4 == "true":
    Sender = "Node4"
elif IS_Node5 == "true":
    Sender = "Node5"

Term = 0
Voted_for = ""
Log = []
timeout = uniform(20.1,35.9)
heartbeat = 10
Votes = 0
Stop_Thread = False


# Listener
def listener(skt):
    global IS_Follower, IS_Candidate, Votes, Voted_for, Term
    print(f"Listener started for:{Sender}")
    # if IS_Follower == "true":
    #     skt.settimeout(timeout)
    while True:
        skt.settimeout(timeout)
        try:
            msg, addr = skt.recvfrom(1024)
            decoded_msg = json.loads(msg.decode('utf-8'))
            print(f"Request recieved: {decoded_msg['request']}, Term: {decoded_msg['term']}")

            if decoded_msg["request"] == "APPEND_RPC" and Term <= decoded_msg["term"]:
                print(f"HeartBeat Recieved from {decoded_msg['LeaderID']}")
                Voted_for = ""
                if Term < decoded_msg["term"]:
                    Term = decoded_msg["term"]
                Votes = 0

            if decoded_msg["request"] == "VOTE_REQUEST" and decoded_msg["term"] >= Term and Voted_for=="":
                print(f'{decoded_msg["sender_name"]} asking for votes...')
                Stop_Thread = True
                message = {"sender_name": Sender, "request": "VOTE_ACK", "term": Term, "key": 0, "value": 0}
                msg_bytes = json.dumps(message).encode('utf-8')
                # print(f"Message Bytes: {msg_bytes}")
                # print(f"Address: {addr[0]}")
                skt.sendto(msg_bytes, (addr[0], 5555))
                Voted_for = addr[0]


            if IS_Candidate == "true":
                if decoded_msg["request"] == "VOTE_ACK" and decoded_msg["term"] <= Term:
                    print(f"{decoded_msg['sender_name']} sent a vote")
                    if Votes > 2:
                        IS_Candidate = "false"
                        IS_LEADER = "true"
                        print(f"New Leader Elected {Sender}")
                        Vote = 0
                        Stop_Thread = False

                        threading.Thread(target=appendRPC, args=[UDP_Socket]).start()
                    else:
                        Votes += 1
        except socket.timeout:
            if IS_Follower=="true":
                print(f"Timed out..starting Election")
                Votes += 1
                Term += 1
                IS_Follower = "false"
                IS_Candidate = "true"
                Voted_for = Sender
                if Sender == "Node1":
                    target1 = "Node2"
                    target2 = "Node3"
                    target3 = "Node4"
                    target4 = "Node5"
                elif Sender == "Node2":
                    target1 = "Node1"
                    target2 = "Node3"
                    target3 = "Node4"
                    target4 = "Node5"
                elif Sender == "Node3":
                    target1 = "Node1"
                    target2 = "Node2"
                    target3 = "Node4"
                    target4 = "Node5"
                elif Sender == "Node4":
                    target1 = "Node1"
                    target2 = "Node2"
                    target3 = "Node3"
                    target4 = "Node5"
                elif Sender == "Node5":
                    target1 = "Node1"
                    target2 = "Node2"
                    target3 = "Node3"
                    target4 = "Node4"


                threading.Thread(target=Voting, args=[target1, target2, target3, target4]).start()


def Voting(reciever1, reciever2, reciever3, reciever4):

    Voting_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    sender_ip = socket.gethostbyname(Sender)

    Voting_Socket.bind((sender_ip, 1111))

    msg = {"sender_name": Sender, "request": "VOTE_REQUEST", "term": Term, "key": None, "value": None,
           "lastLogIndex": 0, "lastLogTerm": 0}

    msg_bytes = json.dumps(msg).encode('utf-8')

    r1 = socket.gethostbyname(reciever1)
    r2 = socket.gethostbyname(reciever2)
    r3 = socket.gethostbyname(reciever3)
    r4 = socket.gethostbyname(reciever4)

    Voting_Socket.sendto(msg_bytes, (r1, 5555))
    Voting_Socket.sendto(msg_bytes, (r2, 5555))
    Voting_Socket.sendto(msg_bytes, (r3, 5555))
    Voting_Socket.sendto(msg_bytes, (r4, 5555))

    Voting_Socket.close()

def appendRPC(skt):
    # for i in range(5):
    #     print(f"Hi Executing Dummy function : {i}")
    #     time.sleep(2)
    global target2, target1, target3, target4, Voted_for
    Voted_for = ""
    msg = {"LeaderID": Sender, "request": "APPEND_RPC", "term": Term, "Entries": [], "prevLogIndex": -1, "prevLogTerm": -1}
    msg_bytes = json.dumps(msg).encode('utf-8')

    if Sender == "Node1":
        target1 = "Node2"
        target2 = "Node3"
        target3 = "Node4"
        target4 = "Node5"
    elif Sender == "Node2":
        target1 = "Node1"
        target2 = "Node3"
        target3 = "Node4"
        target4 = "Node5"
    elif Sender == "Node3":
        target1 = "Node1"
        target2 = "Node2"
        target3 = "Node4"
        target4 = "Node5"
    elif Sender == "Node4":
        target1 = "Node1"
        target2 = "Node2"
        target3 = "Node3"
        target4 = "Node5"
    elif Sender == "Node5":
        target1 = "Node1"
        target2 = "Node2"
        target3 = "Node3"
        target4 = "Node4"

    t1 = socket.gethostbyname(target1)
    t2 = socket.gethostbyname(target2)
    t3 = socket.gethostbyname(target3)
    t4 = socket.gethostbyname(target4)

    while True:
        skt.sendto(msg_bytes, (t1, 5555))
        skt.sendto(msg_bytes, (t2, 5555))
        skt.sendto(msg_bytes, (t3, 5555))
        skt.sendto(msg_bytes, (t4, 5555))
        time.sleep(heartbeat)
        if Stop_Thread:
            break



if __name__ == "__main__":
    print(f"Starting {Sender}")


    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    host_ip = socket.gethostbyname(Sender)

    # Bind the node to sender ip and port
    UDP_Socket.bind((host_ip, 5555))

    threading.Thread(target=listener, args=[UDP_Socket]).start()

    # time.sleep(100000)

