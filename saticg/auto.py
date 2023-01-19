import os
from func_timeout import func_set_timeout
import func_timeout

@func_set_timeout(500)
def main(pddlfile,resultFile,gameType):
    os.system("python SynMS.py %s %s %s"%(pddlfile,resultFile,gameType))


PDDLdirectory=r'domain\1.Sub\1.1Take-away' #执行文件夹
gameType='normal'
# resultFile = r"result\temp"+gameType+".txt" #结果位置c
resultFile = r"result.txt" #结果位置c

gameCatagroy=PDDLdirectory.split('\\')[-1] #游戏类型
PDDLlist = os.listdir(PDDLdirectory)
PDDLlist = sorted(PDDLlist,key=lambda x: os.path.getmtime(os.path.join(PDDLdirectory, x)))

for pddlfile in PDDLlist:
    if 'pddl' in pddlfile:
        
        pddlfile=PDDLdirectory+'\\'+pddlfile
        # print(pddlfile)
        try:
            main(pddlfile,resultFile,gameType)
        except func_timeout.exceptions.FunctionTimedOut:
            f = open(resultFile, 'a')
            f.write('\t'+str('time out')  + '\n')
            f.close()
            print ("timeout!")
        


