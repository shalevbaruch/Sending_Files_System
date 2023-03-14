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
        ssl_sock = ssl.wrap_socket(sock)  # add a layer of security
        server_address = (self.SERVER_IP, self.SERVER_PORT)
        ssl_sock.connect(server_address)
        self.sslSock = ssl_sock
        print(self.sslSock.recv(4096).decode())  # the server sends a "Welcome" message
                    

    def uploadFile(self, filename):
        self.sslSock.send("1 {}".format(filename).encode())
        if len(filename) != 0:
            print("start uploading")
            with open(os.path.join(self.downloadUploadDir, filename), 'rb') as file_to_read:
                for data in file_to_read:
                    self.sslSock.sendall(data)
                self.sslSock.sendall("The upload is completed".encode())
                print("The upload is completed")
        else:
            print("Illegal Filename. Try Again")


    def downloadFile(self, filename):
        self.sslSock.send("2 {}".format(filename).encode())
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