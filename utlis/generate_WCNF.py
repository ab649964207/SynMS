import os
import time
import numpy


def FeatureCheck(numset, featurespool):
    stateAndFeaturesMap = numpy.zeros((len(numset), len(featurespool)), dtype=int)
    for i in range(0, len(numset)):
        for j in range(0, len(featurespool)):
            if (type(numset[0]) == type(1)):
                X = numset[i]
                if (eval(featurespool[j])):
                    stateAndFeaturesMap[i][j] = 1
            elif (len(numset[0]) == 2):
                X = numset[i][0]
                X1 = numset[i][1]
                if (eval(featurespool[j])):
                    stateAndFeaturesMap[i][j] = 1
            elif (len(numset[0]) == 3):
                X = numset[i][0]
                X1 = numset[i][1]
                X2 = numset[i][2]
                if (eval(featurespool[j])):
                    stateAndFeaturesMap[i][j] = 1
    return stateAndFeaturesMap


def genetate_formula_wcnf(winSet, loseSet, featurespool):
    print('winSet',winSet)
    if(len(winSet)==0):
        return '',''
    if(len(featurespool)>11000):
        return 'timeout','timeout'
    fileName=str(time.time())[-7:-1]+'.wcnf'
    t1 = time.time()
    winfeatures = FeatureCheck(winSet, featurespool)
    losingfeatures = FeatureCheck(loseSet, featurespool)
    top_of_wcnf = str(len(featurespool) + 2)

    f = open(fileName, 'w')

    f.write('p wcnf ' + str(len(featurespool)) + ' ' + str(
       len(winSet) * len(loseSet) + len(featurespool)) + ' ' + top_of_wcnf + '\n')
    # f.write('p wcnf ' + str(len(featurespool)) + ' ' + str(
    #     len(winSet) * len(loseSet)) + ' ' + top_of_wcnf + '\n')
    strTemp = ''
    t2 = time.time()

    for i in range(0, len(featurespool)):
       strTemp += '1 -' + str(i + 1) + ' 0\n'
    f.write(strTemp)
    t3 = time.time()

    strTemp = ''
    for i in range(0, len(winSet)):
        for j in range(0, len(loseSet)):
            strTemp += top_of_wcnf + ' '
            for k in range(0, len(featurespool)):
                if (winfeatures[i][k] != losingfeatures[j][k]):
                    strTemp += str(k + 1) + ' '
            strTemp += '0\n'
    t4 = time.time()

    f.write(strTemp)
   

    f.close()
    cutOffTime='0.6'
    if(len(featurespool))>150:
        cutOffTime='3'
    t5 = time.time()
    print('生成wcnf文件耗时',str(t5-t1))
    main = "nuwls-un.exe   "+fileName+" 1 -cutoff "+cutOffTime

    f = os.popen(main)

    data = f.readlines()
    selectFeatures=[]
    for i in data:
        if (i[0] == 'v'):
            temp = i.split(' ')[1]
            for j in range(0,len(temp)):
                # if (item[0] != '-' and item[0] != 'v'):
                #     selectFeatures.append(int(item)-1)
                if (temp[j] == '1'):
                    selectFeatures.append(j)
                    print('选择特征',featurespool[j])
    os.remove(fileName)
    return generateExpression2(selectFeatures,winfeatures,losingfeatures,featurespool)


def generateExpression2(selectFeatures,winfeatures,losefeatures,featurespool):
    print(selectFeatures)
    if(len(selectFeatures)==0):
        return '',''
    tempset = []
    losetempset = []
    lenwinset=len(winfeatures)
    lenloseset=len(losefeatures)
    
    for i in range(0, lenwinset):
        temp=[]
        for j in selectFeatures:
            temp.append(winfeatures[i][j])
        if (temp not in tempset):
            tempset.append(temp)
    for i in range(0, lenloseset):
        temp=[]
        for j in selectFeatures:
            temp.append(losefeatures[i][j])
        if (temp not in losetempset):
            losetempset.append(temp)

    winningFormula='Or('
    for i in range(0, len(tempset)):
        tempStr=''
        for j in range(0,len(tempset[i])):
            if (tempset[i][j] == 1):
                tempStr = tempStr + featurespool[selectFeatures[j]] + ('' if  j==len(tempset[i])-1 else ',')
            else:
                tempStr = tempStr + 'Not(' + featurespool[selectFeatures[j]] +  (')' if  j==len(tempset[i])-1 else '),')
        tempStr='And('+tempStr+ (')' if i==len(tempset)-1 else '),')
        winningFormula=winningFormula+tempStr
    winningFormula=winningFormula+')'
    print(winningFormula)
    losingFormula='Or('
    for i in range(0, len(losetempset)):
        tempStr=''
        for j in range(0,len(losetempset[i])):
            if (losetempset[i][j] == 1):
                tempStr = tempStr + featurespool[selectFeatures[j]] + ('' if  j==len(losetempset[i])-1 else ',')
            else:
                tempStr = tempStr + 'Not(' + featurespool[selectFeatures[j]] +  (')' if  j==len(losetempset[i])-1 else '),')
        tempStr='And('+tempStr+ (')' if i==len(losetempset)-1 else '),')
        losingFormula=losingFormula+tempStr
    losingFormula=losingFormula+')'
    print(losingFormula)
    return winningFormula, losingFormula
    


winSet = [2, 3, 5, 6, 9, 10, 12, 13, 16, 17, 19, 20, 23, 24, 26, 27, 30, 31, 33, 34, 37, 38, 40, 41, 44, 45, 47, 48, 51,
          52, 54, 55, 58, 59]
