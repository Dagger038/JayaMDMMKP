# Filename:         generateRandomSolutions.py
# Author:           Dylan Gaspar
# Class:            GA
# Last Modified:    11/27/2016
# Purpose:          reads in MDMKP problems from local text files and 
#                   prints out the generated constraints and objective
#                   functions

import math
import xlrd
import xlwt
import random
import operator
from operator import itemgetter
import timeit

#'''
def classify(soln, objFunct, varsPerClass, varsNo):
    #sum=0
    count=0
    result=0
    #chunk=objFunct[startId:startId+10]
    for classIdx in range(int(varsNo/varsPerClass)):
        count=0
        indices=[]
        for offset in range(int(varsPerClass)):
            if soln[int(varsPerClass*classIdx)+offset] == 1:
                count+=1
                indices.append(int(varsPerClass*classIdx)+offset)
        chunk=objFunct[int(classIdx*varsPerClass):int(classIdx*varsPerClass)+varsPerClass]
        if count == 1:
            result = 1
        elif count == 0:
            soln[int(classIdx*varsPerClass)+chunk.index(max(chunk))]=1
        else:
            maxValue=0
            maxIndex=0
            '''
            for offset in range(int(varsPerClass)):
                if (int(varsPerClass*classIdx)+offset) in indices:
                    if objFunct[int(varsPerClass*classIdx)+offset] > max:
                        max = objFunct[int(varsPerClass*classIdx)+offset]
                        maxIndex = int(varsPerClass*classIdx)+offset
            '''
            for offset in range(int(varsPerClass)):
                soln[int(varsPerClass*classIdx)+offset]=0
            for index in indices:
                # print (objFunct[index])
                if int(objFunct[index])>int(maxValue):
                    maxValue = objFunct[index]
                    maxIndex = index
                soln[index] = 0
            soln[maxIndex] = 1
    '''
    for i in soln:
        if count>=startId and count<startId+10:
            sum+=i
        count+=1
        #sum+=soln(startId+i)
    
    if sum == 1:
        return 1
    elif sum == 0:
        soln[chunk.index(max(chunk))] = 1
        return 0
    else:
        listOfIndices=[]
        listOfPossibleVars=[]
        count=0
        for i in soln:
            if count>=startId and count<startId+10 and i==1:
                listOfIndices.append(count)
            count+=1
        for index in listOfIndices:
            listOfPossibleVars.append(soln[index])
    '''
#'''    
    
def sumproduct(list1, list2):
    sum=0
    length=len(list2)
    if len(list1)<len(list2):
        length=len(list1)
    for idx in range(int(length)):
        sum += int(list1[idx])*int(list2[idx])
        #print sum
    return sum
    

def violations(soln, constraints, constNo):
    violations=0
    count=0
    for constraint in constraints:
        #print sumproduct(soln, constraint)
        diff = sumproduct(soln, constraint) - int(constraint[len(constraint)-1])
        # if lhs > rhs and we are doing a <= constraint
        if diff > 0 and count < constNo:
            violations += abs(diff)
        # if lhs < rhs and we are doing a >= constraint
        elif diff < 0 and count >= constNo:
            violations += abs(diff)
        count+=1
    return violations
  
  
  
  
# determine if MDMMKP is infeasible by class constraints 
# restricting number of variables so much that demand 
# constraints can not possibly be met  
def infeasible(constraints, constNo, varsNo, varsPerClass):
    #count=0
    constIdx=0
    maxOfClass=0
    lhs=0
    rhs=0
    infeasible=False
    for constraint in constraints:
        #print constraint
        lhs=0
        if constIdx >= constNo:
            for count in range(int(varsNo)+1):
                if count < varsNo:
                    if count%varsPerClass == 0:
                        count = 0
                        lhs += int(maxOfClass)
                        maxOfClass = 0
                    if int(constraint[count]) > int(maxOfClass):
                        maxOfClass=int(constraint[count])
            if lhs < int(constraint[int(varsNo)]):
                #print "Infeasible"
                infeasible = True
            else:
                #print "Feasible"
                filler=True
        constIdx += 1
        #print "Not yet Infeasible"
    #print "Feasible"
    return infeasible
    
    
