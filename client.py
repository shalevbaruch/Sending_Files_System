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
                    

    def uploadFile(self, filename):
        filePath = os.path.join(self.downloadUploadDir, filename)
        if os.path.exists(filePath) and len(filename) != 0:  # if the file exists
            self.sendFile(filename)
        else:
            print("Illegal Filename")


    def sendFile(self, filename):
        filePath = os.path.join(self.downloadUploadDir, filename)
        with open(filePath, 'rb') as file_to_read:
            FileSize = os.path.getsize(filePath)
            if FileSize != 0:
                self.sslSock.sendall("1 {} {}".format(filename, FileSize).encode())
                message = self.sslSock.recv(15).decode()
                print(message)  # a message from the server that he is starting to upload the file
                fileContent = file_to_read.read()
                self.sslSock.sendall(fileContent)
                print("upload is finished")  # a message from the server that he finished the upload
            else:
                print("ERROR: the file is empty")


    def downloadFile(self, filename):
        self.sslSock.sendall("2 {}".format(filename).encode())
        isExist = self.sslSock.recv(5).decode()  # is the file requested actually exist
          # 4 because the length of the first server message in this case is 4 bytes long
        if isExist == "False":  #  we get this message from the server iff the file exists
            print("ERROR: File Not Found ")
            return
        fileSize = self.sslSock.recv(4)
        fileSize = int.from_bytes(fileSize, byteorder='big')
        print("start downloading")
        with open(os.path.join(self.downloadUploadDir, filename), 'wb') as file_to_write:
            writtenBytes = 0  # counter for the bytes that we wrote to the file
            while writtenBytes != fileSize:
                data = self.sslSock.recv(1024)       
                file_to_write.write(data)
                writtenBytes += len(data)
            print("download is finished")
        file_to_write.close()  # not sure if needed becasue of the usage of "with open"

    
    def availableFiles(self):
        self.sslSock.sendall("3".encode())
        listSize = self.sslSock.recv(4)
        listSize = int.from_bytes(listSize, byteorder='big')
        writtenBytes = 0  # counter for the bytes that we wrote to the file
        filesList = b''
        while writtenBytes != listSize:
            data = self.sslSock.recv(1024)
            filesList += data
            writtenBytes += len(data)
        filesList = filesList.decode()
        return filesList


    def closeConnection(self):
        self.sslSock.sendall("4".encode())
        print("connection closed")
        self.sslSock.close()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 9124
    downloadUploadDir = "C:/University/YoungForTech/networks/Sending_Files_System/files_directory"
    client = MyClient(SERVER_IP, SERVER_PORT, downloadUploadDir)
    client.start()