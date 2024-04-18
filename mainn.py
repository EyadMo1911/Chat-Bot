import os
import nltk
import numpy as np
import tensorflow as tf
import random
import json
import pickle


from nltk.stem.lancaster import LancasterStemmer
from time import sleep

# Ensure you have downloaded the necessary NLTK data
nltk.download('punkt')

# Initialize the stemmer
stemmer = LancasterStemmer()

# Load intents file
with open("train.json") as file:
    data = json.load(file)

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = [] 
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))
    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]
        for w in words:
            bag.append(1 if w in wrds else 0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

# Create a model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(8, input_shape=(len(training[0]),), activation='relu'),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(len(output[0]), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Load or train the model
model_file = ".weights.h5"
if os.path.isfile(model_file):
    model.load_weights(model_file)
else:
    model.fit(training, output, epochs=1000, batch_size=8)
    model.save_weights(model_file)
######################################################
from nltk.tokenize import word_tokenize
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s,)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)

 
################################################################



def chat(x):
        inp=x
        results = model.predict(np.array([bag_of_words(inp, words)]))[0]
        results_index = np.argmax(results)
        tag = labels[results_index]
        if results[results_index] > 0.7:  # Threshold can be adjusted
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
            return(random.choice(responses))
        else:
            return("I don't understand!")


