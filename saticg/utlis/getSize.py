import re
from xlrd import open_workbook
from xlutils.copy import copy as xlutcopy
def Size(expression,varpool=[0,1]):
    count1=0
    str1=expression.replace(' ','').replace('\n','')
    while str1.find('Not')>=0 :
        count1+=1
        str1=str1.replace('Not','',1)
    while str1.find('Or')>=0 :
        count1+=1
        str1=str1.replace('Or','',1)
    while str1.find('And')>=0 :
        count1+=1
        str1=str1.replace('And','',1)
    str1=str1.replace('*','-').replace(',','-').replace('+','-').replace('<=','-').replace('>=','-').replace('<','-').replace('>','-').replace('==','-').replace('%','-').replace('(','').replace(')','')
    while True:
        if len(str1)==0:
            break
        if len(str1)==1:
            count1+=countSize(str1,varpool)
            break
        if len(str1)==2 and is_number(str1[0]):
            count1+=countSize(str1,varpool)
            break
        if len(str1)==2:
            count1+=countSize(str1,varpool)
            break
        tempvar=str1[0:str1.find('-')]
        # print(tempvar,'size is',countSize(tempvar,varpool))
        # print(count1)
        count1+=countSize(str1[0:str1.find('-')],varpool)
        str1=str1[str1.find('-')+1:len(str1)]
    return count1

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

def countSize(var,varpool):
    if is_number(var):
        var=float(var)
    if type(var) != type(1.0):
        return 1
    elif var in varpool:
        return 1
    else:
        return 1+countSize(var,expandpool(varpool))
def expandpool(varpool):
    p=[]
    for i in varpool:
        p.append(i)
    # while i < len(varpool):
    i=0
    j=0

    while i < len(varpool):
 
        while j < len(varpool):
   
            if varpool[i]+varpool[j] not in p:
                p.append(varpool[i]+varpool[j])
            j+=1
        i+=1
        j=i
    # print(p)
    return p   


def Getvarpool(pddl):
    num=re.findall('\d+',pddl)
    num = list(set(num))
    num = list(map(int,num))
    if not(0 in num):
        num.append(0)
    if not(1 in num):
        num.append(1)
    if not(2 in num):
        num.append(2)
    return num



def GetSize(gamename,winningformula):
    varpool=Getvarpool(gamename)
    size=Size(winningformula,varpool)
    return size
File='size.xls'
wb = open_workbook(File, encoding_override='utf-8')
new_workbook = xlutcopy(wb) 
new_worksheet = new_workbook.get_sheet(0)
sheet1 = wb.sheet_by_index(0)
row = sheet1.nrows
for i in range(0,row):

    
    new_worksheet.write(i,3,str(GetSize(sheet1.cell_value(i,0),sheet1.cell_value(i,1))))
new_workbook.save(File)