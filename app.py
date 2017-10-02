from flask import Flask, jsonify, request, g, send_file
from flask_pymongo import PyMongo
from RL_brain import QLearningTable
from RL_word_brain import QLearningTable_Word
from Quiz import Quiz
import random
import json
import numpy as np
import gensim
import pandas as pd
from gensim.models.keyedvectors import KeyedVectors

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'quiz'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/quiz'

mongo = PyMongo(app)
model = word_vectors = KeyedVectors.load_word2vec_format('./model/GoogleNews-vectors-negative300.bin', binary=True, limit=50000)
env = Quiz()
RL = QLearningTable(actions=list(range(env.n_actions)))
RL_word = QLearningTable_Word(actions=list(range(2)))
level = {0:'A1',1:'A2',2:'B1',3:'B2',4:'C1',5:'C2'}
word_level = {0:'active',1:'i_active'}
word_action = {0:'r',1:'t'}
@app.route('/')
def index():
    return send_file("templates/index.html")

@app.route('/level', methods=['POST'])
def vocab_level():
    vocab = mongo.db.vocab
    message = request.data.lower()
    results = vocab.find_one({"word": message})
    if results != None:
        output = results.get("level")
    else:
        output = "Not in CEFR Dictionary"
    return output

@app.route('/return_word_table', methods=['POST'])
def return_word_table():
    qtable = pd.DataFrame(
    np.zeros((2, len(word_action))),     # q_table initial values
        columns=word_action,    # actions's name
    )
    user = mongo.db.user
    word_q = request.data.lower()
    results = user.find_one({"name": "Ahmed Zaidi"})
    results = results.get("vocab")
    if results.get(word_q) != None:
        results = results.get(word_q)
        results = results.get("q_"+"table")
        for l in word_level:
            for a in word_action:
                output = results.get(word_level.get(l)+"_"+word_action.get(a))
                qtable.ix[l,a] = output
    else:
        for l in word_level:
            for a in word_action:
                qtable.ix[l,a] = "n/a"

    qtable = qtable.to_dict('records')
    return jsonify(qtable)

@app.route('/word_stats', methods=['POST'])
def word_stats():
    output = {}
    user = mongo.db.user
    word = request.data.lower()
    results = user.find_one({"name": "Ahmed Zaidi"})
    results = results.get("vocab")
    if results.get(word) != None:
        results = results.get(word)
        correct = results.get("correct")
        incorrect = results.get("incorrect")
        attempts = results.get("attempts")
        output = {"Correct":correct,"Incorrect":incorrect,"Attempts":attempts}
    else:
        output = {0:"N/A",1:"N/A",2:"N/A"}
    return jsonify(output)

@app.route('/r_quiz', methods=['POST'])
def reset():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    RL.reset_table()
    user.update(
        {'name': 'Ahmed Zaidi'},
        {
            '$set': {"current_s": 0}
        }
    )
    qtable = RL.get_table()
    qtable = qtable.to_dict('records')
    return jsonify(qtable)

@app.route('/r_word', methods=['POST'])
def reset_word():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    curr_word = results.get("curr_word")
    RL_word.reset_table(curr_word)
    qtable = RL_word.get_table()
    qtable = qtable.to_dict('records')
    return jsonify(qtable)

@app.route('/quiz_level', methods=['POST'])
def quiz_level():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    observation = results.get("current_s")
    return str(observation)

@app.route('/answer', methods=['POST'])
def verify_ans():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    curr_word = results.get("curr_word")
    input_ans = request.data.lower()
    input_ans = input_ans.replace(" ","_")
    answer, reward = check_ans(input_ans)
    update(RL,env,reward)
    update_word(env,reward,curr_word)
    RL.update_table()
    RL_word.update_table(curr_word)
    return answer

@app.route('/curr_imgLoad', methods=['POST'])
def curr_image_load():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    observation = results.get("current_s")
    curr_word = results.get("curr_word")
    #if curr_word == "":
    #    curr_word = env.get_img_src(observation)

    img_level = level.get(observation)
    return img_level+"/"+curr_word+".jpg"

@app.route('/imgLoad', methods=['POST'])
def image_load():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    observation = results.get("current_s")
    curr_image = env.get_img_src(observation)
    img_level = level.get(observation)
    user.update(
        {'name': 'Ahmed Zaidi'},
        {
            '$set': {"curr_word": curr_image}
        }
    )
    return img_level+"/"+curr_image+".jpg"


@app.route('/quiz', methods=['POST'])
def quiz():
    qtable = RL.get_table()
    qtable = qtable.to_dict('records')
    return jsonify(qtable)

@app.route('/quiz_word', methods=['POST'])
def quiz_word():
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    curr_word = results.get("curr_word")
    observation = results.get("current_s")
    if curr_word == "":
        curr_word = env.get_img_src(observation)
        user.update(
            {'name': 'Ahmed Zaidi'},
            {
                '$set': {"curr_word": curr_word}
            }
        )
    qtable = RL_word.get_table(curr_word)
    qtable = qtable.to_dict('records')
    return jsonify(qtable)

def check_ans(answer):
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    curr_word = results.get("curr_word")
    results = results.get("vocab")
    word_results = results.get(curr_word)
    attempts = word_results.get("attempts")
    incorrect = word_results.get("incorrect")
    correct = word_results.get("correct")
    messsage = ""
    score = ''
    attempts = attempts+1
    answers = [curr_word]
    if curr_word in model.vocab:
        a = model.similar_by_word(curr_word, topn=10, restrict_vocab=None)
        for element in a:
            word_name, sim = element
            answers.append(word_name.lower())
            print word_name
    if answer in answers:
        correct = correct +1
        if answer == curr_word:
            message = "Correct!"
            score = '1'
        else:
            message = 'Correct! However, we were expecting '+curr_word+"'."
            score = '1'
    else:
        message = "Incorrect - the correct answer is '"+curr_word+"'."
        score = '0'
        incorrect = incorrect+1

    user.update(
        {'name': 'Ahmed Zaidi'},
        {   '$set': {
                "vocab."+curr_word+".attempts": attempts,
                "vocab."+curr_word+".incorrect": incorrect,
                "vocab."+curr_word+".correct": correct
            }

        }
    )

    return message,score

def update(RL,env,answer):
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    observation = results.get("current_s")
    action = RL.choose_action(observation)
    observation_, reward = env.step(action,answer,observation)
    RL.learn(observation, action, reward, observation_)
    user.update(
        {'name': 'Ahmed Zaidi'},
        {
            '$set': {"current_s": observation_}
        }
    )

    return answer

def update_word(env,answer,word):
    user = mongo.db.user
    results = user.find_one({"name": "Ahmed Zaidi"})
    results = results.get("vocab")
    results = results.get(word)
    observation = results.get("current_s")
    action = RL_word.choose_action(observation)
    observation_, reward = env.step_word(action,answer,observation)
    RL_word.learn(observation, action, reward, observation_, word)
    user.update(
        {'name': 'Ahmed Zaidi'},
        {
            '$set': {"vocab."+word+".current_s": observation_}
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=8080)
