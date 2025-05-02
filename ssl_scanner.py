import sys
import subprocess
import os
import requests
from tkinter import Tk, Checkbutton, Button, Label, IntVar, Radiobutton, messagebox, font
from datetime import datetime

# ------------------ Environment Checks ------------------
if sys.version_info < (3, 6):
    print("[!] Python 3.6 or higher is required.")
    sys.exit(1)

# Auto-install required package
def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure_package("requests")

try:
    import tkinter
except ImportError:
    print("[!] tkinter not found. Please install it manually: sudo apt install python3-tk")
    sys.exit(1)

# ------------------ Constants ------------------
DOMAINS_FILE_URL = "https://raw.githubusercontent.com/nayanxz/expresspros/main/domain.txt"
OUTPUT_DIR = f"ssl_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TESTSSL_REPO = "https://github.com/testssl/testssl.sh.git"
TESTSSL_DIR = "testssl.sh"

# ------------------ Utility Functions ------------------
def load_domains_from_github():
    try:
        response = requests.get(DOMAINS_FILE_URL)
        response.raise_for_status()
        return [line.strip() for line in response.text.splitlines() if line.strip()]
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching domain list: {e}")
        sys.exit(1)

def check_testssl_installed():
    if not os.path.exists(TESTSSL_DIR):
        print("[*] Cloning testssl.sh from GitHub...")
        subprocess.run(["git", "clone", TESTSSL_REPO])
    path = os.path.join(TESTSSL_DIR, "testssl.sh")
    if not os.path.isfile(path):
        print(f"[!] testssl.sh not found at {path}")
        return False
    if not os.access(path, os.X_OK):
        os.chmod(path, 0o755)
    return True

def check_sslscan_installed():
    try:
        subprocess.run(["sslscan", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[!] sslscan not found. Please install it using: sudo apt install sslscan")
        return False
    return True

def scan_with_testssl(domains):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for domain in domains:
        safe = domain.replace('.', '_')
        folder = os.path.join(OUTPUT_DIR, safe)
        os.makedirs(folder, exist_ok=True)
        html_out = os.path.join(folder, f"{safe}.html")
        try:
            subprocess.run(
                [f"./{TESTSSL_DIR}/testssl.sh", "--htmlfile", html_out, domain],
                check=True
            )
            print(f"[+] HTML report generated for {domain}")
        except Exception as e:
            print(f"[!] Error scanning {domain}: {e}")
    print(f"[✓] Reports saved in '{OUTPUT_DIR}'")

def scan_with_sslscan(domains):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for domain in domains:
        safe = domain.replace('.', '_')
        folder = os.path.join(OUTPUT_DIR, safe)
        os.makedirs(folder, exist_ok=True)
        raw_text = ""
        try:
            result = subprocess.run(
                ["sslscan", "--verbose", domain],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True
            )
            raw_text = result.stdout
            html_file = os.path.join(folder, f"{safe}.html")
            with open(html_file, "w") as f:
                f.write(f"<html><body><h2>SSLScan Report: {domain}</h2><pre>{raw_text}</pre></body></html>")
            print(f"[+] HTML report generated for {domain}")
        except Exception as e:
            print(f"[!] Error scanning {domain}: {e}")
    print(f"[✓] Reports saved in '{OUTPUT_DIR}'")

# ------------------ GUI Functions ------------------
def scan_all_domains():
    if scan_method.get() == 0:
        messagebox.showerror("Scan Method Missing", "Please select a scanning method.")
        return
    if scan_method.get() == 1:
        scan_with_testssl(domains)
    elif scan_method.get() == 2:
        scan_with_sslscan(domains)

def scan_selected():
    selected = [domains[i] for i, var in enumerate(checkbox_vars) if var.get()]
    if not selected:
        messagebox.showerror("No Domain Selected", "Please select at least one domain.")
        return
    if scan_method.get() == 0:
        messagebox.showerror("Scan Method Missing", "Please select a scanning method.")
        return
    if scan_method.get() == 1:
        scan_with_testssl(selected)
    elif scan_method.get() == 2:
        scan_with_sslscan(selected)

def exit_app():
    root.destroy()

# ------------------ Main Flow ------------------
if not check_testssl_installed() and not check_sslscan_installed():
    print("[!] Neither testssl.sh nor sslscan is available.")
    sys.exit(1)

domains = load_domains_from_github()

# ------------------ GUI Setup ------------------
root = Tk()
root.title("SSL Scan Selector")
root.geometry("550x800")

title_font = font.Font(family="Helvetica", size=18, weight="bold")
Label(root, text="Expresspros", font=title_font).pack(pady=10)

Label(root, text="Select scanning method:").pack(pady=10)
scan_method = IntVar()
Radiobutton(root, text="testssl.sh", variable=scan_method, value=1).pack(anchor="w", padx=10)
Radiobutton(root, text="sslscan", variable=scan_method, value=2).pack(anchor="w", padx=10)

Label(root, text="Select domains to scan:").pack(pady=10)
checkbox_vars = []
for domain in domains:
    var = IntVar()
    checkbox_vars.append(var)
    Checkbutton(root, text=domain, variable=var, width=60, anchor="w", padx=10).pack(anchor="w", padx=10)

Button(root, text="Scan All Domains", command=scan_all_domains, height=2, width=30).pack(pady=10)
Button(root, text="Scan Selected Domains", command=scan_selected, height=2, width=30).pack(pady=10)
Button(root, text="Exit", command=exit_app, height=2, width=30, bg="red", fg="white").pack(pady=30)

root.mainloop()
