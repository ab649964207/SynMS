import sys
from antlr4 import *
from subfile.PDDLGrammarLexer import PDDLGrammarLexer
from subfile.PDDLGrammarParser import PDDLGrammarParser
from z3 import *
from subfile.MyVisitor import MyVisitor
from subfile.MyVisitor import game
from z3 import *
from opera import *
import copy
import time
import eventlet#导入eventlet这个模块
import threading

ptk = 7#设置
time_out1 = 1200


pddlFile =sys.argv[1] #由文件main.py输入路径
resultFile =sys.argv[2]
game_type = sys.argv[3]
# pddlFile = r"domain\1.Sub\1.1Take-away\Take-away-3.pddl"
# resultFile=r"result.txt"
# game_type = "normal"

input_stream = FileStream(pddlFile) 
lexer = PDDLGrammarLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = PDDLGrammarParser(token_stream)
tree = parser.domain()
visitor = MyVisitor()
visitor.visit(tree) 

fp=open(resultFile,'a')
fp.write("\n"+pddlFile.split('\\')[-1]+"\t")
fp.close()
fp=open(resultFile,'a')

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
(k1, k2, k3) = Ints('k1 k2 k3')

Terminal_Condition=eval(str(game.tercondition).replace(
    'v1', 'X').replace('v2', 'X1').replace('v3', 'X2').replace('v4', 'X3'))
Constarint=eval(str(game.constraint).replace(
    'v1', 'X').replace('v2', 'X1').replace('v3', 'X2').replace('v4', 'X3'))
varList = []
for i in game.var_list:
    i = str(i).replace('v1', 'X').replace('v2', 'X1').replace('v3', 'X2').replace('v4', 'X3')
    varList.append(eval(i))
actions=[]
flag_para = True
for i in game.action_list:
    one = {"action_name": i[0],
           "action_parameter": i[1],
           "precondition": eval(str(i[2]).replace('v1', 'X').replace('v2', 'X1').replace('v3', 'X2').replace('v4', 'X3')),
           "transition_formula": eval(str(i[3]).replace('v1\'', 'Y').replace('v2\'', 'Y1').replace('v3\'', 'Y2').replace('v4\'', 'Y3')
                   .replace('v3', 'X2').replace('v1', 'X').replace('v2', 'X1').replace('v4', 'X3'))}
    print(len(one["action_parameter"]))
    if len(one["action_parameter"])>1 or len(one["action_parameter"])==0: 
        flag_para=False
    actions.append(one)

Game = {"Terminal_Condition":Terminal_Condition,
        "varList":varList,
        "actions": actions,
        "Constraint":Constarint,
        "var_num":game.objectsCount,
        "type":game_type,           
        "appeal_constants": game.constantList} 

if len(varList)>=5:
    fp.write("cannot solve much var or parameter")
    sys.exit()
print("Var List:",varList)
varListY = eval(str(varList).replace('X2','Y2').replace('X1','Y1').replace('X','Y'))
print("Var Y list",varListY)

FunExg = {'Add': Add, 'Sub': Sub, 'Inc': Inc, 'Dec': Dec, 'Ge': Ge, 'ITE': ITE,
          'Gt': Gt, 'OR': OR, 'AND': AND, 'NOT': NOT, 'Equal': Equal, 'Mod': Mod,
          'Unequal': Unequal, 'X': X, 'Y': Y, 'Zero': Zero, 'One': One, 'ModTest': ModTest}
Z3FunExg = {'OR': z3OR, 'AND': z3AND}

p_vocabulary = [
              {'Input': ['Int', 'Int'], 'Output': 'Bool','Function_name': 'Equal', 'arity': 2},
              {'Input': ['Int', 'Int'], 'Output': 'Bool','Function_name': 'Unequal', 'arity': 2},
              {'Input': ['Int', 'Int'], 'Output': 'Bool','Function_name': 'Ge', 'arity':2},
              {'Input': ['Int', 'Int'], 'Output': 'Bool', 'Function_name': 'Gt', 'arity':2},
              {'Input': ['Int', 'Int', 'Int'], 'Output':'Bool', 'Function_name':'ModTest', 'arity':3}]
t_vocabulary = [
            {'Input': ['Int', 'Int'], 'Output':'Int', 'Function_name':'Add', 'arity':2},
            {'Input': ['Int', 'Int'], 'Output': 'Int','Function_name': 'Sub', 'arity':2},
]

ao_vocabulary =[{'Input': ['Bool', 'Bool'], 'Output': 'Bool','Function_name': 'OR', 'arity': 2},
              {'Input': ['Bool', 'Bool'], 'Output': 'Bool','Function_name': 'AND', 'arity': 2},]