loseSet = [0, 1, 4, 7, 8, 11, 14, 15, 18, 21, 22, 25, 28, 29, 32, 35, 36, 39, 42, 43, 46, 49, 50, 53, 56, 57]
featurespool = ['X%2==0', 'X%2==1', 'X%3==0', 'X%3==1', 'X%3==2', 'X%4==0', 'X%4==1', 'X%4==2', 'X%4==3', 'X%5==0',
                'X%5==1', 'X%5==2', 'X%5==3', 'X%5==4', 'X%6==0', 'X%6==1', 'X%6==2', 'X%6==3', 'X%6==4', 'X%6==5',
                'X%7==0', 'X%7==1', 'X%7==2', 'X%7==3', 'X%7==4', 'X%7==5', 'X%7==6', 'X%8==0', 'X%8==1', 'X%8==2',
                'X%8==3', 'X%8==4', 'X%8==5', 'X%8==6', 'X%8==7', 'X%9==0', 'X%9==1', 'X%9==2', 'X%9==3', 'X%9==4',
                'X%9==5', 'X%9==6', 'X%9==7', 'X%9==8', 'X%10==0', 'X%10==1', 'X%10==2', 'X%10==3', 'X%10==4',
                'X%10==5', 'X%10==6', 'X%10==7', 'X%10==8', 'X%10==9', 'X%11==0', 'X%11==1', 'X%11==2', 'X%11==3',
                'X%11==4', 'X%11==5', 'X%11==6', 'X%11==7', 'X%11==8', 'X%11==9', 'X%11==10', 'X%12==0', 'X%12==1',
                'X%12==2', 'X%12==3', 'X%12==4', 'X%12==5', 'X%12==6', 'X%12==7', 'X%12==8', 'X%12==9', 'X%12==10',
                'X%12==11', 'X%13==0', 'X%13==1', 'X%13==2', 'X%13==3', 'X%13==4', 'X%13==5', 'X%13==6', 'X%13==7',
                'X%13==8', 'X%13==9', 'X%13==10', 'X%13==11', 'X%13==12', 'X%14==0', 'X%14==1', 'X%14==2', 'X%14==3',
                'X%14==4', 'X%14==5', 'X%14==6', 'X%14==7', 'X%14==8', 'X%14==9', 'X%14==10', 'X%14==11', 'X%14==12',
                'X%14==13', 'X%15==0', 'X%15==1', 'X%15==2', 'X%15==3', 'X%15==4', 'X%15==5', 'X%15==6', 'X%15==7',
                'X%15==8', 'X%15==9', 'X%15==10', 'X%15==11', 'X%15==12', 'X%15==13', 'X%15==14', 'X%16==0', 'X%16==1',
                'X%17==0', 'X%17==1', 'X%18==0', 'X%18==1', 'X%19==0', 'X%19==1', 'X%20==0', 'X%20==1', 'X%21==0',
                'X%21==1', 'X%22==0', 'X%23==0', 'X%23==1', 'X%24==0', 'X%24==1', 'X%25==0', 'X%25==1', 'X%26==0',
                'X%26==1', 'X%27==0', 'X%27==1', 'X%28==0', 'X%28==1', 'X%29==0', 'X%29==1', 'X%30==0', 'X%30==1',
                'X%31==0', 'X%31==1', 'X==0', 'X==1', 'X==2', 'X==3', 'X==4', 'X==5', 'X==6', 'X==7', 'X==8', 'X==9',
                'X==10', 'X==11', 'X==12', 'X==13', 'X==14', 'X==15', 'X==16', 'X==17', 'X==18', 'X==19', 'X==20',
                'X==21', 'X==22', 'X==23', 'X>0', 'X>1', 'X>2', 'X>3', 'X>4', 'X>5', 'X>6', 'X>7', 'X>8', 'X>9', 'X>10',
                'X>11', 'X>12', 'X>13', 'X>14', 'X>15', 'X>16', 'X>17', 'X>18', 'X>19', 'X>20', 'X>21', 'X>22', 'X>23',
                'X>24', 'X>25', 'X>26', 'X>27', 'X>28', 'X>29', 'X>30', 'X>31', 'X>32', 'X>33', 'X>34', 'X>35', 'X>36',
                'X>37', 'X>38', 'X>39', 'X>40', 'X>41', 'X>42', 'X>43', 'X>44', 'X>45', 'X>46', 'X>47', 'X>48', 'X>49',
                'X>40', 'X>41', 'X>42', 'X>43', 'X>44', 'X>45', 'X>46', 'X>47', 'X>48', 'X>49', 'X>50', 'X>51', 'X>52',
                'X>53', 'X>54', 'X>55', 'X>56', 'X>57', 'X>58', 'X>59', 'X>60', 'X>61', 'X>62', 'X>63', 'X>64', 'X>65',
                'X>66', 'X>67', 'X>68', 'X>69', 'X>70', 'X>71', 'X>72', 'X>73', 'X>74', 'X>75', 'X>76', 'X>77', 'X>78',
                'X>79', 'X>80', 'X>81', 'X>82', 'X>83', 'X>84', 'X>85', 'X>86', 'X>87', 'X>88', 'X>89', 'X>90', 'X>91',
                'X>92', 'X>93', 'X>94', 'X>95', 'X>96', 'X>97', 'X>98', 'X>99']


# genetate_formula_wcnf(winSet, loseSet, featurespool)




# [[0, 0, 0, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]
# [[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0]]