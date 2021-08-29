import random
#import numpy as np
from string import ascii_lowercase
import math


HANGMAN_PICS = ['''
   +---+
       |
       |
       |
      ===''', '''
   +---+
   O   |
       |
       |
      ===''', '''
   +---+
   O   |
   |   |
       |
      ===''', '''
   +---+
   O   |
  /|   |
       |
      ===''', '''
   +---+
   O   |
  /|\  |
       |
      ===''', '''
   +---+
   O   |
  /|\  |
  /    |
      ===''', '''
   +---+
   O   |
  /|\  |
  / \  |
      ===''']


class environment:
    word = ""
    turns = 6
    guess = ''
    guesses = ''

    def __init__(self, word, turns=6):
        # make agent in here ???
        self.word = word.lower()
        self.turns = turns
        self.board = ['_'] * len(self.word)

    def reset_board(self):
        self.board = ['_'] * len(self.word)
        return self.board

    def checkBoard(self):
        failed = 0
        wordAsString = ''
        for index, char in enumerate(self.word):
            if char in self.guesses:
                wordAsString += ' ' + char + ' '
                self.board[index] = char
            else:
                wordAsString += ' _ '
                failed += 1

        return self.board

    def takeGuess(self, g):
        self.guess = g
        reward = 0
        self.guesses += self.guess
        self.checkBoard()
        if self.guess not in self.word:
            self.turns -= 1
            reward = -1
        else:
            reward = 1
        newboard = []
        for l in self.board:
            newboard.append(l)
        return newboard, self.turns, reward

    def getGuess(self):
        # have thinking go on in here
        correct = False
        c = self.guess
        if self.takeGuess(c)[2] == 1:
            correct = True
        return c, correct


