# Filename:         generateRandomSolutions.py
# Author:           Dylan Gaspar
# Class:            GA
# Last Modified:    02/15/2018
# Purpose:          reads in MDMKP problems from local text files and 
#                   prints out the generated constraints and objective
#                   functions

import math
import xlrd
import xlwt
import random
import operator
import copy
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
  
def violations2(soln, constraints, constNo, varsNo):
    violations=0
    count=0
    for constraint in constraints:
        diff = sumproduct(soln, constraint[0:varsNo]) - int(constraint[len(constraint)-1])
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
    
def NBHD(soln, obj, constraints, constNo, varsNo, varsPerClass):
    #'''
    modSoln = copy.deepcopy(soln)
    prevSoln = copy.deepcopy(soln)
    while(True):
        # NBHD Search on best solution from each Jaya iteration
        for classIdx in range(int(int(varsNo)/int(varsPerClass))):
            begin = classIdx * varsPerClass
            end = begin + varsPerClass
            classToCheck = [range(varsPerClass),obj[begin:end],modSoln[begin:end]]
            sortedClass = copy.deepcopy(classToCheck)
            
            # sort the class by best obj funct coefficients
            sorts = zip(*sorted(zip(classToCheck[1], classToCheck[0], classToCheck[2]),reverse=True)) # sort on classToCheck[1] 
            sortedClass = [list(sorts[1]), list(sorts[0]), list(sorts[2])]   # convert to list of lists in correct order of lists
                
            # go down obj funct coeff's for one class and try to make a 
            # lower or same violation soln with a higher obj funct value
            for var in range(int(varsPerClass)):
                if sortedClass[2][var] == 1:   
                    break
                else:
                    unsortedClass = copy.deepcopy(sortedClass)
                    unsortedClass[2] = [0 for i in range(varsPerClass)]
                    unsortedClass[2][var] = 1
                    
                    # unsort sortedClass
                    # sort the class by proper variable order
                    unsorted = zip(*sorted(zip(unsortedClass[0], unsortedClass[1], unsortedClass[2]))) # sort on unsortedClass[0] 
                    unsortedClass = [list(unsorted[0]), list(unsorted[1]), list(unsorted[2])]   # convert to list of lists
                        
                    newSoln = modSoln[0:begin] + unsortedClass[2] + modSoln[end:-2]
                    
                    #print(newSoln)
                    
                    newSoln.append(violations(newSoln, constraints, constNo))
                    newSoln.append(sumproduct(newSoln, obj))
                    if newSoln[-2] <= modSoln[-2]:              # if less or same violations,
                        if newSoln[-1] > modSoln[-1]:           # if better obj funct val,
                            modSoln = copy.deepcopy(newSoln)    # make it new soln to work with
                            break                               # and leave this class
                            
            
                            
        classify(modSoln, obj, varsPerClass, varsNo) # needed to ensure class constraints are obeyed
        
        if modSoln[-2] <= prevSoln[-2]:              # if less or same violations,
            if modSoln[-1] > prevSoln[-1]:           # if better obj funct val,
                prevSoln = copy.deepcopy(modSoln)    # make it new solution to try to improve upon
            else:                                    # otherwise, same violations and same or worse obj funct
                break                                # therefore, done searching 
                
    return copy.deepcopy(prevSoln)
    
    
