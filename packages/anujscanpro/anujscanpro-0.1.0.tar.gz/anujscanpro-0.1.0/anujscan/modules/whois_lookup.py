import whois
from core import logger

def run(domain):
    logger.log(f"Running WHOIS lookup for: {domain}")
    try:
        result = whois.whois(domain)

        # Convert complex data to string for JSON saving
        data = {}
        for k, v in result.items():
            try:
                data[k] = str(v)
            except:
                data[k] = None

        # Print result to console
        for key, value in data.items():
            print(f"{key}: {value}")

        return data  # <- important for --save
    except Exception as e:
        logger.log(f"Error: {e}", "ERROR")
        return {"error": str(e)}
