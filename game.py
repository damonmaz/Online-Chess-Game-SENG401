'''
the main game
author:@techwithtim
requirements:see requirements.txt
'''

import subprocess
import sys
import get_pip

def install(package):
    """
    Installs package using pip

    Arguments:
        package (string): The name of the package to install
    """
    subprocess.call([sys.executable, "-m", "pip", "install", package])

#Try to import or install pygame
try:
    print("[GAME] Trying to import pygame")
    import pygame
except:
    print("[EXCEPTION] Pygame not installed")

    try:
        print("[GAME] Trying to install pygame via pip")
        import pip
        install("pygame")
        print("[GAME] Pygame has been installed")
    except:
        print("[EXCEPTION] Pip not installed on system")
        print("[GAME] Trying to install pip")
        get_pip.main()
        print("[GAME] Pip has been installed")
        try:
            print("[GAME] Trying to install pygame")
            import pip
            install("pygame")
            print("[GAME] Pygame has been installed")
        except:
            print("[ERROR 1] Pygame could not be installed")


import pygame
import os
import time
from client import Network
import pickle
from board import BOARD_SIZE
pygame.font.init()


#Game timing constants
DEFAULT_PLAYING_TIME = 900  # 15 minutes in seconds
UPDATE_COUNT = 60  # frames before board update
SET_TIMER = 3000
   
#Window drawing constants
WINDOW_MARGIN = 113
WINDOW_SIZE = 525 
    
WIDTH = 750
HEIGHT = 750

#Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

#Text constants
TEXT10 = 10
TEXT20 = 20
TEXT30 = 30
TEXT50 = 50
TEXT80 = 80
TEXT300 = 300
TEXT500 = 500
TEXT520 = 520
TEXT700 = 700

#Load images
board = pygame.transform.scale(pygame.image.load(os.path.join("img","board_alt.png")), (WIDTH, HEIGHT))
chessbg = pygame.image.load(os.path.join("img", "chessbg.png"))

turn = "w"

def menu_screen(win, name):
    """
    Displays menu screen and handles user interactions

    Arguments:
        win (pygame.Surface): The window surface to draw on
        name (string): The player name
    """
    global bo, chessbg
    run = True
    offline = False

    #Try to connect to the server
    while run:
        win.blit(chessbg, (0,0))
        small_font = pygame.font.SysFont("comicsans", TEXT50)
        
        if offline:
            off = small_font.render("Server Offline, Try Again Later...", 1, RED)
            win.blit(off, (WIDTH / 2 - off.get_width() / 2, TEXT500))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False

            #If the user clicks the screen, try to connect to the server
            if event.type == pygame.MOUSEBUTTONDOWN:
                offline = False
                try:
                    bo = connect()
                    run = False
                    main()
                    break
                except:
                    print("Server Offline")
                    offline = True


    
