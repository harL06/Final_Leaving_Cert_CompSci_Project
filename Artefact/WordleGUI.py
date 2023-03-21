import PySimpleGUI as sg
import csv
import random
import math
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
# Allows you to use matplotlib within pysimplegui
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

now = datetime.now()


# Imports list of possible words from the text file

# There's two seperate lists imported. THere's a large list (~12972 words) that wordle accepts as guesses
# THere's a shorter list (~2315 words) that the answer can actually be
def wordImport():
    inputWordList = []
    f = open("valid-wordle-words.txt", "r", encoding="utf8")
    for line in f:
        inputWordList.append(line.strip("\n"))
    print(len(inputWordList), "valid words loaded...")
    
    answerWordList = []
    f = open("wordle-answers-alphabetical.txt", "r", encoding="utf8")
    for line in f:
        answerWordList.append(line.strip("\n"))
    print(len(answerWordList), "answer words loaded...")
    
    return inputWordList, answerWordList

def randomWord():
    # Picks random word from list
    chosenWord = answerWordList[random.randint(0, (len(answerWordList)-1))]
    return(chosenWord)


# Validates inputted guesses - called every guess
def guessValidation(currentGuess):

    if len(currentGuess) != 5:
        return "Invalid Guess - Not five letters!", ""

    elif currentGuess not in inputWordList:
        return "Invalid Guess", ""

    elif len(currentGuess) == 5 and currentGuess in inputWordList:
        return "", currentGuess

# Manages the colour updating of the inputted words
def colours(guess, wordList, chosenWord):
    
    previousGuesses.append(list(guess))
    
    
    # Makes colours
    cGreen = "#538d4f"
    cYellow = "#b59f3b"
    cGrey = "#3a3a3c"

    chosenWordList = list(chosenWord)
    
    # Checks to see if guessed letter should be green
    index = 0
    colourList = [" ", " ", " ", " ", " "]
    for letter in guess:
        if letter == chosenWordList[index]:
            colourList[index] = cGreen
            chosenWordList[index] = " "
        index += 1
        
    index = 0
    
    # Checks to see if guessed letter should be yellow
    for letter in guess:
        if letter in chosenWordList:
            if colourList[index] != '#538d4f':
                colourList[index] = cYellow
                chosenWordList[chosenWordList.index(letter)] = " "
        index += 1
    
    # If a letter is neither green nor yellow, it should be grey
    index = 0
    for item in colourList:
        if item == " ":
            colourList[index] = cGrey
        index += 1
        
    previousColours.append(colourList)
    return colourList
        


def logResults(gameType):
    # store guesses as full words rather than lists of letters
    try:
        with open("recorded_game_data.csv", 'a', encoding='UTF8', newline='') as f:
            # This creates a csv writer
            writer = csv.writer(f)
            
            
            # Cleans up the guess lists to write to csv
            cleanGuessList = []
            for guess in previousGuesses:
                cleanGuessList.append("".join(guess))
            gameGuesses = ":".join(cleanGuessList)
            
            # Cleans up the colour lists to write to csv : G = green - Y = yellow - X = grey
            cleanColourList = []
            
            for guess in previousColours:

                currentColours = []
                for colour in guess:
                    if colour == "#538d4f": # green
                        currentColours.append("G")
                    
                    elif colour == "#b59f3b": # yellow
                        currentColours.append("Y")
                        
                    elif colour == "#3a3a3c": # grey
                        currentColours.append("X")

                cleanColourList.append("".join(currentColours))

            gameColours = ":".join(cleanColourList)
            # Create a new row on the CSV file and logs this data
            logLine = [gameGuesses, gameColours, gameType]

            writer.writerow(logLine)
    except IOError:
        print("Could not log results! Please close Excel.")
        
# Simulation eliminating words from the possible list. If letter is grey, remove any words with it in it
# If it is yellow, remove any words that don't have it in it
# If it is green, remove words that don't have that letter in that exact place
def eliminateWords(guess, pullRemainingWords, colourList):
    remainingWords = pullRemainingWords.copy() 
    
    notGreen=[]
    notYellow=[]
    yLetters=[]
    notGrey=[]
    i = 0
    for letter in guess:
        if colourList[i] == "#538d4f" or colourList[i] == "#b59f3b":
            yLetters.append(guess[i])

        i+=1
    i=0
    for letter in guess:
        if infoGreen == True:
            if colourList[i] == "#538d4f": #green
                yLetters.append(guess[i])
                
                for word in remainingWords:
                    if str(word[i]) != str(guess[i]):

                        notGreen.append(word)
                for item in notGreen:
                    if item in remainingWords:
                        remainingWords.remove(item)
        if infoYellow == True:
            if colourList[i] == "#b59f3b": #yellow
                yLetters.append(guess[i])
                for word in remainingWords:
                    if word.find(guess[i]) == -1 or str(word[i]) == str(guess[i]):
                        notYellow.append(str(word))

                for item in notYellow:
                    if item in remainingWords:
                        remainingWords.remove(item)
        if infoGrey== True:
            if colourList[i] == "#3a3a3c" and guess[i] not in yLetters: #grey
                for word in remainingWords:
                    if word.find(guess[i]) != -1:
                        notGrey.append(str(word))

                for item in notGrey:
                    if item in remainingWords:
                        remainingWords.remove(item)
        i+=1

    if guess in remainingWords:
        remainingWords.remove(guess)

    return remainingWords

