import socket
import pickle
import time

class Network:
    
    BUFFER_SIZE = 4096*8
    TIMEOUT = 5
    
    def __init__(self):
        """
        Initialize the Network class. 
        Creates a socket, sets up connection parameters, and establishing a connection to the server
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"
        self.port = 5555
        self.addr = (self.host, self.port) #address being connected to
        self.board = self.connect()
        self.board = pickle.loads(self.board) #unplickles board data

    def connect(self):
        """
        connect to the server

        Returns:
            Data recieved from server, which represents the board state
        """
        self.client.connect(self.addr)
        return self.client.recv(self.BUFFER_SIZE)

    def disconnect(self):
        """
        Close connection to server
        """
        self.client.close()

    def send(self, data, pick=False):
        """
        Sends data to the server and waits for response

        Arguments:
            data (string or pickled object): The data to send
            pick (string or pickled object): If True, data sent as pickled object, else data is sent as string

        Returns:
            servers response (string or pickled object)
        """
        #Timer for timeout
        start_time = time.time()
        while time.time() - start_time < self.TIMEOUT:
            #semd data to server
            try:
                if pick:
                    self.client.send(pickle.dumps(data))
                else:
                    self.client.send(str.encode(data))
                reply = self.client.recv(self.BUFFER_SIZE)
                
                #load reply and break loop
                try:
                    reply = pickle.loads(reply)
                    break
                except Exception as e:
                    print(e)

            except socket.error as e:
                print(e)


        return reply