def enumerate():
    SigSet = []
    ExpSet = []
    SizeOneExps = []
    ItemsNum = []
    ItemsVar = []

    SizeOneExps.append({'Expression': 0, 'Isnum': True, 'size': 1})
    SizeOneExps.append({'Expression': 1, 'Isnum': True, 'size': 1})
    SizeOneExps.append({'Expression': X, 'Isnum': False, 'size': 1})
    for i in Game["appeal_constants"]:
        SizeOneExps.append({'Expression': eval(i), 'Isnum': True, 'size': 1})
    if Game["var_num"] == 2:
        SizeOneExps.append({'Expression': X1, 'Isnum': False, 'size': 1})
    elif Game["var_num"] == 3:
        SizeOneExps.append({'Expression': X1, 'Isnum': False, 'size': 1})
        SizeOneExps.append({'Expression': X2, 'Isnum': False, 'size': 1})
    elif Game["var_num"] == 4:
        SizeOneExps.append({'Expression': X1, 'Isnum': False, 'size': 1})
        SizeOneExps.append({'Expression': X2, 'Isnum': False, 'size': 1})
        SizeOneExps.append({'Expression': X3, 'Isnum': False, 'size': 1})

    for i in SizeOneExps:
        Goal1 = []
        if (i['Isnum']):  # 数字
            for num in range(len(pts)):  # count反例数
                Goal1.append(i['Expression'])
            if Goal1 not in SigSet:  # Sigset标记
                SigSet.append(Goal1)
                i['outputData'] = Goal1
                ExpSet.append(i)  # 表达式添加一个输出项，将表达式加到表达式集合中
        else:
            if i['Expression'] == X:
                for pt in pts:
                    Goal1.append(pt[0])
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)  # SigSet 保留不同的值
                    i['outputData'] = Goal1
                    ExpSet.append(i)  # size_one_表达式 添加到 EXPset
            if i['Expression'] == X1:
                for pt in pts:
                    Goal1.append(pt[1])
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)
                    i['outputData'] = Goal1
                    ExpSet.append(i)
            if i['Expression'] == X2:
                for pt in pts:
                    Goal1.append(pt[2])
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)
                    i['outputData'] = Goal1
                    ExpSet.append(i)
            if i['Expression'] == X3:
                for pt in pts:
                    Goal1.append(pt[3])
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)
                    i['outputData'] = Goal1
                    ExpSet.append(i)
    li = 2
    SigSetP = []
    ExpSetP = []
    while True:
        print("size",li)
        for i in t_vocabulary:
            for size1 in range(1, li):  # add(num,num)
                for choose1 in ExpSet:
                    if choose1['size'] == size1:
                        for choose2 in ExpSet:
                            if choose2['size'] == li-size1:
                                if termination_sign:
                                    Thread1.cancel()
                                    fp.write("time out")
                                    sys.exit(0)
                                term = FunExg[i['Function_name']](choose1['Expression'], choose2['Expression'])
                                Goal1 = []
                                for k1, h in zip(choose1['outputData'], choose2['outputData']):
                                    Goal1.append(FunExg[i['Function_name']](k1, h))
                                if Goal1 not in SigSet:  # 更新SigSet ExgSet
                                    SigSet.append(Goal1)
                                    i['outputData'] = Goal1
                                    ExpSet.append(
                                        {'Expression': term, 'Isnum': choose1['Isnum'] and choose2['Isnum'], 'outputData': Goal1, 'size': li})
        
        for i in p_vocabulary:  # == > >=
            if i['arity'] == 2:
                for size1 in range(1, li):  # add(num,num)
                    for choose1 in ExpSet:
                        if choose1['size'] == size1:
                            for choose2 in ExpSet:
                                if choose2['size'] == li-size1 :
                                    if termination_sign:
                                        Thread1.cancel()
                                        fp.write("time out")
                                        sys.exit(0)
                                    pred = FunExg[i['Function_name']](choose1['Expression'], choose2['Expression'])
                                    Goal1 = []
                                    for k1, h in zip(choose1['outputData'], choose2['outputData']):
                                        Goal1.append(FunExg[i['Function_name']](k1, h))
                            
                                    if Goal1 == ptsGoal:
                                        return pred
                                    if Goal1 not in SigSetP:  # 更新SigSet ExgSet
                                        SigSetP.append(Goal1)
                                        i['outputData'] = Goal1
                                        ExpSetP.append(
                                            {'Expression': pred, 'outputData': Goal1, 'size': li})
            if i['arity'] == 3 and li >= 3: # %=
                for size1 in range(1,li):
                    for choose1 in ExpSet:
                        if choose1['size'] == size1 and choose1['Isnum']==False:
                            for size2 in range(1,li):
                                for choose2 in ExpSet:
                                    if choose2['size'] == size2 and choose2['Isnum'] and choose2['Expression']>0:
                                        for choose3 in ExpSet:
                                            if choose3['size']== li-size1-size2 and choose3['Isnum'] and choose3['Expression']<choose2['Expression']:
                                                try:
                                                    if termination_sign:
                                                        Thread1.cancel()
                                                        fp.write("time out")
                                                        sys.exit(0)
                                                    pred = FunExg[i['Function_name']](choose1["Expression"], choose2["Expression"], choose3["Expression"])
                                                    Goal1 = []
                                                    for k1,h,m in zip(choose1['outputData'],choose2['outputData'],choose3['outputData']):
                                                        Goal1.append(FunExg[i['Function_name']](k1,h,m))
                                                    if Goal1 == ptsGoal:
                                                        return pred
                                                    if Goal1 not in SigSetP:
                                                        SigSetP.append(Goal1)
                                                        i['outputData'] = Goal1
                                    
                                                        ExpSetP.append({'Expression': pred, 'outputData': Goal1, 'size': li})
                                                except ZeroDivisionError:
                                                    pass
        if li>=4:
            for i in ao_vocabulary:
                for size1 in range(1,li):
                    for choose1 in ExpSetP:
                        if choose1["size"] == size1:
                            for choose2 in ExpSetP:
                                if choose2["size"] ==li+1-size1 and choose1 != choose2:
                                    if termination_sign:
                                        Thread1.cancel()
                                        fp.write("time out")
                                        sys.exit(0)
                                    pred = Z3FunExg[i['Function_name']](choose1['Expression'], choose2['Expression'])
                                    
                                    Goal1 = []
                                    for k1, h in zip(choose1['outputData'], choose2['outputData']):
                                        Goal1.append(FunExg[i['Function_name']](k1, h))
                                    if Goal1 == ptsGoal:
                                        return pred
                                    if Goal1 not in SigSetP:  # 更新SigSet ExgSet
                                        SigSetP.append(Goal1)
                                        i['outputData'] = Goal1
                                        ExpSetP.append({'Expression': pred, 'outputData': Goal1, 'size': li})
        li += 1

