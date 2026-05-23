import socket
import threading
import sys
import json
import time

if len(sys.argv)<3:
    print("Format:")
    print("python p2p_node.py IP PORT")
    sys.exit()

MY_IP=sys.argv[1]
MY_PORT=int(sys.argv[2])

message_counter=0
lock=threading.Lock()

#################################
# Load Config
#################################

with open("config.json","r") as f:
    config=json.load(f)

KNOWN_PEERS=config["peers"]

#################################
# Load Local Files
#################################

local_files=[]

try:
    with open("shared_files.txt","r") as f:
        local_files=[x.strip() for x in f.readlines()]
except:
    pass


#################################

def write_log(text):

    with open("activity.log","a") as f:
        f.write(
            time.strftime("[%H:%M:%S] ")
            +text+"\n"
        )

#################################

def register_file():

    file=input("Nama file:")

    local_files.append(file)

    with open(
            "shared_files.txt",
            "a"
    ) as f:

        f.write(file+"\n")

    print("File berhasil ditambahkan")


#################################

def handle_client(conn,addr):

    global message_counter

    try:

        data=conn.recv(
            1024
        ).decode()

        if data.startswith(
                "SEARCH"
        ):

            with lock:

                message_counter+=1

            filename=data.split(":")[1]

            print(
            f"\n[REQUEST] {addr} mencari {filename}"
            )

            write_log(
            f"SEARCH {filename} dari {addr}"
            )

            if filename in local_files:

                response=(
                f"FOUND:"
                f"{filename}:"
                f"{MY_IP}:"
                f"{MY_PORT}"
                )

            else:

                response=(
                f"NOTFOUND:{filename}"
                )

            conn.send(
                response.encode()
            )

    except Exception as e:

        print(e)

    finally:

        conn.close()

#################################

def server_mode():

    s=socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    s.bind(
        (MY_IP,MY_PORT)
    )

    s.listen(5)

    print(
    f"\nNode aktif "
    f"{MY_IP}:{MY_PORT}"
    )

    while True:

        conn,addr=s.accept()

        t=threading.Thread(
            target=handle_client,
            args=(conn,addr)
        )

        t.daemon=True

        t.start()


#################################

def response_handler(data):

    token=data.split(":")

    if token[0]=="FOUND":

        print(
        f"\n[FILE DITEMUKAN]"
        )

        print(
        f"Nama File : {token[1]}"
        )

        print(
        f"Pemilik : {token[2]}"
        )

        print(
        f"Port : {token[3]}"
        )

#################################

def search_file(filename):

    for p_ip,p_port in KNOWN_PEERS:

        if(
            p_ip==MY_IP
            and
            p_port==MY_PORT
        ):
            continue

        try:

            c=socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            c.settimeout(2)

            c.connect(
                (p_ip,p_port)
            )

            msg=f"SEARCH:{filename}"

            c.send(
                msg.encode()
            )

            response=(
                c.recv(1024)
                .decode()
            )

            if(
                response.startswith(
                    "FOUND"
                )
            ):

                response_handler(
                    response
                )

            c.close()

        except Exception:

            print(
            f"[ERROR]"
            f"{p_ip}"
            f" tidak aktif"
            )


#################################

threading.Thread(
target=server_mode,
daemon=True
).start()

while True:

    print("\n=====MENU=====")

    print("1.Register File")

    print("2.Search File")

    print("3.Lihat File")

    print("4.Total Search")

    print("5.Exit")

    pilihan=input(
    "Pilih:"
    )

    if pilihan=="1":

        register_file()

    elif pilihan=="2":

        nama=input(
        "Nama file:"
        )

        search_file(
            nama
        )

    elif pilihan=="3":

        print(
            local_files
        )

    elif pilihan=="4":

        print(
        f"Jumlah request:"
        f"{message_counter}"
        )

    else:

        break