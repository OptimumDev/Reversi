import socket
import multiprocessing


print('starting server...')

PORT = 37001
ADDRESS = ('0.0.0.0', PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def handle_connection(client, address):
    with client:
        while True:
            data = client.recv(65535)
            if data:
                client.sendall(data)
            else:
                print('Connection was closed')
                break

with server:
    server.bind(ADDRESS)
    server.listen(socket.SOMAXCONN)

    alive = set()
    while True:
        client, client_addres = server.accept()
        print('Receive message from {}'.format(client_addres))

        process = multiprocessing.Process(
            target=lambda:(server.close(), handle_connection()), args=(client, client_addres))
        process.daemon = True
        process.start()
        alive.add(process)

        client.close()

        for p in list(alive):
            if not p.is_alive():
                p.join()
                alive.remove(p)