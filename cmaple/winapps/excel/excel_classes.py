'''
Created on Apr 12, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

from pprint import pprint
import win32com.client
import sys
xlc = win32com.client.constants
try:
    test = xlc.xlEdgeBottom
except AttributeError as err:
    et = win32com.client.gencache.EnsureDispatch("Excel.Application")
    del et
    xlc = win32com.client.constants
from collections import OrderedDict
from os.path import isfile, join
from shtechparser.helpers.helpers import set_attrs
from shtechparser.shtechcabal.severities import severity

def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

class excel_cell():

    def __init__(self,_excel_worksheet,cell,row,column):
        self.cell = cell
        self._excel_cell = _excel_worksheet.Cells(row,column)

    def set_value(self):
        if type(self.cell.cell_value) is str:
            self._excel_cell.Value = self.cell.cell_value.split('~')[-1]
        else:
            self._excel_cell.Value = self.cell.cell_value

    def set_comment(self):
        self._excel_cell.AddComment(self.cell.cell_comment)

    def set_font_size(self):
        pass
    
    def set_font_bold(self):
        if self.cell.cell_font_bold:
            self._excel_cell.Font.Bold = True
            
    def set_font_italic(self):
        pass
    
    def set_box_border_thick(self):
        if self.cell.cell_box_border_thick:
            self._excel_cell.BorderAround(xlc.xlContinuous,xlc.xlThick)

    def set_wrap(self):
        if self.cell.cell_wrap:
            self._excel_cell.WrapText = True
                
    def process_cell(self):
        for attr_key in dir(self):
            if attr_key.startswith('set_'):
                cell_attr_name = attr_key.replace('set_','cell_')
                cell_attr = getattr(self.cell,cell_attr_name)
                if not cell_attr is None:
                    getattr(self,attr_key)()

class write_excel_workbook():
    
    def __init__(self,book,show_tech_directory):
        self.book = book
        self.workbook_name = self.book.book_name
        self.show_tech_directory = show_tech_directory
        self.excel_app = excel_app()
        self.excel_app.add_workbook(show_tech_directory,self.workbook_name)
        self.excel_workbook = self.excel_app.workbooks[self.workbook_name]
        self.current_excel_worksheet = None
        self.header_start_column = 0
        self.field_start_row = 0
        
    def write_worksheets(self):
        for worksheet_name, worksheet in self.book.sheets.items():
            self.current_excel_worksheet = self.get_worksheet(worksheet_name)
            self.write_worksheet(worksheet)
       
    def get_worksheet(self,worksheet_name):
        _worksheet = None
        for sheet in self.excel_workbook.Worksheets:
            if sheet.Name == worksheet_name:
                _worksheet = sheet
                _worksheet.Cells.Clear()
        if not _worksheet:
            self.excel_workbook.Worksheets.Add()
            _worksheet = self.excel_workbook.ActiveSheet
            _worksheet.Name = worksheet_name
        return _worksheet

    def write_worksheet(self,worksheet):
        for table_name, table in worksheet.tables.items():
            self.write_table(table)
            
    def write_table(self,table):
        top = table.top
        left = table.left
        header_column_offset = len(table.field_levels)
        field_row_offset = len(table.header_levels)
        self.field_start_row = top + field_row_offset
        self.write_field_columns(table.field_levels,self.field_start_row,left)
        self.header_start_column = left + header_column_offset
        self.write_header_columns(table.header_levels[0],self.field_start_row,self.header_start_column)
        self.write_data_matrix(table.data_matrix)
        self.write_pivot()
              
    def write_pivot(self):
        top = 1
        left = 1
        self.current_excel_worksheet = self.get_worksheet('all_pivot')
        self.current_excel_worksheet.Cells(top, left).Value = 'hostname'
        self.current_excel_worksheet.Cells(top, left+1).Value = 'category'
        self.current_excel_worksheet.Cells(top, left+2).Value = 'stat'
        self.current_excel_worksheet.Cells(top, left+3).Value = 'severity'
        self.current_excel_worksheet.Cells(top, left+4).Value = 'value'
        top += 1
        for worksheet_name, worksheet in self.book.sheets.items():
            for table_name, table in worksheet.tables.items():
                for field_name, headers in table.data_matrix.matrix.items():
                    for header_name, cell in headers.items():
                        if cell.cell_value == 0:
                            continue
                        if cell.pivot_path:
                            cell_path_parts = cell.pivot_path.split('~')
                            this_left = left
                            for cell_path_part in cell_path_parts:
                                self.current_excel_worksheet.Cells(top, this_left).Value = cell_path_part
                                this_left += 1
                            severity_lookup_string = ''
                            if '->' in cell_path_parts[2]:
                                severity_lookup_string = cell_path_parts[2].split('->')[-1]
                            else:
                                severity_lookup_string = cell_path_parts[2]
                            severity_known = False
                            for severity_key, severity_string in severity.items():
                                if severity_key in severity_lookup_string:
                                    severity_known = True
                                    self.current_excel_worksheet.Cells(top, this_left).Value = severity_string
                            if not severity_known:
                                self.current_excel_worksheet.Cells(top, this_left).Value = 'unknown'
                            this_left += 1
                            self.current_excel_worksheet.Cells(top, this_left).Value = cell.cell_value
                        top += 1
        used_range_address = self.current_excel_worksheet.UsedRange.Address
        all_pivot_address = 'all_pivot!'+used_range_address
        all_pivot_source_range = self.current_excel_worksheet.Range(all_pivot_address)
        self.excel_workbook.Names.Add(Name="all_pivot", RefersTo='={}'.format(all_pivot_address))
        self.current_excel_worksheet.UsedRange.NumberFormat = "0"
        
        self.current_excel_worksheet = self.get_worksheet('all_pivot_table')
        pc = self.excel_workbook.PivotCaches().Create(SourceType=xlc.xlDatabase,
                                                   SourceData=all_pivot_source_range,
                                                   Version=xlc.xlPivotTableVersion15)
        all_pivot_dest_range = self.current_excel_worksheet.Range('all_pivot_table!$A$1')
        pt = pc.CreatePivotTable(TableDestination=all_pivot_dest_range,
                         TableName='all_pivot_table_1',
                         DefaultVersion=xlc.xlPivotTableVersion15)
        pt.PivotFields('hostname').Orientation = xlc.xlRowField
        pt.PivotFields('hostname').Position = 1
        pt.PivotFields('category').Orientation = xlc.xlRowField
        pt.PivotFields('category').Position = 2
        pt.PivotFields('stat').Orientation = xlc.xlRowField
        pt.PivotFields('stat').Position = 3
        pt.PivotFields('severity').Orientation = xlc.xlPageField
        pt.PivotFields('severity').CurrentPage = "ASA Internal - High"
        pt.PivotFields('severity').Position = 1
        pt.PivotFields('value').Orientation = xlc.xlDataField
        pt.PivotFields('Count of value').Caption = 'Sum of value'
        
        pt.PivotFields('Sum of value').Function = xlc.xlSum

    def write_field_columns(self,field_levels,top,left):
        def write_field(parent_fields,field,top,left):
            parent_fields_copy = parent_fields.copy()
            if not field.child_fields:
                field.row_number = top
                field_list = parent_fields_copy.copy()
                field_list.append(field)
                for field in field_list:
                    self.write_excel_cell(field, top, left)
                    left += 1
                return top+1
            else:
                parent_fields_copy.append(field)
                for child_field in field.child_fields:
                    top = write_field(parent_fields_copy,child_field,top,left)
                return top
        
        fcn_left = left
        for field_level in field_levels:
            for field_column_name, field_column in field_level.items():
                self.write_excel_cell(field_column, top, fcn_left)
                fcn_left += 1
        top += 1
        first_column = field_levels[0][list(field_levels[0].keys())[0]]
        for field_name, field in first_column.fields.items():
            top = write_field([],field,top,left)

    def write_header_columns(self,header_columns,top,left):
        for header_column_name, header_column in header_columns.items():
            for header_name, header in header_column.headers.items():
                self.write_excel_cell(header, top, left)
                header.column_number = left
                left += 1

    def write_data_matrix(self,data_matrix):
        dm_range = '{}{}:{}{}'.format(colnum_string(self.header_start_column),self.field_start_row+1,
                                      colnum_string(self.header_start_column+data_matrix.column_count-1),
                                      self.field_start_row+data_matrix.row_count
                                      )
        data_matrix.matrix_range = dm_range
        self.current_excel_worksheet.Range(dm_range).Borders(xlc.xlInsideHorizontal).LineStyle=xlc.xlContinuous
        self.current_excel_worksheet.Range(dm_range).Borders(xlc.xlInsideHorizontal).Weight=xlc.xlThin
        self.current_excel_worksheet.Range(dm_range).Borders(xlc.xlInsideVertical).LineStyle=xlc.xlContinuous
        self.current_excel_worksheet.Range(dm_range).Borders(xlc.xlInsideVertical).Weight=xlc.xlThin
        self.current_excel_worksheet.Range(dm_range).BorderAround(xlc.xlContinuous,xlc.xlThin)
        for field_name, headers in data_matrix.matrix.items():
            for header_name, cell in headers.items():
                top = cell.field.row_number
                left = cell.header.column_number
                self.write_excel_cell(cell, top, left)
        self.current_excel_worksheet.UsedRange.NumberFormat = "0"

    def write_field_column(self,field_column,top,left):
        pass
            
    def write_column(self):
        pass
        
    def write_excel_cell(self,table_cell,row,column):
        _excel_cell = excel_cell(self.current_excel_worksheet,table_cell,row,column)
        _excel_cell.process_cell()
        
    def get_range(self):
        pass

class excel_app():
    def __init__(self):
        self.app = self.get_excel_app()
        self.workbooks = {}
        
    def get_excel_app(self):
        e = win32com.client.Dispatch("Excel.Application")
        if e:
            e.Visible = True
            return e
        else:
            return None
    
    def add_workbook(self,show_tech_directory,workbook_name):
        workbook = excel_workbook(self.app,show_tech_directory,workbook_name)
        self.workbooks[workbook_name] = workbook.workbook

class excel_workbook():
    
    def __init__(self,app,show_tech_directory,workbook_name):
        self.app = app
        self.show_tech_directory = show_tech_directory
        self.workbook_name = workbook_name
        self.workbook = self.get_workbook()
        self.worksheets = {}
    
    def get_workbook(self):
        if not self.app:
            return None
        
        book_path = '{}\\{}'.format(self.show_tech_directory,self.workbook_name)
        if isfile(book_path):
            book = self.app.Workbooks.Open(book_path)
        else:
            self.app.Workbooks.Add()
            self.app.ActiveWorkbook.SaveAs(book_path)
            book = self.app.ActiveWorkbook
        if not book:
            return None
        else:
            return book
    
    def add_worksheet(self,worksheet_name):
        worksheet = excel_worksheet(self.workbook,worksheet_name)
        self.worksheets[worksheet_name] = worksheet
    
class excel_worksheet():
    
    def __init__(self,workbook,worksheet_name):
        self.workbook = workbook
        self.worksheet_name = worksheet_name
        self.worksheet = self.get_worksheet()
        self.ranges = {}
        
    def get_worksheet(self):
        worksheet = None
        for sheet in self.workbook.Worksheets:
            if sheet.Name == self.worksheet_name:
                worksheet = sheet
                worksheet.Cells.Clear()
        if worksheet is None:
            self.workbook.Worksheets.Add()
            worksheet = self.workbook.ActiveSheet
            worksheet.Name = self.worksheet_name
        return worksheet

    def add_table(self,range_name,top,left):
        range = excel_range(self.worksheet,range_name,top,left)
        self.ranges[range_name] = range

    def get_used_range(self):
        pass

    def get_first_free_row(self):
        pass

    def get_first_free_col(self):
        pass

class excel_range():
    
    def __init__(self,worksheet,table_name,top,left,**kwargs):
        self.top = top
        self.left = left
        self.worksheet = worksheet
        self.table_name = table_name
        self.range = self.worksheet.Cell(top,left)
        self.range.Name = self.table_name
        self.header_levels = []
        self.field_levels = []
        self.header_rows = {}
        self.field_columns = {}
        self.data_matrix = [[]]
        self.pivots = []
        
