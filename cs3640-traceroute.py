import time
import dpkt
import socket
import argparse

def make_icmp_socket(ttl, timeout=3):
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    s.settimeout(timeout)
    return s

def send_icmp_echo(sock, id, seq, destination):
    # ICMP Echo Request
    echo = dpkt.icmp.ICMP.Echo()
    echo.id = id
    echo.seq = seq
    echo.data = b'Hello'

    # ICMP 
    icmp = dpkt.icmp.ICMP()
    icmp.type = dpkt.icmp.ICMP_ECHO
    icmp.data = echo

    # Send ICMP packet
    sock.sendto(bytes(icmp.pack()), (destination, 0))

def traceroute(destination, n_hops):
    for ttl in range(1, n_hops+1):
        try:
            # Create socket
            sock = make_icmp_socket(ttl)

            # Send echo request
            start_time = time.time()
            send_icmp_echo(sock, ttl, ttl, destination)

            # Receive response
            response, address = sock.recvfrom(1500)
            end_time = time.time()

            icmp_type = response[20]

            if icmp_type == 11:  # TTL exceeded
                print(f'destination = {destination}; hop {ttl} = {address[0]}; rtt = {(end_time - start_time)*1000:.2f} ms')
            elif icmp_type == 0:  # ICMP Echo Reply
                print(f'destination = {destination}; reached destination in {ttl} hops')
                break
        except socket.timeout:
            print(f'destination = {destination}; hop {ttl} = Timed Out')
        except Exception as e:
            print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple ICMP traceroute implementation.')
    parser.add_argument('-destination', required=True, help='Destination IP')
    parser.add_argument('-n_hops', type=int, required=True, help='Maximum number of hops')
    args = parser.parse_args()

    traceroute(args.destination, args.n_hops)
