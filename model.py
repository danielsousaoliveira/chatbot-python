# 
# File: model.py
# Author: Daniel Oliveira
#

### Neural Network Build ###

## Import dependencies ##

from tensorflow import keras
import numpy as np

## Build Deep Neural Network to train our chatbot ##

def NeuralNetwork(input, output):
    
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(128,input_shape=(len(input[0]),),activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dropout(0.5))
    model.add(keras.layers.Dense(len(output[0]),activation='softmax'))
    sgd = keras.optimizers.SGD(learning_rate=0.01, decay=1e-6, momentum = 0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer = sgd, metrics = ['accuracy'])

    history = model.fit(np.array(input), np.array(output), epochs=200, batch_size=5, verbose=1)
    model.save('chatmodel.h5', history)

    return model

## Save model to external file ##