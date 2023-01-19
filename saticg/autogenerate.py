from cgi import print_arguments
from fileinput import filename
import os


PDDLdirectory = r'domain\1.Sub\1.3S,D-MarkGame'  # 执行文件夹
gameType = 'normal'
allressult=[]
# for line in open(r"gameresult.io"):
#     line = line.replace('\n', '')
#     temp={}
#     temp['name']=line.split('\t')[0]
#     temp['formula']=line.split('\t')[1]
#     temp['type']=line.split('\t')[3]
#     allressult.append(temp)
# print(len(allressult))
gameCatagroy = PDDLdirectory.split('\\')[-1]  # 游戏类型
PDDLlist = os.listdir(PDDLdirectory)
PDDLlist = sorted(PDDLlist, key=lambda x: os.path.getmtime(
    os.path.join(PDDLdirectory, x)))
resultFile = '4-17output-'+gameCatagroy+gameType+".txt"  # 结果位置
# print(resultFile)
# resultFile = r"output-Sub-Td-imark-misere.txt" #结果位置
gamenotfound = []


for pddlfile in PDDLlist:
    if 'pddl' in pddlfile:
        # game_name = pddlfile.split('\\')[-1].split('.pddl')[0]
        # # print(game_name)
        # for game in allressult:
        #     # print(game['name'])
        #     if game['name']==game_name and game['formula']=='not_found' and game['type']==gameType:
        #         pddlfile=PDDLdirectory+'\\'+pddlfile
        #         print(pddlfile)
        #         os.system("python main.py %s %s %s"%(pddlfile,resultFile,gameType))
        # print(filename_result)
   
        # else:
        #     continue
          
            # pddlfile=PDDLdirectory+'\\'+pddlfile
            # print(pddlfile)
            # os.system("python main.py %s %s %s"%(pddlfile,resultFile,gameType))
        
    
#         # print(filename_result)
#         if (filename_result  in resultList):
#             print(filename_result)
            # gamenotfound.append(filename_result)

        # number_ofparas=pddlfile.split('(')[-1].split(')')[0].split(',').__len__()
        # if number_ofparas<=3:
        #     pddlfile=PDDLdirectory+'\\'+pddlfile
        #     print(pddlfile)
        #     os.system("python main.py %s %s %s"%(pddlfile,resultFile,gameType))

        pddlfile=PDDLdirectory+'\\'+pddlfile
        print(pddlfile)
        os.system("python main.py %s %s %s"%(pddlfile,resultFile,gameType))


