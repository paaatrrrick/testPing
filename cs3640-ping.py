import time
import dpkt
import socket
import argparse
import struct

def make_icmp_socket(ttl, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    s.settimeout(timeout)
    return s

def send_icmp_echo(sock, payload, id, seq, destination):
    # ICMP Echo Request
    echo = dpkt.icmp.ICMP.Echo()
    echo.id = id
    echo.seq = seq
    echo.data = payload

    # ICMP 
    icmp = dpkt.icmp.ICMP()
    icmp.type = dpkt.icmp.ICMP_ECHO
    icmp.data = echo

    # Send ICMP packet
    sock.sendto(bytes(icmp.pack()), (destination, 0))

def recv_icmp_response():
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    data, addr = s.recvfrom(1500)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple ICMP ping implementation.')
    parser.add_argument('-destination', required=True, help='Destination IP')
    parser.add_argument('-n', type=int, required=True, help='Number of pings')
    parser.add_argument('-ttl', type=int, required=True, help='Time to Live')
    args = parser.parse_args()

    total_time = 0
    successful_pings = 0
    for i in range(args.n):
        try:
            # Create socket
            sock = make_icmp_socket(args.ttl, 1)  # 1 second timeout

            # Send echo request
            start_time = time.time()
            send_icmp_echo(sock, b'Hello', i, i, args.destination)

            # Receive response
            response = recv_icmp_response()
            end_time = time.time()

            rtt = (end_time - start_time) * 1000  # in ms
            total_time += rtt
            successful_pings += 1

            print(f'destination = {args.destination}; icmp_seq = {i}; icmp_id = {i}; ttl = {args.ttl}; rtt = {rtt:.1f} ms')

        except socket.timeout:
            print(f'destination = {args.destination}; icmp_seq = {i}; icmp_id = {i}; ttl = {args.ttl}; Request timed out')
        
        except Exception as e:
            print(e)

    average_rtt = total_time / successful_pings if successful_pings else 0
    print(f'Average rtt: {average_rtt:.1f} ms; {successful_pings}/{args.n} successful pings.')
