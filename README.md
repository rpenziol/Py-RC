# Py-RC

Py-RC is a simple IRC-like protocol implemented in Python. The purpose of this project is to define and implement a network protocol for a Networking Protocols class.
   
### Usage
This project requires a Linux environment and Python 2.7. This project also requires that port 31415 be open and available.

The server is started by executing in the terminal
```
python server.py
```

The client is started by executing in the terminal
```
python client.py [X.X.X.X]
```
where X.X.X.X should be replaced with the IP address of the host server.

### Commands
To create a chat room
```
/mkroom
```
To join a chat room, or multiple chat rooms
```
/join [room names]
```
To leave a chat room
```
/leave [room name]
```
To list the members of a chat room
```
/members [room name]
```
To list the available chat rooms
```
/listrooms
```
To send a message to a chat room, or multiple chat rooms
```
/rmessage [room names]: [message]
```
To send a message directly to another user
```
/dmessage [username]: [message]
```
To safely disconnect from the server
```
/quit
```
