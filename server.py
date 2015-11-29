import socket
import select
import sys
import sqlite3

HOST = ''
PORT = 31415
#List of connected clients
CONNECTION_LIST = []
#Mapping of connections and their usernames
ONLINE_USERNAMES = {}
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
                    broadcast_message(server_socket, client, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    client.close()
                    CONNECTION_LIST.remove(client)
                    continue

    server_socket.close()


def incoming_protocol_handler(server_socket, client_id, message):
    if(client_id not in ONLINE_USERNAMES.keys()):
        client_id.send("Server: Please login or register\n")

    broadcast_message(server_socket, client_id, message)


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


if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_server())
