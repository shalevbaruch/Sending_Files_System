import socket
import ssl
import os



class MyClient():
    def __init__(self, SERVER_IP, SERVER_PORT, downloadUploadDir, ssl_sock=None) -> None:
        self.SERVER_IP = SERVER_IP
        self.SERVER_PORT = SERVER_PORT
        self.downloadUploadDir = downloadUploadDir
        self.sslSock = ssl_sock
    def start(self):  # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connecting to remote computer 9124
            ssl_sock = ssl.wrap_socket(sock)  # add a layer of security
            server_address = (self.SERVER_IP, self.SERVER_PORT)
            ssl_sock.connect(server_address)
            self.sslSock = ssl_sock
            print(self.sslSock.recv(4096).decode())
            while True:
                try:
                    client_msg = input("Select an option\n1 + File Name - Upload a file\n"
                                    "2 + File Name - Download a file\n3 - Get List of files\n4 - exit\n")
                except:
                    print("forced_close, connection cut off")
                    break
                else:
                    self.sslSock.send(client_msg.encode())
                    if len(client_msg) == 0:
                        print("ERROR: COMMAND NOT FOUND. TRY AGAIN")
                    elif client_msg[0] == "1":  # the client wants to upload a file to the server
                        self.case1(client_msg)
                    elif  client_msg[0] == "2":  # the client wants to download a file from the server
                        self.case2(client_msg)
                    else:  # means client_msg[0] == 3 or client_msg[0] == 4 or invalid message
                        message_from_server = self.sslSock.recv(4096).decode()
                        print(message_from_server)
                        if message_from_server == "end of conversation":
                            break
                    

    def case1(self, client_msg):
        filename = client_msg[1:].strip()
        if len(filename) != 0:
            print("start uploading")
            with open(os.path.join(self.downloadUploadDir, filename), 'rb') as file_to_read:
                for data in file_to_read:
                    self.sslSock.sendall(data)
                self.sslSock.sendall("The upload is completed".encode())
                print("The upload is completed")
        else:
            print("Illegal Filename. Try Again")


    def case2(self, client_msg):
        filename = client_msg[1:].strip()
        message = self.sslSock.recv(1024).decode()
        print(message)
        if message != "start downloading":  #  we get this message from the server iff filename is legal
            return
        
        with open(os.path.join(self.downloadUploadDir, filename), 'wb') as file_to_write:
            while True:
                data = self.sslSock.recv(1024)       
                if data == b'download finished':  # no more data to write to the file
                    print("download is finished")
                    break
                file_to_write.write(data)
            file_to_write.close()  # not sure if needed becasue of the usage of "with open"


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 9124
    downloadUploadDir = "C:/University/YoungForTech/networks/Sending_Files_System/files_directory"
    client = MyClient(SERVER_IP, SERVER_PORT, downloadUploadDir)
    client.start()