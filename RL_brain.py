import numpy as np
import pandas as pd
from pymongo import MongoClient
import settings
class QLearningTable:
    def __init__(self, actions, learning_rate=0.1, gamma=0.9, epsilon=0.9):
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client.quiz
        self.level = {0:'A1',1:'A2',2:'B1',3:'B2',4:'C1',5:'C2'}
        self.action = {0:'b',1:'r',2:'f'}
        self.user = db.user
        self.actions = actions
        self.lr = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = pd.DataFrame(
        np.zeros((6, len(actions))),     # q_table initial values
            columns=self.actions,    # actions's name
        )
        self.q_table.set_value(0,1,1)
        self.q_table.set_value(1,1,1)
        self.q_table.set_value(2,1,1)
        self.q_table.set_value(3,1,1)
        self.q_table.set_value(4,1,1)
        self.q_table.set_value(5,1,1)

    def reset_table(self, username):
        for l in self.level:
            for a in self.action:
                if a == 1:
                    self.user.update(
                        {'name': username},
                        {
                            '$set':
                            {
                                "q_table."+self.level.get(l)+"_"+self.action.get(a): 1
                            }
                        }
                    )
                else:
                    self.user.update(
                        {'name': username},
                        {
                            '$set':
                            {
                                "q_table."+self.level.get(l)+"_"+self.action.get(a): 0
                            }
                        }
                    )

    def update_table(self, username):
        for l in self.level:
            for a in self.action:
                self.user.update(
                    {'name': username},
                    {
                        '$set':
                        {
                            "q_table."+self.level.get(l)+"_"+self.action.get(a): round(self.q_table.ix[l,a],4)
                        }
                    }
                )

    def get_table(self, username):
        results = self.user.find_one({"name": username})
        results = results.get("q_table")
        for l in self.level:
            for a in self.action:
                output = results.get(self.level.get(l)+"_"+self.action.get(a))
                self.q_table.ix[l,a] = output

        return self.q_table


    def choose_action(self, observation):
        # action selection
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.ix[observation, :]
            action = state_action.argmax()
        else:
            # choose random action
            action = np.random.choice(self.actions)
        return action

    def learn(self, s, a, r, s_, username):
        self.get_table(username)
        q_predict = self.q_table.ix[s, a]
        if s_ != 5:
            q_target = r + self.gamma * self.q_table.ix[s_,:].max()
        else:
            q_target = r
        self.q_table.ix[s, a] += self.lr * (q_target - q_predict)
        self.update_table(username)
        
