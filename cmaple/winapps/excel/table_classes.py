'''
Created on Apr 15, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''

from collections import OrderedDict
from shtechparser.helpers.helpers import set_attrs
from shtechparser.shtechcabal.severities import severity

class __cell_base():

    def __init__(self,**kwargs):
        set_attrs(self,**kwargs)

    def set_hostname(self,hostname):
        self.cell_hostname = hostname

    def set_value(self,value):
        self.cell_value = value

    def set_comment(self,comment):
        self.cell_comment = comment

    def set_font_size(self,font_size):
        self.cell_font_size = font_size
        
    def set_font_bold(self,font_bold):
        self.cell_font_bold = font_bold
        
    def set_font_italic(self,font_italic):
        self.cell_font_italic = font_italic
        
    def set_box_border_thick(self,box_border_thick):
        self.cell_box_border = box_border_thick

    def set_borders(self,borders):
        self.cell_borders = borders
        
    def set_wrap(self,wrap):
        self.cell_wrap = wrap

class book():
    def __init__(self,book_name):
        self.book_name = book_name
        self.sheets = {}
        
    def add_sheet(self,sheet_name):
        _sheet = sheet(sheet_name)
        self.sheets[sheet_name] = _sheet
        return _sheet

class sheet(__cell_base):
    def __init__(self,sheet_name):
        self.sheet_name = sheet_name
        self.tables = {}
        
    def add_table(self,table_name,top,left):
        _table = table(table_name,top,left)
        self.tables[table_name] = _table
        return _table

class table(__cell_base):
    
    def __init__(self,table_name,top,left,**kwargs):
        self.top = top
        self.left = left
        self.table_name = table_name
        self.header_levels = []
        self.field_levels = []
        self.data_matrix = data_matrix()
        self.row_count = 0
        self.column_count = 0

    def add_field_level(self):
        self.column_count += 1
        level = OrderedDict()
        self.field_levels.append(level)
        return level
    
    def add_field_column(self,column_name,level):
        _field_column = field_column(level,column_name)
        level[column_name] = _field_column
        return _field_column
    
    def add_header_level(self):
        self.row_count += 1
        level = OrderedDict()
        self.header_levels.append(level)
        return level
    
    def add_header_column(self,column_name,level):
        _header_column = header_column(level,column_name)
        level[column_name] = _header_column
        return _header_column
    
    def add_pivot(self,wc):
        pass
    
    def _assign_cell_column(self,wc):
        pass
    
    def _assign_cell_row(self,wc):
        pass

class data_matrix(__cell_base):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.row_count = 0
        self.column_count = 0
        self.matrix = {}
        self.matrix_range = None

    def add_data(self,_field,_header,pivot_path=None,severity=None):
        _data = data(_field,_header,pivot_path,severity)
        if not _field.cell_value in self.matrix:
            self.matrix[_field.cell_value] = {}
        self.matrix[_field.cell_value][_header.cell_value] = _data
        if len(_field.parent_field_column.fields) > self.row_count:
            self.row_count = len(_field.parent_field_column.fields)
        if len(_header.parent_header_column.parent_level) > self.column_count:
            self.column_count = len(_header.parent_header_column.parent_level)
        
        return _data
    
class header_column(__cell_base):
    
    def __init__(self,parent_level,column_name,**kwargs):
        super().__init__(**kwargs)
        self.parent_level = parent_level
        self.cell_value = column_name
        self.headers = OrderedDict()
        self.column_count = 0

    def add_header(self,header_name,parent_header=None):
        self.column_count += 1
        _header = header(self,header_name,parent_header)
        self.headers[header_name] = _header
        return _header

class header(__cell_base):

    def __init__(self,parent_header_column,header_name,parent_header,**kwargs):
        super().__init__(**kwargs)
        self.parent_header_column = parent_header_column
        self.cell_value = header_name
        self.parent_header = parent_header
        self.column_number = None

class field_column(__cell_base):
    
    def __init__(self,parent_level,column_name,**kwargs):
        super().__init__(**kwargs)
        self.parent_level = parent_level
        self.cell_value = column_name
        self.fields = OrderedDict()
        self.row_count = 0

    def add_field(self,field_name,parent_field=None):
        self.row_count += 1
        _field = field(self,field_name,parent_field)
        self.fields[field_name] = _field
        return _field

class field(__cell_base):

    def __init__(self,parent_field_column,field_name,parent_field,**kwargs):
        super().__init__(**kwargs)
        self.parent_field_column = parent_field_column
        self.cell_value = field_name
        self.parent_field = parent_field
        self.child_fields = []
        if not self.parent_field is None:
            self.parent_field.child_fields.append(self)
        self.row_number = None

class data(__cell_base):

    def __init__(self,_field,_header,pivot_path,severity,**kwargs):
        super().__init__(**kwargs)
        self.field = _field
        self.header = _header
        self.pivot_path = pivot_path
        self.severity = severity
        
class table_column(__cell_base):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cells = []

class table_row(__cell_base):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cells = []

