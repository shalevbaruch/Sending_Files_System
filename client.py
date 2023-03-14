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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connecting to remote computer 9124
        ssl_sock = ssl.wrap_socket(sock)  # add a security layer
        server_address = (self.SERVER_IP, self.SERVER_PORT)
        ssl_sock.connect(server_address)
        self.sslSock = ssl_sock
        print(self.sslSock.recv(4096).decode())  # the server sends a "Welcome" message
                    

    def uploadFile(self, filename):
        filePath = os.path.join(self.downloadUploadDir, filename)
        if os.path.exists(filePath) and len(filename) != 0:  # if the file exists
            self.sendFile(filename)
        else:
            print("Illegal Filename. Try Again")


    def sendFile(self, filename):
        filePath = os.path.join(self.downloadUploadDir, filename)
        with open(filePath, 'rb') as file_to_read:
            FileSize = os.path.getsize(filePath)
            if FileSize != 0:
                self.sslSock.send("1 {} {}".format(filename, FileSize).encode())
                print(self.sslSock.recv(1024).decode())  # a message from the server that he is starting to upload the file
                fileContent = file_to_read.read()
                self.sslSock.send(fileContent)
                print(self.sslSock.recv(1024).decode())  # a message from the server that he finished the upload
            else:
                print("ERROR: the file is empty")


    def downloadFile(self, filename):
        self.sslSock.send("2 {}".format(filename).encode())
        message = self.sslSock.recv(22).decode()  # 22 because the length of the first message in this case is 21 bytes long
        message = message.split(",")
        print(message[0])
        if message[0] != "start downloading":  #  we get this message from the server iff filename is legal
            return
        
        with open(os.path.join(self.downloadUploadDir, filename), 'wb') as file_to_write:
            fileSize = int(message[1])
            data = self.sslSock.recv(fileSize)       
            file_to_write.write(data)
            end_message = self.sslSock.recv(17).decode()
            print(end_message)
        file_to_write.close()  # not sure if needed becasue of the usage of "with open"

    
    def availableFiles(self):
        self.sslSock.send("3".encode())
        message_from_server = self.sslSock.recv(4096).decode()
        return message_from_server


    def closeConnection(self):
        self.sslSock.send("4".encode())
        print("connection closed")
        self.sslSock.close()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 9124
    downloadUploadDir = "C:/University/YoungForTech/networks/Sending_Files_System/files_directory"
    client = MyClient(SERVER_IP, SERVER_PORT, downloadUploadDir)
    client.start()