# Code to implement MatPlotLib with pySimpleGUI
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.get_tk_widget().forget()
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# Generates the guess frequency distribution for the simulation play
def drawHist(x_data, noGenerations, simWin):
    plt.cla()
    p1 = plt.hist(x_data, bins=np.arange(1,8)-0.5, range=[1,8], color="#538d4f", ec="#ffffff")


    plt.xticks(range(1,8), color = 'white')
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white') 
    plt.yticks(color = 'white')


    title=("Generations: "+str(noGenerations)+"\nWins: "+ str(simWin))
    plt.title(title, color="white")
    plt.xlabel("Number of Guesses", fontweight='bold', color="white")
    plt.ylabel("Frequency", fontweight='bold', color="white")
    


    plt.tight_layout()
    fig = plt.gcf()

    fig.set_facecolor('#121213')

   
    return fig

def drawLetterHist(x_data, sortingType):
    plt.cla()

    if sortingType == "Alpha":
        x_data = sorted(x_data)
    elif sortingType == "Freq":
        x_data = [item for items, c in Counter(x_data).most_common() for item in [items] * c]
    
    p1 = plt.hist(x_data, bins=np.arange(0,27)-0.5, range=[0,27], color="#538d4f", ec="#ffffff")


    plt.xticks(range(0,26), color = 'white')
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white') 
    plt.yticks(color = 'white')


    title=("Letter Frequency in Guesses")
    plt.title(title, color="white")
    plt.xlabel("Letters", fontweight='bold', color="white")
    plt.ylabel("Frequency", fontweight='bold', color="white")
    


    plt.tight_layout()
    fig = plt.gcf()

    fig.set_facecolor('#121213')

   
    return fig



def drawQValueGraph(topQValuesDisplay):
    topQValuesDisplay = int(topQValuesDisplay)
    plt.cla()
    dfQValues = pd.read_csv("Q_Values.csv")
    QValueWords = list(dfQValues[dfQValues.columns[0]])
    QValues = list(dfQValues[dfQValues.columns[1]])
    
    
    sortedWords = [x for _,x in sorted(zip(QValues,QValueWords), reverse=True)]
    sortedValues = sorted(QValues, reverse=True)
        


    
    p1 = plt.barh(sortedWords[0:topQValuesDisplay], sortedValues[0:topQValuesDisplay], color="#538d4f", ec="#ffffff")


    plt.yticks(color = 'white')

    plt.xticks(color = 'white')

    title=("Top "+ str(topQValuesDisplay) +" Q Values")
    plt.title(title, color="white")
    plt.xlabel("Q Value", fontweight='bold', color="white")
    plt.ylabel("Word", fontweight='bold', color="white")
    

    plt.tight_layout()
    fig = plt.gcf()

    fig.set_facecolor('#121213')
    return fig

def drawBasicStatsGraph(UseSPdata, UseMPdata, UseSIMdata):
    # Pulls all recorded game data from CSV
    dfGameData = pd.read_csv("recorded_game_data.csv")
    guessData = list(dfGameData[dfGameData.columns[0]])
    colourData = list(dfGameData[dfGameData.columns[1]])
    gameType = list(dfGameData[dfGameData.columns[2]])
    

    
    recordedWordList = []
    recordedColourList = []
    

    gameGuessCount = 0
    i = 0
    listOfGuessCounts = []
    for game in guessData:

        if (UseSPdata == True and gameType[i] == "Singleplayer") or (UseMPdata == True and gameType[i] == "Multiplayer") or (UseSIMdata == True and gameType[i] == "Simulation"):

            gameGuessList = []
            for word in (game.split(":")):
                gameGuessList.append(word)
                
                
            listOfGuessCounts.append(len(gameGuessList))



        i+=1
    
    gameTypeString = ""
    gameTypesIncluded = []
    if UseSPdata == True:
        gameTypesIncluded.append("Singleplayer")
    if UseMPdata == True:
        gameTypesIncluded.append("Multiplayer")
    if UseSIMdata == True:
        gameTypesIncluded.append("Simulation")
    
    for value in gameTypesIncluded:
        gameTypeString = gameTypeString + str(value) + "  "
    
    SPGameCount = 0
    MPGameCount = 0
    SIMGameCount = 0
    for game in gameType:
        if game == "Singleplayer":
            SPGameCount += 1
        if game == "Multiplayer":
            MPGameCount += 1
        if game == "Simulation":
            SIMGameCount += 1
    
    
    p1 = plt.figure()
    ax = p1.add_subplot()
    p1.subplots_adjust(top=0.85)
    ax.axis([0, 10, 0, 10])
    
    averageGuessCount = sum(listOfGuessCounts) / len(listOfGuessCounts)
    listOfGuessCounts.sort()
    mid = len(listOfGuessCounts) // 2
    median = (listOfGuessCounts[mid] + listOfGuessCounts[~mid]) / 2
    
    ax.text(0, 9, ("Basic Statistics for: \n" + gameTypeString), fontsize = 14, fontweight="bold")
    ax.text(0, 2, ('Total number of games recorded: ' + str(len(guessData))
                   + "\n\nNumber of Singleplayer games: " + str(SPGameCount)
                   + "\nNumber of Multiplayer games: " + str(MPGameCount)
                   + "\nNumber of Simulation games: " + str(SIMGameCount)
                   + "\n\nAverage Number of Guesses: " + str(averageGuessCount)
                   + "\n\nMedian Number of Guesses: " + str(median)
                   )
            , fontsize = 14 )


    plt.axis('off')

    fig = plt.gcf()

    fig.set_facecolor('#ffffff')
    return fig
    

