import socket
import select
import sys
import string

PORT = 31415
USERNAME = ''
AUTHENTICATED = False
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

#Handles protocol messages coming in from the server
def incoming_protocol_handler(client_socket, message):
    if not message:
        print '\nDisconnected from chat server'
        sys.exit()

    command = message.split(': ')

    if command[0] == 'LOGINSUCCESS':
        global AUTHENTICATED
        AUTHENTICATED = True

    elif command[0] == 'ERR_USERNAMEUNAVAILABLE':
        sys.stdout.write("Error: That username is unavailable\n")
        login_prompt(client_socket)

    elif AUTHENTICATED == False:
        garbage = "Empty"

    else:
        sys.stdout.write(message)
        prompt()


#Handles creation of protocol messages to send to the server
def outgoing_protocol_handler(client_socket, message):
    if AUTHENTICATED == False:
        login_prompt(client_socket)
    else:
        client_socket.send(message)


def login_prompt(client_socket):
    global USERNAME
    USERNAME = raw_input('Please enter your desired username: ')
    client_socket.send('LOGIN: ' + USERNAME)


def prompt():
    sys.stdout.write('<' + USERNAME + '> ')
    sys.stdout.flush()


if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_client())
