import socket
import threading
import time

# Configuration
GNB_IP = "xxxx.xxxx.xxxx.xxxx"  # Replace with gNB IP
GNB_PORT = 12345  # Replace with gNB port

CORE_IPS = [
    "xxxx.xxxx.xxxx.xxxx",  # Replace with 5G core IPs
    "xxxx.xxxx.xxxx.xxxx",
    "xxxx.xxxx.xxxx.xxxx"
]
CORE_PORT = 23456  # Replace with 5G core port

# Buffer size for receiving data
BUFFER_SIZE = 4096

def forward_request_to_cores(request, core_ips, core_port):
    responses = {}
    def handle_response(sock):
        try:
            while True:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                if data:
                    responses[sock.getpeername()] = data
                else:
                    break
        except socket.error:
            pass

    # Create and send request to all cores
    socks = []
    for ip in core_ips:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Timeout for receiving response
        sock.sendto(request, (ip, core_port))
        socks.append(sock)

    # Start threads to handle responses
    threads = [threading.Thread(target=handle_response, args=(sock,)) for sock in socks]
    for thread in threads:
        thread.start()

    # Wait for responses and close sockets
    for sock in socks:
        sock.close()

    for thread in threads:
        thread.join()

    # Return the first response received
    if responses:
        return min(responses.values(), key=lambda r: len(r))  # Simple method to pick the first response
    return None

def handle_gnb_requests():
    # Set up server to receive requests from gNB
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((GNB_IP, GNB_PORT))

    while True:
        request, _ = server_socket.recvfrom(BUFFER_SIZE)
        if request:
            print(f"Received request from gNB: {request}")

            # Forward request to 5G cores
            response = forward_request_to_cores(request, CORE_IPS, CORE_PORT)

            if response:
                # Send the response back to gNB
                server_socket.sendto(response, (GNB_IP, GNB_PORT))
            else:
                print("No response from 5G cores")

if __name__ == "__main__":
    handle_gnb_requests()
