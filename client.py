import socket
import select
import sys
import string
import getpass

PORT = 31415
USERNAME = ''
authenticated = False
#Available message buffer size
RECV_BUFFER = 4096

def chat_client():

    if(len(sys.argv) < 2):
        print 'Usage : python client.py hostname'
        sys.exit()

    HOST = sys.argv[1]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)

    #Attempt connection to remote host
    try:
        client_socket.connect((HOST, PORT))
    except:
        print 'Unable to connect'
        sys.exit()

    print('Connected to remote host.')

    #Main while loop to send/receive messages
    while True:
        CONNECTION_LIST = [sys.stdin, client_socket]

        #Get list of readable sockets
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            #Incoming message from server
            if sock == client_socket:
                incoming_msg = sock.recv(RECV_BUFFER)
                incoming_protocol_handler(sock, incoming_msg)

            #User-entered message
            else:
                outgoing_msg = sys.stdin.readline()
                outgoing_protocol_handler(client_socket, outgoing_msg)
                prompt()


def incoming_protocol_handler(server_socket, message):
    if not message:
        print '\nDisconnected from chat server'
        sys.exit()
    else:
        sys.stdout.write(message)
        prompt()


def outgoing_protocol_handler(client_socket, message):
    client_socket.send(message)


def prompt():
    sys.stdout.write('<' + USERNAME + '> ')
    sys.stdout.flush()


if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_client())
