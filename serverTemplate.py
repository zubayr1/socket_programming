from socket import *
import hashlib
import os
#

# Generate md5 hash function
#
def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)


def get_hash_of_file_data(file_name):
    STRING=''
    f = open(os.getcwd()+'/serverfolder/'+file_name, 'rb') #read in binary
                    
    l = f.read(1024)

    while(l):
        STRING+=str(l)
        l= f.read(1024)
    f.close()
    BYTES = str.encode(STRING)
    return generate_md5_hash(BYTES)


# Define Server URL and PORT
serverPort = 7700 #10048#
serverURL = "localhost"


# Create TCP socket for future connections
#
serverSocket = socket(AF_INET, SOCK_STREAM)

# Bind URL and Port to the created socket
#
serverSocket.bind((serverURL, serverPort))


# Start listening for incoming connection (1 client at a time)
#
serverSocket.listen(1)
print("Server is listening on port: " + str(serverPort))


while True:
    # 
    # Accept incoming client connection
    #
    if not os.path.exists('serverfolder'):
        os.makedirs('serverfolder')
        
    connectSocket, addr = serverSocket.accept()
    print("Client connected: " + str(addr))
    
    clientRequest = connectSocket.recv(1024)    
    print('Received Request', clientRequest)
    
    if clientRequest==b'LIST_FILES':
        print("Client Wants to Get the List of Files")
        
        if(len(os.listdir(os.getcwd() + '/serverfolder')))==0:
            print("Sending Empty Directory Message")
            serverResponse= 'No files available at the moment.'
            
            serverResponsetobytes = str.encode(serverResponse)
            
            connectSocket.sendall(serverResponsetobytes)
        else:
            arr = os.listdir(os.getcwd() + '/serverfolder')
            print("Sending File Information...")
            for i in arr:
                print('Sending Info of: '+i)
                fileinfoinbytes = str.encode(get_hash_of_file_data(i)+' '+i+" " +str(round(os.path.getsize(os.getcwd()+'/serverfolder'+'/'+i)/1024,4))+' KB'+"\0/")
                connectSocket.sendall(fileinfoinbytes)
                
            ENDOFFILE = str.encode('eof')
            connectSocket.sendall(ENDOFFILE)
            
    elif clientRequest==b'UPLOAD':
        print("Asking for File Name and File Size")
        inpinstr = 'Send File Name and File Size'
        inpinbytes = str.encode(inpinstr)
        connectSocket.sendall(inpinbytes)
        
        receivedfileinfo = connectSocket.recv(1024)
        print('File Name and Size: ',str(receivedfileinfo)[1:])
        filename=str(receivedfileinfo)[2:].split(';')
        serverconf = 'ready to receive a file'
        
        print(serverconf)
        connectSocket.sendall(str.encode(serverconf))
        
        CHECK=True
        
        with open('serverfolder/'+filename[0], 'wb') as f:
            print('Trying to Upload File')

            while(CHECK):
                print('Receiving Data...')
                data = connectSocket.recv(1024)
                print('data: ', data)
                if data.endswith(b'\x00/eof') or data==b'' or data==b'404:File Not Exists' or data==b'eof':
                    CHECK=False
                    
                if data.endswith(b'\x00/eof'):
                    data =data[0:len(data)-5]
                    
                f.write(data)
        f.close()
        if data!=b'404:File Not Exists':
            md5hash = get_hash_of_file_data(filename[0])
            print('Sending md5 Hash')
            connectSocket.sendall(str.encode(md5hash))
            clientuploadmessage = connectSocket.recv(1024)
            print(str(clientuploadmessage)[1:])
        if data!=b'404:File Not Exists':
            print('File Uploaded Successfully')
        else:
            os.remove('serverfolder/'+str(filename[0]))
            print('File could not be Uploaded')
    
    elif clientRequest==b'DOWNLOAD':
        print('Request for File Download')
        inpinstr = 'Send File ID'
        inpinbytes = str.encode(inpinstr)
        connectSocket.sendall(inpinbytes)
        fileid = connectSocket.recv(1024)
        print('Requested File ID', fileid)
        
        if(len(os.listdir(os.getcwd() + '/serverfolder')))==0:
            print("Sending Empty Directory Message")
            serverResponse= 'No files available at the moment.'
            
            serverResponsetobytes = str.encode(serverResponse)
            
            connectSocket.sendall(serverResponsetobytes)
        else:
            arr = os.listdir(os.getcwd() + '/serverfolder')
            print("Sending File Data...")
            FLAG=0
            for i in arr:
                if(str.encode(get_hash_of_file_data(i))==fileid):
                    print('Requested File', i)
                    FLAG=1
                    connectSocket.send(str.encode(i))
                    f = open(os.getcwd()+'/serverfolder/'+i, 'rb') #read in binary
                    
                    l = f.read(1024)
                    
                    while(l):
                        connectSocket.send(l)
                        print('Sent: ',l)
                        l= f.read(1024)
                    f.close()
                    
                    ENDOFFILE = str.encode('eof')
                    connectSocket.sendall(ENDOFFILE)
                    print('End of Sending File')
                    
                    
            if(FLAG==0):
                fileinfo = '404:File Not Exists'
                print(fileinfo)
                fileinfo = str.encode(fileinfo)
                connectSocket.send(fileinfo)
                
            
    else:
        wrong_command= "WRONG COMMAND"
        print(wrong_command)
        wrong_command = str.encode("WRONG COMMAND")
        connectSocket.send(wrong_command)
                
    
    

    #close TCP connection
    print('Closing Server Connection with the Existing Client')
    connectSocket.close()