def createData(UseSPdata, UseMPdata, UseSIMdata):
    dfGameData = pd.read_csv("recorded_game_data.csv")
    guessData = list(dfGameData[dfGameData.columns[0]])
    gameType = list(dfGameData[dfGameData.columns[2]])
    

    
    
    # Test code to pull in data
    totalLetters = []
    
    i = 0
    
    for strGame in guessData:
        
        
        gameWords = []
        gameWords.append(strGame.split(":"))
        for game in gameWords:
            for word in game:
                for letter in list(word):
                    if (UseSPdata == True and gameType[i] == "Singleplayer") or (UseMPdata == True and gameType[i] == "Multiplayer") or (UseSIMdata == True and gameType[i] == "Simulation"):
                        totalLetters.append(letter)
        i += 1
    
    return(totalLetters)

def generateQValues():
    
    # Pulls all recorded game data from CSV
    dfGameData = pd.read_csv("recorded_game_data.csv")
    guessData = list(dfGameData[dfGameData.columns[0]])
    colourData = list(dfGameData[dfGameData.columns[1]])
    
    recordedWordList = []
    recordedColourList = []
    
    
    # Makes a list of all words and then makes a list of what colours each word got
    for game in guessData:
        for word in (game.split(":")):
            recordedWordList.append(word)
    for game in colourData:
        for colour in (game.split(":")):
            recordedColourList.append(colour)

    
    # Starts generating Q-Values
    qValuesDict = {}
    usedWordList = []
    i = 0
    global qValueProgress
    oldProgressValue = 0

    
    popUpWindow['-PROGRESS_BAR-'].update(current_count= 0, max=100)
    
    for word in recordedWordList:
        if round((i / len(recordedWordList)) * (100/1)) != oldProgressValue and round((i / len(recordedWordList)) * (100/1)) % 2 == 0:
            qValueProgress = round((i / len(recordedWordList)) * (100/1))
            oldProgressValue = qValueProgress
            popUpWindow['-PROGRESS_BAR-'].update(qValueProgress)

            
        
        

        currentWordQValue = 0
        # Make an average of every word that appears
        if word in qValuesDict and word not in usedWordList:
            usedWordList.append(word)
            j = 0
            wordRepeatCount = 0
            colourAverage = 0
            for repeatWord in recordedWordList:

                if repeatWord == word:
                    
                    wordRepeatCount += 1

                    for colour in list(recordedColourList[j]):

                        if colour == "G":
                            colourAverage += 2
                        elif colour == "Y":
                            colourAverage += 1
                j +=1
            
            colourAverage = colourAverage / wordRepeatCount
                  
            qValuesDict[word] = colourAverage

            
        # Sets q-value if word only appears once
        elif word not in qValuesDict:
            for colour in list(recordedColourList[i]):
                if colour == "G":
                    currentWordQValue += 2
                elif colour == "Y":
                    currentWordQValue += 1
                else:
                    currentWordQValue += .01
            qValuesDict[word] = currentWordQValue
        i+=1
    

    try:
        with open("Q_Values.csv", 'w', encoding='UTF8', newline='') as f:
            # create the csv writer
            writer = csv.writer(f)
            
            for value in qValuesDict:
                logLine = [value, qValuesDict[value]]

                writer.writerow(logLine)
    except IOError:
        print("Could not log results! Please close Excel.")
    return qValuesDict


# Initializes word variable as a blank word as no word is inputted yet
word = "     "

error = ""


# Sets up a custom theme
new_theme = {"BACKGROUND": '#121213', "TEXT": "#ffffff", "INPUT": sg.COLOR_SYSTEM_DEFAULT,
             "TEXT_INPUT": sg.COLOR_SYSTEM_DEFAULT, "SCROLL": sg.COLOR_SYSTEM_DEFAULT,
             "BUTTON": sg.OFFICIAL_PYSIMPLEGUI_BUTTON_COLOR, "PROGRESS": sg.COLOR_SYSTEM_DEFAULT, "BORDER": 0.5,
             "SLIDER_DEPTH": 1, "PROGRESS_DEPTH": 0
             }

sg.theme_add_new('MyTheme', new_theme)
sg.theme('MyTheme')

    

wordList = list(word)

# This sets up a function to call the boxes which make up the words
def TextChar(value, key):
    return sg.Input(value, key=key, font='Any 22 bold', size=(2,2),disabled_readonly_background_color='#121213', text_color="white", justification='center', border_width=1,  p=2, enable_events=True, disabled=True)

# --------------------------------------------

# Main Menu

# --------------------------------------------

layout = [
    [sg.Text('Wordle', font='Cyrene 20 bold', justification='center', p=6)],
    [sg.HSeparator(), sg.Text('Gameplay', font='Cyrene 10', justification='center', p=6), sg.HSeparator()],
    [sg.Button("Singleplayer", button_color="#818384", size=(10,1), p=6, font='Any 12 bold')],
    [sg.Button("Multiplayer", button_color="#818384", size=(10,1), p=6, font='Any 12 bold')],
    [sg.HSeparator(), sg.Text('Computer', font='Cyrene 10', justification='center', p=6), sg.HSeparator()],
    [sg.Button("Simulation", button_color="#818384", size=(10,1), p=6, font='Any 12 bold')],
    [sg.Button("Graph Maker", button_color="#818384", size=(10,1), p=6, font='Any 12 bold')]
    ]

window = sg.Window('Wordle', layout, finalize=True, element_justification='c')



while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event=="Exit":
        window.close()
        break

    if event == "Singleplayer" or event == "Multiplayer" or event == "Simulation" or event == "Graph Maker":
        window.close()
        break
    



# --------------------------------------------

