import socket
from _thread import *
from board import Board, BOARD_SIZE
from game import DEFAULT_PLAYING_TIME
import pickle
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connections = 0
games = {0:Board(8, 8)}
spectartor_ids = [] 
specs = 0

#Connection settings
SERVER = "localhost"
PORT = 5555
MAX_CONNECTIONS = 6

server_ip = socket.gethostbyname(SERVER)

#bind server to port
try:
    s.bind((SERVER, PORT))

except socket.error as e:
    print(str(e))

#wait for connections
s.listen()
print("[START] Waiting for a connection")


def read_specs():
    """
    Reads spectator ids from a file and stores them in `spectartor_ids` list variable
    If the file doesn't exist, creates an empty file
    """
    global spectartor_ids

    spectartor_ids = []
    try:
        with open("specs.txt", "r") as f:
            for line in f:
                spectartor_ids.append(line.strip())
    except:
        print("[ERROR] No specs.txt file found, creating one...")
        open("specs.txt", "w")


def threaded_client(conn, game, spec=False):
    """
    Handle communication with clients
    
    Arguments:
        conn: connection object for the client.
        game: game identifier.
        spec: flag indicating if the client is a spectator or not
    """
    global pos, games, current_id, connections, specs
    BUFFER_SIZE = 8192 * 3
    BUFFER_SIZE2 = 128

    if not spec:
        name = None
        bo = games[game]

        # assign peice color
        if connections % 2 == 0:
            current_id = "w"
        else:
            current_id = "b"

        bo.start_user = current_id

        # Pickle the object and send it to the SERVER
        data_string = pickle.dumps(bo)

        if current_id == "b":
            bo.ready = True
            bo.start_time = time.time()

        conn.send(data_string)
        connections += 1


        while True:
            if game not in games:
                break

            try:
                d = conn.recv(BUFFER_SIZE)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    #player selecting piece
                    if data.count("select") > 0:
                        all = data.split(" ")
                        col = int(all[1])
                        row = int(all[2])
                        color = all[3]
                        bo.select(col, row, color)

                    #check for winner
                    if data == "winner b":
                        bo.winner = "b"
                        print("[GAME] Player b won in game", game)
                    if data == "winner w":
                        bo.winner = "w"
                        print("[GAME] Player w won in game", game)

                    #update valid moves
                    if data == "update moves":
                        bo.update_moves()

                    #set player names
                    if data.count("name") == 1:
                        name = data.split(" ")[1]
                        if current_id == "b":
                            bo.p2_name = name
                        elif current_id == "w":
                            bo.p1_name = name

                    #print("Recieved board from", current_id, "in game", game)

                    #Adjust the player timers
                    if bo.ready:
                        if bo.turn == "w":
                            bo.time1 = DEFAULT_PLAYING_TIME - (time.time() - bo.start_time) - bo.stored_time_one
                        else:
                            bo.time2 = DEFAULT_PLAYING_TIME - (time.time() - bo.start_time) - bo.stored_time_two

                    send_data = pickle.dumps(bo)
                    #print("Sending board to player", current_id, "in game", game)

                conn.sendall(send_data)

            except Exception as e:
                print(e)
        
        #remove connection and delete game
        connections -= 1
        try:
            del games[game]
            print("[GAME] Game", game, "ended")
        except:
            pass
        print("[DISCONNECT] Player", name, "left game", game)
        conn.close()

    else:
        #update available games for viewing and send to spectator
        available_games = list(games.keys())
        game_ind = 0
        bo = games[available_games[game_ind]]
        bo.start_user = "s"
        data_string = pickle.dumps(bo)
        conn.send(data_string)

        while True:
            available_games = list(games.keys())
            bo = games[available_games[game_ind]]
            try:
                #recieve and handle spectator data
                d = conn.recv(BUFFER_SIZE2)
                data = d.decode("utf-8")
                if not d:
                    break
                else:
                    try:
                        if data == "forward":
                            print("[SPECTATOR] Moved Games forward")
                            game_ind += 1
                            if game_ind >= len(available_games):
                                game_ind = 0
                        elif data == "back":
                            print("[SPECTATOR] Moved Games back")
                            game_ind -= 1
                            if game_ind < 0:
                                game_ind = len(available_games) -1

                        bo = games[available_games[game_ind]]
                    except:
                        print("[ERROR] Invalid Game Recieved from Spectator")

                    #send current game data to spectator
                    send_data = pickle.dumps(bo)
                    conn.sendall(send_data)

            except Exception as e:
                print(e)

        print("[DISCONNECT] Spectator left game", game)
        specs -= 1
        conn.close()


while True:
    read_specs()
    #check for space for new connections
    if connections < MAX_CONNECTIONS:
        conn, addr = s.accept()
        spec = False
        g = -1
        print("[CONNECT] New connection")

        #find available game
        for game in games.keys():
            if games[game].ready == False:
                g=game

        #create new game if none are available
        if g == -1:
            try:
                g = list(games.keys())[-1]+1
                games[g] = Board(BOARD_SIZE, BOARD_SIZE)
            except:
                g = 0
                games[g] = Board(BOARD_SIZE, BOARD_SIZE)

        '''if addr[0] in spectartor_ids and specs == 0:
            spec = True
            print("[SPECTATOR DATA] Games to view: ")
            print("[SPECTATOR DATA]", games.keys())
            g = 0
            specs += 1'''

        print("[DATA] Number of Connections:", connections+1)
        print("[DATA] Number of Games:", len(games))

        start_new_thread(threaded_client, (conn,g,spec))
