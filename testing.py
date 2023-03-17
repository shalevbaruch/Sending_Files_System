import client
import sys
sys.path.append("C:/University/YoungForTech/networks")  # it is working, The "error" offered should be ignored
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9124
downloadUploadDir = "C:/University/YoungForTech/networks/Sending_Files_System/files_directory"
client = client.MyClient(SERVER_IP, SERVER_PORT, downloadUploadDir)
client.start()
# client.downloadFile("file123.txt")
# print(client.availableFiles())
# client.uploadFile("file98.txt")
# client.uploadFile("")
# print(client.availableFiles())
client.closeConnection()