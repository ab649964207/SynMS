


from subfile.PDDLGrammarLexer import PDDLGrammarLexer
from subfile.PDDLGrammarParser import PDDLGrammarParser
from subfile.MyVisitor import Item, MyVisitor
from subfile.MyVisitor import game
from subfile.opera import *

from antlr4 import *
from z3 import *



# pddlFile =sys.argv[1] #由文件main.py输入路径
# resultFile =sys.argv[2]
# game_type = sys.argv[3]


X = Int('X')
X1 = Int('X1')
X2 = Int('X2')
Y = Int('Y')
Y1 = Int('Y1')
Y2 = Int("Y2")

k = Int('k')
l = Int('l')
(k1, k2, k3) = Ints('k1 k2 k3')


class GameClass:
    Game=[]
    global_transition_formula=''
    position=[]
    TerminatePosition=[]
    winSet=[]
    loseSet=[]
    NotConstraint=[]
    frequency=1
 

    def __init__(self, pddlFile, game_type,frequency):
        self.frequency=frequency
        self.Game= self.getGameinformation(pddlFile,game_type)
        self.NotConstraint=str(self.Game['Constraint']).replace('And','').replace('(','').replace(')','').replace(' ','').replace('X2','k').replace('X1','j').replace('X','i').replace('<=','>').replace('>=','<').replace('!=','==').split(',')
        self.global_transition_formula=self.getTransitionFormula(self.Game)
        self.position=self.getPosition(self.Game)
        self.TerminatePosition=self.GetTeminataposition(self.Game,self.position)

        [self.winSet,self.loseSet]=self.generateWinSetandLoseSet()

        

    def getPosition(self,Game):
        position = []
        if Game['var_num'] == 1:
            for i in range(0, 1000):
                position.append('illegal')
        elif Game['var_num'] == 2:
            for i in range(0, 200):
                position.append([])
                for j in range(0, 200):
                    position[i].append('illegal')
        elif Game['var_num'] == 3:
            for i in range(0, 200):
                position.append([])
                for i1 in range(0, 200):
                    position[i].append([])
                    for i2 in range(0, 200):
                        position[i][i1].append("illegal")
        return position
    def getGameinformation(self,pddlFile,game_type):
        X = Int('X')
        X1 = Int('X1')
        X2 = Int('X2')
        Y = Int('Y')
        Y1 = Int('Y1')
        Y2 = Int("Y2")
        k = Int('k')
        l = Int('l')
        (k1, k2, k3) = Ints('k1 k2 k3')
        input_stream = FileStream(pddlFile)
        lexer = PDDLGrammarLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = PDDLGrammarParser(token_stream)
        tree = parser.domain()
        visitor = MyVisitor()
        visitor.visit(tree)

        Terminal_Condition = eval(str(game.tercondition).replace(
            'v1', 'X').replace('v2', 'X1').replace('v3', 'X2'))
        Constarint = eval(str(game.constraint).replace(
            'v1', 'X').replace('v2', 'X1').replace('v3', 'X2'))
        varList = []
        for i in game.var_list:
            i = str(i).replace('v1', 'X').replace('v2', 'X1').replace('v3', 'X2')
            varList.append(eval(i))
        actions = []


        for i in game.action_list:
            one = {"action_name": i[0],
                "action_parameter": i[1],
                "precondition": eval(str(i[2]).replace('v1', 'X').replace('v2', 'X1').replace('v3', 'X2')),
                "transition_formula": eval(str(i[3]).replace('v1\'', 'Y').replace('v2\'', 'Y1').replace('v3\'', 'Y2').replace('v3', 'X2').replace('v1', 'X').replace('v2', 'X1'))}
            actions.append(one)

        Game = {"Terminal_Condition": Terminal_Condition,
                "varList": varList,
                "actions": actions,
                "Constraint": Constarint,
                "var_num": game.objectsCount,
                "type": game_type,
                "appeal_constants": game.constantList}

        print("Var List:",varList)
        varListY = eval(str(varList).replace('X2','Y2').replace('X1','Y1').replace('X','Y'))
        print("Var Y list",varListY)
        Game['varListY']=varListY

        return Game
    def getTransitionFormula(self,Game):
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
        return global_transition_formula
    def GetTeminataposition(self,Game,position):
        TerminatePosition=[]
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
        print("All terminate position:\n\t", TerminatePosition)
        return TerminatePosition

    def isLossingState(self,*v):
        position=self.position
        global_transition_formula=self.global_transition_formula
        Game=self.Game
       
        # print("verify",v,"is lose or win:")
        if len(v) == 1:
            if v[0]>=1000:
                return 'illegal'
            else:
                for i in v:  # default position < 100
                    if i >= 1000:
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
                        position[i[0]] = self.isLossingState(i[0])
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
                        # print(temp)
                        # print(s.check())
                        if (s.check() == sat):
                            m = s.model()
                            temp.append([m[Y].as_long(), m[Y1].as_long()])  # 全局转移解
                        else:
                            break
                    is_losing = True
                    s = Solver()
                    s.add(Game["Constraint"])
                    s.add(X == x, X1 == y)
                    if(s.check() == unsat):
                        continue
                    for i in temp:
                        if(position[i[0]][i[1]] == 'illegal'):
                            position[i[0]][i[1]] = self.isLossingState(i[0], i[1])

                    for i in temp:
                        is_losing = is_losing and not position[i[0]][i[1]]
                    if (is_losing):
                        position[x][y] = True
                    else:
                        position[x][y] = False

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
                            # print(temp)
                            # print(s.check())
                            if s.check() == sat:
                                m = s.model()
                                temp.append(
                                    [m[Y].as_long(), m[Y1].as_long(), m[Y2].as_long()])  # 全局转移解
                            else:
                                break
                            
                        is_losing = True
                        s = Solver()
                        s.add(Game["Constraint"])
                        s.add(X == x, X1 == y, X2 == z)
                        if(s.check() == unsat):
                            continue
                        for i in temp:
                            if(position[i[0]][i[1]][i[2]] == 'illegal'):
                  
                                position[i[0]][i[1]][i[2]] = self.isLossingState(i[0], i[1], i[2])
             
                        for i in temp:
                            is_losing = is_losing and not position[i[0]][i[1]][i[2]]
                            # if(position[i[0]][i[1]][i[2]]==True):
                            #     if([i[0],i[1],i[2]] not in self.loseSet):
                            #         self.loseSet.append([i[0],i[1],i[2]])
                            # if(position[i[0]][i[1]][i[2]]==False):
                            #     if([i[0],i[1],i[2]] not in self.winSet):
                            #         self.winSet.append([i[0],i[1],i[2]])
                  
                                
                        if (is_losing):
                            

                            position[x][y][z] = True
                            # print('''%s,%s,%s'''%(x,y,z),self.position[x][y][z])
                        else:
                            position[x][y][z] = False
                            # print('''%s,%s,%s'''%(x,y,z),self.position[x][y][z])
            
            # print('''%s,%s,%s'''%(x,y,z),self.position[x][y][z])
            for i in range(0,10):
                for j in range(0,10):
                    for k in range(0,10):
                        if(position[i][j][k]==True):
                            if([i,j,k] not in self.loseSet):
                                self.loseSet.append([i,j,k])
                        if(position[i][j][k]==False):
                            if([i,j,k] not in self.winSet):
                                self.winSet.append([i,j,k])
  
            return position[v[0]][v[1]][v[2]]
    def isIllegalState(self,*v):
        if len(v)==1:
            i=v[0]
            for expression in self.NotConstraint:
                if(eval(expression)):
                    return True
            return False
        if len(v)==2:
            i=v[0]  
            j=v[1]
            for expression in self.NotConstraint:
                if(eval(expression)):
                    return True
            return False    
        if len(v)==3:
            i=v[0]  
            j=v[1]
            k=v[2]
            for expression in self.NotConstraint:
                if(eval(expression)):
                    return True
            return False 
    def isIllegalState(self,*v):
        if len(v)==1:
            i=v[0]
            for expression in self.NotConstraint:
                if(eval(expression)):
                    return True
            return False
        if len(v)==2:
            i=v[0]  
            j=v[1]
            for expression in self.NotConstraint:
                if(eval(expression)):
                    return True
            return False    
        if len(v)==3:
            i=v[0]  
            j=v[1]
            k=v[2]
            for expression in self.NotConstraint:
                if(eval(expression)):
                    return True
            return False 
    def generateWinSetandLoseSet(self):
        Game=self.Game
        TerminatePosition=self.TerminatePosition
        loseSet=[]
        winSet=[]
        if Game['var_num'] == 1:
            if(self.frequency==1):
                max=35
            if(self.frequency==2):
                max=60
            if(self.frequency==3):
                max=100
            for i in range(0,max):
                if(self.isIllegalState(i)):
                    continue
                if ([i] in TerminatePosition and Game["type"] == "normal"):
                        loseSet.append(i)
                        continue
                if ([i] in TerminatePosition and Game["type"] == "misere"):
                        winSet.append(i)
                        continue
                if (self.isLossingState(i)):
                    loseSet.append(i)
                else:
                    winSet.append(i)
        if Game['var_num'] == 2:
            if(self.frequency==1):
                max=30
            if(self.frequency==2):
                max=35
            if(self.frequency==3):
                max=15
            print('teminate',TerminatePosition)
            
            for i in range(0,100):
                if(len(loseSet)+len(winSet)>=max):
                    break
                for j in range(0,10):
                    if(self.isIllegalState(i,j)):
                        continue
                    if ([i,j] in TerminatePosition and Game["type"] == "normal"):
                        loseSet.append([i,j])
                        continue
                    if ([i,j] in TerminatePosition and Game["type"] == "misere"):
                        winSet.append([i,j])
                        continue
                    if (self.isLossingState(i,j)):
                        loseSet.append([i,j])
                        if(len(loseSet)+len(winSet)>=max):
                            break
                    else:
                        winSet.append([i,j])
                        if(len(loseSet)+len(winSet)>=max):
                            break
        if Game['var_num'] == 3:
            if(self.frequency==1):
                max=5
            if(self.frequency==2):
                max=60
            if(self.frequency==3):
                max=30
            print('teminate',TerminatePosition)
            for i in range(0,5):
                for j in range(0,5):
                    for k in range(0,5):
                        if(self.isIllegalState(i,j,k)):
                            continue
                        if ([i,j,k] in TerminatePosition):
                            loseSet.append([i,j,k])
                            continue
                        if ([i,j,k]  in TerminatePosition and Game["type"] == "normal"):
                            loseSet.append([i,j,k] )
                            if(len(loseSet)+len(winSet)>=max):
                                break
                            continue
                        if ([i,j,k]  in TerminatePosition and Game["type"] == "misere"):
                            winSet.append([i,j,k] )
                            if(len(loseSet)+len(winSet)>=max):
                                break
                            continue
                     
                        if (self.isLossingState(i,j,k)):
                            loseSet.append([i,j,k])
                            if(len(loseSet)+len(winSet)>=max):
                                break
                        else:
                            winSet.append([i,j,k])
        return [winSet,loseSet]

    def generateActionWorkMap(self):
        X = Int('X')
        X1 = Int('X1')
        X2 = Int('X2')
        Y = Int('Y')
        Y1 = Int('Y1')
        Y2 = Int("Y2")
        k = Int('k')
        l = Int('l')
        workMap=[]
        print('win',self.winSet)
        print('lose',self.Game["actions"])
        if self.Game['var_num'] == 1:
            for actoin in self.Game["actions"]:
                # workMap.append({actoin:{}})
                
                actoinParams=[]
                # 动作参数为1的情况
                while(True):
                    s = Solver()
                    s.add(actoin["precondition"])
                    s.add(self.Game["Constraint"])
                    s.add(X<60)
                    for params in actoinParams:
                        s.add(Or(k!=params))
                    if(s.check() == sat):
                        m = s.model()
                        print(m)
                        actoinParams.append(m[k].as_long())
                    else:
                        break
                actoinParams.append(X)
                for param in actoinParams:
                    workMap.append(
                        {
                            "actionName":actoin["action_name"],
                            "actionParam":param,
                            "workSet":[],
                            "notWorkSet":[],
                            "Valid":True
                        }
                    )
                for state in self.winSet:
                    for param in actoinParams:
                        # print("验证动作","动作名称",actoin["action_name"],"参数",param,"当前状态点:",state)
                        s = Solver()
                        s.add(X==state)
                        s.add(k==param)
                        s.add(actoin["transition_formula"])
                        s.add(self.Game["Constraint"])
                        if(s.check() == sat):
                            m = s.model()
                            # print(m[Y].as_long())
                            # print("验证Work(s,a)->",'s=',state,'a=',actoin["action_name"],param)
                            if(self.isLossingState(m[Y].as_long())):
                                # print("在",state,"执行完",actoin["action_name"],param,'到达必败点',"work为True")
                                for actionMap in workMap:
                                    if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                        actionMap["workSet"].append(state)
                            else:   
                                # print("在",state,"执行完",actoin["action_name"],param,'到达必胜点',"work为False")
                                for actionMap in workMap:
                                    if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                        actionMap["notWorkSet"].append(state)
                        else:
                            for actionMap in workMap:
                                if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                    actionMap["notWorkSet"].append(state)
                for actionMap in workMap:
                    actionMap["notWorkSet"]=actionMap["notWorkSet"]+self.loseSet
            return workMap
        

        if self.Game['var_num'] == 2:
            for actoin in self.Game["actions"]:
                # workMap.append({actoin:{}})
                print(actoin)

                actoinParams=[]
                # 动作参数为1的情况
                if(len(actoin['action_parameter'])==1):
                    while(True):
                        print()
                        s = Solver()
                        s.add(actoin["precondition"])
                        s.add(self.Game["Constraint"])
                        s.add(X<10)
                        s.add(Y<10)
                        s.add(X1<10)
                        s.add(Y1<10)
                        for params in actoinParams:
                            s.add(Or(k!=params))
                        if(s.check() == sat):
                            m = s.model()
                            print(m)
                            actoinParams.append(m[k].as_long())
                        else:
                            break
                    actoinParams.append(X1 - X)
                    actoinParams.append(X - X1)
                if(len(actoin['action_parameter'])==2):
                    while(True):
                        print()
                        s = Solver()
                        s.add(actoin["precondition"])
                        s.add(self.Game["Constraint"])
                        s.add(X<10)
                        s.add(Y<10)
                        s.add(X1<10)
                        s.add(Y1<10)
                        for params in actoinParams:
                            s.add(Not(And(k==params[0],l==params[1])))
                        if(s.check() == sat):
                            m = s.model()
                            print(m)
                            actoinParams.append([m[k].as_long(),m[l].as_long()])
                        else:
                            break
                for param in actoinParams:
                    workMap.append(
                        {
                            "actionName":actoin["action_name"],
                            "actionParam":param,
                            "workSet":[],
                            "notWorkSet":[],
                            "Valid":True
                        }
                    )
                print(workMap)
                for state in self.winSet:
                    for param in actoinParams:
                        # print("验证动作","动作名称",actoin["action_name"],"参数",param,"当前状态点:",state)
                        s = Solver()
                        s.add(X==state[0])
                        s.add(X1==state[1])
                        if(len(actoin['action_parameter'])==1):
                            s.add(k==param)
                        if(len(actoin['action_parameter'])==2):
                            s.add(k==param[0])
                            s.add(l==param[1])
                        s.add(actoin["transition_formula"])
                        s.add(self.Game["Constraint"])
                        if(s.check() == sat):
                            m = s.model()
                            # print(m[Y].as_long())
                            print("验证Work(s,a)->",'s=',state,'a=',actoin["action_name"],param)
                            if(self.isLossingState(m[Y].as_long(),m[Y1].as_long())):
                                # print("在",state,"执行完",actoin["action_name"],param,'到达必败点',"work为True")
                                for actionMap in workMap:
                                    if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                        actionMap["workSet"].append(state)
                            else:   
                                # print("在",state,"执行完",actoin["action_name"],param,'到达必胜点',"work为False")
                                for actionMap in workMap:
                                    if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                        actionMap["notWorkSet"].append(state)
                        else:
                            for actionMap in workMap:
                                if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                    actionMap["notWorkSet"].append(state)
                        
                for actionMap in workMap:
                    actionMap["notWorkSet"]=actionMap["notWorkSet"]+self.loseSet
            return workMap

        if self.Game['var_num'] == 3:
                for actoin in self.Game["actions"]:
                    # workMap.append({actoin:{}})
                    
                    actoinParams=[]
                    # 动作参数为1的情况
                    while(True):
                        print()
                        s = Solver()
                        s.add(actoin["precondition"])
                        s.add(self.Game["Constraint"])
                        s.add(X<10)
                        s.add(X1<10)
                        s.add(X2<10)
                        s.add(Y<10)
                        s.add(Y1<10)
                        s.add(Y2<10)
                        for params in actoinParams:
                            s.add(Or(k!=params))
                        if(s.check() == sat):
                            m = s.model()
                            print(m)
                            actoinParams.append(m[k].as_long())
                        else:
                            break
                    actoinParams.append(X)
                    actoinParams.append(X1)
                    actoinParams.append(X2)
                    actoinParams.append(X - X1)
                    actoinParams.append(X - X2)
                    actoinParams.append(X1 - X2)
                    #TODO 添加semiground_action
                    for param in actoinParams:
                        workMap.append(
                            {
                                "actionName":actoin["action_name"],
                                "actionParam":param,
                                "workSet":[],
                                "notWorkSet":[],
                                "Valid":True
                            }
                        )
                    print(workMap)
                    for state in self.winSet:
                        for param in actoinParams:
                            # print("验证动作","动作名称",actoin["action_name"],"参数",param,"当前状态点:",state)
                            s = Solver()
                            s.add(X==state[0])
                            s.add(X1==state[1])
                            s.add(X2==state[2])
                            s.add(k==param)
                            s.add(actoin["transition_formula"])
                            s.add(self.Game["Constraint"])
                            if(s.check() == sat):
                                m = s.model()
                                # print(m[Y].as_long())
                                print("验证Work(s,a)->",'s=',state,'a=',actoin["action_name"],param)
                                if(self.isLossingState(m[Y].as_long(),m[Y1].as_long(),m[Y2].as_long())):
                                    # print("在",state,"执行完",actoin["action_name"],param,'到达必败点',"work为True")
                                    for actionMap in workMap:
                                        if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                            actionMap["workSet"].append(state)
                                else:   
                                    # print("在",state,"执行完",actoin["action_name"],param,'到达必胜点',"work为False")
                                    for actionMap in workMap:
                                        if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                            actionMap["notWorkSet"].append(state)
                            else:
                                for actionMap in workMap:
                                    if actionMap["actionName"]==actoin["action_name"] and actionMap["actionParam"]==param:
                                        actionMap["notWorkSet"].append(state)
                            
                    for actionMap in workMap:
                        actionMap["notWorkSet"]=actionMap["notWorkSet"]+self.loseSet
                return workMap
            