def repair(soln, obj, constraints, constNo, varsNo, varsPerClass):
    repairing=soln
    count=0
    #print repairing[varsNo]
    while repairing[varsNo] > 0:
        lastRepair=copy.deepcopy(repairing)
        #print repairing[varsNo]
        lhsOrig=lhs(soln, constraints, varsNo)
        classesAnalysis=[]
        for classIdx in range(int(varsNo/varsPerClass)):
            classAnalysis=[]
            for offset in range(int(varsPerClass)):
                if repairing[int(varsPerClass*classIdx)+offset] == 1:
                    #print "HERE"
                    index=int(varsPerClass*classIdx)+offset
                    coeffs=[]
                    itx=0
                    lhsDrop=copy.deepcopy(lhsOrig)
                    for const in constraints:
                        coeffs.append(const[index])
                        lhsDrop[itx]=lhsDrop[itx]-int(const[index])
                        itx+=1
                    classAnalysis.append([index,coeffs,repairing[varsNo],repairing[varsNo+1]])
                    #classAnalysis.append([index,coeffs,repairing[varsNo]])
                    for others in range(int(varsPerClass)):
                        if repairing[int(varsPerClass*classIdx)+others] != 1:
                            #print "HERE"
                            idx=int(varsPerClass*classIdx)+others
                            coeffsNew=[]
                            lhsAdd=copy.deepcopy(lhsDrop)
                            itx=0
                            for const in constraints:
                                coeffsNew.append(const[idx])
                                lhsAdd[itx]=lhsAdd[itx]+int(const[idx])
                                itx+=1
                            classRepair=copy.deepcopy(repairing)
                            classRepair=classSwap(classRepair, idx, varsNo, varsPerClass)
                            classAnalysis.append([idx,coeffsNew,score(lhsAdd, constraints, constNo),sumproduct(classRepair, obj)])
                            #print classAnalysis
                            #classAnalysis.append([idx, coeffsNew, score(lhsAdd, constraints, constNo)])
                    classAnalysis = sorted(classAnalysis, key=itemgetter(3), reverse=True)
                    classAnalysis = sorted(classAnalysis, key=itemgetter(2))
                    classesAnalysis.append(classAnalysis[0])
                    '''
                    # sort the solutions, first by obj funct, then by violations
                    # this causes solutions with the same violations to be sorted next by obj funct
                    solutions = sorted(solutions, key=itemgetter(int(varsNo+1)), reverse=True)
                    solutions = sorted(solutions, key=itemgetter(int(varsNo)))
                    '''
                    
            #print classAnalysis
        classesAnalysis = sorted(classesAnalysis, key=itemgetter(3), reverse=True)
        classesAnalysis = sorted(classesAnalysis, key=itemgetter(2))
        #classesAnalysis = sorted(classesAnalysis, key=itemgetter(2), reverse=True)
        #print classesAnalysis
        
        
        
        repaired = classSwap(repairing, classesAnalysis[0][0], varsNo, varsPerClass)
        repairing = repaired
        repairing[-2] = violations2(repairing, constraints, constNo,varsNo)
        repairing[-1] = sumproduct(repairing, obj)
        classify(repairing, obj, varsPerClass, varsNo)
        if repairing[varsNo] == 0 or repairing == lastRepair:
                return repairing
        
        ''' Can't just loop through the classesAnalysis, need to re-evaluate
        for analysis in classesAnalysis:
            #print analysis
            repaired = classSwap(repairing, analysis[0], varsNo, varsPerClass)
            
            
            repairing = repaired
            repairing[-2] = violations2(repairing, constraints, constNo,varsNo)
            repairing[-1] = sumproduct(repairing, obj)
            
            #print repairing
            if repairing[varsNo] == 0:
                return repairing
        #'''
        '''
        count+=1
        if count > 100:
            f = open('issues.txt', 'w')
            f.write(str(soln)+"\n")
            f.write(str(obj)+"\n")
            f.write(str(constraints)+"\n")
            f.write(str(constNo)+"\n")
            f.write(str(varsNo)+"\n")
            f.write(str(repairing)+"\n")
            f.close()
            print repairing
            return soln
        #'''
    #return repair(repairing, obj, constraints, constNo, varsNo, varsPerClass)
    return repairing
                        
# TODO: should probably delete
def improvement(originalCoeffs, newCoeffs, constNo):
    sum=0
    for index in range(len(originalCoeffs)):
        if index < constNo:
            sum = sum + (int(originalCoeffs[index]) - int(newCoeffs[index]))
        else:
            sum = sum - (int(originalCoeffs[index]) - int(newCoeffs[index]))
    return(sum)
    
def classSwap(soln, index, varsNo, varsPerClass):
    classIdx = index - (index%varsPerClass)
    for idx in range(int(varsPerClass)):
        soln[classIdx+idx]=0
    soln[index]=1
    #print soln
    return soln
    
def lhs(soln, constraints, varsNo):
    lhsVector=[]
    count=0
    for constraint in constraints:
        lhsSum = sumproduct(soln, constraint[0:varsNo]) #- int(constraint[len(constraint)-1])
        lhsVector.append(abs(lhsSum))
        count+=1
    return lhsVector
    