def enumerateK():
    SigSet = []
    ExpSet = []
    SizeOneExps = []
    ItemsNum = []
    ItemsVar = []

    SizeOneExps.append({'Expression': 0, 'Isnum': True, 'size': 1})
    SizeOneExps.append({'Expression': 1, 'Isnum': True, 'size': 1})
    SizeOneExps.append({'Expression': X, 'Isnum': False, 'size': 1})
    for i in Game["appeal_constants"]:
        SizeOneExps.append({'Expression': eval(i), 'Isnum': True, 'size': 1})
    if Game["var_num"] == 2:
        SizeOneExps.append({'Expression': X1, 'Isnum': False, 'size': 1})
    elif Game["var_num"] == 3:
        SizeOneExps.append({'Expression': X1, 'Isnum': False, 'size': 1})
        SizeOneExps.append({'Expression': X2, 'Isnum': False, 'size': 1})
    elif Game["var_num"] == 4:
        SizeOneExps.append({'Expression': X1, 'Isnum': False, 'size': 1})
        SizeOneExps.append({'Expression': X2, 'Isnum': False, 'size': 1})
        SizeOneExps.append({'Expression': X3, 'Isnum': False, 'size': 1})

    for i in SizeOneExps:
        Goal1 = []
        if (i['Isnum']):  # 数字
            for num in range(len(pts)):  # count反例数
                Goal1.append(i['Expression'])
            if Goal1 == ptsGoal:
                    return i['Expression']
            if Goal1 not in SigSet:  # Sigset标记
                SigSet.append(Goal1)
                i['outputData'] = Goal1
                ExpSet.append(i)  # 表达式添加一个输出项，将表达式加到表达式集合中
                
        else:
            if i['Expression'] == X:
                for pt in pts:
                    Goal1.append(pt[0])
                if Goal1 == ptsGoal:
                    return i['Expression']
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)  # SigSet 保留不同的值
                    i['outputData'] = Goal1
                    ExpSet.append(i)  # size_one_表达式 添加到 EXPset
                    if Goal1 == ptsGoal:
                        return i['Expression']
            if i['Expression'] == X1:
                for pt in pts:
                    Goal1.append(pt[1])
                if Goal1 == ptsGoal:
                    return i['Expression']
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)
                    i['outputData'] = Goal1
                    ExpSet.append(i)
            if i['Expression'] == X2:
                for pt in pts:
                    Goal1.append(pt[2])
                if Goal1 == ptsGoal:
                    return i['Expression']
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)
                    i['outputData'] = Goal1
                    ExpSet.append(i)
            if i['Expression'] == X3:
                for pt in pts:
                    Goal1.append(pt[3])
                if Goal1 == ptsGoal:
                    return i['Expression']
                if Goal1 not in SigSet:
                    SigSet.append(Goal1)
                    i['outputData'] = Goal1
                    ExpSet.append(i)
    li = 2
    while True:
        print("size",li)
        for i in t_vocabulary:
            for size1 in range(1, li):  # add(num,num)
                for choose1 in ExpSet:
                    if choose1['size'] == size1:
                        for choose2 in ExpSet:
                            if choose2['size'] == li-size1:
                                if termination_sign:
                                    Thread1.cancel()
                                    fp.write("time out")
                                    sys.exit(0)
                                term = FunExg[i['Function_name']](choose1['Expression'], choose2['Expression'])
                                Goal1= []
                                for k1, h in zip(choose1['outputData'], choose2['outputData']):
                                    Goal1.append(FunExg[i['Function_name']](k1, h))
                                if Goal1 == ptsGoal:
                                    return term
                                if Goal1 not in SigSet:  # 更新SigSet ExgSet
                                    SigSet.append(Goal1)
                                    i['outputData'] = Goal1
                                    ExpSet.append(
                                        {'Expression': term, 'Isnum': choose1['Isnum'] and choose2['Isnum'], 'outputData': Goal1, 'size': li})
    
        li += 1                    

"""global transition formula"""
global_transition_formula = "Or("
for i in Game["actions"]:
    if i['action_parameter'] != []:
        temp = "["
        for j in i['action_parameter']:
            temp = temp+str(j)+","
        temp = temp[:-1]
        temp += "],"
        global_transition_formula = global_transition_formula + \
            "Exists("+temp+str(i["transition_formula"])+"),"
    else:
        global_transition_formula = global_transition_formula + \
            str(i["transition_formula"])+","

global_transition_formula = global_transition_formula[:-1]
global_transition_formula = global_transition_formula+")"

print("Global transition formula:\n\t", global_transition_formula)
global_transition_formula = simplify(eval(global_transition_formula))


"""
递归得到反例所要使用的点集合
"""
position = []
if Game['var_num'] == 1:
    for i in range(0, 100):
        position.append('illegal')
elif Game['var_num'] == 2:
    for i in range(0, 100):
        position.append([])
        for j in range(0, 100):
            position[i].append('illegal')
elif Game['var_num'] == 3:
    for i in range(0, 100):
        position.append([])
        for i1 in range(0, 100):
            position[i].append([])
            for i2 in range(0, 100):
                position[i][i1].append("illegal")
