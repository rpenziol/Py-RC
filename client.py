import socket
import select
import sys
import string

#Available message buffer size
RECV_BUFFER = 4096

def chat_client():

    if(len(sys.argv) < 3) :
        print 'Usage : python client.py hostname port'
        sys.exit()

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(2)

    #Attempt connection to remote host
    try :
        client_socket.connect((HOST, PORT))
    except :
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
                data = sock.recv(RECV_BUFFER)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    sys.stdout.write(data)
                    prompt()

            #User-entered message
            else :
                msg = sys.stdin.readline()
                client_socket.send(msg)
                prompt()

def prompt() :
    sys.stdout.write('<Username> ')
    sys.stdout.flush()

if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_client())