# Singleplayer MODE 

# --------------------------------------------

if event == "Singleplayer":
    
    
    # Pulls in word list and picks one
    inputWordList, answerWordList = wordImport()

    # Picks the game's word
    chosenWord = randomWord()

    previousGuesses = []
    previousColours = []
    
    
    # Sets up the layout for the GUI
    layout = [
        [sg.Text('Wordle', font='Cyrene 20 bold', justification='center')],
        [[TextChar(wordList[col].upper(), (row, col)) for col in range(5)]for row in range(6)],
        [sg.Text('Input a word:', font="Any 12")],
        [sg.InputText("", key="inBox", font='Any 15 bold', size=(15,1))],
        [sg.Submit(button_color="#818384", font="Any 10")],
        [sg.Text(error, key="errorMessage")]
    ]



    # Initialises Window
    window = sg.Window('Wordle', layout, finalize=True, element_justification='c')

    window[("inBox")].set_focus()  


    currentRow = 0



    while True:
        event, values = window.read()
        
        
        if event == "Cancel":
            break
        
        
        #closes programme when you click to X out of it
        if event == sg.WIN_CLOSED or event=="Exit" or currentRow == 6:
            break
        
        
        window[("inBox")].set_focus() 
        
        #print(values)
        # Tests to see if input is 5 letters long and updates the display to match inputted word
        if type(values["inBox"]) != "NoneType" and len(values["inBox"]) == 5 :
            
            # Sends inputted word to ensure it is a valid guess
            guess = (str(values["inBox"]).lower())
            error, word = guessValidation(guess)
            
            
            if error == "":
                wordList = list(word)
                window["errorMessage"].update("")
                
                
                
                
                # Puts inputted word into the 5 boxes on the current row
                [[window[(currentRow, col)].update(wordList[col].upper(), disabled=False, background_color="#3a3a3c") for col in range(5)]]
                
                colourList = colours(wordList, inputWordList, chosenWord)
                
                i = 0
                for colour in colourList:
                    [window[(currentRow, i)].update(disabled=False, background_color=colour)]
                    i += 1
                wordList = list(word)
                window["inBox"].update("")
                
                #moves onto the next row
                currentRow += 1
                
                # If all letters are green, display the "You Win" pop-up
                if colourList == ['#538d4f', '#538d4f', '#538d4f', '#538d4f', '#538d4f']:
                    
                    logResults("Singleplayer")
                    
                    
                    window[("inBox")].update(disabled=True)
                    window[("Submit")].update(disabled=True)
                    
                    
                    # Layout of YOU WIN popup
                    PopUplayout = [
                    [sg.Text("You Win!", font='Cyrene 15 bold', p=10)],
                    [sg.Button("Awesome", button_color="#818384", font="Any 10", p=10)],
                    ]
                    sg.Window("WINNER", PopUplayout, modal=True, finalize=True, element_justification='c').read(close=True)
                    

                    
                elif currentRow == 6:
                    logResults("Singleplayer")
                    
                    
                    # Layout of YOU WIN popup
                    
                    PopUplayout = [
                    [sg.Text("Better Luck Next Time!", font='Cyrene 15 bold', p=15)],
                    [sg.Text("The word was:", font='Cyrene 10', p=2)],
                    [sg.Text(chosenWord.upper(), font='Cyrene 10 bold', p=2)],
                    [sg.Button("Oh Okay ):", button_color="#818384", font="Any 10", p=10)],
                    ]
                    sg.Window('Loss', PopUplayout, modal=True, finalize=True, element_justification='c').read(close=True)

                
            else:
                window["errorMessage"].update(error)
                
                
    window.close()


# --------------------------------------------

# Multiplayer MODE 

# --------------------------------------------


