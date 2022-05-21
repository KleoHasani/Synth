from dataclasses import dataclass
from socket import socket
from typing import Tuple

from synth.types.Address import Address

@dataclass
class Connection:
    client: socket
    address: Tuple[socket, Address]
