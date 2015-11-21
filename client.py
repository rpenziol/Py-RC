import socket

def main():
    HOST = raw_input("Enter the server IP address you'd like to connect to: ")
    PORT = 31415

    sock = socket.socket()
    sock.connect((HOST, PORT))

    user_input = ""

    #Main while loop to send/receive messages
    while user_input != '/q':
        user_input = raw_input()

if __name__ == '__main__': main()