elif Game['var_num'] == 4:
    for i in range(0, 100):
        position.append([])
        for i1 in range(0, 100):
            position[i].append([])
            for i2 in range(0, 100):
                position[i][i1].append([])
                for i3 in range(0, 100):
                    position[i][i1][i2].append("illegal")

"""
set all terminate state position  #求出范围内所有的终态位置 一般是一个，但有时不止一个
"""
TerminatePosition = []  # 保存已经求出来的解点坐标
while(True):
    s = Solver()
    s.add(Game["Terminal_Condition"])
    s.add(Game["Constraint"])
    if Game["var_num"] == 1:
        s.add(X < 200)
        for i in TerminatePosition:
            s.add(X != i[0])
        if(s.check() == sat):
            m = s.model()
            a = m[X].as_long()
            TerminatePosition.append([a])
            if Game["type"] == "normal":
                position[a] = True  # normal
            else:
                position[a] = False  # misere
        else:
            break
    elif Game["var_num"] == 2:
        s.add(X < 100, X1 < 100)
        for i in TerminatePosition:
            s.add(Or(X != i[0], X1 != i[1]))
        if s.check() == sat:
            m = s.model()
            a = m[X].as_long()
            b = m[X1].as_long()
            TerminatePosition.append([a, b])
            if(Game["type"] == "normal"):
                position[a][b] = True
            else:
                position[a][b] = False
        else:
            break
    elif Game["var_num"] == 3:
        s.add(X < 100, X1 < 100, X2 < 100)
        for i in TerminatePosition:
            s.add(Or(X != i[0], X1 != i[1], X2 != i[2]))
        if s.check() == sat:
            m = s.model()
            a = m[X].as_long()
            b = m[X1].as_long()
            c = m[X2].as_long()
            TerminatePosition.append([a, b, c])
            if(Game["type"] == "normal"):
                position[a][b][c] = True
            else:
                position[a][b][c] = False
        else:
            break
    elif Game["var_num"] == 4:
        s.add(X < 100, X1 < 100, X2 < 100, X3 < 100)
        for i in TerminatePosition:
            s.add(Or(X != i[0], X1 != i[1], X2 != i[2], X3 != i[3]))
        if s.check() == sat:
            m = s.model()
            a = m[X].as_long()
            b = m[X1].as_long()
            c = m[X2].as_long()
            d = m[X3].as_long()
            TerminatePosition.append([a, b, c, d])
            if(Game["type"] == "normal"):
                position[a][b][c][d] = True
            else:
                position[a][b][c][d] = False
        else:
            break
print("All terminate position:\n\t", TerminatePosition)

