# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
import os

# Generate md5 hash function
#
def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)


def get_hash_of_file_data(file_name):
    STRING=''
    f = open(os.getcwd()+'/clientfolder/'+file_name, 'rb', ) #read in binary
                    
    l = f.read(1024)

    while(l):
        STRING+=str(l)
        l= f.read(1024)
    f.close()
    BYTES = str.encode(STRING)
    return generate_md5_hash(BYTES)


# Define Server URL and PORT
#
serverPort = 7700
serverURL = "localhost"


# Create TCP socket for future connections
#
clientSocket = socket(AF_INET, SOCK_STREAM)


# 
# Connect the client to the specified server
#
clientSocket.connect((serverURL, serverPort))
print("Client connected to server: " + serverURL + ":" + str(serverPort))


# This client implements the following scenario:
# 1. LIST_FILES
# 2a. UPLOAD the specified file
# 2b. Check MD5
# 3. LIST_FILES
# 4a. DOWNLOAD the previously uploaded file
# 4b. Check MD5
#
#close TCP connection
inp = input("Client Request Type: ")
inpinbytes = str.encode(inp)
clientSocket.sendall(inpinbytes)

#f5fba746a759eac2276de29418a8731f 

while not clientSocket._closed:
    responsefileinfo= clientSocket.recv(1024)
    
    if responsefileinfo==b'eof' or responsefileinfo==b'WRONG COMMAND' or responsefileinfo==b'':
        if responsefileinfo==b'WRONG COMMAND':
            print(responsefileinfo)
        break
    else:    
        responsefileinfo = responsefileinfo.decode("utf-8").split("\0/")
        if responsefileinfo[0]!='eof':
            print('Received Request: ', responsefileinfo[0])
        if len(responsefileinfo)==2:
            if responsefileinfo[1]!='' and responsefileinfo[1]!='eof':
                print('Received Request: ', responsefileinfo[1])
        if(responsefileinfo[0]=='Send File ID'):
            inpfileid = input('Give File ID: ')
            inpfileid = str.encode(inpfileid)
            clientSocket.send(inpfileid)
            reqfilename = clientSocket.recv(1024)
            
            if reqfilename!=b'404:File Not Exists' and reqfilename!=b'No files available at the moment.':
                print('Requested File Name: ', reqfilename)
                if not os.path.exists('clientfolder'):
                    os.makedirs('clientfolder')
                CHECK=True
                with open('clientfolder/'+str(reqfilename).replace("'", "")[1:], 'wb') as f:
                    print('Trying to Open File')

                    while(CHECK):
                        print('Receiving Data...')
                        data = clientSocket.recv(1024)
                        print('data: ', data)
                        if data==b'eof' or data==b'404:File Not Exists' or data==b'' or data==b'Sending Empty Directory Message':
                            CHECK=False
                            break
                        f.write(data)
                f.close()
                print('File Downloaded Successfully')
            else:
                print(reqfilename)
                print('File Could not be Downloaded')
        elif(responsefileinfo[0]=='Send File Name and File Size'):
            filename = input('Send File Name: ')
            filesize = input('Send File Size: ')
            inpfromclient = str.encode(filename+';'+filesize )
            clientSocket.sendall(inpfromclient)
            
            serverconf = clientSocket.recv(1024)
            print('Server Response: ',str(serverconf)[1:])
            if serverconf==b'ready to receive a file':
                arr = os.listdir(os.getcwd() + '/clientfolder')
                print("Sending File Data...")
                
                FLAG=0
                for i in arr:
                    if i==filename:
                        FLAG=1
                        f = open(os.getcwd()+'/clientfolder/'+i, 'rb') #read in binary
                        l = f.read(1024)
                        while(l):
                            clientSocket.send(l)
                            
                            print('Sent: ',l)
                            l= f.read(1024)
                        f.close()
                        
                        
                        ENDOFFILE = str.encode('\0/eof')
                        clientSocket.send(ENDOFFILE)
                        print('End of Sending File')
                if FLAG==1:
                    hashfromserver = clientSocket.recv(1024)
                    uploadmessage=''
                    if hashfromserver==str.encode(get_hash_of_file_data(filename)):
                        uploadmessage='SUCCESS'
                    else:
                        uploadmessage='FAIL'
                    clientSocket.send(str.encode(uploadmessage))
                    print('Upload: ', uploadmessage)
                    print('Closing Client Connection')
                    clientSocket.close()
                
                if(FLAG==0):
                    fileinfo = '404:File Not Exists'
                    print(fileinfo)
                    fileinfo = str.encode(fileinfo)
                    clientSocket.send(fileinfo)
                    print('Closing Client Connection')
                    clientSocket.close()
            else:
                print('Could not get Confirmation from Server')
                break
            
if not clientSocket._closed:
    print('Closing Client Connection')
    clientSocket.close()