def merge(solutions, newSolns, varsNo, solnNo, solnToKeep):
    temp = [[None]*(int(varsNo)+2) for _ in range(len(solutions))]
    list=0
    for soln in solutions:
        index=0
        for var in soln:
            temp[list][index]=var
            #print temp[list]
            index+=1
        list+=1
            
    #print len(temp)
    for soln in newSolns:
        temp.append(soln)
    #print temp[-1]
    # sort the temp, first by violations, then obj funct 
    temp = sorted(temp, key=itemgetter(int(varsNo+1)), reverse=True)
    temp = sorted(temp, key=itemgetter(int(varsNo)))
    return temp[0:solnToKeep]
    
    

    
    
    
    
def main():
    '''
    excelName='mdmkp_ct1_1.xls'
    book = xlrd.open_workbook(excelName)
    '''
    
    start = timeit.default_timer()
    
    for probSet in [2,3,4,5,6,7,8,9]:
        for modJaya in [False]:
    
            filename='mdmkp_ct' + str(probSet) + '.txt'
            
            file = open(filename)
            
            varsNo=0
            constNo=0
            defsNo=int(file.readline())
            #defsNo=1
            # number of solutions to randomly generate
            solnNo=200
            solnToKeep=30
            varsPerClass=10
            # number of Jaya iterations
            jayaIterations=200 #100-200, 600
            # whether using Mod Jaya
            #modJaya=False
            gtConstNo=1
            #[[None]*5 for _ in range(5)]
            solutions=[[]]*solnNo
            
            
            # create excel book for this problem set
            book = xlwt.Workbook(encoding="utf-8")
            
            infeasibleNo=0
            
            # problem definition number for the excel name
            probNo=1
            
            # for each problem definition (6 different obj functs per definition),
            for definition in range(defsNo):
                
                # get the number of vars and constraints
                params = file.readline().split(' ')
                varsNo = int(params[0])
                constNo = int(params[1])
                
                
                # define list of <= and >= constraints and obj functs
                elConst = []
                egConst = []
                objFuncts = []
                
                # get the <= constraints
                for constraint in range(constNo):
                    const = file.readline().split(' ')
                    const.remove('\n')
                    elConst.append(const)
                # get the rhs vals in varsNo+1th position in each list
                elrhs = file.readline().split(' ')
                elrhs.remove('\n')
                index=0
                for rhs in elrhs:
                    elConst[index].append(rhs)
                    index+=1
                  
                # get the >= constraints
                for constraint in range(constNo):
                    const = file.readline().split(' ')
                    const.remove('\n')
                    egConst.append(const)
                # get the rhs vals in varsNo+1th position in each list
                egrhs = file.readline().split(' ')
                egrhs.remove('\n')
                index=0
                for rhs in egrhs:
                    egConst[index].append(int(rhs)/int(varsPerClass))
                    index+=1
                #for const in egConst: print const[len(const)-1]
                
                # get 6 obj functs
                for n in range(6):
                    funct = file.readline().split(' ')
                    funct.remove('\n')
                    objFuncts.append(funct)
                    
                
                
                #if(definition<10): continue # skip if working on first 10 definitions (60 probs)
                
                
                
                # write one sheet to the current excel book
                sheet = book.add_sheet("Sheet " + str(probNo))
                # sheet.write(row, col, value)
                    
                objFunctIdx=1
                for obj in objFuncts:
                
                    #define how many >= constraints are to be used
                    if objFunctIdx%3 == 1:
                        gtConstNo=1
                    elif objFunctIdx%3 == 2:
                        gtConstNo=int(constNo)/2
                    else:
                        gtConstNo=int(constNo)
                    
                    # randomly generated
                    solutions=[[None]*int(varsNo) for _ in range(int(solnNo))]
                    # made with Jaya
                    newSolns=[[None]*int(varsNo) for _ in range(int(solnToKeep))]
                    # combined solution
                    comboSolns=[[None]*int(varsNo) for _ in range(int(solnToKeep))]
                    constraints = []
                    
                    # add the <= constraints
                    for constraint in elConst:
                        constraints.append(constraint)
                    # add the >= constraints
                    for constIdx in range(int(gtConstNo)):
                        constraints.append(egConst[constIdx])
                        
                    #print constraints
                    
                    
                    
                    # generates random solutions
                    for soln in solutions:
                        #soln.append(random.randint(0,1))
                        for classIdx in range(int(varsNo/varsPerClass)):
                            # choose which var in each class gets used
                            theOne = random.randint(0,varsPerClass-1)
                            for j in range(int(varsPerClass)):
                                #print classIdx+j
                                if j == theOne:
                                    soln[(varsPerClass*classIdx)+j] = 1
                                else:
                                    soln[(varsPerClass*classIdx)+j] = 0
                        # appends violations, then objective function value
                        soln.append(violations(soln, constraints, constNo))
                        soln.append(sumproduct(soln, obj))
                    
                    # sort the solutions, first by violations, then obj funct 
                    solutions = sorted(solutions, key=itemgetter(int(varsNo+1)), reverse=True)
                    solutions = sorted(solutions, key=itemgetter(int(varsNo)))
                    
                    # take the best 30
                    # TODO: make sure the first 30 are unique
                    solutions = solutions[0:solnToKeep]
                    
                    
                    # testing for infeasibility between class and dewmand constraints
                    #if infeasible(constraints, constNo, varsNo, varsPerClass): infeasibleNo+=1
                    
                        
                    
                    
                    
                    # JAYA / MOD JAYA algorithm
                    bestSoln = solutions[0]
                    worstSoln = solutions[-1]
                    
                    # perform Jaya/Mod Jaya to create new solutions
                    for _ in range(jayaIterations):
                        #bestSoln = solutions[0]
                        #worstSoln = solutions[-1]
                        for i in range(len(solutions)):
                            for j in range(int(varsNo)):
                                r1 = random.randint(0,1)
                                r2 = random.randint(0,1)
                                
                                # TODO: need to update solutions list to use comboSolns after each iteration of Jaya
                                # DONE
                                currSolnVar = solutions[i][j]   
                                
                                newSolns[i][j] = currSolnVar + r1*(bestSoln[j]-currSolnVar) - r2*(worstSoln[j]-currSolnVar)
                                
                                # Binarization
                                if newSolns[i][j] <= 0:
                                    newSolns[i][j] = 0
                                else:
                                    newSolns[i][j] = 1
                            #print newSolns[i]
                            # make the newSolns obey class constraints
                            classify(newSolns[i], obj, varsPerClass, varsNo)
                            
                            # add violations and obj funct to each newSoln
                            if len(newSolns[i]) <= varsNo:
                                newSolns[i].append(violations(newSolns[i], constraints, constNo))
                                newSolns[i].append(sumproduct(newSolns[i], obj))
                            else:
                                newSolns[i][-2] = (violations(newSolns[i], constraints, constNo))
                                newSolns[i][-1] = (sumproduct(newSolns[i], obj))
                            
                            
                            #makeFeasible(newSolns[i])
                            
                            
                            if (not(modJaya)):
                                if newSolns[i][int(varsNo)] <= solutions[i][int(varsNo)] and newSolns[i][int(varsNo)+1] > solutions[i][int(varsNo)+1]:
                                    comboSolns[i] = newSolns[i]
                                    #print comboSolns[i]
                                else:
                                    comboSolns[i] = solutions[i]
                                    #print comboSolns[i]
                        #print comboSolns[0]
                        #print newSolns
                        
                        # sort the newSolns, first by violations, then obj funct 
                        newSolns = sorted(newSolns, key=itemgetter(int(varsNo+1)), reverse=True)
                        newSolns = sorted(newSolns, key=itemgetter(int(varsNo)))
                        newSolns = newSolns[0:solnToKeep]
                        
                        if modJaya:
                            comboSolns = merge(solutions, newSolns, varsNo, solnNo, solnToKeep)
                        
                        
                        # sort the comboSolns, first by violations, then obj funct 
                        comboSolns = sorted(comboSolns, key=itemgetter(int(varsNo+1)), reverse=True)
                        comboSolns = sorted(comboSolns, key=itemgetter(int(varsNo)))
                        comboSolns = comboSolns[0:solnToKeep]
                        
                        solutions = comboSolns
                        
                        
                        
                        # grab the best and worst of the new 30 comboSolns
                        bestSoln = comboSolns[0]
                        worstSoln = comboSolns[-1]
                        # end of Jaya iteration
                    
                    
                    for classIdx in range(int(int(varsNo)/int(varsPerClass))):
                        for var in range(int(varsPerClass)):
                            if(comboSolns[0][int(var + (classIdx*varsPerClass))] == 1):
                                #print int(var + (classIdx*varsPerClass))
                                sheet.write(objFunctIdx+5, classIdx+5, int(var + (classIdx*varsPerClass)))
                    sheet.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+1, comboSolns[0][-2])
                    sheet.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, comboSolns[0][-1])
                    
                    
                    
                    # needed for determining the number of >= constraints
                    # and which row to write into in each excel sheet
                    objFunctIdx+=1
                
                
                probNo+=1
            
            # used to keep track of spreadsheets for debugging algorithm
            debug="Debug_"+str(jayaIterations)+"itr"
            if(modJaya):
                book.save(filename[:-4] +debug+'_modJaya.xls')
            else:
                book.save(filename[:-4] +debug+'_Jaya.xls')
            print('Book Saved: ' + filename[:-4] +debug+'_Jaya.xls')
            
    # tracking runtime   
    stop = timeit.default_timer()
    print (stop - start)
    '''
    # number of solutions to randomly generate
    solnNo=100
    solnToKeep=30
    varsPerClass=10
    gtConstNo=1
    #[[None]*5 for _ in range(5)]
    solutions=[[]]*solnNo
    
    
    # for all the sheets in the excel file
    for name in book.sheet_names():
        # only on the first sheet (can delete later to do all sheets)
        if name.endswith('1'):
            sheet = book.sheet_by_name(name)
            varsNo = sheet.cell(1,4).value
            constNo = sheet.cell(2,4).value
            gtConstNo=int(constNo)
            objFunct = []
            solutions=[[None]*int(varsNo) for _ in range(int(solnNo))]
            constraints = [[None]*int(varsNo) for _ in range(int(constNo+gtConstNo))]
            for index in range(int(varsNo)):
                objFunct.append(int(sheet.cell(5,index+3).value))
                
            constIdx=0
            for constraint in constraints:
                varIdx=0
                for var in constraint:
                    #print sheet.cell(constIdx+7,varIdx+3).value
                    constraint[varIdx] = (int(sheet.cell(constIdx+7,varIdx+3).value))
                    varIdx+=1
                #print constraint
                #constraint.append(int(sheet.cell(constIdx+7,int(varsNo)+2+3).value))
                #print constraint
                constIdx+=1
            #print constraints
                
            constIdx=0
            for constraint in constraints:
                constraint.append(int(sheet.cell(constIdx+7,int(varsNo)+2+3).value))
                #print constraint
                constIdx+=1
            
            #print objFunct
            #print constraints[0]
            
            for soln in solutions:
                #soln.append(random.randint(0,1))
                for classIdx in range(int(varsNo/varsPerClass)):
                    # choose which var in each class gets used
                    theOne = random.randint(0,varsPerClass-1)
                    for j in range(int(varsPerClass)):
                        #print classIdx+j
                        if j == theOne:
                            soln[(varsPerClass*classIdx)+j] = 1
                        else:
                            soln[(varsPerClass*classIdx)+j] = 0
                    #classify(soln, objFunct, i*varsPerClass)
                #soln.append(violations())
            #print solutions[0]

            

            # after extensive testing, I have concluded that nested for 
            # loops and .append() do not work as expected with each other

            #print constraints
            #print solutions
            constVal=10000
            objFunctVal=10000
            count=0
            for soln in solutions:
                soln.append(violations(soln, constraints, constNo))
                soln.append(sumproduct(soln, objFunct))
                ''
                soln.append(constVal)
                soln.append(objFunctVal)
                if count%2 == 0:
                    constVal=constVal-100
                objFunctVal=objFunctVal-100
                count+=1
                ''
            #print constraints
            #print solutions[0:30]
            solutions = sorted(solutions, key=itemgetter(int(varsNo+1)), reverse=True)
            solutions = sorted(solutions, key=itemgetter(int(varsNo)))
            solutions = solutions[0:30]
            #print solutions[0:30]
            print infeasible(constraints, constNo, varsNo, varsPerClass)
    '''

        
if __name__ == '__main__':
	main()

