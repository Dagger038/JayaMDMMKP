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
    
        # sheet.write(row, col, value)
        newBook = xlwt.Workbook(encoding="utf-8")
        
        newSheet = newBook.add_sheet("Sheet1")
        
        
        myColOffset = 7 + ((100 if dataSet % 3 == 1 else 250 if dataSet % 3 == 2 else 500)/classSize)
        
        myRowOffset = 6
        
        finalRow = 2
        finalCol = 1
        
        filename='mdmkp_ct'+str(dataSet)+'Debug_200itr_Jaya.xls'
        myBook = open_workbook(filename,on_demand=True)
        
        
        
        
            
        sheetNum = 0
            
        for name in myBook.sheet_names():
            
            mySheet = myBook.sheet_by_name(name)
            for type in range(0,6):
                jayaVals[sheetNum][type] = mySheet.cell(myRowOffset+type,myColOffset).value
                newSheet.write(sheetNum, 2*type, jayaVals[sheetNum][type])
            sheetNum+=1
            # sheet.cell(row,col).value
        
            # jaya
            #jayaVal = mySheet.cell(myRowCurr,myColOffset).value
            #newSheet.write(finalRow, finalCol+1, jayaVal)
        
            myBook.unload_sheet(name)
                
        myBook.release_resources()
    
            
    
    
        newBook.save('mdmkpc10pc_ct'+str(dataSet)+'_200itr.xls')
        print('Book '+str(dataSet)+' saved')
    
    


if __name__ == '__main__':
	main()

