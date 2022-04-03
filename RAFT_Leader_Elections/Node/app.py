import socket
import time
import threading
import json
import traceback
import os
import random

IS_LEADER = os.environ['IS_LEADER']
IS_Follower = os.environ['IS_Follower']
IS_Candidate = os.environ['IS_Candidate']
Sender = os.environ['Sender']
Term = os.environ['Term']
Current_term = 0
Voted_for = ""
Log = []
timeout = random.randrange(250,350)
heartbeat = 100



# Listener
def listener(skt):
    if IS_Follower == "True":
        while True:
            skt.settimeout(timeout)
            try:
                msg, addr = skt.recvfrom(1024)
                decoded_msg = json.loads(msg.decode('utf-8'))
                if decoded_msg["request"] == "VOTE_REQUEST" and decoded_msg["term"] <= Term:
                    message = {"sender_name": Sender, "request": "VOTE_ACK", "term": term, "key": null, "value": null}
                    msg_bytes = json.dumps(message).encode()
                    skt.sendto(msg_bytes, (addrr, 1111))
                    term += 1
            except socket.timeout:
                print(f"ERROR while fetching from socket : {traceback.print_exc()}")
            
        

            if decoded_msg["request"] == "TIMEOUT":
                time.sleep(timeout)
        


    print("Exiting Listener Function")

# Dummy Function
def AppendRPC(skt):
    # for i in range(5):
    #     print(f"Hi Executing Dummy function : {i}")
    #     time.sleep(2)
    msg = {"LeaderID": Sender, "request": "APPEND_RPC", "term": term, "Entries": [], "prevLogIndex": -1, "prevLogTerm": -1}
    msg_bytes = json.dumps(msg).encode()

    if Sender == "Node1":
        target1 = "Node2"
        target2 = "Node3"
    elif Sender == "Node2":
        target1 = "Node1"
        target2 = "Node3"
    elif Sender == "Node3":
        target1 = "Node1"
        target2 == "Node2"

    while True:
        skt.sendto(msg_bytes, (target1, 5555))
        skt.sendto(msg_bytes, (target2, 5555))
        time.sleep(heartbeat)




if __name__ == "__main__":
    print(f"Starting {Sender}")


    # Creating Socket and binding it to the target container IP and port
    UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind the node to sender ip and port
    UDP_Socket.bind((Sender, 5555))

    if IS_Follower == "true":
        threading.Thread(target=listener, args=[UDP_Socket]).start()

    if IS_LEADER == "true":
        threading.Thread(target=AppendRPCR, args=[UDP_Socket]).start()
        UDP_Socket1 = bind((Sender),1111)
        threading.Thread(target=listener, args=[UDP_Socket1]).start()

    print("Started both functions, Sleeping on the main thread for 10 seconds now")
    time.sleep(10)
    print(f"Completed Node Main Thread Node 2")
