import requests
from core import logger

def run(domain):
    url = f"http://{domain}"
    logger.log(f"Fetching headers for: {url}", "INFO")
    headers = {}
    try:
        res = requests.get(url, timeout=5)
        for k, v in res.headers.items():
            print(f"{k}: {v}")
            headers[k] = v
    except Exception as e:
        logger.log(f"Error: {e}", "ERROR")
        return {"error": str(e)}

    return {"url": url, "headers": headers}
