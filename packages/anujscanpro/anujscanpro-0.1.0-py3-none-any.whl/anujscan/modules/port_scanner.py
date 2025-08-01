import socket
from core import logger

def run(target):
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 8080]
    open_ports = []

    logger.log(f"Scanning ports for: {target}", "INFO")

    for port in ports:
        try:
            sock = socket.socket()
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            if result == 0:
                logger.log(f"Port {port} is OPEN", "SUCCESS")
                open_ports.append(port)
            sock.close()
        except Exception as e:
            logger.log(f"Error on port {port}: {e}", "ERROR")

    return {"target": target, "open_ports": open_ports}
