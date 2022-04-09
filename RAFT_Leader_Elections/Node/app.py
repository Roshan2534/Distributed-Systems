import socket
import time
import threading
import json
import traceback
import os
from random import uniform, randint

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
timeout = uniform(6.1,8.5)
heartbeat = 1
Votes = 0
Stop_Thread = False
Leader = ""
stop_listener = False

# Listener
def listener(skt):
    global IS_Follower, IS_Candidate, Votes, Voted_for, Term, IS_LEADER, Stop_Thread, Leader, stop_listener
    print(f"Listener started for:{Sender}")
    # if IS_Follower == "true":
    #     skt.settimeout(timeout)
    while True:
        if stop_listener == True:
            break
        skt.settimeout(timeout)
        try:
            msg, addr = skt.recvfrom(1024)
            decoded_msg = json.loads(msg.decode('utf-8'))
            print(f"Request recieved: {decoded_msg['request']}, Term: {decoded_msg['term']}, Sender: {decoded_msg['sender_name']}")

            if decoded_msg["request"] == "APPEND_RPC" and Term > decoded_msg["term"]:
                print(f"Leader has smaller term {decoded_msg['term']}..Starting Election")
                if IS_LEADER == "true":
                    IS_LEADER = "false"
                    Stop_Thread = True
                if IS_Follower == "true":
                    print(f"Timed out..starting Election")
                    Votes += 1
                    Term += 1
                    IS_Follower = "false"
                    IS_Candidate = "true"
                    Voted_for = Sender

                    threading.Thread(target=Voting, args=[Sender]).start()

            elif decoded_msg["request"] == "APPEND_RPC":
                if IS_LEADER == "true":
                    IS_LEADER = "false"
                    IS_Follower = "true"
                    Stop_Thread = True
                if decoded_msg["term"] > Term:
                    Term = decoded_msg["term"]
                if IS_Candidate == "true" and decoded_msg["term"] >= Term:
                    IS_Candidate = "false"
                    IS_Follower = "true"
                if IS_LEADER == "true":
                    Stop_Thread = True
                print(f"HeartBeat Received from {decoded_msg['LeaderID']}")
                Leader = decoded_msg["LeaderID"]
                Voted_for = ""
                Votes = 0

            if decoded_msg["request"] == "CONVERT_FOLLOWER":
                if IS_Candidate == "true":
                    print("Candidate going to be Follower!")
                    IS_Candidate = "false"
                    IS_Follower = "true"
                elif IS_LEADER == "true":
                    print("Leader going to be Follower!")
                    Stop_Thread = True
                    IS_LEADER = "false"
                    IS_Follower = "true"
                elif IS_Follower == "true":
                    print("Already a FOllower!")
                    continue

            if decoded_msg["request"] == "LEADER_INFO":
                message = {"sender_name": Sender, "request": None, "term": None, "key": "LEADER", "value": Leader}
                msg_bytes = json.dumps(message).encode('utf-8')

                skt.sendto(msg_bytes, (addr[0], 5555))

            if decoded_msg["request"] == "TIMEOUT":
                print(f"Timing out {Sender}")
                raise socket.timeout


            if decoded_msg["request"] == "SHUTDOWN":
                print(f'Shutting down all threads on {Sender}')
                skt.close()
                Stop_Thread = True
                stop_listener = True

            if decoded_msg["request"] == "VOTE_REQUEST" and decoded_msg["term"] >= Term and Voted_for=="":
                print(f'{decoded_msg["sender_name"]} asking for votes...')
                if IS_LEADER == "true":
                    IS_LEADER = "false"
                    IS_Follower = "true"
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
                    if Votes > 2 and IS_Candidate == "true":
                        IS_Candidate = "false"
                        IS_LEADER = "true"
                        print(f"New Leader Elected {Sender}")
                        Votes = 0
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

                threading.Thread(target=Voting, args=[Sender]).start()


def Voting(sender):
    sender1 = sender

    r1, r2, r3, r4 = getTarget(sender1)

    Voting_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    sender_ip = socket.gethostbyname(Sender)

    Voting_Socket.bind((sender_ip, 1111))

    msg = {"sender_name": Sender, "request": "VOTE_REQUEST", "term": Term, "key": None, "value": None,
           "lastLogIndex": 0, "lastLogTerm": 0}

    msg_bytes = json.dumps(msg).encode('utf-8')

    if r1 != None:
        Voting_Socket.sendto(msg_bytes, (r1, 5555))

    if r2 != None:
        Voting_Socket.sendto(msg_bytes, (r2, 5555))

    if r3 != None:
        Voting_Socket.sendto(msg_bytes, (r3, 5555))

    if r4 != None:
        Voting_Socket.sendto(msg_bytes, (r4, 5555))

    Voting_Socket.close()

def appendRPC(skt):
    global target2, target1, target3, target4, Voted_for, Stop_Thread, Leader
    if IS_LEADER == "true":
        Leader = Sender
    Voted_for = ""
    msg = {"sender_name": Sender, "LeaderID": Sender, "request": "APPEND_RPC", "term": Term, "Entries": [], "prevLogIndex": -1, "prevLogTerm": -1}
    msg_bytes = json.dumps(msg).encode('utf-8')

    r1, r2, r3, r4 = getTarget(Sender)

    while True:
        # if Stop_Thread == True:
        #     print(f'{Sender} no longer leader, no heartbeats')
        #     break
        if Stop_Thread == True:
            print(f'{Sender} no longer leader, no heartbeats')
            break

        if r1 != None:
            skt.sendto(msg_bytes, (r1, 5555))

        if r2 != None:
            skt.sendto(msg_bytes, (r2, 5555))

        if r3 != None:
            skt.sendto(msg_bytes, (r3, 5555))

        if r4 != None:
            skt.sendto(msg_bytes, (r4, 5555))

        time.sleep(heartbeat)


def getTarget(sender):
    sender1 = sender

    if sender1 == "Node1":
        target1 = "Node2"
        target2 = "Node3"
        target3 = "Node4"
        target4 = "Node5"
    elif sender1 == "Node2":
        target1 = "Node1"
        target2 = "Node3"
        target3 = "Node4"
        target4 = "Node5"
    elif sender1 == "Node3":
        target1 = "Node1"
        target2 = "Node2"
        target3 = "Node4"
        target4 = "Node5"
    elif sender1 == "Node4":
        target1 = "Node1"
        target2 = "Node2"
        target3 = "Node3"
        target4 = "Node5"
    elif sender1 == "Node5":
        target1 = "Node1"
        target2 = "Node2"
        target3 = "Node3"
        target4 = "Node4"

    try:
        r1 = socket.gethostbyname(target1)
    except socket.gaierror:
        r1 = None
        print(f"Host Closed {target1}")

    try:
        r2 = socket.gethostbyname(target2)
    except socket.gaierror:
        r2 = None
        print(f"Host Closed {target2}")

    try:
        r3 = socket.gethostbyname(target3)
    except socket.gaierror:
        r3 = None
        print(f"Host Closed {target3}")

    try:
        r4 = socket.gethostbyname(target4)
    except socket.gaierror:
        r4 = None
        print(f"Host Closed {target4}")

    return r1, r2, r3, r4


if __name__ == "__main__":
    print(f"Starting {Sender}")


    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    host_ip = socket.gethostbyname(Sender)

    # Bind the node to sender ip and port
    UDP_Socket.bind((host_ip, 5555))

    threading.Thread(target=listener, args=[UDP_Socket]).start()

    # time.sleep(100000)

