import socket
import select
import sys
import struct

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
    l_onoff = 1
    l_linger = 0
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', l_onoff, l_linger))
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

    global AUTHENTICATED

    command = message.split(': ')

    if AUTHENTICATED == False:

        if command[0] == 'LOGINSUCCESS':
            AUTHENTICATED = True

        elif command[0] == 'ERRUSERNAMEUNAVAILABLE':
            sys.stdout.write("Error: That username is unavailable\n")
            login_prompt(client_socket)


    elif command[0] == 'JOINED':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print command[1] + " has joined the server.\n"
        prompt()

    elif command[0] == 'MESSAGE':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print '<' + command[1] + '> ' + command[2]  #Sending user, followed by username
        prompt()

    elif command[0] == 'LROOM':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'List of rooms: ' + command[1]
        prompt()

    elif command[0] == 'JOINEDROOM':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'Joined room: ' + command[1]
        prompt()

    elif command[0] == 'LEFTROOM':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'Left room: ' + command[1]
        prompt()

    elif command[0] == 'ERRNOSUCHROOM':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'Room "' + command[1] + '" does not exist.'
        prompt()

    elif command[0] == 'ERRALREADYMEMBER':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'You are already a member of the room "' + command[1] + '".'
        prompt()

    elif command[0] == 'ERRNOTMEMBER':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'You are not a member of the room "' + command[1] + '".'
        prompt()

    elif command[0] == 'ERRNOSUCHUSER':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print 'The user "' + command[1] + '" does not exist.'
        prompt()

    elif command[0] == 'ROOMMEMBERS':
        #Clear prompt before printing
        print '\x1b[2K\r'
        #Print room name, followed by list of members
        print 'List of room "' + command[1] + '" members: ' + command[2]
        prompt()

    elif command[0] == 'RMESSAGE':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print '[ ' + command[1] + ' ]' + '<' + command[2] + '> ' + command[3]
        prompt()

    elif command[0] == 'DMESSAGE':
        #Clear prompt before printing
        print '\x1b[2K\r'
        print '[PRIVATE] <' + command[1] + '> ' + command[2]
        prompt()

    else:
        #Clear prompt before printing
        print '\x1b[2K\r'
        print message
        prompt()

#Handles creation of protocol messages to send to the server
def outgoing_protocol_handler(client_socket, message):

    command = message.rsplit()

    if AUTHENTICATED == False:
        login_prompt(client_socket)

    elif command[0] == '/mkroom':
        client_socket.send('MKROOM: ' + command[1])

    elif command[0] == '/listrooms':
        client_socket.send('LISTROOMS: ')

    elif command[0] == '/join':
        #Remove user command, send concatinated list of room names
        del command[0]
        client_socket.send('JOINROOM: ' + " ".join(command))

    elif command[0] == '/leave':
        client_socket.send('LEAVEROOM: ' + command[1])

    elif command[0] == '/members':
        client_socket.send('ROOMMEMBERS: ' + command[1])

    elif command[0] == '/rmessage':
        #Remove user command, send concatinated list of rooms, and message
        del command[0]
        client_socket.send('RMESSAGE: ' + " ".join(command))

    elif command[0] == '/dmessage':
        #Remove user command, send username concatinated with message
        del command[0]
        client_socket.send('DMESSAGE: ' + " ".join(command))

    elif command[0] == '/quit':
        client_socket.send('QUIT: ')

    else:
        client_socket.send('MESSAGE: ' + USERNAME + ': ' + message)


def login_prompt(client_socket):
    global USERNAME
    USERNAME = raw_input('Please enter your desired username: ')
    client_socket.send('LOGIN: ' + USERNAME)


def prompt():
    sys.stdout.write('<' + USERNAME + '>: ')
    sys.stdout.flush()


if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_client())