def isLossingState(*v):
    if termination_sign:
        Thread1.cancel()
        fp.write("time out")
        sys.exit(0)
    # print("Insert",v," into isLossingstate:")
    for i in v:  # default position < 100
        if i >= 100:
            return 'illegal'
    if len(v) == 1:
        if position[v[0]] != 'illegal':
            return position[v[0]]
        for x in range(0, v[0] + 1):
            if (position[x] != 'illegal'):
                continue
            temp = []
            while (True):
                s = Solver()
                s.add(global_transition_formula)
                s.add(Game["Constraint"])
                s.add(X == x)
                for i in temp:
                    s.add(Or(Y != i[0]))
                if (s.check() == sat):
                    m = s.model()
                    temp.append([m[Y].as_long()])
                else:
                    break
            is_losing = True
            s = Solver()
            s.add(Game["Constraint"])
            s.add(X == x)
            if (s.check() == unsat):
                continue
            for i in temp:
                if (position[i[0]] == 'illegal'):
                    position[i[0]] = isLossingState(i[0])
            for i in temp:
                is_losing = is_losing and not position[i[0]]
            if (is_losing):
                position[x] = True
            else:
                position[x] = False
        return position[v[0]]
    elif len(v) == 2:
        if position[v[0]][v[1]] != 'illegal':  # 已经访问过了的，直接访问值，没有的
            return position[v[0]][v[1]]
        for x in range(0, v[0]+1):  # 遍历所有的点去设置状态
            for y in range(0, v[1]+1):
                if(position[x][y] != 'illegal'):
                    continue
                temp = []  # 存放转移后的解 y y1即执行动作后的值
                while (True):
                    s = Solver()
                    s.add(global_transition_formula)
                    s.add(Game["Constraint"])
                    s.add(X == x, X1 == y)
                    for i in temp:
                        s.add(Or(Y != i[0], Y1 != i[1]))
                    if (s.check() == sat):
                        m = s.model()
                        temp.append([m[Y].as_long(), m[Y1].as_long()])  # 全局转移解
                    else:
                        break
                # print('Transilate 773 of',x,y,":\t",temp) #存放状态 438 [[2, 1], [2, 0], [1, 1]]
                is_losing = True
                s = Solver()
                s.add(Game["Constraint"])
                s.add(X == x, X1 == y)
                if(s.check() == unsat):
                    continue
                for i in temp:
                    if(position[i[0]][i[1]] == 'illegal'):
                        position[i[0]][i[1]] = isLossingState(i[0], i[1])
                for i in temp:
                    is_losing = is_losing and not position[i[0]][i[1]]
                if (is_losing):
                    position[x][y] = True
                else:
                    position[x][y] = False
        # print("判断出给定的表达式：",v,"is",position[v[0]][v[1]])
        return position[v[0]][v[1]]
    elif len(v) == 3:
        if position[v[0]][v[1]][v[2]] != 'illegal':  # 已经访问过了的，直接访问值，没有的
            return position[v[0]][v[1]][v[2]]
        for x in range(0, v[0]+1):  # 遍历所有的点去设置状态
            for y in range(0, v[1]+1):
                for z in range(0, v[2]+1):
                    if(position[x][y][z] != 'illegal'):
                        continue
                    temp = []  # 存放转移后的解 y y1即执行动作后的值
                    while (True):
                        s = Solver()
                        s.add(global_transition_formula)
                        s.add(Game["Constraint"])
                        s.add(X == x, X1 == y, X2 == z)
                        for i in temp:
                            s.add(Or(Y != i[0], Y1 != i[1], Y2 != i[2]))
                        if s.check() == sat:
                            m = s.model()
                            temp.append(
                                [m[Y].as_long(), m[Y1].as_long(), m[Y2].as_long()])  # 全局转移解
                        else:
                            break
                    # print('438',temp) 存放状态 438 [[2, 1], [2, 0], [1, 1]]
                    is_losing = True
                    s = Solver()
                    s.add(Game["Constraint"])
                    s.add(X == x, X1 == y, X2 == z)
                    if(s.check() == unsat):
                        continue
                    for i in temp:
                        if(position[i[0]][i[1]][i[2]] == 'illegal'):
                            position[i[0]][i[1]][i[2]] = isLossingState(
                                i[0], i[1], i[2])
                    for i in temp:
                        is_losing = is_losing and not position[i[0]
                                                               ][i[1]][i[2]]
                    if (is_losing):
                        position[x][y][z] = True
                    else:
                        position[x][y][z] = False
        return position[v[0]][v[1]][v[2]]
    elif len(v) == 4:
        if position[v[0]][v[1]][v[2]][v[3]] != 'illegal':  # 已经访问过了的，直接访问值，没有的
            return position[v[0]][v[1]][v[2]][v[3]]
        for x in range(0, v[0]+1):  # 遍历所有的点去设置状态
            for y in range(0, v[1]+1):
                for z in range(0, v[2]+1):
                    for z1 in range(0,v[3]+1):
                        if(position[x][y][z][z1]!= 'illegal'):
                            continue
                    temp = []  # 存放转移后的解 y y1即执行动作后的值
                    while (True):
                        s = Solver()
                        s.add(global_transition_formula)
                        s.add(Game["Constraint"])
                        s.add(X == x, X1 == y, X2 == z, X3 ==z1)
                        for i in temp:
                            s.add(Or(Y != i[0], Y1 != i[1], Y2 != i[2], Y3 != i[3]))
                        if s.check() == sat:
                            m = s.model()
                            temp.append(
                                [m[Y].as_long(), m[Y1].as_long(), m[Y2].as_long(),m[Y3].as_long()])  # 全局转移解
                        else:
                            break
                    # print('438',temp) 存放状态 438 [[2, 1], [2, 0], [1, 1]]
                    is_losing = True
                    s = Solver()
                    s.add(Game["Constraint"])
                    s.add(X == x, X1 == y, X2 == z, X3 == z1)
                    if(s.check() == unsat):
                        continue
                    for i in temp:
                        if(position[i[0]][i[1]][i[2]][i[3]] == 'illegal'):
                            position[i[0]][i[1]][i[2]][i[3]] = isLossingState(
                                i[0], i[1], i[2], i[3])
                    for i in temp:
                        is_losing = is_losing and not position[i[0]][i[1]][i[2]][i[3]]
                    if (is_losing):
                        position[x][y][z][z1] = True
                    else:
                        position[x][y][z][z1] = False
        return position[v[0]][v[1]][v[2]][v[3]]

