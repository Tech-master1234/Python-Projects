import socket
import ipaddress
import threading
import webbrowser
import psutil

PORT = 8010
TIMEOUT = 0.5
FOUND = False
LOCK = threading.Lock()

def get_valid_adapters():
    adapters = []
    for iface, addrs in psutil.net_if_addrs().items():
        stats = psutil.net_if_stats().get(iface)
        if not stats or not stats.isup:
            continue  # Skip interfaces that are down
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                subnet = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                adapters.append((iface, subnet))
    return adapters

def check_host(ip):
    global FOUND
    if FOUND:
        return
    try:
        with socket.create_connection((str(ip), PORT), timeout=TIMEOUT):
            with LOCK:
                if not FOUND:
                    print(f"[+] Found server at {ip}:{PORT}")
                    FOUND = True
                    webbrowser.open(f"http://{ip}:{PORT}")
    except:
        pass

def scan_subnet(iface, subnet):
    print(f"[i] Scanning {subnet} on interface '{iface}'...")
    threads = []
    for ip in subnet.hosts():
        t = threading.Thread(target=check_host, args=(ip,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def scan_all_interfaces():
    adapters = get_valid_adapters()
    if not adapters:
        print("[-] No active Ethernet or Wi-Fi interfaces found.")
        return

    for iface, subnet in adapters:
        if FOUND:
            break
        scan_subnet(iface, subnet)

    if not FOUND:
        print("[-] No server found on any interface.")

if __name__ == "__main__":
    scan_all_interfaces()
