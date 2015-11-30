import socket
import select
import sys
from collections import defaultdict

HOST = ''
PORT = 31415
CONNECTION_LIST = []  #List of connected clients
ONLINE_USERNAMES = {}  #Mapping of connections and their usernames
ROOMS = defaultdict(list)  #Mapping of room names to list of users in room
RECV_BUFFER = 4096


def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    #Add server socket to readable connections
    CONNECTION_LIST.append(server_socket)
    print "Chat server started on port " + str(PORT)

    while True:
        #Concurrency control lists
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST,[],[])

        for client in read_sockets:
            #New connection
            if client == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                #broadcast_message(server_socket, sockfd, "[%s:%s] is now connected\n" % addr)

            #Incoming message
            else:
                try:
                    data = client.recv(RECV_BUFFER)
                    if data:
                        incoming_protocol_handler(server_socket, client, data)

                except:
                    #broadcast_message(server_socket, client, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline - chat_server" % addr
                    #client.close()
                    #CONNECTION_LIST.remove(client)
                    #del ONLINE_USERNAMES[client]
                    #continue

    server_socket.close()


#Handle incoming messages from clients
def incoming_protocol_handler(server_socket, client_id, message):
    #Note using global variable
    global ONLINE_USERNAMES, ROOMS

    command = message.split(': ')

    if command[0] == 'LOGIN':
        #If username not an online user, add them to dictionary of online users
        if command[1] not in ONLINE_USERNAMES.values():
            ONLINE_USERNAMES[client_id] = command[1]
            client_id.send('LOGINSUCCESS')
            broadcast_message(server_socket, client_id, 'JOINED: ' + ONLINE_USERNAMES[client_id])

        else:
            client_id.send('ERR_USERNAMEUNAVAILABLE')

    elif command[0] == 'MESSAGE':
        broadcast_message(server_socket, client_id, message)

    elif command[0] == 'MKROOM':
        ROOMS[command[1]] = ()
        broadcast_message(server_socket, 0, 'New room available: ' + command[1])

    elif command[0] == 'LISTROOMS':
        room_names = ''
        for name in ROOMS.keys():
            room_names += name

        client_id.send(room_names)

    else:
        broadcast_message(server_socket, client_id, message)


#Send message to all online clients - except the sending client
def broadcast_message(server_socket, client_id, message):
    #Do not send message to server's socket or sending client
    for client in CONNECTION_LIST:
        if client != server_socket and client != client_id:
            try :
                client.send(message)

            except :
                #If unable to send to a socket, close and remove the connection
                client.close()
                CONNECTION_LIST.remove(client)
                broadcast_message(server_socket, client, "Client (%s, %s) is offline" % addr)
                print "Client (%s, %s) is offline - broadcast_message" % addr
                del ONLINE_USERNAMES[client]


if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_server())
