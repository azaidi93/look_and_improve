from RL_brain import QLearningTable
from Quiz import Quiz
from sys import argv
import os
import settings
class Run_app:
    def __init__(self):
        env = Quiz()
        RL = QLearningTable(actions=list(range(env.n_actions)))

    def get_table():
        return RL.q_table

    def update(self):
        observation = 0
        for episode in range(1000):
            while True:

                action = RL.choose_action(observation)
                answer = raw_input("Answer: ")
                observation_, reward = env.step(action,answer,observation)
                print answer
                RL.learn(observation, action, reward, observation_, settings.GLOBAL_USERNAME)
                observation = observation_


    #if __name__ == "__main__":

    #    path = "images/"
    #    dirs = os.listdir(path)
    #    for folder in dirs:
    #        if not folder.startswith("."):
    #            f_path = "images/"+folder+"/"
    #            f_dirs = os.listdir(f_path)
    #            for images in f_dirs:
    #                if not images.startswith("."):
    #                    print folder,images
