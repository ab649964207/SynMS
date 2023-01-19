#传入特征池和winset，loseSet 可以返回

import time
import numpy
from z3 import *
from func_timeout import func_set_timeout

class ExpressionClass:
    lenwinset=0
    lenloseset=0
    lenfeaturesPool=0
    featurePool=[]
    Game=[]

    
    def __init__(self, Game,featurePool,actionMap,winning_formula_of_game):
        self.Game=Game
        self.actionMap=actionMap
        self.lenwinset = len(actionMap["workSet"])
        self.featurePool = featurePool
        self.lenloseset = len(actionMap["notWorkSet"])
        self.lenfeaturesPool=len(featurePool)
        self.winfeatures = numpy.zeros((self.lenwinset, self.lenfeaturesPool), dtype=int)
        self.losefeatures = numpy.zeros((self.lenloseset, self.lenfeaturesPool), dtype=int)
        self.FeatureCheck(actionMap["workSet"],self.winfeatures)
        self.FeatureCheck(actionMap["notWorkSet"],self.losefeatures)
        self.winning_formula_of_game=winning_formula_of_game
        if(len(self.winfeatures)):
            self.winning_formula, self.losing_fomula = self.getCandidateFeatures()
            self.validationPolicy()
        else:
            self.winning_formula = ''
            self.losing_fomula = ''

    def validationPolicy(self):
        X = Int('X')
        X1 = Int('X1')
        X2 = Int('X2')
        X3 = Int('X3')
        Y = Int('Y')
        Y1 = Int('Y1')
        Y2 = Int("Y2")
        Y3 = Int("Y3")
        k = Int('k')
        l = Int('l')
        print('验证策略:',self.actionMap["actionName"]+'('+str(self.actionMap['actionParam'])+')'+':'+self.winning_formula)
        s=Solver()
        for action in self.Game['actions']:
            if action["action_name"]==self.actionMap["actionName"]:
                s.add(action["precondition"])
                s.add(action["transition_formula"])
        s.add(self.Game["Constraint"])
        s.add(eval(self.winning_formula))
        s.add(k==self.actionMap['actionParam'])
        s.add(eval(self.winning_formula_of_game.replace('X','Y')))
        if (s.check() == sat):
            m = s.model()
            print(m)
            print('此策略验证失败')
        else:
            print('此策略验证成功')
        # s.add()
        # s.add(self.Game[""])

