import numpy as np
import pandas as pd
from pymongo import MongoClient

class QLearningTable_Word:
    def __init__(self, actions, learning_rate=0.1, gamma=0.9, epsilon=1):
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client.quiz
        self.level = {0:'active',1:'i_active'}
        self.action = {0:'r',1:'t'}
        self.user = db.user
        self.actions = actions
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = pd.DataFrame(
        np.zeros((2, len(actions))),     # q_table initial values
            columns=self.actions,    # actions's name
        )

    def reset_table(self,word):
            words = []
            results = self.user.find_one({"name": "Ahmed Zaidi"})
            results = results.get("vocab")
            print (len(results))
            for key, value in results.items() :
                words.append(key)

            for word in words:
                for l in self.level:
                    for a in self.action:
                        if l == 0 and a == 0:
                            self.user.update(
                                {'name': 'Ahmed Zaidi'},
                                {
                                    '$set': {"vocab."+word+".q_table."+self.level.get(l)+"_"+self.action.get(a): 0.1}
                                }

                            )
                        else:
                            self.user.update(
                                {'name': 'Ahmed Zaidi'},
                                {
                                    '$set': {"vocab."+word+".q_table."+self.level.get(l)+"_"+self.action.get(a): 0}
                                }

                            )
                self.user.update(
                    {'name': 'Ahmed Zaidi'},
                    {
                        '$set': {"vocab."+word+".current_s": 0}
                    }

                )


    def update_table(self,word):
        for l in self.level:
            for a in self.action:
                self.user.update(
                    {'name': 'Ahmed Zaidi'},
                    {
                        '$set': {"vocab."+word+".q_table."+self.level.get(l)+"_"+self.action.get(a): round(self.q_table.ix[l,a],4)}
                    }
                )

    def get_table(self,word):
        self.check_word(word)
        results = self.user.find_one({"name": "Ahmed Zaidi"})
        results = results.get("vocab")
        results = results.get(word)
        results = results.get("q_"+"table")
        for l in self.level:
            for a in self.action:
                output = results.get(self.level.get(l)+"_"+self.action.get(a))
                self.q_table.ix[l,a] = output

        return self.q_table

    def check_word(self,word):
        results = self.user.find_one({"name": "Ahmed Zaidi"})
        results = results.get("vocab")
        if results.get(word) == None:
            self.create_table(word)

    def create_table(self,word):
        results = self.user.find_one({"name": "Ahmed Zaidi"})
        self.user.update(
            {'name': 'Ahmed Zaidi'},
            {   '$set': {
                    "vocab."+word:{
                        "attempts": 0,
                        "incorrect": 0,
                        "correct": 0,
                        "current_s": 0,
                        "q_table":{
                            "active_r": 0.1,
                            "active_t": 0,
                            "i_active_r": 0,
                            "i_active_t": 0
                        }
                }

            }}
        )

    def choose_action(self, observation):
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.ix[observation, :]
            print self.q_table.ix[observation, :]
            action = state_action.argmax()
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_, word):
        self.get_table(word)
        q_predict = self.q_table.ix[s, a]
        if s_ != 1:
            q_target = r + self.gamma * self.q_table.ix[s_,:].max()
        else:
            q_target = r
        self.q_table.ix[s, a] += self.lr * (q_target - q_predict)
        self.update_table(word)
