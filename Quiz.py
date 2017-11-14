# -*- coding: utf-8 -*-


from xml.dom import minidom
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import time
import random
import os
from os.path import basename
from pymongo import MongoClient
import settings


class Quiz(object):
    def __init__(self):

        super(Quiz,self).__init__()
        self.action_space = ['b','s','f']
        self.state_space = ['A1','A2','B1','B2','C1','C2']
        self.n_actions = len(self.action_space)
        self.current_state = 0
        rootdir = 'static/img'
        self.A1={}
        self.A2={}
        self.B1={}
        self.B2={}
        self.C1={}
        self.C2={}
        client = MongoClient('mongodb://127.0.0.1:27017/')
        db = client.quiz
        self.user = db.user

        for subdir, dirs, files in os.walk(rootdir):
            level =  subdir[-2:]
            for file in files:
                if not file.startswith('.'):
                    file = os.path.splitext(file)[0]
                    if level == 'A1':
                        self.A1.update({file:level})
                    if level == 'A2':
                        self.A2.update({file:level})
                    if level == 'B1':
                        self.B1.update({file:level})
                    if level == 'B2':
                        self.B2.update({file:level})
                    if level == 'C1':
                        self.C1.update({file:level})
                    if level == 'C2':
                        self.C2.update({file:level})

    def get_img_src(self,level, username):
        i=1
        image = "bike"
        while (i==1):
            if level == 0:
                image = random.choice(self.A1.keys())
            if level == 1:
                image = random.choice(self.A2.keys())
            if level == 2:
                image = random.choice(self.B1.keys())
            if level == 3:
                image = random.choice(self.B2.keys())
            if level == 4:
                image = random.choice(self.C1.keys())
            if level == 5:
                image = random.choice(self.C2.keys())
            results = self.user.find_one({"name": username})
            results = results.get("vocab")
            if results.get(image) == None:
                i=0
            else:
                results = results.get(image)
                i = results.get("current_s")

        return image

    def step_word(self,action,answer,s):
        reward = 0
        print "Current State: ",s
        if action == 0:
            s_ = s
        else:
            if s == 0:
                s_ = 1
            else:
                s_ = 0

        if answer=='0':
            reward=reward+1
        else:
            reward= reward-1
        print "Reward: ",reward

        return s_, reward

    def step(self,action,answer,s):
        reward = 0
        print "Current State: ",s
        if action == 0:
            if s!= 0:
                s_ = s-1
            else:
                s_ = s
        elif action == 1:
            s_ = s

        else:
            if s != 5:
                s_ = s+1
            else:
                s_ = s

        if answer=='0':
            reward=reward+1
        else:
            reward= reward-1
        print "Reward: ",reward

        return s_, reward