class qAgent:
    # Agent makes best guess based on previously encountered words

    # Possible character guesses
    charArray = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    # Starting word bank
    # Loadable
    knownWords = ['ant', 'baboon', 'badger', 'bat', 'bear', 'beaver', 'camel', 'cat', 'clam', 'cobra', 'cougar',
                  'coyote', 'crow', 'deer', 'dog', 'donkey', 'duck', 'eagle', 'ferret', 'fox', 'frog', 'goat',
                  'goose', 'hawk', 'lion', 'lizard', 'llama', 'mole', 'monkey', 'moose', 'mouse', 'mule', 'newt',
                  'otter', 'owl', 'panda', 'parrot', 'pigeon', 'python', 'rabbit', 'ram', 'rat', 'raven', 'rhino',
                  'salmon', 'seal', 'shark', 'sheep', 'skunk', 'sloth', 'snake', 'spider', 'stork', 'swan', 'tiger',
                  'toad', 'trout', 'turkey', 'turtle', 'weasel', 'whale', 'wolf', 'wombat', 'zebra']

    # cut down version of word bank (used to find best word)
    possibleWords = []

    # Counts amounts of words with a certain letter
    wordsWithLetter = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "f": 0, "g": 0, "h": 0, "i": 0, "j": 0,
                       "k": 0, "l": 0, "m": 0, "n": 0, "o": 0, "p": 0, "q": 0, "r": 0, "s": 0, "t": 0,
                       "u": 0, "v": 0, "w": 0, "x": 0, "y": 0, "z": 0, "!": -math.inf}

    # Loadable
    qTable = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "f": 0, "g": 0, "h": 0, "i": 0, "j": 0,
              "k": 0, "l": 0, "m": 0, "n": 0, "o": 0, "p": 0, "q": 0, "r": 0, "s": 0, "t": 0,
              "u": 0, "v": 0, "w": 0, "x": 0, "y": 0, "z": 0, "!": -math.inf}

    gamestates = []

    def __init__(self, game, autoRefresh=False):
        self.gameEnvironment = game  # the game
        self.wordLength = len(self.gameEnvironment.word)  # the amount of starting spaces in the game
        self.autoRefresh = autoRefresh
        self.loadWordBank()
        self.loadQTable()
        self.charArray = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                          'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    def loadWordBank(self):
        file = open("wordbank.txt", "r")
        self.knownWords = file.read().splitlines()
        file.close()

    def saveWordBank(self):
        file = open("wordbank.txt", "w")
        lines = []
        for i in self.knownWords:
            lines.append(i+'\n')
        file.writelines(lines)
        file.close()

    def loadQTable(self):
        file = open("qtable.txt", "r")
        lines = file.read().splitlines()
        count = 0
        for i in self.qTable:
            if lines[count] != "-inf":
                self.qTable[i] = float(lines[count])
            else:
                self.qTable[i] = -math.inf
            count += 1
        file.close()

    def saveQTable(self):
        file = open("qtable.txt", "w")
        lines = []
        for i in self.qTable:
            lines.append(str(self.qTable[i]) + '\n')
        file.writelines(lines)
        file.close()

    def wordsOfLength(self):
        # Sets the list of possible words to words with the target length
        s = []
        for i in self.knownWords:
            if len(i) == self.wordLength:
                s.append(i)
        self.possibleWords = s
        return s

    def bestGuess(self):
        # Calculates the most frequent letter
        for i in self.possibleWords:
            for j in self.wordsWithLetter:
                if i.find(j) != -1 and j in self.charArray:
                    self.wordsWithLetter[j] += 1
        guess = "!"  # placeholder to be overwritten
        # Set the guess with the highest count
        for k in self.wordsWithLetter:
            if k in self.charArray:
                if self.wordsWithLetter[k] > self.wordsWithLetter[guess]:
                    guess = k
        # remove the guess from charArray so it cannot be guessed again
        #print(guess, self.charArray)
        self.charArray.remove(guess)

        # Reset the dictionary for future calculations
        self.wordsWithLetter = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "f": 0, "g": 0, "h": 0, "i": 0, "j": 0,
                                "k": 0, "l": 0, "m": 0, "n": 0, "o": 0, "p": 0, "q": 0, "r": 0, "s": 0, "t": 0,
                                "u": 0, "v": 0, "w": 0, "x": 0, "y": 0, "z": 0, "!": -math.inf}
        return guess

    def refineList(self, guessValue, attemptedGuess):
        # Cut down the list depending on if the guess was right or wrong
        s = []
        for i in self.possibleWords:
            # If guess was right, only keep the words with that guess
            if guessValue == 1:
                if i.find(attemptedGuess) != -1:
                    s.append(i)
            # If guess was not right, only keep the words without that guess
            if guessValue == -1:
                if i.find(attemptedGuess) == -1:
                    s.append(i)
        self.possibleWords = s
        self.refineQTable(guessValue, attemptedGuess)

    def refineQTable(self, guessValue, attemptedGuess):
        if guessValue == 1:
            self.qTable[attemptedGuess] += 1
            # print(self.qTable)
        if guessValue == -1:
            self.qTable[attemptedGuess] -= .5
            # print(self.qTable)

    def playGame(self):
        self.possibleWords = self.wordsOfLength()
        while self.gameEnvironment.turns > 0 and '_' in self.gameEnvironment.checkBoard():
            if len(self.charArray) > 0 and len(self.possibleWords) > 0:
                print(self.possibleWords)
                print(self.charArray)
                s = self.bestGuess()
                # print(s)
                v = self.gameEnvironment.takeGuess(s)
                self.refineList(v[2], s)
                self.gamestates.append((s, v[0]))
                print((s, v[0]))
            elif len(self.possibleWords) == 0:
                print(self.possibleWords)
                print(self.charArray)
                guess = "!"
                validGuess = []
                for k in self.charArray:
                    if self.qTable[k] == self.qTable[guess]:
                        validGuess.append(k)
                    if self.qTable[k] > self.qTable[guess]:
                        guess = k
                        validGuess = [k]
                guess = random.choice(validGuess)
                v = self.gameEnvironment.takeGuess(guess)
                self.charArray.remove(guess)
                self.refineQTable(v[2], guess)
                self.gamestates.append((guess, v[0]))

                print((guess, v[0]))
            else:
                break

        if self.gameEnvironment.word not in self.knownWords:
            self.knownWords.append(self.gameEnvironment.word)
        self.saveWordBank()
        self.saveQTable()


    def resetGame(self, newWord=None):
        # Reset the game for another round
        if newWord is None:
            self.gameEnvironment = environment(word=input("Enter new word ").lower())
        else:
            self.gameEnvironment = environment(word=newWord)

        self.wordLength = len(self.gameEnvironment.word)

        self.charArray = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                          'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

        self.possibleWords = self.wordsOfLength()

        self.wordsWithLetter = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0, "f": 0, "g": 0, "h": 0, "i": 0, "j": 0,
                                "k": 0, "l": 0, "m": 0, "n": 0, "o": 0, "p": 0, "q": 0, "r": 0, "s": 0, "t": 0,
                                "u": 0, "v": 0, "w": 0, "x": 0, "y": 0, "z": 0, "!": -math.inf}
        self.playGame()


foo = environment(word="nick")
bar = qAgent(foo)
bar.playGame()
print('new word')
foo = environment(word="kyle")
bar = qAgent(foo)
bar.playGame()
print('new word')
foo = environment(word="nick")
bar = qAgent(foo)
bar.playGame()



