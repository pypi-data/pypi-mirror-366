# mymodule.py
import argparse, threading, keyboard, time
from kvserver.server import KivyLiveServer


def start_server(server):
    while True:
        server.recv_conn()

def main():
    parser = argparse.ArgumentParser(description="A simple greeting module.")
    parser.add_argument("port", nargs="?", type=int, default=7000, help="The port to run the server on (default: 5000)")
    args = parser.parse_args()
    
    server = KivyLiveServer(args.port)
    threading.Thread(target=lambda:start_server(server), daemon=True).start()
    time.sleep(.1)
    # print("Press R to reload\n ")
    print(f"\n\n Press Q to exit")
    while True:
        key = keyboard.read_key()
        # if key == "r" or key == "R":
        #     print(f"Reloading...")
        #     server.on_reload()
        if key == "q" or key == "Q":
            break



if __name__ == "__main__":
    main()


