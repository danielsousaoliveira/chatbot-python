# Chatbot in Python

Conversational agent using Python, Flask and Javascript

## Architecture

The application consists of three layers: a Flask web backend, an NLP/ML chatbot engine, and a MySQL database.

```
Browser (JavaScript chatbox)
    ↓  POST /crexusers/predict  { message }
Flask app  (app.py)
    ↓  communicate(text, id, name)
Chatbot engine  (chatbot.py → utils.py)
    ↓  SQL queries
MySQL database  (db.py)
```

### ML Pipeline

The chatbot uses an **intent classification** approach:

**Training** (run once with `python train.py`):
1. Load intent patterns from `intents.json`
2. Tokenise and lemmatise patterns with NLTK
3. Encode as binary bag-of-words vectors
4. Train a 3-layer dense neural network (128 → 64 → *n_intents*, softmax)
5. Save artefacts: `chatmodel.h5`, `words.plk`, `classes.plk`

**Inference** (every user message):
1. Load saved model and vocabulary
2. Convert user input to bag-of-words vector
3. Run forward pass; filter predictions below 0.2 confidence
4. Look up matching intent in `intents.json`; pick a random answer
5. Apply template substitutions (`%%Name%%`, `%%TIME%%`) and handle special intents (Buy/Sell update the user's BTC balance in MySQL)

### Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-MySQLdb |
| NLP | NLTK (tokenisation, lemmatisation) |
| ML | TensorFlow / Keras (Sequential NN) |
| Database | MySQL |
| Frontend | Vanilla JS, HTML/CSS |

### Database Schema

```sql
accounts (id, username, name, password, email, balance)
```

Passwords are hashed with bcrypt. `balance` holds the user's simulated BTC units.

## Setup

1. Clone this repository and create a virtual environment

```bash
$ git clone
$ cd chatbot-python
$ python3 -m venv venv
$ . venv/bin/activate
```

2. Install dependencies and packages

```bash
$ (venv) pip install -r requirements.txt
$ (venv) python3

> > > import nltk
> > > nltk.download('punkt')
> > > nltk.download('punkt_tab')
> > > nltk.download('wordnet')

```

## Run

1. Train the chatbot

```bash
$ (venv) python3 train.py
```

2. Run the app

```bash
$ (venv) python3 app.py
```

3. Go to website

http://localhost:5000/crexusers/

4. Login using one of the users

Username: daniel
Password: pass1

5. Test the chatbot

## Example

![Example](static/images/img1.png)

## Roadmap

[x] ~~Create simple intents file to categorize sentences~~ \
[x] ~~Build Neural Network to train the chatbot~~ \
[x] ~~Use Lemmatization and convert data in numerical values~~ \
[x] ~~Ability to check for client info~~ \
[x] ~~Answer and complete orders from users~~ \
[ ] Add other AI features
