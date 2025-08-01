import ssl
import socket
from core import logger
from datetime import datetime

def run(domain):
    context = ssl.create_default_context()
    cert_info = {}

    try:
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                cert_info["issuer"] = str(cert.get("issuer"))
                cert_info["subject"] = str(cert.get("subject"))
                cert_info["valid_from"] = cert.get("notBefore")
                cert_info["valid_to"] = cert.get("notAfter")

                expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry - datetime.utcnow()).days
                cert_info["days_until_expiry"] = days_left

                for k, v in cert_info.items():
                    logger.log(f"{k}: {v}", "INFO")

    except Exception as e:
        logger.log(f"SSL error: {e}", "ERROR")
        return {"error": str(e)}

    return {"target": domain, "certificate": cert_info}
