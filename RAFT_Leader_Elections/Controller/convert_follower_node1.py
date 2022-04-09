import json
import socket
import traceback
import time

# Wait following seconds below sending the controller request
time.sleep(10)

# Read Message Template
msg = json.load(open("Message.json"))

# Initialize
sender = "Controller"
target = "Node1"
port = 5555

# Request
msg['sender_name'] = sender
msg['request'] = "LEADER_INFO"


# Socket Creation and Binding
skt = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
skt.bind((sender, port))

# Send Message
try:
    # Encoding and sending the message
    skt.sendto(json.dumps(msg).encode('utf-8'), (target, port))
except:
    #  socket.gaierror: [Errno -3] would be thrown if target IP container does not exist or exits, write your listener
    print(f"ERROR WHILE SENDING REQUEST ACROSS : {traceback.format_exc()}")

while True:
        message, addr = skt.recvfrom(1024)
        decoded_msg = json.loads(message.decode('utf-8'))
        print(decoded_msg)
        # target1 = decoded_msg['value']
        target1 = "Node2"
        msg['request'] = "TIMEOUT"
        print(f"New Request Created : {msg}")
        msg_bytes = json.dumps(msg).encode('utf-8')
        skt.sendto(msg_bytes, (target1, 5555))