# returns violations from lhs values compared to rhs values from the constraints
def score(lhsAdd, constraints, constNo):
    violations=0
    count=0
    for constraint in constraints:
        diff = lhsAdd[count] - int(constraint[len(constraint)-1])
        # if lhs > rhs and we are doing a <= constraint
        if diff > 0 and count < constNo:
            violations += abs(diff)
        # if lhs < rhs and we are doing a >= constraint
        elif diff < 0 and count >= constNo:
            violations += abs(diff)
        count+=1
    return violations
    
def sortSolns(solns,varsNo,solnToKeep):
    solns = sorted(solns, key=itemgetter(int(varsNo+1)), reverse=True)
    solns = sorted(solns, key=itemgetter(int(varsNo)))
    solns = solns[0:solnToKeep]
    return solns
    
def isSolnBetter(soln1, soln2, varsNo):
    if soln1[varsNo] == soln2[varsNo]:
        return (soln1[varsNo+1] > soln2[varsNo+1])
    return (soln1[varsNo] < soln2[varsNo])
    
#####################################################################################################################################################
    
def main():
    '''
    excelName='mdmkp_ct1_1.xls'
    book = xlrd.open_workbook(excelName)
    '''
    
    # number of solutions to randomly generate
    solnNo=200
    solnToKeep=30
    varsPerClass=10
    # number of Jaya iterations
    jayaIterations=200 #100-200, 600
    
    # for 3 best, 2 random approach
    rNbhd1=random.randint(3,solnToKeep)
    rNbhd2=rNbhd1
    while(rNbhd1==rNbhd2):
        rNbhd2=random.randint(3,solnToKeep)
        
    # make false for TLBO or subsets
    isJaya = False
    
    # make false for Learning
    isTeaching = True
    
    # make false to let other algorithms run
    # when using TLBO, make sure isJaya = False
    #   and isTeaching starts off True
    isTLBO = False
    
    random.seed(9001)
    
    start = timeit.default_timer()
    
    for probSet in [6]:
        for modJaya in [False]:
    
            filename='mdmkp_ct' + str(probSet) + '.txt'
            
            file = open(filename)
            
            varsNo=0
            constNo=0
            defsNo=int(file.readline())
            #defsNo=1
            
            # whether using Mod Jaya
            #modJaya=False
            gtConstNo=1
            #[[None]*5 for _ in range(5)]
            solutions=[[]]*solnNo
            
            # stop at this number of iterations without improvement
            itrsWithoutImprovement=10
            
            # number of times NBHD made it better
            modBetterNo = 0
            
            # create excel book for this problem set
            book = xlwt.Workbook(encoding="utf-8")
            
            # create excel book for NBHD searches
            bookNbhd = xlwt.Workbook(encoding="utf-8")
            
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
                
                itrsRun=0
                
                # write one sheet to the current excel book
                sheet = book.add_sheet("Sheet " + str(probNo))
                # sheet.write(row, col, value)
                
                # write one sheet to the NBHD excel book
                sheetNbhd = bookNbhd.add_sheet("Sheet " + str(probNo))
                    
                objFunctIdx=1
                for obj in objFuncts:
                    '''
                    # used to check dataset 6 prob 24 with TBO
                    if(probNo < 4):
                        break;
                    #''' 
                    #seems to not be here anymore?
                    
                    # reseeding RNG for each new problem to make the initial pop.
                    # the same for all problems
                    random.seed(9001)
                    
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
                    
                    solnsHash = copy.deepcopy(solutions)
                    solnIdx = 0
                    
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
                        
                        # TODO: add repair function
                        # DONE
                        if soln[varsNo] > 0:
                            soln = repair(soln, obj, constraints, constNo, varsNo, varsPerClass)
                            
                        solnHash = hash(frozenset(soln))
                            
                        # redoing soln if not unique
                        while(solnHash in solnsHash):
                            for classIdx in range(int(varsNo/varsPerClass)):
                                theOne = random.randint(0,varsPerClass-1)
                                for j in range(int(varsPerClass)):
                                    if j == theOne:
                                        soln[(varsPerClass*classIdx)+j] = 1
                                    else:
                                        soln[(varsPerClass*classIdx)+j] = 0
                            soln[-2] = (violations(soln, constraints, constNo))
                            soln[-1] = (sumproduct(soln, obj))
                            
                            if soln[varsNo] > 0:
                                soln = repair(soln, obj, constraints, constNo, varsNo, varsPerClass)
                                
                            solnHash = hash(frozenset(soln))
                        
                        solnsHash[solnIdx] = solnHash
                        solnIdx+=1
                    
                    # sort the solutions, first by obj funct, then by violations
                    # this causes solutions with the same violations to be sorted next by obj funct
                    solutions = sorted(solutions, key=itemgetter(int(varsNo+1)), reverse=True)
                    solutions = sorted(solutions, key=itemgetter(int(varsNo)))
                    
                    # take the best 30
                    solutions = solutions[0:solnToKeep]
                    
                    # only keep the first 30 hashes
                    solnsHash = solnsHash[0:solnToKeep]
                    
                    # testing for infeasibility between class and demand constraints
                    #if infeasible(constraints, constNo, varsNo, varsPerClass): infeasibleNo+=1
                    
                        
                    
                    
                    
                    # JAYA / MOD JAYA / TLBO algorithm
                    bestSoln = solutions[0]
                    worstSoln = solutions[-1]
                    medianSoln = solutions[solnToKeep/2]
                    improveSoln = bestSoln
                    
                    # if no improvement for 10 straight iterations, terminate
                    count = 0
                    
                    # zero out for each problem within problem definition
                    itrsRun=0
                    
                    # perform Jaya/Mod Jaya/TLBO to create new solutions
                    for _ in range(jayaIterations):
                        itrsRun+=1
                        #bestSoln = solutions[0]
                        #worstSoln = solutions[-1]
                        #print "BEST"
                        #print bestSoln[-1]
                        
                        # zero out the hash list each generation
                        ''' Not necessary
                        for aHash in solnsHash:
                            aHash = 0.1
                        #'''
                        
                        for i in range(len(solutions)):
                            flip = 1
                            Xi = i
                            if(not(isTeaching) and not(isJaya)):
                                while(Xi == i):
                                    Xi = random.randint(0,len(solutions)-1)
                                # for Learning, determine if partner is better
                                flip = (-1) if isSolnBetter(solutions[Xi],solutions[i],varsNo) else 1
                            for j in range(int(varsNo)):
                                r1 = random.randint(0,1)    # 0,1 Uniform Distribution
                                r2 = random.randint(0,1)    # 0,1 Uniform Distribution
                                Tf = random.randint(1,2)    # Teaching Factor
                                
                                
                                # TODO: need to update solutions list to use comboSolns after each iteration of Jaya
                                # DONE
                                currSolnVar = solutions[i][j]   
                                
                                # first equation is Jaya, second is Teaching phase, third is Learning phase
                                newSolns[i][j] = (currSolnVar + r1*(bestSoln[j]-currSolnVar) - r2*(worstSoln[j]-currSolnVar)
                                    if isJaya else ((currSolnVar + r1*(bestSoln[j] - (Tf*medianSoln[j]))) 
                                    if isTeaching else (currSolnVar + flip*r1*(currSolnVar - solutions[Xi][j]))))
                                
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
                            
                            # repair newSoln
                            if newSolns[i][varsNo] > 0:
                                #print newSolns[i]
                                newSolns[i] = repair(newSolns[i], obj, constraints, constNo, varsNo, varsPerClass)
                                #classify(newSolns[i], obj, varsPerClass, varsNo)
                                #print newSolns[i]
                            
                            newHash = hash(frozenset(newSolns[i]))
                            
                            
                            # TODO: check for instances of better violations, but worse obj funct
                            # if violations are less, immediately replace
                            # if violations are the same, keep better obj funct
                            # if violations are worse, throw away new solution
                            if (not(modJaya)):
                                '''
                                if newSolns[i][int(varsNo)] <= solutions[i][int(varsNo)] and newSolns[i][int(varsNo)+1] > solutions[i][int(varsNo)+1]:
                                    comboSolns[i] = newSolns[i]
                                    #print comboSolns[i]
                                #'''
                                if (not(newHash in solnsHash) and isSolnBetter(newSolns[i],solutions[i],varsNo)):
                                    comboSolns[i] = copy.deepcopy(newSolns[i])
                                    solnsHash[i] = newHash
                                    #if i == 0: print "NEW"
                                else:
                                    comboSolns[i] = copy.deepcopy(solutions[i])
                                    #print comboSolns[i]
                                    #if i == 0: print 'OLD'
                        #print newSolns[0][-1]
                        #print solutions[0][-1]
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
                        
                        solutions = copy.deepcopy(comboSolns)
                        
                        # TODO: rework so it's explicitly the same solution X times in a row
                        #       not just X times of the prev. best and curr. best being the same
                        if count == 0:
                            improveSoln = copy.deepcopy(bestSoln)
                            count+=1
                        else:
                            if(improveSoln == comboSolns[0]):
                                count+=1
                                if(count==itrsWithoutImprovement):
                                    break
                            else:
                                count=0
                        # used to alternate between teaching and learning phases in TLBO
                        if(isTLBO):
                            isTeaching = not(isTeaching)
                        
                        # if no improvement for x iterations, stop
                        '''
                        if(bestSoln[-1] == comboSolns[0][-1]):
                            count+=1
                            if(count==itrsWithoutImprovement):
                                break
                        else:
                            count=0
                        #'''
                            
                        
                        # grab the best, worst, and median of the new 30 comboSolns
                        bestSoln = comboSolns[0]
                        worstSoln = comboSolns[-1]
                        medianSoln = comboSolns[solnToKeep/2]
                    # end of JAYA / MODJAYA / TLBO 
                    
                    
                    modSoln = copy.deepcopy(comboSolns[0])
                    finalSoln = comboSolns[0] # used to save final soln reported
                    
                    
                    ''' NBHD on 3 best unique
                    finalSolns = []
                    usedSolns = []
                    count=0
                    stop=3
                    for curSoln in comboSolns:
                        if curSoln in usedSolns:
                            finalSolns.append(curSoln)
                            continue
                        else:
                            usedSolns.append(curSoln)
                            finalSolns.append(NBHD(curSoln, obj, constraints, constNo, varsNo, varsPerClass))
                            count+=1
                            if count >= stop:
                                break
                    finalSolns = sorted(finalSolns, key=itemgetter(int(varsNo+1)), reverse=True)
                    finalSolns = sorted(finalSolns, key=itemgetter(int(varsNo)))
                    finalSolns = finalSolns[0:solnToKeep]
                    
                    modSoln = finalSolns[0]
                    if modSoln[-1] > comboSolns[0][-1] and modSoln[-2] == 0:
                        #comboSolns[0] = copy.deepcopy(modSoln)
                        finalSoln = modSoln
                        #print modSoln
                        modBetterNo += 1
                        print("NBHD got better: " + str(modBetterNo) + "\n")
                        print("NBHD Objective: " + str(modSoln[-1]) + " \nJaya Objective: " + str(comboSolns[0][-1]) + "\n")
                    #'''
                    

                    
                    
                    ''' NBHD on just the best
                    modSoln = NBHD(comboSolns[0], obj, constraints, constNo, varsNo, varsPerClass)
                    # original way of grabbing the nbhd answer 
                    if modSoln[-1] > comboSolns[0][-1] and modSoln[-2] == 0:
                        #comboSolns[0] = copy.deepcopy(modSoln)
                        finalSoln = modSoln
                        #print modSoln
                        modBetterNo += 1
                        print("NBHD got better: " + str(modBetterNo) + "\n")
                        print("NBHD Objective: " + str(modSoln[-1]) + " \nJaya Objective: " + str(comboSolns[0][-1]) + "\n")
                    #'''
                    
                    
                    print "\nNumber of Iterations: " + str(itrsRun)
                    print "Problem Number:       " + str(6*(probNo-1)+objFunctIdx)
                    #print finalSoln
                    
                    for classIdx in range(int(int(varsNo)/int(varsPerClass))):
                        for var in range(int(varsPerClass)):
                            if(finalSoln[int(var + (classIdx*varsPerClass))] == 1):
                                #print int(var + (classIdx*varsPerClass))
                                sheet.write(objFunctIdx+5, classIdx+5, int(var + (classIdx*varsPerClass)))
                    sheet.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+1, finalSoln[-2])
                    if(finalSoln[varsNo] == 0):
                        sheet.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, finalSoln[-1])
                    else:
                        sheet.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, 0)
                    #sheetNbhd.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, finalSoln[-1])
                    sheet.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+3, itrsRun)
                    #print finalSoln[-2], finalSoln[-1], itrsRun
                    
                    # NBHD search on just the best
                    modSoln = NBHD(comboSolns[0], obj, constraints, constNo, varsNo, varsPerClass)
                    # original way of grabbing the nbhd answer 
                    if modSoln[-1] > comboSolns[0][-1] and modSoln[-2] == 0:
                        #comboSolns[0] = copy.deepcopy(modSoln)
                        finalSoln = modSoln
                        #print modSoln
                        modBetterNo += 1
                        print("NBHD got better:      " + str(modBetterNo))
                        print("NBHD Objective:       " + str(modSoln[-1]) + " \nOriginal Objective:   " + str(finalSoln[-1]))
                    else:
                        print("NBHD stayed the same: ")
                        print("Original Objective:   " + str(finalSoln[-1]))
                    #print finalSoln
                    # save book for NBHD search results
                    for classIdx in range(int(int(varsNo)/int(varsPerClass))):
                        for var in range(int(varsPerClass)):
                            if(finalSoln[int(var + (classIdx*varsPerClass))] == 1):
                                #print int(var + (classIdx*varsPerClass))
                                sheetNbhd.write(objFunctIdx+5, classIdx+5, int(var + (classIdx*varsPerClass)))
                    sheetNbhd.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+1, finalSoln[-2])
                    if(finalSoln[varsNo] == 0):
                        sheetNbhd.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, finalSoln[-1])
                    else:
                        sheetNbhd.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, 0)
                    #sheetNbhd.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+2, finalSoln[-1])
                    sheetNbhd.write(objFunctIdx+5, int(varsNo)/int(varsPerClass)+5+3, itrsRun)
                    #print finalSoln[-2], finalSoln[-1], itrsRun
                    
                    # needed for determining the number of >= constraints
                    # and which row to write into in each excel sheet
                    objFunctIdx+=1
                
                
                probNo+=1
            
            # used to keep track of spreadsheets for debugging algorithm
            debug="Debug_"+str(jayaIterations)+"itr_" + str(itrsWithoutImprovement) + "itrsWithoutImprovement_seeded_NBHD_none_Repair_each_Unique"
            debugNbhd="Debug_"+str(jayaIterations)+"itr_" + str(itrsWithoutImprovement) + "itrsWithoutImprovement_seeded_NBHD_once_Repair_each_Unique"
            if(isTLBO):
                book.save(filename[:-4] +debug+'_TLBO.xls')
                print('Book Saved: ' + filename[:-4] +debug+'_TLBO.xls')
                bookNbhd.save(filename[:-4] +debugNbhd+'_TLBO.xls')
                print('Book Saved: ' + filename[:-4] +debugNbhd+'_TLBO.xls')
            elif(modJaya):
                book.save(filename[:-4] +debug+'_modJaya.xls')
                bookNbhd.save(filename[:-4] +debugNbhd+'_modJaya.xls')
            elif(isJaya):
                book.save(filename[:-4] +debug+'_Jaya.xls')
                print('Book Saved: ' + filename[:-4] +debug+'_Jaya.xls')
                bookNbhd.save(filename[:-4] +debugNbhd+'_Jaya.xls')
                print('Book Saved: ' + filename[:-4] +debugNbhd+'_Jaya.xls')
            elif(isTeaching):
                book.save(filename[:-4] +debug+'_TBO.xls')
                print('Book Saved: ' + filename[:-4] +debug+'_TBO.xls')
                bookNbhd.save(filename[:-4] +debugNbhd+'_TBO.xls')
                print('Book Saved: ' + filename[:-4] +debugNbhd+'_TBO.xls')
            else:
                book.save(filename[:-4] +debug+'_LBO.xls')
                print('Book Saved: ' + filename[:-4] +debug+'_LBO.xls')
                bookNbhd.save(filename[:-4] +debugNbhd+'_LBO.xls')
                print('Book Saved: ' + filename[:-4] +debugNbhd+'_LBO.xls')
            
            
    # tracking runtime   
    stop = timeit.default_timer()
    print (stop - start)
    
        
if __name__ == '__main__':
	main()

