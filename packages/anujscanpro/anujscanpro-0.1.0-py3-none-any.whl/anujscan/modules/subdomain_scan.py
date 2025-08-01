import requests
from core import logger

def run(domain):
    logger.log(f"Scanning subdomains for: {domain}", "INFO")
    wordlist = ["www", "mail", "ftp", "test", "dev"]
    found = []

    for sub in wordlist:
        url = f"http://{sub}.{domain}"
        try:
            res = requests.get(url, timeout=2)
            logger.log(f"Found: {url}", "SUCCESS")
            found.append(url)
        except:
            pass

    if not found:
        logger.log("No subdomains found.", "ERROR")

    return {"target": domain, "subdomains": found}
