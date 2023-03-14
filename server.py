import socket
import select
import ssl
import os


def handle(server, ssl_client_soc, command_option, client_msg):  # the server message to the client
    match command_option:
        case '1':  # the client wants to upload a file
            case1(server, ssl_client_soc, client_msg)
        case '2':  # the client wants to download a a file
            case2(server, ssl_client_soc, client_msg)
            
        case '3':  # the client requests the list of the available files that the server holds
            fileList = " ".join(server.FILES_LIST)
            ssl_client_soc.send("The available files to download are: {}".format(fileList).encode())
            
        case '4':  # the client wants to close the connection
            raise ValueError("end of conversation")  # creating exception to close the socket
        case _:
            ssl_client_soc.send("error - command option not found\n".encode())  # not in the protocol rules, actually can't get here


def case1(server, ssl_client_soc, client_msg): 
        client_msg = client_msg.split(" ")  # splitting between the type of the command, the filename and the file-size 
        filename = client_msg[1]  # the name of the file that the client wants to upload, strip to remove the first space
        ssl_client_soc.send("start uploading".encode())
        with open(os.path.join(server.FILES_DIR_PATH, filename), 'wb') as file_to_write:
            fileSize = int(client_msg[2])
            data = ssl_client_soc.recv(fileSize)
            file_to_write.write(data)
            ssl_client_soc.send("upload is over".encode())


def case2(server, ssl_client_soc, client_msg):
    reqFile = client_msg[1:].strip()  # this is the file to be downloaded
    if reqFile in server.FILES_LIST:  # if the server has the file
        filePath = os.path.join(server.FILES_DIR_PATH, reqFile)
        with open(filePath, 'rb') as file_to_send:
            fileSize = os.path.getsize(filePath)
            ssl_client_soc.send("start downloading,{}".format(fileSize).encode())  # this message is 22 bytes long
            fileContent = file_to_send.read()
            ssl_client_soc.sendall(fileContent)
            ssl_client_soc.sendall("download finished".encode())
            # for data in file_to_send:
            #     ssl_client_soc.sendall(data)
            # ssl_client_soc.sendall("download finished".encode())
    else:
        ssl_client_soc.send("ERROR: File Not Found ".encode())  # Padding a space so that the length of the message is 22







class My_Server():

    def __init__(self, LISTEN_PORT, SIMULTANEOUS_REQUESTS_LIMIT, FILES_DIR_PATH, FILES_LIST=[], HANDLE=handle) -> None:
        self.LISTEN_PORT = LISTEN_PORT
        self.SIMULTANEOUS_REQUESTS_LIMIT = SIMULTANEOUS_REQUESTS_LIMIT
        self.FILES_LIST = FILES_LIST
        self.FILES_DIR_PATH = FILES_DIR_PATH
            

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:
            server_address = ('', self.LISTEN_PORT)
            listen_socket.bind(server_address)
            listen_socket.listen(self.SIMULTANEOUS_REQUESTS_LIMIT)
            connections = {listen_socket}
            to_remove = []  # includes all the sockets that every client closes
            print("Server is listening")
            while True:
                # readable contains sockets that received a message (that we haven't read yet) from the client,
                # or the listen_socket for apply new connection
                readable, _, _ = select.select(connections, [], connections)
                for connection in readable:
                    if connection is listen_socket:  # a client wants to connect, probably starts the 3-way handshake of TCP
                        client_soc, client_address = listen_socket.accept()
                        ssl_client_soc = ssl.wrap_socket(client_soc, server_side=True, certfile="server.crt", keyfile="server.key")
                        ssl_client_soc.send("Welcome\n".encode())
                        connections.add(ssl_client_soc)
                    else:  # receive a message from a client - a request
                        try:
                            client_msg = connection.recv(4096).decode()
                            command_option = client_msg[0]  # type of the command
                            handle(self, connection, command_option, client_msg)
                        except Exception:  # case 4 (client wants to close the socket) or any other Exception with the socket
                            to_remove.append(connection)

                for s in to_remove:  # remove all the sockets that the clients closed from the current connections list
                    connections.remove(s)
                    s.close()
                to_remove = []





if __name__ == "__main__":
    path = "C:/University/YoungForTech/networks/Sending_Files_System/cloud"
    server = My_Server(9124, 5, path ,os.listdir(path))
    server.start()