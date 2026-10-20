"""
NetMonitor - monitoring client
Collects system info (psutil) and basic network info (scapy ARP scan),
then reports it to the TCP server using MySocket (Windows API via ctypes).
"""

import ctypes
import json
import os
import platform
import time

import psutil
from my_socket import MySocket, AF_INET, INVALID_SOCKET, SOCKADDR_IN, ws2

try:
    from scapy.all import ARP, Ether, srp
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000
SCAN_SUBNET = "192.168.1.0/24"
INTERVAL_SECONDS = 10

SOCK_DGRAM = 2


def get_local_ip():
    wsadata = ctypes.create_string_buffer(400)
    ws2.WSAStartup(0x0202, wsadata)

    s = ws2.socket(AF_INET, SOCK_DGRAM, 0)
    if s == INVALID_SOCKET:
        return "127.0.0.1"
    try:
        addr = SOCKADDR_IN()
        addr.sin_family = AF_INET
        addr.sin_port = ws2.htons(80)
        addr.sin_addr = ws2.inet_addr(b"8.8.8.8")
        ws2.connect(s, ctypes.byref(addr), ctypes.sizeof(addr))

        local_addr = SOCKADDR_IN()
        addr_len = ctypes.c_int(ctypes.sizeof(local_addr))
        ws2.getsockname(s, ctypes.byref(local_addr), ctypes.byref(addr_len))

        ws2.inet_ntoa.argtypes = [ctypes.c_uint32]
        ws2.inet_ntoa.restype = ctypes.c_char_p
        ip = ws2.inet_ntoa(local_addr.sin_addr)
        return ip.decode('utf-8') if ip else "127.0.0.1"
    except Exception:
        return "127.0.0.1"
    finally:
        ws2.closesocket(s)


def count_devices_on_lan():
    if not SCAPY_AVAILABLE:
        return 0
    try:
        arp = ARP(pdst=SCAN_SUBNET)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        answered, _ = srp(ether / arp, timeout=2, verbose=False)
        return len(answered)
    except Exception as exc:
        print(f"[!] Network scan failed (needs admin + Npcap): {exc}")
        return 0


def collect_report():
    return {
        "hostname": platform.node(),
        "ip_address": get_local_ip(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage(os.sep).percent,
        "devices_found": count_devices_on_lan(),
    }


def send_report(report):
    client = MySocket()
    client.connect(SERVER_HOST, SERVER_PORT)
    client.send(json.dumps(report) + "\n")
    response = client.receive()
    print(f"[>] Sent report, server replied: {response.strip()}")
    client.close()


def main():
    print(f"[*] NetMonitor client starting, reporting to {SERVER_HOST}:{SERVER_PORT}")
    while True:
        report = collect_report()
        print(f"[*] Collected: {report}")
        try:
            send_report(report)
        except OSError:
            print("[!] Could not reach the server - is server.py running?")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
