import os, select, socket, pickle, time
from qrcode_term import qrcode_string
from json import dumps
from time import sleep
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from kvserver.soc_ip import wlan_ip
from threading import Thread

"""Constants Variables"""
text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
is_binary = lambda byte: bool(byte.translate(None, text_chars))
observer_path = os.getcwd()
print(observer_path)
# observer_path = "."
ip = "127.0.0.1"

class KivyLiveServer(FileSystemEventHandler):
    def __init__(self, port, **kwargs):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((wlan_ip, port))
        except:
            self.server_socket.bind((ip, port))
        if wlan_ip == "[Errno 101]":
            print(f"\nSERVER RUNNING...\nWLAN ADDR: kvc://\nLOCAL ADDR: kvc://{ip}:{port}")
        else:
            print(f"\nSERVER RUNNING...\nWLAN ADDR: kvc://{wlan_ip}:{port}\nLOCAL ADDR: kvc://{ip}:{port}")
        
        """QR CODE"""
        print("         OR          \nScan the Qr-code to connect\n\n")
        
        if not wlan_ip == "[Errno 101]":
            txt = f"kvc://{wlan_ip}:{port}"
            b = qrcode_string(txt, frame_width=1,ansi_white=False)
            print(b)
        else:
            txt = f"kvc://{ip}:{port}"
            b = qrcode_string(txt, frame_width=1,ansi_white=False)
            print(b)
        
        self.already_send = False
        
        
        self.server_socket.listen()
        self.socket_list = [self.server_socket]
        self.client = {}
        self.HEADER_LENGTH = 64
        Thread(target=self._observer, daemon=True).start()

    def _observer(self):
        observer = Observer()
        observer.schedule(self, path=observer_path, recursive=True)
        observer.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    
    """Handles delete events"""
    def on_deleted(self, event):
        self.filepath = event.src_path
        for clients in self.client:
            try:
                data_ = {
                        "cmd":"DELETE",
                        "path":self.filepath
                    }
                self.client[clients].send(dumps(data_).encode("utf-8"))
            except ConnectionResetError as e:
                print(e)
                print(f"{clients}:, Disconnected.")
            except socket.error as e:
                pass
                # print(e)
                # print(f"Error while sending data to \'[{clients}\', check connection.")
                    
    """Create new file or folder here"""
    def on_created(self, event):
        self.filepath = event.src_path
        init_size = -1
        if os.path.exists(self.filepath):
            while True:
                current_size = os.path.getsize(self.filepath)
                # print(current_size)
                if current_size == init_size:
                    break
                else:
                    init_size = os.path.getsize(self.filepath)
                    time.sleep(2)
        if not event.is_directory:
            try:
                binary = is_binary(open(self.filepath, "rb").read(1024))
                with open(self.filepath, "rb" if binary else "r") as file:
                    code_data = file.read()
                    
                for clients in self.client:
                    try:
                        data_ = {
                            "cmd":"MODIFY",
                            "path":os.path.relpath(self.filepath)
                        }
                        self.client[clients].send(dumps(data_).encode("utf-8"))
                        self.client[clients].send(pickle.dumps(code_data))
                        self.client[clients].send(b"<FINISH_INITIAL_LOAD>")
                        self.already_send = True
                    except ConnectionResetError as e:
                        print(e)
                        print(f"{clients}:, Disconnected.")
                    except socket.error as e:
                        pass
                        # print(e)
                        # print(f"Error while sending data to \'[{clients}\', check connection.")
            except:pass     
                
        elif event.is_directory:
            for clients in self.client:
                try:
                    self.client[clients].send(
                    dumps({"cmd":"CREATE", "data": self.filepath}).encode("utf-8")
                    )
                except ConnectionResetError as e:
                    print(e)
                    print(f"{clients}:, Disconnected.")
                except socket.error as e:
                    pass
                    # print(e)
                    # print(f"Error while sending data to \'[{clients}\', check connection.")
                    
            
    """Handles changes made to the source code"""
    def on_modified(self, event):
        self.filepath = event.src_path
        if not event.is_directory:
            try:
                binary = is_binary(open(self.filepath, "rb").read(1024))
                with open(self.filepath, "rb" if binary else "r") as file:
                    code_data =  file.read()
                
                for clients in self.client:
                    try:
                        data_ = {
                            "cmd":"MODIFY",
                            "path":os.path.relpath(self.filepath)
                        }
                        if not self.already_send:
                            self.client[clients].send(dumps(data_).encode("utf-8"))
                            self.client[clients].send(pickle.dumps(code_data))
                            self.client[clients].send(b"<FINISH_INITIAL_LOAD>")
                        else:
                            self.already_send = False
                    except ConnectionResetError as e:
                        print(e)
                        print(f"{clients}:, Disconnected.")
                    except socket.error as e:
                        pass
                        # printr(e)
                        # print(f"Error while sending data to \'[{clients}\', check connection.")
            except:pass                  

    def on_reload(self):
        for clients in self.client:
            try:
                data_ = {
                    "cmd":"RELOAD"
                }
                self.client[clients].send(dumps(data_).encode("utf-8"))
                # Thread(target=self.recv_msg, args=(self.client[clients], "")).start()
            except ConnectionResetError as e:
                self.client[clients].close()
                # self.client.pop(clients)
                print(clients)
                print(self.client)
                print(e)
                print(f"{clients}:, Disconnected.")
            except socket.error as e:
                pass
                # print(e)
                # Logger.e
    
    def recv_conn(self):
        read_socket, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)
        for notified_socket in read_socket:
            if notified_socket == self.server_socket:
                client_socket, client_address = self.server_socket.accept()
                #Logger.info(f"NEW CONNECTION: [ADDR]: {client_address[0]}:{client_address[1]}")
                self.socket_list.append(client_socket)
                # self.client.update({f"{client_address[0]}:{client_address[1]}": client_socket})
                self.client = {f"{client_address[0]}:{client_address[1]}": client_socket}
                Thread(target=self.recv_msg, args=(client_socket, client_address)).start()

    def recv_msg(self, client_socket, address):
        file_dir = {}
        for folder, _, file in os.walk(observer_path):
            dir = folder.replace(observer_path, "")
            if dir != "" or dir.startswith("/") or dir.startswith("\\"):
                dir = folder.replace(observer_path+"\\", "").replace(observer_path+"/", "")
            
            if (not file) or folder.startswith("./.") or folder == "__pycache__":
                continue
            for i in file:
                if i.count(".")<=1 and i != "server.py" and i != "win_ip.py":
                    binary = is_binary(open(os.path.join(folder, i), "rb").read(1024))
                    with open(os.path.join(folder, i), "rb" if binary else "r") as f:
                        
                        file_dir.update({os.path.join(dir, i): f.read()})
        data = pickle.dumps(file_dir)
        client_socket.send(f"{len(data):<{self.HEADER_LENGTH}}".encode())
        client_socket.send(data)
        client_socket.send(b"<FINISH_INITIAL_LOAD>")


    