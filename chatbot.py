# 
# File: chatbot.py
# Author: Daniel Oliveira
#

### Conversation Agent Backend Functions ###

## Import dependencies ##

import pickle, json
from utils import *
from tensorflow import keras

# Create array to save user question tags #

inputarray = ["first"]

## Import Natural Language Toolkit including WordNet, and NN Model ##

def importModel():

    with open('intents.json', 'r') as jsondata:
        intents = json.load(jsondata)
    words = pickle.load(open('words.plk','rb'))
    classes = pickle.load(open('classes.plk','rb'))
    model = keras.models.load_model('chatmodel.h5')

    return intents, words, classes, model                     

## Function to communicate with the chatbot ##
# inputmsg - Question from user
# id - User ID
# name - User Name

def communicate(inputmsg, id, name):

    intents, words, classes, model = importModel()
    prediction, flag = predictclass(inputmsg, model, words, classes)
    result = findanswer(prediction, intents, inputmsg, inputarray, flag, id, name)
    inputarray.append(prediction[0]['intent'])

    return result
    
# Returns chatbot's answer for any user question #