# 宽松反例---遍历一个满足约束不在反例集中的点 ptList=[[pt1],[pt2],[pt3]]
def FindCountExample(ptList):
    if Game["var_num"] == 1:
        i = 1
        while(True):
            if i>100:
                global example_run_out_sign 
                example_run_out_sign = True
                return 'illegal'
            for v1 in range(0, i):
                if [v1] not in ptList and [v1] not in pts:
                    s = Solver()
                    s.add(Game["Constraint"])
                    s.add(X == v1)
                    if (s.check() == sat):
                        return [v1]
                        # 严格反例模式
                        boolTemp = isLossingState(v1)
                        boolTemp2 = eval(str(e).replace(
                            str(X), str(v1)))
                        s = Solver()
                        if boolTemp == False:
                            s.add(True, boolTemp2)
                            if(s.check() == sat):
                                return [v1]
                        elif boolTemp == True:
                            s.add(True, boolTemp2)
                            if(s.check() == unsat):
                                return [v1]
                    else:
                        continue
            i += 1
    elif Game["var_num"] == 2:
        i = 1
        if i>100:
            example_run_out_sign = True
            return 'illegal'
        while(True):
            for v1 in range(0, i+1):  # 没有点（0,1）啊
                v2 = i-v1  # 遍历所有的v1v2=i的组合 按照size遍历
                # print("828",v1,v2)
                if [v1, v2] not in ptList and [v1, v2] not in pts:
                    s = Solver()
                    s.add(Game["Constraint"])  # 满足约束条件
                    s.add(X == v1, X1 == v2)
                    if s.check() == sat:
                        # print("find example:", v1, v2)
                        return [v1, v2]
                        # print(expr)
                        # 要求在这里就设置为严格反例
                        # print("该轮枚举：", v1, v2)
                        boolTemp = isLossingState(v1, v2)
                        boolTemp2 = eval(str(e).replace(
                            str(X1), str(v2)).replace(str(X), str(v1)))
                        s = Solver()
                        if boolTemp == False:
                            s.add(True, boolTemp2)
                            if(s.check() == sat):
                                return [v1, v2]
                        elif boolTemp == True:
                            s.add(True, boolTemp2)
                            if(s.check() == unsat):
                                return [v1, v2]
                    else:
                        continue
            i = i+1
    elif Game["var_num"] == 3:
        i = 1
        while True:
            if i>100:
                example_run_out_sign = True
                return 'illegal'
            for v1 in range(0, i+1):
                for v2 in range(0, i-v1+1):
                    v3 = i-v1-v2
                    if [v1, v2, v3] not in ptList and [v1, v2, v3]not in pts:
                        s = Solver()
                        s.add(Game["Constraint"])  # 满足约束条件
                        s.add(X == v1, X1 == v2, X2 == v3)
                        if s.check() == sat:
                            return [v1, v2, v3]
                            # 严格反例模式
                            boolTemp = isLossingState(v1, v2, v3)
                            boolTemp2 = eval(str(e).replace(
                                str(X1), str(v2)).replace(str(X2), str(v3)).replace(str(X), str(v1)))
                            s = Solver()
                            if boolTemp == False:
                                s.add(True, boolTemp2)
                                if(s.check() == sat):
                                    return [v1, v2, v3]
                            elif boolTemp == True:
                                s.add(True, boolTemp2)
                                if(s.check() == unsat):
                                    return [v1, v2, v3]
                        else:
                            continue
            i = i+1
    elif Game["var_num"] == 4:
        i = 1
        while True:
            if i>100:
                example_run_out_sign = True
                return 'illegal'
            for v1 in range(0, i+1):
                for v2 in range(0, i-v1+1):
                    for v3 in range(0, i-v1-v2+1):
                        v4 = i-v1-v2-v3
                        if [v1, v2, v3, v4] not in ptList and [v1, v2, v3, v4]not in pts:
                            s = Solver()
                            s.add(Game["Constraint"])  # 满足约束条件
                            s.add(X == v1, X1 == v2, X2 == v3, X3 == v4)
                            if s.check() == sat:
                                return [v1, v2, v3, v4]
                                # 严格反例模式
                                boolTemp = isLossingState(v1, v2, v3)
                                boolTemp2 = eval(str(e).replace(
                                    str(X1), str(v2)).replace(str(X2), str(v3)).replace(str(X), str(v1)))
                                s = Solver()
                                if boolTemp == False:
                                    s.add(True, boolTemp2)
                                    if(s.check() == sat):
                                        return [v1, v2, v3]
                                elif boolTemp == True:
                                    s.add(True, boolTemp2)
                                    if(s.check() == unsat):
                                        return [v1, v2, v3]
                            else:
                                continue
            i = i+1


def outRange(*v):
    for i in v:  # default position < 100
        if i >= 100 or i < 0:
            return 'illegal'

def satfindstate(ptk):
    ptK = ptk
    ptList = []
    m = s.model()
    value = []
    for i in Game["varList"]:
        value.append(m[i].as_long())
    if outRange(*value) != 'illegal':
        print("反例：",value)
        ptK -= 1
        ptList.append(value)
        if(ptK == 0):
            return ptList
    # while ptK > 0:
    #     if len(value) == 1:
    #         s.add(X!=value[0])
    #     elif len(value) == 2:
    #         s.add(Or(X!=value[0],X1!=value[1]))
    #     elif len(value) == 3:
    #         s.add(Or(X!=value[0],X1!=value[1],X2!=value[2]))
    #     if s.check() == sat:
    #         m = s.model()
    #         value =[]
    #         for i in Game['varList']:
    #             value.append(m[i].as_long())  
    #         print("策略不满足,反例是:",value)
    #         ptK = ptK - 1
    #         ptList.append(value)
    #     else:
    #         print("没有更多的反例了")
    #         break
    while ptK>0:
        pt = FindCountExample(ptList)
        print("find countExample:",pt)
        if pt =='illegal':#例子用完了，返回ptList
            return ptList
        if outRange(*pt) == 'illegal':
            continue
        else:
            ptK -= 1
            ptList.append(pt)
    print(ptk,"example generate:\t", ptList)
    return ptList           

def unkownfindstate(ptk):
    ptK = ptk
    ptList = []
    while True:
        pt = FindCountExample(ptList)
        if pt =='illegal':#例子用完了，返回ptList
            return ptList
        if outRange(*pt) == 'illegal':
            continue
        else:
            ptK -= 1
            ptList.append(pt)
            if(ptK == 0):
                print("InitializeStates",ptk,"example generate:\t", ptList)
                return ptList




start_winning_formula_time = time.time()
termination_sign = False #超时标志

def programTimeOut():
    global termination_sign
    termination_sign = True
    Thread1.cancel()

Thread1 = threading.Timer(time_out1, programTimeOut)
Thread1.start()

pts = []
ptsGoal = []
Maxsize = 1

