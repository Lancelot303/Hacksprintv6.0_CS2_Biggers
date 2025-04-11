#!/usr/bin/env python3
import json
import socket
from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, RR, A, QTYPE

# Configuration
OUTPUT_FILE = "dns_requests.json"   # File to store intercepted domain names
UPSTREAM_DNS = "8.8.8.8"
UPSTREAM_PORT = 53
DNS_PORT = 53
BIND_ADDRESS = "192.168.1.13"

def log_domain(domain):
    data = {"url": domain}
    try:
        with open(OUTPUT_FILE, "a") as f:
            json.dump(data, f)
            f.write("\n")
    except Exception as e:
        print(f"[ERROR] Could not write domain: {e}")

def forward_request(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        sock.sendto(request.pack(), (UPSTREAM_DNS, UPSTREAM_PORT))
        response_data, _ = sock.recvfrom(4096)
        return DNSRecord.parse(response_data)
    except:
        return request.reply()

class SilentDNSResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname).rstrip(".")
        log_domain(qname)
        return forward_request(request)

if __name__ == "__main__":
    print("Started DNS Server.....")
    resolver = SilentDNSResolver()
    udp_server = DNSServer(resolver, port=DNS_PORT, address=BIND_ADDRESS, tcp=False)
    tcp_server = DNSServer(resolver, port=DNS_PORT, address=BIND_ADDRESS, tcp=True)
    udp_server.start_thread()
    tcp_server.start_thread()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