if event == "Multiplayer":
    
    # Sets up muliplayer option menu
    
    layout = [
    [sg.Push(), sg.Text('Wordle', font='Cyrene 20 bold', justification='center'), sg.Push()],
    [sg.Text('Please enter the players\' names:', font="Any 12")],
    [sg.Text('Player 1:', font="Any 12"), sg.InputText("", key="player1", font='Any 15 bold', size=(15,1))],
    [sg.Text('Player 2:', font="Any 12"), sg.InputText("", key="player2", font='Any 15 bold', size=(15,1))],
    [sg.Text('', font="Any 12")],
    [sg.Text('Select number of rounds:', font="Any 12")],
    [sg.Text('Best of:', font="Any 12"), sg.Radio(1, "rounds", key='rounds1', default=False, font="Any 12"), sg.Radio(3, "rounds", key='rounds3', default=True, font="Any 12"), sg.Radio(5, "rounds", key='rounds5', default=False, font="Any 12")],
    [sg.Push(), sg.Submit(button_color="#818384", font="Any 10", p=12), sg.Push()]
    ]
    
    window = sg.Window('Wordle', layout, finalize=True)
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        
        elif event == "Submit" and values["player1"] != ""and values["player2"] != "" and values["player2"] != values["player1"]:
            break
    
    window.close()
    
    # Takes in number of rounds

    if values["rounds1"] == True:
        noRounds = 1
    elif values["rounds3"] == True:
        noRounds = 3
    elif values["rounds5"] == True:
        noRounds = 5
        
    
    
    p1 = values["player1"].title()
    p2 = values["player2"].title()
    players = {p1:0, p2:0}
    
    currentRound = 1
    currentPlayer = p1
    
    
    # Pulls in word list
    inputWordList, answerWordList = wordImport()
    
    # -----------------------------
    # Sets up multiplayer game
        
    while currentRound <= (noRounds * 2):
        
        # Sets up different settings for each player/round
        if (currentRound % 2) == 0:
            currentPlayer = p2
        elif (currentRound % 2) != 0:
            currentPlayer = p1
        
        roundTitle = ("Round " + str(math.ceil(currentRound / 2)))
        playerTitle = (currentPlayer + "'s turn")
        
        


        # Picks the game's word
        chosenWord = randomWord()
        previousGuesses = []
        previousColours = []
        
        
        playerOneScore = [
            [sg.Text((p1+":"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(players[p1]), font='Cyrene 15', justification='centre')]
            ]
                
        playerTwoScore = [
            [sg.Text((p2+":"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(players[p2]), font='Cyrene 15', justification='centre')]
            ]
        
        
        # Sets up the layout for the GUI
        layout = [
            [sg.Text(roundTitle, font='Cyrene 20 bold', justification='center')],
            [sg.Text(playerTitle, font='Cyrene 18', justification='center')],
            [sg.Text("", font='Cyrene 10', justification='center')],
            [sg.Column(playerOneScore, element_justification='c', key="p1s"), sg.VSeperator(), sg.Column(playerTwoScore, element_justification='c', key="p2s")],
            
            [[TextChar("", (row, col)) for col in range(5)]for row in range(6)],
            [sg.Text('Input a word:', font="Any 12")],
            [sg.InputText("", key="inBox", font='Any 15 bold', size=(15,1))],
            [sg.Submit(button_color="#818384", font="Any 10")],
            [sg.Text(error, key="errorMessage")]
        ]



        # Initialises Window
        window = sg.Window('Wordle', layout, finalize=True, element_justification='c')

        window[("inBox")].set_focus()  



        currentRow = 0
        
        while True:
            event, values = window.read()
            
            
            if event == "Cancel":
                break
            

            
            #closes programme when you click to X out of it
            if event == sg.WIN_CLOSED or event=="Exit" or currentRow == 6:
                break
            
            
            window[("inBox")].set_focus()
            
            
            # Tests to see if input is 5 letters long and updates the display to match inputted word
            if type(values["inBox"]) != "NoneType" and len(values["inBox"]) == 5 :
                
                # Sends inputted word to ensure it is a valid guess
                guess = (str(values["inBox"]).lower())
                error, word = guessValidation(guess)
                
                
                if error == "":
                    wordList = list(word)
                    window["errorMessage"].update("")
                    
                    
                    
                    
                    # Puts inputted word into the 5 boxes on the current row
                    [[window[(currentRow, col)].update(wordList[col].upper(), disabled=False, background_color="#3a3a3c") for col in range(5)]]
                    
                    colourList = colours(wordList, inputWordList, chosenWord)
                    
                    i = 0
                    for colour in colourList:
                        [window[(currentRow, i)].update(disabled=False, background_color=colour)]
                        i += 1

                    window["inBox"].update("")
                    
                    #moves onto the next row
                    currentRow += 1
                    
                    # If all letters are green, display the "You Win" pop-up
                    done = False
                    if colourList == ['#538d4f', '#538d4f', '#538d4f', '#538d4f', '#538d4f']:
                        logResults("Multiplayer")
                        
                        
                        window[("inBox")].update(disabled=True)
                        window[("Submit")].update(disabled=True)
                        
                        
                        # Layout of YOU WIN popup
                        PopUplayout = [
                        [sg.Text("You Win!", font='Cyrene 15 bold', p=10)],
                        [sg.Button("Awesome", button_color="#818384", font="Any 10", p=10)],
                        ]
                        sg.Window("WINNER", PopUplayout, modal=True, finalize=True, element_justification='c').read(close=True)
                        
                        players[currentPlayer] += currentRow
                        
                        
                        break
                    
                    
                    
                    elif currentRow == 6 and colourList != ['#538d4f', '#538d4f', '#538d4f', '#538d4f', '#538d4f']:
                        logResults("Multiplayer")
                        # Layout of YOU LOSE popup
                        
                        
                        window[("inBox")].update(disabled=True)
                        window[("Submit")].update(disabled=True)
                        
                        PopUplayout = [
                        [sg.Text("Better Luck Next Time!", font='Cyrene 15 bold', p=15)],
                        [sg.Text("The word was:", font='Cyrene 10', p=2)],
                        [sg.Text(chosenWord.upper(), font='Cyrene 10 bold', p=2)],
                        [sg.Button("Oh Okay ):", button_color="#818384", font="Any 10", p=10)],
                        ]
                        sg.Window('Loss', PopUplayout, modal=True, finalize=True, element_justification='c').read(close=True)
                        
                        currentRow = 0
                        
                        players[currentPlayer] += 10
                        
                        done = True
                        break
                        
                    
                else:
                    window["errorMessage"].update(error)

        
        

        # Updates round count and ensures window isn't caught in exit loop
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        if currentRow == 6 and done == True:
            break
        
        currentRound += 1
        
        
        window.close()
        
    #print(currentRound) 
    if currentRound == ((noRounds * 2) + 1):
        # Do winner/score screen
        window.close()
        
        if players[p2] > players[p1]:
            message = (str(p1) + " wins!")
        if players[p1] > players[p2]:
            message = (str(p2) + " wins!")
        if players[p1] == players[p2]:
            message = ("It is a draw!")
        
        
        playerOneScore = [
            [sg.Text((p1+":"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(players[p1]), font='Cyrene 15', justification='centre')]
            ]
                
        playerTwoScore = [
            [sg.Text((p2+":"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(players[p2]), font='Cyrene 15', justification='centre')]
            ]
        
        PopUplayout = [
        [sg.Text("Final Scores:", font='Cyrene 15 bold', p=15)],
        [sg.Column(playerOneScore, element_justification='c', key="p1s"), sg.VSeperator(), sg.Column(playerTwoScore, element_justification='c', key="p2s")],
        [sg.Text(message, font='Cyrene 12 bold', p=15)],
        [sg.Button("Awesome", button_color="#818384", font="Any 10", p=10)],
        ]
        
        sg.Window('Scores', PopUplayout, modal=True, finalize=True, element_justification='c').read(close=True)

    else:
        window.close()


# --------------------------------------------

# Simulation MODE 

# --------------------------------------------
if event == "Simulation":
    
    # Sets up simulation option menu
    
    simOptions = ["Random", "Machine Learning"]
    
    layout = [
    [sg.Push(), sg.Text('Wordle', font='Cyrene 20 bold', justification='center'), sg.Push()],
    [sg.Text('Simulation Type:', font="Any 12"), sg.Combo((simOptions), expand_x=True, button_background_color="#538d4f", button_arrow_color="#ffffff", text_color="#ffffff", key="simType", font='Any 12', readonly=True, background_color="#121213", size=(20,1), enable_events=True)],
    [sg.vbottom(sg.Text('Select number of generations:', font="Any 12")), sg.Slider((1,1000), expand_x=True,key="generation", default_value=10, orientation="horizontal")],
    [sg.vbottom(sg.Text('Select delay between generations:', font="Any 12")), sg.Slider((0,5), key="delay",resolution=.1, expand_x=True,default_value=2, orientation="horizontal")],
    [sg.Text("", font="Any 12")],
    [sg.Text('Advanced Options', font="Any 8 bold"), sg.HSeparator()],
    [sg.Text('Use information from:', font="Any 8"), sg.Checkbox("Green", default=True, font="Any 8", key="infoGreen"), sg.Push(), sg.Checkbox("Yellow", default=True, font="Any 8", key="infoYellow"), sg.Push(), sg.Checkbox("Grey", font="Any 8", default=True, key="infoGrey"), sg.Push()],
    [sg.Text('Machine Learning Settings:', font="Any 8 bold"), sg.HSeparator()],
    [sg.vbottom(sg.Text('Discovery Constant:', font="Any 8")), sg.Slider((0,100), key="discoverConstant",resolution=1, expand_x=True,default_value=50, size=(10,10), orientation="horizontal")],
    [sg.Push(), sg.Submit(button_color="#818384", font="Any 10", p=12), sg.Push()]
    ]
    
    window = sg.Window('Wordle', layout, finalize=True)
    
    element = window['simType']
    
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event=="Exit":
            break
        elif event == 'simType':
            element.widget.select_clear()
        
        elif event == "Submit" and values["simType"] != "":
            pauseTime = float(values["delay"])
            discoverConstant = int(values["discoverConstant"])
            noGenerations = int(values["generation"])
            simType = values["simType"]
            infoGreen = values["infoGreen"]
            infoYellow = values["infoYellow"]
            infoGrey = values["infoGrey"]
            break
    
    window.close()



    currentGen = 1
    simLoss = 0
    simWin = 0

    guessCount = []
    # Pulls in word list
    inputWordList, answerWordList = wordImport()
    

    # THIS IS WHERE WE GENERATE THE Q VALUES
    if values["simType"] == "Machine Learning":
        
        
        
        layout = [[sg.Text("Generating Q-Values. Please wait...", font="Any 12 bold", p=10)],
                  [sg.ProgressBar(0, orientation='h', size=(50, 10), border_width=4, key='-PROGRESS_BAR-',bar_color=("#538d4f", "#3a3a3c"), p=10)]]
                
        popUpWindow = sg.Window('Generating', layout, modal=True, finalize=True, element_justification='c')
        
        while True:
            window.refresh()
            qValuesDict = generateQValues()

            popUpWindow.close()
            break
        
    while currentGen <= noGenerations:
        
        
        genTitle = ("Generation " + str(currentGen))
        
        
        
        
        
        ## Picks the game's word
        chosenWord = randomWord()
        previousGuesses = []
        previousColours = []
        
        
        wins = [
            [sg.Text(("Wins:"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(simWin), font='Cyrene 15', justification='centre')]
            ]
                
        losses = [
            [sg.Text(("Losses:"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(simLoss), font='Cyrene 15', justification='centre')]
            ]
        
        
        # Sets up the layout for the GUI
        layout = [
            [sg.Text(genTitle, font='Cyrene 20 bold', justification='center')],
            [sg.Text("", font='Cyrene 10', justification='center')],
            [sg.Column(wins, element_justification='c', key="wins"), sg.VSeperator(), sg.Column(losses, element_justification='c', key="losses")],
            
            [[TextChar("", (row, col)) for col in range(5)]for row in range(6)],

        ]



        # Initialises Window
        window = sg.Window('Wordle', layout, finalize=True, element_justification='c')
        

        currentRow = 0
        
        newWordList = answerWordList
        
        
        while True:

                
            window.refresh()
            time.sleep(pauseTime * .01)

            
            #closes programme when you click to X out of it
            if event == sg.WIN_CLOSED or event=="Exit" or currentRow == 6:
                break
            
            
            # Sends inputted word to ensure it is a valid guess

            if len(newWordList) > 0 and values["simType"] == "Random":
                guess = newWordList[random.randint(0, (len(newWordList)-1))]

                
                
            # This makes it choose random words based on the weights of the Q-Values
            # -------------

            if len(newWordList) > 0 and values["simType"] == "Machine Learning":
 
                newQValueList = []
                for word in newWordList:
                    if word in qValuesDict:
                        newQValueList.append(qValuesDict[word])
                    else:
                        newQValueList.append(0.01)


                
                discoveryRandom = random.randint(0, 10)

                if discoveryRandom <= (discoverConstant / 10):

                    guess = random.choices(newWordList, weights=newQValueList)
                    guess = guess[0]
                
                else:

                    orderedQValues = sorted(newQValueList, reverse=True)
                    highestQValue = orderedQValues[0]
                    i=0
                    for value in newQValueList:
                        if value == highestQValue:
                            guess = newWordList[i]
                            break
                        i+=1

                
            if len(newWordList) == 1:
                guess = newWordList[0]


            error, word = guessValidation(guess)
            
            wordList = list(word)
            
            
            
            
            
            # Puts inputted word into the 5 boxes on the current row
            [[window[(currentRow, col)].update(wordList[col].upper(), disabled=False, background_color="#3a3a3c") for col in range(5)]]
            
            colourList = colours(wordList, inputWordList, chosenWord)
            
            i = 0
            for colour in colourList:
                [window[(currentRow, i)].update(disabled=False, background_color=colour)]
                i += 1

            
            # Updates the words to pick out of, eliminating words it cannot be
            if len(newWordList) >= 1:
                newWordList = eliminateWords(guess, newWordList, colourList) 
            #moves onto the next row
            currentRow += 1

            
            # If all letters are green, display the "You Win" pop-up
            done = False
            
            if colourList == ['#538d4f', '#538d4f', '#538d4f', '#538d4f', '#538d4f']:
                logResults("Simulation")
                simWin += 1
                guessCount.append(int(len(previousGuesses)))
                window.refresh()
                time.sleep(pauseTime)
                break
            
            
            
            elif currentRow == 6 and colourList != ['#538d4f', '#538d4f', '#538d4f', '#538d4f', '#538d4f']:
                logResults("Simulation")
                simLoss += 1
                window.refresh()
                time.sleep(pauseTime)
                currentRow = 0
                
                
                done = True
                break
                    
                
               
            

            if event == sg.WIN_CLOSED or event=="Exit":
                break
            if currentRow == 6 and done == True:
                break
        
        currentGen += 1
      
        window.close()
        
    if currentGen == noGenerations+1:
        # Do wins/losses, guesscount distribution screen
        

        playerOneScore = [
            [sg.Text(("Wins:"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(simWin), font='Cyrene 15', justification='centre')]
            ]
                
        playerTwoScore = [
            [sg.Text(("Losses:"), font='Cyrene 15', justification='centre')],
            [sg.Text(str(simLoss), font='Cyrene 15', justification='centre')]
            ]
        
        dt_string = now.strftime("%d-%m-%Y-%H%M")
        defaultfilename = str("Sim_Gen"+str(noGenerations)+"_"+dt_string)
        PopUplayout = [
        [sg.Text("Final Scores:", font='Cyrene 15 bold', p=15)],
        [sg.Column(playerOneScore, element_justification='c', key="p1s"), sg.VSeperator(), sg.Column(playerTwoScore, element_justification='c', key="p2s")],
        [sg.HSeparator()],
        [sg.Text("Guess Count Distribution:", font='Cyrene 15 bold', p=15)],
        [sg.Canvas(key='guessDist', size=(1,1))],
        [sg.Text("Save PDF as: ", key="saveText",font='Cyrene 15', p=0), sg.Input(defaultfilename, font='Cyrene 15',p=0, key="filename"), sg.Button("Save", button_color="#538d4f", font="Any 10", p=10)],
        [sg.Button("Awesome", button_color="#818384", font="Any 10", p=10)]
        ]
        window = sg.Window('Scores', PopUplayout, modal=True, finalize=True, element_justification='c')
        
        simFig = drawHist(guessCount, noGenerations, simWin)
        figure_canvas_agg = draw_figure(window['guessDist'].TKCanvas, simFig)
        window.refresh()
        window.move_to_center()
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event=="Exit" or event=="Awesome":
                break
            if event == "Save":
                fileName = values["filename"]
                savedText = "File saved as: " + str(fileName) + ".pdf"
                window["filename"].update("Saving...", disabled = True)
                window.refresh()
                
                
                simFig.savefig(fileName + ".pdf", bbox_inches='tight')
                window["saveText"].update(savedText, visible = True)
                window["filename"].update("File Saved", visible = False, disabled = True)
                window["Save"].update(disabled = True)

        window.close()

    else:
        window.close()


# --------------------------------------------

# Graph Maker MODE 

# --------------------------------------------



if event == "Graph Maker":
    

    while True:    
        
        # List of choosable options
        graphOptions = ["Letter Frequency", "Q Values", "Basic Statistics"]
        
        
        # Defines different settings layouts
       
        
        currentSetting = 0
        

        # Sets default file name
        dt_string = now.strftime("%d-%m-%Y-%H%M")
        defaultfilename = str(dt_string)
        
        # Defines layout for the "graph maker" menu. Has an array of option which will pass to a function that arranges data and generates graphs
        RightColLayout = [
        [sg.Canvas(key='graphGUI', size=(1,1))],
        [sg.Text("Save PDF as: ", key="saveText",font='Cyrene 15', p=0, visible=False), sg.Input(defaultfilename, visible = False, font='Cyrene 15',p=0, key="filename"), sg.Button("Save", visible=False, key="saveGraph", button_color="#538d4f", font="Any 10", p=10)],
                          ]
        

        
        LeftColLayout = [
        [sg.Text("Graph Maker", font='Cyrene 15 bold', p=15)],
        [sg.Text('Graph Type:', font="Any 8"), sg.Combo((graphOptions), expand_x=True,  button_background_color="#538d4f", button_arrow_color="#ffffff", text_color="#ffffff", key="-graphType-", font='Any 8', readonly=True, background_color="#121213", size=(20,1), enable_events=True)],
        [sg.Text('Collect Data From:', font="Any 8 bold"), sg.HSeparator()],
        [sg.Text('Game Type:', font="Any 8"), sg.Checkbox("SinglePlayer", default=True, font="Any 8", key="SPdata"), sg.Push(), sg.Checkbox("Multiplayer", default=True, font="Any 8", key="MPdata"), sg.Push(), sg.Checkbox("Simulation", font="Any 8", default=True, key="SIMdata"), sg.Push()],


        

        # Draws Graph
        [sg.Button("Draw Graph", button_color="#538d4f", font="Any 10", p=5)],
        [sg.Button("New Graph", button_color="#538d4f", font="Any 10", p=5)],
        [sg.Button("Exit", button_color="#818384", font="Any 10", p=10)]
        ]
        layout = [[sg.Column(LeftColLayout, element_justification='c'), sg.Column(RightColLayout)]]
        window = sg.Window('Wordle', layout, modal=True, finalize=True, element_justification='c')
        
        
        changeLayout = 0
        graphSettingsLayouts = {
            0:[
            [sg.Text("Letter Frequency Options", font='Cyrene 15 bold', p=15)],
            [sg.Text("Sort by:", font= "Any 8", p=15), sg.Radio("Alphabetical Order", "sortingType", key='freqSetAlpha', default=True, font="Any 8"), sg.Radio("Most Frequent", "sortingType", key='freqSetFreq', default=False, font="Any 8")],
            [sg.Submit(button_color="#538d4f", font="Any 10", p=10)]
            ],
            1:[
            [sg.Text("Q Value Graphing Options", font='Cyrene 15 bold', p=15)],
            [sg.vbottom(sg.Text("Amount of values to display:", font= "Any 8", p=15)), sg.Slider((10,30), size=(30,15), expand_x=True,key="topQValues", default_value=10, orientation="horizontal")],
            [sg.Submit(button_color="#538d4f", font="Any 10", p=10)]
            ]
            }
        
        window.refresh()
        window.move_to_center()
        figure_canvas_agg = None
        
        # Window loop
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event=="Exit":
                break
            if event == event=="New Graph":
                break
            
            
            # Pop up windows for specific graph settings

            if event == "-graphType-":
                graphChoice = graphOptions.index(values["-graphType-"])
                
                if values["-graphType-"] != "Basic Statistics":
                    PopUplayout = graphSettingsLayouts[graphChoice]
                
                    popUpWindow = sg.Window('Graph Options', PopUplayout, modal=True, finalize=True, element_justification='c')
                
                    while True:
                        event, values = popUpWindow.read()
                        
                        if graphChoice == 0:
                            if values["freqSetAlpha"] == True:
                                sortingType = "Alpha"
                            else:
                                sortingType = "Freq"
                        
                        if graphChoice == 1:
                            topQValuesDisplay = (values["topQValues"])

                        
                        
                        if event == sg.WIN_CLOSED or event=="Submit":
                            break
                        
                    popUpWindow.close()
                window["-graphType-"].update(disabled = True)

                
            
            

                
            # Draws the graph
            if event == "Draw Graph" and values["-graphType-"] != "":

                
                # Calls function to create data required
                UseSPdata = values["SPdata"]
                UseMPdata = values["MPdata"]
                UseSIMdata = values["SIMdata"]
                
                
                totalLetters = createData(UseSPdata, UseMPdata, UseSIMdata)
                
                # Clears canvas
                if figure_canvas_agg:
                    plt.close('all')
                    figure_canvas_agg.get_tk_widget().forget()
                    
                    
                # Calls function to create graph using data generated
                if values["-graphType-"] == "Letter Frequency":
                    
                    simFig = drawLetterHist(totalLetters, sortingType)
                
                if values["-graphType-"] == "Q Values":
                    
                    simFig = drawQValueGraph(topQValuesDisplay)
                    
                if values["-graphType-"] == "Basic Statistics":
                    
                    simFig = drawBasicStatsGraph(UseSPdata, UseMPdata, UseSIMdata)
                    
                # Displays Graph
                figure_canvas_agg = draw_figure(window['graphGUI'].TKCanvas, simFig)
                
                # Makes the saving options visible
                dt_string = now.strftime("%d-%m-%Y-%H%M")
                defaultfilename = str(values["-graphType-"]) + "_" + str(dt_string)
                
                window["filename"].update(defaultfilename)
                window["saveText"].update(visible = True)
                window["filename"].update(visible = True)
                window["saveGraph"].update(visible = True)
                
                
                
                # Updates window and recentres it
                
                window.refresh()
                window.move_to_center()
        
            
            # Save Graph as pdf
            if event == "saveGraph":
                fileName = values["filename"]
                savedText = "File saved as: " + str(fileName) + ".pdf"
                window["filename"].update("Saving...", disabled = True)
                window.refresh()
                
                
                simFig.savefig(fileName + ".pdf", bbox_inches='tight')
                window["saveText"].update(savedText, visible = True)
                window["filename"].update("File Saved",visible = False, disabled = True)
                window["saveGraph"].update(disabled = True, visible=False)

        
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        window.close()
    window.close()    