"""合成必胜公式"""
e = X==X
while True:
    if termination_sign:
        Thread1.cancel()
        fp.write("time out")
        sys.exit(0)
    print(pts)
    print(ptsGoal)  
    last_e = e

    e = enumerate()
    print("枚举的结果是",e)
    e1 = eval(str(e).replace("X1", "Y1").replace("X2", "Y2").replace("X", "Y"))
    if(Game["type"]=="normal"):
        con1 = And(Game["Terminal_Condition"], Not(e))
        con2 = And(Game["Constraint"], Not(e), ForAll(
            varListY, Or(Not(global_transition_formula), Not(e1))))
        con3 = And(Game["Constraint"], e, Exists(varListY, And(global_transition_formula, e1)))
    elif(Game["type"]=="misere"):
        con1 = And(Game["Terminal_Condition"], e)
        con2 = And(Game["Constraint"], Not(e), Not(Game["Terminal_Condition"]), ForAll(varListY, Implies(global_transition_formula, Not(e1))))
        con3 = And(Game["Constraint"], e, Exists(varListY, And(global_transition_formula, e1)))
    s = Solver()
    s.add(con1)
    s.set('timeout', 60000)
    print(s.check())
    if(s.check() == sat):  
        examples=satfindstate(ptk)
    else:                          
        print("condition1 sat")
        s = Solver()
        s.add(con2)
        s.set('timeout', 60000)
        print(s.check())
        if(s.check() == sat): 
            examples=satfindstate(ptk)
        else:                      
            print("condition2 sat")
            s = Solver()
            s.add(con3)
            s.set('timeout', 60000)
            print(s.check())
            if(s.check() == sat): 
                examples=satfindstate(ptk)
            else: 
                print("condition3 sat")
                losing_formula = e
                print( '-----------------------------------------------------------------------------')
                print("The Winning formula of this game is:", Not(losing_formula))
                generate_winning_formula_time = (time.time() - start_winning_formula_time)
                print("Time to generate the winning formula:",generate_winning_formula_time)
                generate_winning_formula_time=str(round(generate_winning_formula_time,2))
                fp=open(resultFile,'a')
                fp.write(str(simplify(Not(losing_formula)))+"\t"+generate_winning_formula_time + "\t")
                fp.close() #先把结果写进去
                fp=open(resultFile,'a')
                break
    if Game["var_num"] == 1:
        for i in examples:  # k个反例 [[0],[1],[2]]
                if i[0] not in pts:
                    pts.append([i[0]])
                    ptsGoal.append(isLossingState(i[0]))
    elif Game["var_num"] == 2:
        for i in examples:
            if [i[0], i[1]] not in pts:
                pts.append([i[0], i[1]])
                ptsGoal.append(isLossingState(i[0], i[1]))
    elif Game["var_num"] == 3:
        for i in examples:
            if [i[0], i[1], i[2]] not in pts:
                pts.append([i[0], i[1], i[2]])
                ptsGoal.append(isLossingState(i[0], i[1], i[2]))
    elif Game["var_num"] == 4:
        for i in examples:
            if [i[0], i[1], i[2], i[3]] not in pts:
                pts.append([i[0], i[1], i[2], i[3]])
                ptsGoal.append(isLossingState(i[0], i[1], i[2], i[3]))



if  flag_para==False:
    fp.write("cannot solve much var or parameter")
    Thread1.cancel()
    sys.exit()

winning_formula =  Not(losing_formula)
winning_formula_Y = eval(str(winning_formula).replace("X1", "Y1").replace("X2", "Y2").replace("X", "Y"))

def refine_the_winning_formula(Losing_formula):
    try:
        C = str(Losing_formula)
        # print('612',C)    X == X1 + 1
        C = C.replace(' ', '')  # X==X1+1
        Ct = []
        # gou'zhao
        if (C.find('And') == -1 and C.find('Or') == -1):  # 表达式没有and or
            if (C.find('==') != -1 and (type(eval(C[(C.find('==') + 2):])) == type(1)) and C.find('%') == -1):
                Ct = []
                Ct.append(C.replace('==', '<'))
                Ct.append(C.replace('==', '>'))
            elif (C.find('==') != -1 and (type(eval(C[(C.find('==') + 2):])) == type(X)) and C.find('%') == -1):
                Ct = []
                Ct.append(C.replace('==', '<'))
                Ct.append(C.replace('==', '>'))
            # a%b==c
            elif (C.find('%') != -1 and (type(eval(C[(C.find('==') + 2):])) == type(1))):
                Ct = []
                num = eval(C[(C.find('%') + 1):C.find('==')]) - 1  # b
                num_original = eval(C[(C.find('==') + 2):])  # c
                while (num >= 0):
                    if (num != num_original):  # b!=c and b>=0
                        C = C[:C.find('==') + 2]
                        C = C + str(num)     # a+b
                        Ct.append(C)
                        # Ct.append(C.replace(C[(C.find('==') + 2):], str(num)))
                    num = num - 1
        else:
            if ((C.find('X') != -1 and C.find('X1') == -1) or (C.find('X') == -1 and C.find('X1') != -1)):
                if (C.find('%') != -1 and (type(eval(C[(C.find('==') + 2):C.find(',')])) == type(1)) and C.find(
                        'Or') != -1):
                    Ct = []
                    num = eval(C[(C.find('%') + 1):C.find('==')]) - 1
                    prnum = []
                    pre = C.find('==')
                    while (pre != -1):
                        prnum.append(eval(C[pre + 2]))
                        pre = C.find('==', pre + 1)
                    # print(prnum)
                    while (num >= 0):
                        if (num not in prnum):
                            Ct.append(C[C.find('X'):C.find(',')].replace(
                                C[C.find('==') + 2], str(num)))
                        num = num - 1
            else:
                if (C.find('And') != -1):
                    C1 = C
                    C1 = C1.replace('And', 'Or')
                    C1 = C1.replace('==', '!=')
                    C1 = C1.replace('Or(', '')
                    C1 = C1.replace(')', '')
                    Ct = C1.split(',')
        print("Covers of this game:", Ct)
        refinement = []
        for i in Ct:
            i = eval(i)
            refinement.append(i)
        return refinement
    except:
        print("error")
        fp.write("block much")
        Thread1.cancel()
        sys.exit(0)

