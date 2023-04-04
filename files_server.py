import socket
import select
import os
import ssl
import threading

from general_server import My_Server


path = "C:/University/Cyber/networks/Sending_Files_System/cloud"
listen_port = 9124
simultaneous_requests_limit = 5
files_list = []


def get_files(folder_path):
    files = os.listdir(folder_path)
    
    for file in files:
        if os.path.isfile(os.path.join(folder_path, file)):
            files_list.append(file)


def handle(client_soc, client_soc_address):  # the server message to the client
    while True:
        client_msg = client_soc.recv(1024).decode()
        print(client_msg)
        command_option = client_msg[0]
        match command_option:
            case '1':  # the client wants to upload a file
                case1(client_soc, client_msg)

            case '2':  # the client wants to download a a file
                case2(client_soc, client_msg)
                
            case '3':  # the client requests the list of the available files that the server holds
                fileList = " ".join(files_list)
                client_soc.sendall(len(fileList).to_bytes(4, byteorder='big'))
                client_soc.sendall(fileList.encode())
                
            case '4':  # the client wants to close the connection
                client_soc.sendall("closing_the_socket".encode())
                client_soc.close()
                break
            
            case _:
                client_soc.sendall("error - command option not found\n".encode())  # not in the protocol rules, actually can't get here


def case1(client_soc, client_msg): 
        client_msg = client_msg.split(" ")  # splitting between the type of the command, the filename and the file-size 
        filename = client_msg[1]  # the name of the file that the client wants to upload
        client_soc.sendall("start uploading".encode())
        with open(os.path.join(path, filename), 'wb') as file_to_write:
            fileSize = int(client_msg[2])
            bytes_written = 0
            while bytes_written != fileSize:
                data = client_soc.recv(1024)
                file_to_write.write(data)
                bytes_written += len(data)
            files_list.append(filename)


def case2(client_soc, client_msg):
    reqFile = client_msg[1:].strip()  # this is the filename to be downloaded
    if reqFile in files_list:  # if the server has the file
        client_soc.sendall("True ".encode())  # Padding with a space so that the message length will be 5 as "False"

        filePath = os.path.join(path, reqFile)
        with open(filePath, 'rb') as file_to_send:
            fileSize = os.path.getsize(filePath)
            client_soc.sendall(fileSize.to_bytes(4, byteorder='big'))  # this message is 4 bytes long
            fileContent = file_to_send.read()
            client_soc.sendall(fileContent)
    else:
        client_soc.sendall("False".encode())  



if __name__ == "__main__":
    get_files(path)
    server = My_Server(listen_port, simultaneous_requests_limit, handle=handle)
    server.start()