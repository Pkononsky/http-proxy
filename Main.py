import re
import select
import socket

input_sockets = list()
BUFFER = 4096

from_to = dict()

def check_connection_to_network():
    try:
        sock = socket.socket()
        sock.connect(("google.com", 80))
        sock.close()
        return True
    except:
        return False


if __name__ == '__main__':
    if not check_connection_to_network():
        print("Нет подключения к интернету")
        os.abort()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 8080))
    server.listen(200)
    input_sockets.append(server)

    while True:
        inp_sock, _, _ = select.select(input_sockets, [], [])
        for sock in inp_sock:
            if sock == server:
                conn, addr = sock.accept()
                data = conn.recv(BUFFER)
                print(data)

                if not data:
                    continue

                site_port_http = re.findall(b"CONNECT (.+) ", data)[0]
                host, port = site_port_http.split(b" ")[0].split(b":")
                print(host, port)
                host_start = host.split(b".")[0]
                if host_start in [b"ads", b"reklama", b"an", b"zen", b"tpc", b"avatars", b"cdn", b"pagead2", b"adservice", b"securepubads"]:
                    continue

                target = socket.socket()
                target.connect((host.decode(), int(port.decode())))
                conn.send(b"HTTP/1.0 200 Connection established\r\n\r\n")

                input_sockets.append(conn)
                input_sockets.append(target)

                from_to[conn] = target
                from_to[target] = conn
                break

            try:
                data = sock.recv(BUFFER)
                if data:
                    if sock == server:
                        print(data)
                    from_to[sock].send(data)
                else:
                    out = from_to[sock]
                    input_sockets.remove(sock)
                    input_sockets.remove(out)

                    sock.close()
                    out.close()

                    del from_to[out]
                    del from_to[sock]
                    break
            except:
                sock.close()
                try:
                    input_sockets.remove(sock)
                except:
                    pass