def redraw_game_window(win, bo, p1, p2, color, ready):
    """
    Redraws the game window with the current game state

    Arguments:
        win (pygame.Surface): The window surface to draw on
        bo (Board): The game board object
        p1 (int): Player 1's remaining time
        p2 (int): Player 2's remaining time
        color (string): The player's color
        ready (bool): Whether the game is ready to start
    """
    win.blit(board, (0, 0))
    bo.draw(win, color)

    #Draw the timer
    format_time_one = str(int(p1//UPDATE_COUNT)) + ":" + str(int(p1%UPDATE_COUNT))
    format_time_two = str(int(p2 // UPDATE_COUNT)) + ":" + str(int(p2 % UPDATE_COUNT))
    if int(p1%UPDATE_COUNT) < 10:
        format_time_one = format_time_one[:-1] + "0" + format_time_one[-1]
    if int(p2%UPDATE_COUNT) < 10:
        format_time_two = format_time_two[:-1] + "0" + format_time_two[-1]

    #Draw the player names and timers
    font = pygame.font.SysFont("comicsans", TEXT30)
    try:
        txt = font.render(bo.p1Name + "\'s Time: " + str(format_time_two), 1, WHITE)
        txt2 = font.render(bo.p2Name + "\'s Time: " + str(format_time_one), 1, WHITE)
    except Exception as e:
        print(e)
    win.blit(txt, (TEXT520, TEXT10))
    win.blit(txt2, (TEXT520, TEXT700))

    txt = font.render("Press q to Quit", 1, WHITE)
    win.blit(txt, (TEXT10, TEXT20))

    #Draw the game state
    if color == "s":
        txt3 = font.render("SPECTATOR MODE", 1, RED)
        win.blit(txt3, (WIDTH/2-txt3.get_width()/2, TEXT10))

    if not ready:
        show = "Waiting for Player"
        if color == "s":
            show = "Waiting for Players"
        font = pygame.font.SysFont("comicsans", TEXT80)
        txt = font.render(show, 1, RED)
        win.blit(txt, (WIDTH/2 - txt.get_width()/2, TEXT300))

    if not color == "s":
        font = pygame.font.SysFont("comicsans", TEXT30)
        if color == "w":
            txt3 = font.render("YOU ARE WHITE", 1, RED)
            win.blit(txt3, (WIDTH / 2 - txt3.get_width() / 2, TEXT10))
        else:
            txt3 = font.render("YOU ARE BLACK", 1, RED)
            win.blit(txt3, (WIDTH / 2 - txt3.get_width() / 2, TEXT10))

        if bo.turn == color:
            txt3 = font.render("YOUR TURN", 1, RED)
            win.blit(txt3, (WIDTH / 2 - txt3.get_width() / 2, TEXT700))
        else:
            txt3 = font.render("THEIR TURN", 1, RED)
            win.blit(txt3, (WIDTH / 2 - txt3.get_width() / 2, TEXT700))

    pygame.display.update()


def end_screen(win, text):
    """
    Displays the end screen with the given text

    Arguments:
        win (pygame.Surface): The window surface to draw on
        text (string): The text to display on the end screen
    """
    
    #Draw the end screen
    pygame.font.init()
    font = pygame.font.SysFont("comicsans", TEXT80)
    txt = font.render(text,1, RED)
    win.blit(txt, (WIDTH / 2 - txt.get_width() / 2, TEXT300))
    pygame.display.update()

    pygame.time.set_timer(pygame.USEREVENT+1, SET_TIMER)
    
    #Wait for user to close the window
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                run = False
            elif event.type == pygame.KEYDOWN:
                run = False
            elif event.type == pygame.USEREVENT+1:
                run = False


def click(pos):
    """
    Converts a mouse click position to board coordinates

    Arguments:
        pos (tuple): The (x, y) position of the mouse click

    Returns:
        tuple: The (i, j) board coordinates or (-1, -1) if out of bounds
    """
    x = pos[0]
    y = pos[1]
    
    #Check if the click is within the board
    if WINDOW_MARGIN < x < WINDOW_MARGIN + WINDOW_SIZE:
        if WINDOW_MARGIN < y < WINDOW_MARGIN + WINDOW_SIZE:
            divX = x - WINDOW_MARGIN
            divY = y - WINDOW_MARGIN
            i = int(divX / (WINDOW_SIZE/BOARD_SIZE))
            j = int(divY / (WINDOW_SIZE/BOARD_SIZE))
            return i, j

    return -1, -1


def connect():
    """
    Connects to the game server and retrieves the initial game board

    Returns:
        Board: The initial game board object
    """
    global n
    n = Network()
    return n.board


def main():
    """
    main function to run the game
    """
    global turn, bo, name

    color = bo.start_user
    count = 0

    bo = n.send("update_moves")
    bo = n.send("name " + name)
    clock = pygame.time.Clock()
    run = True

    #Main game loop
    while run:
        if not color == "s":
            p1_time = bo.time1
            p2_time = bo.time2
            if count == UPDATE_COUNT:
                bo = n.send("get")
                count = 0
            else:
                count += 1
            clock.tick(30)

        #Redraw the game window
        try:
            redraw_game_window(win, bo, p1_time, p2_time, color, bo.ready)
        except Exception as e:
            print(e)
            end_screen(win, "Other player left")
            run = False
            break

        #Check for game over conditions
        if not color == "s":
            if p1_time <= 0:
                bo = n.send("winner b")
            elif p2_time <= 0:
                bo = n.send("winner w")

            if bo.check_mate("b"):
                bo = n.send("winner b")
            elif bo.check_mate("w"):
                bo = n.send("winner w")

        if bo.winner == "w":
            end_screen(win, "White is the Winner!")
            run = False
        elif bo.winner == "b":
            end_screen(win, "Black is the winner")
            run = False

        #Handle user interactions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and color != "s":
                    # quit game
                    if color == "w":
                        bo = n.send("winner b")
                    else:
                        bo = n.send("winner w")

                if event.key == pygame.K_RIGHT:
                    bo = n.send("forward")

                if event.key == pygame.K_LEFT:
                    bo = n.send("back")


            if event.type == pygame.MOUSEBUTTONUP and color != "s":
                if color == bo.turn and bo.ready:
                    pos = pygame.mouse.get_pos()
                    bo = n.send("update moves")
                    i, j = click(pos)
                    bo = n.send("select " + str(i) + " " + str(j) + " " + color)
    
    n.disconnect()
    bo = 0
    menu_screen(win)

name = input("Please type your name: ")
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
menu_screen(win, name)
