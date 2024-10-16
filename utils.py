# 
# File: utils.py
# Author: Daniel Oliveira
#

### All the utility functions used on the other files ###

## Import dependencies ##

import nltk, random, time
import numpy as np
from db import *
from nltk.stem import *
from nltk.corpus import wordnet as wn

# Import WordNet Lemmatizer #

lem = WordNetLemmatizer()

# Use Natural Language Toolkit to divide Intents file into Lemmatized words, its classes and tokens #

def prepareintents(intents):

    words = []; classes = []; tokens = []

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            wordlist = nltk.word_tokenize(pattern)
            words.extend(wordlist)
            tokens.append((wordlist, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words, classes = stemintents(words,classes)

    return words, classes, tokens

# Lemmatize Words to make it easier (i.e. universities == university) #

def stemintents(words,classes):

    charign = ['!','?','.',',']
    words = [lem.lemmatize(word) for word in words if word not in charign]
    words = sorted(set(words))
    classes = sorted(set(classes))

    return words, classes

# Transform words into value data, preparing it for the NN #

def preparenn(words,classes,tokens):

    training = []
    output = [0]*len(classes)

    for token in tokens:
        queue = []
        pattern = token[0]
        pattern = [lem.lemmatize(word.lower()) for word in pattern]
        for word in words:
            queue.append(1 if word in pattern else 0)
        outputs = list(output)
        outputs[classes.index(token[1])] = 1
        training.append([queue, outputs])

    random.shuffle(training)
    training = np.array(training, dtype=object)
    xtrain = list(training[:,0])
    ytrain = list(training[:,1])

    return xtrain, ytrain

# Predict the class of one given question, using trained data #

def predictclass(inputmsg, model, words, classes):

    wn.ensure_loaded()
    returnlist = []

    sentence, flag = preparesentence(inputmsg, words)
    result = model.predict(np.array([sentence]))[0]
    results = [[i,r] for i,r in enumerate(result) if r > 0.2]
    results.sort(key=lambda x: x[1], reverse=True)
 
    for r in results:
        returnlist.append({'intent': classes[r[0]], 'probability': str(r[1])})
        if float(r[1]) < 0.28:
            flag = True

    return returnlist, flag

# Prepare the question for prediction function #

def preparesentence(inputmsg, words):

    sentence = nltk.word_tokenize(inputmsg)
    sentence = [lem.lemmatize(word) for word in sentence]
    flag = True
    output = [0]*len(words)

    for t in sentence:
            if wn.synsets(t):
                flag = False

    for w in sentence:
        for i, word in enumerate(words):
            if word == w:
                output[i] = 1

    return np.array(output), flag

# Using predicted class, choose one random answer from the pre-defined ones, and then make needed changes #

def findanswer(prediction, intents, inputmsg, inputarray, flag, id, name):

    tag = prediction[0]['intent']
    intentlist = intents['intents']
    result = ""
    flag2 = True

    # Check if there is a second input related to a user order #

    if inputarray[-1] == "Buy" or inputarray[-1] == "Sell" or inputarray[-1] == "Password" or inputarray[-1] == "Email":
        flag2 = False

    for i in intentlist:

        if i['tag'] == tag:

            result = random.choice(i['answers'])

            # No answer found for the question #

            if flag and flag2: 
                result = "Not sure if i understood that can you put it in another words?"

            # User requests current time #

            elif i['tag'] == "Time" and flag2:
                result = result.replace("%%TIME%%", time.strftime("%c"))

            # User requests buy order #    

            elif i['tag'] == "Buy" and flag2:
                try:
                    value = int(''.join(filter(str.isdigit, inputmsg)))
                except ValueError:
                    result = "How many BTC do you want to buy?"
                else:
                    updateBalance(id, value, True)
                    result = "Done! Please reload page to see your balance"

            # User requests sell order #

            elif i['tag'] == "Sell" and flag2:
                try:
                    value = int(''.join(filter(str.isdigit, inputmsg)))
                except ValueError:
                    result = "How many BTC do you want to sell?"
                else:
                    updateBalance(id, value, False)
                    result = "Done! Please reload page to see your balance"

            # Initial greetings using real user name #

            elif i['tag'] == "Greeting" and flag2:
                result = result.replace("%%Name%%", name.split()[0])

            # User requests his name #   

            elif i['tag'] == "Name" and flag2:
                result = result.replace("%%Name%%", name)

            # Handling second inputs from user orders #

            else:
                if inputarray[-1] == "Buy":
                    try:
                        value = int(''.join(filter(str.isdigit, inputmsg)))
                    except ValueError:
                        result = "Please try again using a correct value"
                    else:
                        updateBalance(id, value, True)
                        result = "Done! Please reload page to see your balance"

                elif inputarray[-1] == "Sell":
                    try:
                        value = int(''.join(filter(str.isdigit, inputmsg)))
                    except ValueError:
                        result = "Please try again using a correct value"
                    else:
                        updateBalance(id, value, False)
                        result = "Done! Please reload page to see your balance"

                elif inputarray[-1] == "Password":
                    print(inputmsg)
                    updatePassword(id,inputmsg)
                    result = "Done! Your password is updated"
                elif inputarray[-1] == "Email":
                    updateEmail(id,inputmsg)
                    result = "Done! Your email is updated"  

    return result

