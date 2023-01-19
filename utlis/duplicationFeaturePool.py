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


def duplicationFeaturePool(featuresPool,winset,loseset):
    winfeatures = FeatureCheck(winset, featuresPool)
    losingfeatures = FeatureCheck(loseset, featuresPool)
    result=[]
    if(len(winset)==0):
        return result
    hashset = set()
    for k in range(0, len(featuresPool)):
        for i in range(0, len(winset)):
            for j in range(0, len(loseset)):
                if (winfeatures[i][k] != losingfeatures[j][k]):
                    if(featuresPool[k] not in hashset):
                        result.append(featuresPool[k])
                        hashset.add(featuresPool[k])
                    break
            else:
                
                continue
            break
    return result

