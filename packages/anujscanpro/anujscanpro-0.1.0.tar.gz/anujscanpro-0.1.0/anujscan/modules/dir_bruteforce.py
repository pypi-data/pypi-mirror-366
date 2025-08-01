import requests
from core import logger

def run(domain):
    logger.log(f"Running directory brute-force on: {domain}")
    paths = ["admin", "login", "dashboard", "test", "backup"]
    url = f"http://{domain.strip('/')}"
    found = []

    for path in paths:
        full_url = f"{url}/{path}"
        try:
            res = requests.get(full_url, timeout=3)
            if res.status_code == 200:
                logger.log(f"Found: {full_url} [Status: 200]", "SUCCESS")
                found.append(full_url)
            elif res.status_code in [301, 302]:
                logger.log(f"Redirect: {full_url} [Status: {res.status_code}]", "INFO")
        except:
            continue

    return {"target": domain, "directories_found": found}
