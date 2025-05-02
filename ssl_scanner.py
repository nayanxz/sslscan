import subprocess
import os
import requests
import git
from tkinter import Tk, Checkbutton, Button, Label, IntVar, Radiobutton, messagebox, font
from datetime import datetime

# Constants
DOMAINS_FILE_URL = "https://raw.githubusercontent.com/nayanxz/expresspros/main/domain.txt"
OUTPUT_DIR = f"ssl_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TESTSSL_REPO_URL = "https://github.com/testssl/testssl.sh.git"
SSLSCAN_URL = "https://github.com/rbsec/sslscan/releases/download/v1.0.13/sslscan_1.0.13_amd64.deb"

# Load domains from GitHub
def load_domains_from_github():
    try:
        response = requests.get(DOMAINS_FILE_URL)
        response.raise_for_status()
        return [line.strip() for line in response.text.splitlines() if line.strip()]
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching domain list from GitHub: {e}")
        exit(1)

# Function to clone the testssl.sh repository from GitHub
def clone_testssl_repo():
    if not os.path.isdir("testssl.sh"):
        print("[!] testssl.sh repository not found. Cloning...")
        try:
            git.Repo.clone_from(TESTSSL_REPO_URL, "testssl.sh")
            print("[+] Cloned testssl.sh repository successfully!")
        except git.exc.GitCommandError as e:
            print(f"[!] Error cloning testssl.sh repository: {e}")
            exit(1)

# Function to check if sslscan is installed, if not, download it
def download_sslscan():
    try:
        subprocess.run(["sslscan", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except FileNotFoundError:
        print("[!] sslscan not found. Downloading sslscan...")
        try:
            response = requests.get(SSLSCAN_URL)
            response.raise_for_status()
            with open("sslscan.deb", "wb") as f:
                f.write(response.content)
            print("[+] Downloaded sslscan package successfully!")
            print("[*] Installing sslscan...")
            subprocess.run(["sudo", "dpkg", "-i", "sslscan.deb"], check=True)
            print("[+] sslscan installed successfully!")
        except requests.exceptions.RequestException as e:
            print(f"[!] Error downloading sslscan: {e}")
            exit(1)

# Check if sslscan is installed
def check_sslscan_installed():
    try:
        subprocess.run(["sslscan", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print("[!] sslscan encountered an error.")
        return False
    except FileNotFoundError:
        download_sslscan()
        return True
    return True

# Function to check if testssl.sh is available and executable
def check_testssl_installed():
    if not os.path.isdir("testssl.sh"):
        clone_testssl_repo()
    testssl_path = "./testssl.sh/testssl.sh"
    if not os.access(testssl_path, os.X_OK):
        print("[*] testssl.sh not executable. Fixing...")
        os.chmod(testssl_path, 0o755)
    return True

# Run testssl.sh
def scan_with_testssl(selected_domains):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for domain in selected_domains:
        safe = domain.replace('.', '_')
        folder = os.path.join(OUTPUT_DIR, safe)
        os.makedirs(folder, exist_ok=True)
        txt_out = os.path.join(folder, f"{safe}.txt")
        html_out = os.path.join(folder, f"{safe}.html")

        try:
            with open(txt_out, "w") as out:
                process = subprocess.Popen(
                    ["./testssl.sh/testssl.sh", "--htmlfile", html_out, domain],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in process.stdout:
                    print(line, end='')
                    out.write(line)
            print(f"[+] Done: {domain}")
        except Exception as e:
            print(f"[!] Error scanning {domain}: {e}")
    print(f"[✓] Reports saved in '{OUTPUT_DIR}'")

# Run sslscan
def scan_with_sslscan(selected_domains):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for domain in selected_domains:
        safe = domain.replace('.', '_')
        folder = os.path.join(OUTPUT_DIR, safe)
        os.makedirs(folder, exist_ok=True)
        txt_out = os.path.join(folder, f"{safe}.txt")

        try:
            with open(txt_out, "w") as out:
                process = subprocess.Popen(
                    ["sslscan", "--verbose", domain],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in process.stdout:
                    print(line, end='')
                    out.write(line)
            print(f"[+] Done: {domain}")
        except Exception as e:
            print(f"[!] Error scanning {domain}: {e}")
    print(f"[✓] Reports saved in '{OUTPUT_DIR}'")

# GUI actions
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

# Requirements check
if not check_testssl_installed() and not check_sslscan_installed():
    print("[!] Neither testssl.sh nor sslscan is available.")
    exit(1)

# Load domains
domains = load_domains_from_github()

# GUI Setup
root = Tk()
root.title("Expresspros SSL Scanner v1.0")
root.geometry("550x800")

label = Label(root, text="Expresspros", font=("Helvetica", 24, "bold"), fg="blue")
label.pack(pady=10)

label = Label(root, text="Select Scanning Tools:")
label.pack(pady=10)

scan_method = IntVar()
Radiobutton(root, text="testssl.sh (Detailed Vulnerability Scan)", variable=scan_method, value=1).pack(anchor="w", padx=10)
Radiobutton(root, text="sslscan (Quick Scan)", variable=scan_method, value=2).pack(anchor="w", padx=10)

label2 = Label(root, text="Select domains to scan:")
label2.pack(pady=10)

checkbox_vars = []
for domain in domains:
    var = IntVar()
    checkbox_vars.append(var)
    chk = Checkbutton(root, text=domain, variable=var, width=60, anchor="w", padx=10)
    chk.pack(anchor="w", padx=10)

# Buttons
Button(root, text="Scan All Domains", command=scan_all_domains, height=2, width=30).pack(pady=10)
Button(root, text="Scan Selected Domains", command=scan_selected, height=2, width=30).pack(pady=10)
Button(root, text="Exit", command=exit_app, height=2, width=30, bg="red", fg="white").pack(pady=30)

root.mainloop()
