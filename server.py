#!/usr/bin/python
import socket
import select
import sys
import struct
from collections import defaultdict
from time import sleep

HOST = ''
PORT = 31415
CONNECTION_LIST = []  #List of connected clients
ONLINE_USERNAMES = {}  #Mapping of connections and their usernames
ROOMS = defaultdict(list)  #Mapping of room names to list of users in room
RECV_BUFFER = 4096


def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    l_onoff = 1
    l_linger = 0
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', l_onoff, l_linger))
    #server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                    #The client unexpectedly disconnected
                    disconnect(client, addr)

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
            client_id.send('ERRUSERNAMEUNAVAILABLE')

    elif command[0] == 'MESSAGE':
        broadcast_message(server_socket, client_id, message)

    elif command[0] == 'MKROOM':
        ROOMS[command[1]]
        #Broadcast to all, including sender
        broadcast_message(server_socket, 0, 'New room available: ' + command[1])

    elif command[0] == 'LISTROOMS':
        list_rooms(client_id)

    elif command[0] == 'JOINROOM':
        join_rooms(client_id, command[1])

    elif command[0] == 'LEAVEROOM':
        leave_room(client_id, command[1])

    elif command[0] == 'ROOMMEMBERS':
        list_members(client_id, command[1])

    elif command[0] == 'RMESSAGE':
        rooms = command[1].split(' ')
        room_message(client_id, rooms, command[2])

    elif command[0] == 'DMESSAGE':
        direct_message(client_id, command[1], command[2])

    elif command[0] == 'QUIT':
        disconnect(client_id)

    else:
        broadcast_message(server_socket, client_id, message)


#Send message to all online clients - except the sending client_id
def broadcast_message(server_socket, client_id, message):
    #Do not send message to server's socket or sending client
    for client in CONNECTION_LIST:
        if client != server_socket and client != client_id:
            client.send(message)


#Add client's username to list of rooms
def join_rooms(client_id, rooms):
    global ROOMS
    room_list = rooms.split()

    for room in room_list:
        sleep(0.1) #Prevent sending messages too fast, thus concatenating messages TODO: Add more elegant solution
        if room in ROOMS.keys():
            if client_id not in ROOMS[room]:
                #Map socket to room name
                ROOMS[room].append(client_id)
                client_id.send('JOINEDROOM: ' + room)
            else:
                client_id.send('ERRALREADYMEMBER: ' + room)
        else:
            send_error_nosuchroom(client_id, room)


#Remove client's username from given room's list of members
def leave_room(client_id, room):
    global ROOMS
    if room in ROOMS.keys(): #check that the room exists
        if client_id in ROOMS[room]: #check that user is in room
            #Loop up username for client's socket, and remove them from the room
            ROOMS[room].remove(client_id)
            client_id.send("LEFTROOM: " + room)
        else:
            send_error_notmember(client_id, room)

    else:
        send_error_nosuchroom(client_id, room)


#Send client list of all rooms
def list_rooms(client_id):
    #Get all room names, seperated by spaces
    client_id.send('LROOM: ' + ", ".join(ROOMS.keys()))


#Send client list of clients in a given 'room'
def list_members(client_id, room):
    if room in ROOMS.keys():
        members = []
        #If the room exists, give its name, followed by the list of members
        for socket in ROOMS[room]:
            members.append(ONLINE_USERNAMES[socket])
        client_id.send('ROOMMEMBERS: ' + room + ': ' + ", ".join(members))
    else:
        send_error_nosuchroom(client_id, room)


#Send a message to all members of a list of rooms
def room_message(client_id, room_list, message):
    for room in room_list:
        sleep(0.1) #Prevent sending messages too fast, thus concatenating messages TODO: Add more elegant solution
        if room in ROOMS.keys():  #Check that room exists
            if client_id in ROOMS[room]:  #Check that sender belongs to room
                for client in ROOMS[room]:
                    client.send('RMESSAGE: ' + room + ': ' + ONLINE_USERNAMES[client_id] + ': ' + message)
            else:
                send_error_notmember(client_id, room)
        else:
            send_error_nosuchroom(client_id, room)


#Send a message to the target user
def direct_message(client_id, target_username, message):
    if target_username in ONLINE_USERNAMES.values():
        #Reverse dictionary lookup to get target's socket
        target_username_socket = (key for key,value in ONLINE_USERNAMES.items() if value == target_username).next()
        target_username_socket.send('DMESSAGE: ' + ONLINE_USERNAMES[client_id] + ': ' + message)

        #Send message to self, unless private message was directed as oneself
        if client_id != target_username_socket:
            client_id.send('DMESSAGE: ' + ONLINE_USERNAMES[client_id] + ': ' + message)
    else:
        client_id.send('ERRNOSUCHUSER: ' + target_username)


#Send the client an error message warning that the room doesn't exist
def send_error_nosuchroom(client_id, room):
    client_id.send('ERRNOSUCHROOM: ' + room)


#Send the client an error to inform that they're not a member of the room
def send_error_notmember(client_id, room):
    client_id.send('ERRNOTMEMBER: ' + room)


#Remove client data from server, and disconnect
def disconnect(client_id, addr):
    client_id.close() #Close socket
    #Remove user from all rooms
    for room in ROOMS:
        if client_id in ROOMS[room]:
            ROOMS[room].remove(client_id)

    #Remove user from list of online users
    del ONLINE_USERNAMES[client_id]
    CONNECTION_LIST.remove(client_id)
    print 'Client (%s, %s) is offline.' % addr

if __name__ == '__main__':
    #Exit application if any unhandled exception is thrown
    sys.exit(chat_server())
