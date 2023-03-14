import client

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9124
downloadUploadDir = "C:/University/YoungForTech/networks/Sending_Files_System/files_directory"
client = client.MyClient(SERVER_IP, SERVER_PORT, downloadUploadDir)
client.start()

client.closeConnection()