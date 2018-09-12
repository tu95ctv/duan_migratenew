# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import os
import inspect

from xlutils.filter import process,XLRDReader,XLWTWriter
import xlrd, xlwt


from odoo.addons.tonkho.controllers.controllers import  download_ml_for_bb



def write_merge_cell(row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            return crange
    return None
def copy2(wb):
    w = XLWTWriter()
    process(
        XLRDReader(wb,'unknown.xls'),
        w
        )
    return w.output[0][1], w.style_list

def update_content(dlcv_obj):
    directory_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    directory_path = os.path.split(os.path.abspath(directory_path))[0]
    directory_path =  os.path.join(directory_path, u'file_import',u'Mẫu BBBG 2018.xls')
    rdbook= xlrd.open_workbook(directory_path, formatting_info=True )#formatting_info=True
    sheetx = 0
    rdsheet = rdbook.sheet_by_index(sheetx)
    wtbook_c, style_list = copy2(rdbook)
    wtsheet_c = wtbook_c.get_sheet(sheetx)
    wtbook = xlwt.Workbook()
    wtsheet = wtbook.add_sheet(u'First')
    for row in range(1,rdsheet.nrows):
        wtsheet.row(row).height_mismatch = True
        wtsheet.row(row).height = wtsheet_c.row(row).height 
    for col in range(1,rdsheet.ncols):
        wtsheet.col(col).width =  wtsheet_c.col(col).width
    merge_tuple_list =  rdsheet.merged_cells
    print ('merge_tuple_list',merge_tuple_list)
    fixups = [(0, 0), (1, 0),(0,3),(1,3),
                (3,0),(5,0),(6,0),
                (9,0),(9,2)
              ]

     
    for rowx, colx in fixups:
        xf_index = rdsheet.cell_xf_index(rowx, colx)
        val = rdsheet.cell_value(rowx,colx)
        crange = write_merge_cell(rowx, colx, merge_tuple_list)
        print ('crange',crange)
        if crange ==None:
            wtsheet.write(rowx, colx, val, style_list[xf_index])
        else:
            wtsheet.write_merge(crange[0],crange[1]-1,crange[2],crange[3]-1, val, style_list[xf_index])
            
    download_ml_for_bb(dlcv_obj,worksheet=wtsheet,row_index=15) 
            
            
    
    return wtbook
#     wtbook.save(u'C:/D4/test_folder/Mẫu BBBG 2018hehe.xls')
    
    


