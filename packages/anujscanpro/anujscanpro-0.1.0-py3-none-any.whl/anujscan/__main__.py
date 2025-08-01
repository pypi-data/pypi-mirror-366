import json
import os
import random
from pyfiglet import Figlet
from colorama import init, Fore, Style
from yaspin import yaspin

# Initialize colorama
init(autoreset=True)

from anujscan.modules import (
    subdomain_scan,
    whois_lookup,
    http_headers,
    port_scanner,
    ssl_checker,
    dir_bruteforce
)

def banner():
    fonts = [
        'slant', 'standard', 'big', 'banner3-D', 'cybermedium',
        'isometric1', 'larry3d', 'starwars', 'doom', 'smslant'
    ]
    font = random.choice(fonts)
    figlet = Figlet(font=font)
    print(Fore.CYAN + figlet.renderText("AnujScan"))
    print(Fore.MAGENTA + "🚀 AnujScan Pro - Recon Toolkit CLI 🚀\n")

def save_output(module, target, data):
    os.makedirs("output", exist_ok=True)
    filename = f"output/{module}_{target.replace('.', '_')}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(Fore.MAGENTA + f"[+] Results saved to {filename}")

def main():
    banner()

    modules = {
        "1": ("WHOIS Lookup", whois_lookup.run),
        "2": ("Subdomain Scanner", subdomain_scan.run),
        "3": ("HTTP Headers", http_headers.run),
        "4": ("Port Scanner", port_scanner.run),
        "5": ("SSL Certificate Checker", ssl_checker.run),
        "6": ("Directory Brute-Forcer", dir_bruteforce.run),
        "0": ("Exit", None)
    }

    print(Fore.YELLOW + "📦 Select a Module to Run:")
    for key, (name, _) in modules.items():
        print(Fore.YELLOW + f"  {key}. {name}")

    choice = input(Fore.GREEN + "\n🎯 Enter your choice: ").strip()

    if choice not in modules:
        print(Fore.RED + "[!] Invalid choice. Exiting.")
        return

    if choice == "0":
        print(Fore.CYAN + "👋 Goodbye!")
        return

    module_name, module_func = modules[choice]
    target = input(Fore.GREEN + "🌐 Enter target domain/IP: ").strip()
    save_input = input(Fore.GREEN + "💾 Save result to file? (y/n): ").lower().strip()
    save = save_input == "y"

    print(Fore.CYAN + f"\n[+] Running {module_name} on {target}...\n")

    result = None
    with yaspin(text=f"Scanning {target}...", color="cyan") as spinner:
        try:
            result = module_func(target)
            spinner.ok(Fore.GREEN + "✔ Done")
        except Exception as e:
            spinner.fail(Fore.RED + "✖ Failed")
            print(Fore.RED + f"[!] Error: {e}")
            return

    if save and result:
        module_key = module_name.lower().replace(" ", "_")
        save_output(module_key, target, result)

if __name__ == "__main__":
    main()
