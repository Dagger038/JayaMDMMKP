# Filename:         remodExcel.py
# Author:           Dylan Gaspar
# Class:            GA
# Last Modified:    12/19/2016
# Purpose:          

import math
import xlrd
from xlrd import open_workbook
import xlwt
import random
import operator
from operator import itemgetter

def main():
    
    classSize = 10
    
    for dataSet in [1,2,3,4,5,6,7,8,9]:
        # 2D list of jaya values [[None]*numOfElts for _ in range(numOfLists)]
        jayaVals = [[None]*6 for _ in range(15)]
        
        # 2D list of number of iterations
        jayaItrs = [[None]*6 for _ in range(15)]
    
        # sheet.write(row, col, value)
        newBook = xlwt.Workbook(encoding="utf-8")
        
        newSheet = newBook.add_sheet("Sheet1")
        
        
        myColOffset = 7 + ((100 if dataSet % 3 == 1 else 250 if dataSet % 3 == 2 else 500)/classSize)
        
        myRowOffset = 6
        
        finalRow = 2
        finalCol = 1
        
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_none_Repair_Jaya.xls'
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_once_Repair_Jaya.xls'
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_each_Repair_Jaya.xls'
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_once_3best_2rand_Repair_Jaya.xls'
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_once_3best_unique_Repair_Jaya.xls'
        tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_once_3best_unique_Repair_each_Jaya.xls'
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_once_Repair_each_Jaya.xls'
        #tag = 'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_none_Repair_each_Jaya.xls'
        
        filename='mdmkp_ct'+str(dataSet)+tag
        #filename='mdmkp_ct'+str(dataSet)+'Debug_200itr_10itrsWithoutImprovement_seeded_NBHD_everyItr_Jaya.xls'
        myBook = open_workbook(filename,on_demand=True)
        
        
        
        
            
        sheetNum = 0
            
        for name in myBook.sheet_names():
            
            mySheet = myBook.sheet_by_name(name)
            for type in range(0,6):
                jayaVals[sheetNum][type] = mySheet.cell(myRowOffset+type,myColOffset).value
                jayaItrs[sheetNum][type] = mySheet.cell(myRowOffset+type,myColOffset+1).value
                newSheet.write(sheetNum, 2*type, jayaVals[sheetNum][type])
                newSheet.write(sheetNum, 2*type+1, jayaItrs[sheetNum][type])
            sheetNum+=1
            # sheet.cell(row,col).value
        
            # jaya
            #jayaVal = mySheet.cell(myRowCurr,myColOffset).value
            #newSheet.write(finalRow, finalCol+1, jayaVal)
        
            myBook.unload_sheet(name)
                
        myBook.release_resources()
    
            
        newBook.save('mdmkpc10pc_ct'+str(dataSet)+tag[37:])
        #newBook.save('mdmkpc10pc_ct'+str(dataSet)+'_200itr_10itrsWithoutImprovement_NBHD_everyItr_Jaya.xls')
        print('Book '+str(dataSet)+' saved')
    
    


if __name__ == '__main__':
	main()

