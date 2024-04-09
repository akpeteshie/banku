import os
import signal
import socket
import time

# defines socket parameters
SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 5

# function that terminates zombies
def grim_reaper(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(
                    -1,
                    os.WNOHANG
                    )
        except OSError:
            return

        if pid == 0:
            return

# function that handles requests
def handle_request(client_connection):
    # receives client message
    request = client_connection.recv(1024)
    print('Child PID: {pid}. Parent PID {ppid}'.format(pid=os.getpid(), ppid=os.getppid()))
    print(request.decode())
    http_response = b"""\
            HTTP/1.1 200 OK

            Hello, World!
            """
    client_connection.sendall(http_response)
    time.sleep(3)

# function that serves requests
def serve_forever():
    # initializes socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))
    print('Parent PID (PPID): {pid}\n'.format(pid=os.getpid()))

    signal.signal(signal.SIGCHLD, grim_reaper)

    while True:
        try:
            client_connection, client_address = listen_socket.accept()
        except IOError as e:
            code, msg = e.args
            if code == errno.EINTR:
                continue
            else:
                raise

        # creates subprocess
        pid = os.fork()

        if pid == 0:
            # closes child socket duplicate
            listen_socket.close()
            handle_request(client_connection)
            client_connection.close()
            # eexits child process
            os._exit(0)
        else:
            client_connection.close()

if __name__ == "__main__":
    serve_forever()