def generatePt(cover, pts, action_constraint):
    s = Solver()
    s.add(cover)
    s.add(action_constraint)
    if(Game["var_num"] == 1):
        for pt in pts:
            s.add(Or(X != pt[0]))
    if(Game["var_num"] == 2):
        for pt in pts:
            s.add(Or(X != pt[0], X1 != pt[1]))
    if(Game["var_num"] == 3):
        for pt in pts:
            s.add(Or(X != pt[0], X1 != pt[1], X2 != pt[2]))
    if(Game["var_num"] == 4):
        for pt in pts:
            s.add(Or(X != pt[0], X1 != pt[1], X2 != pt[2], X3 != pt[3]))
    s.check()
    m = s.model()
    if(Game["var_num"] == 1):
        return [m[X].as_long()]
    if (Game["var_num"] == 2):
        return [m[X].as_long(), m[X1].as_long()]
    if (Game["var_num"] == 3):
        return [m[X].as_long(), m[X1].as_long(),m[X2].as_long()]
    if (Game["var_num"] == 4):
        return [m[X].as_long(), m[X1].as_long(),m[X2].as_long(),m[X3].as_long()]

def findK(action_precondition, action_transition_formula, action_constraint, pt):  # 相当于代入SMT中
    s = Solver()
    s.add(Not(winning_formula_Y))
    s.add(action_precondition)
    s.add(action_transition_formula)
    s.add(action_constraint)
    s.add(X == pt[0])
    if(Game["var_num"] == 2):
        s.add(X1 == pt[1])
    if(Game["var_num"] == 3):
        s.add(X1 == pt[1])
        s.add(X2 == pt[2])
    if(Game["var_num"] == 4):
        s.add(X1 == pt[1])
        s.add(X2 == pt[2])
        s.add(X3 == pt[3])
    if(s.check() == sat):  # 添加所有的条件判断是解是否合理
        m = s.model()
        return m[k].as_long()  # 求解出k值
    else:
        return "no suitable k"



start_refine = time.time()
winningStrategy = []
refinement = refine_the_winning_formula(losing_formula)
flag_strategy = True
for cover in refinement:
    print("725cover:",cover)
    s = Solver()
    s.add(cover)
    s.add(Game["Constraint"])
    if(s.check() == unsat):  # 判断cover是否满足约束条件
        continue
    flagAct = False
    for action in actions:
        pts.clear()
        ptsGoal.clear()
        print("动作",action["action_name"])
        while (True):
            if termination_sign:
                fp.write("time out")
                Thread1.cancel()
                sys.exit(0)
            print(pts)
            print(ptsGoal)
            e = enumerateK() #只能枚举一个参数的
            print(e)
            s = Solver()
            # if (str(e) != str(last_e)):
            action_temp = copy.deepcopy(action)
            if (str(action_temp).find("k") != -1):  # 改
                action_temp = eval(str(action_temp).replace("k", '('+str(e)+')'))
            if Game["type"] == "normal":
                s.add(Not(Implies(And(cover, Game["Constraint"]), And(action_temp["precondition"],
                ForAll(varListY, Implies(action_temp["transition_formula"], Not(winning_formula_Y)))))))
            else :
                s.add(Not(Implies(And(cover, Game["Constraint"],Not(Game["Terminal_Condition"])), And(action_temp["precondition"],
                ForAll(varListY, Implies(action_temp["transition_formula"], Not(winning_formula_Y)))))))  

            if (s.check() == unsat):
                winningStrategy.append(
                    [cover, action["action_name"]+"("+str(e)+")"])
                flagAct = True
                break
            else:
                num1 = 0
                num2 = 0
                m = s.model()  # model模型解
                pt = [m[X].as_long()]
                if(Game["var_num"] == 2):
                    pt = [m[X].as_long(),m[X1].as_long()]
                if Game["var_num"] ==3:
                    pt = [m[X].as_long(),m[X1].as_long(),m[X2].as_long()]
                if Game["var_num"] ==4:
                    pt = [m[X].as_long(),m[X1].as_long(),m[X2].as_long(),m[X3].as_long()]
                print("生成反例",pt)
                s_tem = Solver()
                s_tem.add(cover)
                s_tem.add(X == pt[0])
                if (Game["var_num"] == 2):
                    s_tem.add(X1 == pt[1])
                if (Game["var_num"] == 3):
                    s_tem.add(X1 == pt[1])
                    s_tem.add(X2 == pt[2])
                if (Game["var_num"] == 4):
                    s_tem.add(X1 == pt[1])
                    s_tem.add(X2 == pt[2])
                    s_tem.add(X3 == pt[3])
                print(s_tem.check())
                if(s_tem.check() != sat):
                    pt = generatePt(cover, pts, Game["Constraint"])
                result = findK(action["precondition"], action["transition_formula"], Game["Constraint"], pt)
                if result == "no suitable k":
                    print("794no suitable k")
                    break
            # else:
            #     print('two expresion equal')
            #     pt = generatePt(cover, pts, Game["Constraint"])
            #     result = findK(action["precondition"], action["transition_formula"], Game["Constraint"], pt)
            #     if result == "no suitable k":
            #         print("794no suitable k")
            #         break
            if pt not in pts:
                pts.append(pt)
                ptsGoal.append(result)
    if flagAct == False:
        flag_strategy = False
        break
winningStrategyTime = (time.time() - start_refine)
print(winningStrategy)
print("time use:",winningStrategyTime)
if flag_strategy:
    fp.write(str(winningStrategy)+"\t"+str(round(winningStrategyTime,2)))
else:
    fp.write("have cover not action")
Thread1.cancel()