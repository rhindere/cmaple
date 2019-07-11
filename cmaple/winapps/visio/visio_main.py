'''
Created on Apr 30, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''
from pprint import pprint
import win32com.client
import sys
vc = win32com.client.constants
# try:
#     test = xlc.xlEdgeBottom
# except AttributeError as err:
#     et = win32com.client.gencache.EnsureDispatch("Excel.Application")
#     del et
#     xlc = win32com.client.constants
from collections import OrderedDict
from os.path import isfile, join

class VisioApp():
    def __init__(self):
        self.w32_app = self.get_visio_app()
        self.drawings = {}
        
    def get_visio_app(self):
        v = win32com.client.Dispatch("Visio.Application")
        if v:
            v.Visible = True
            return v
        else:
            return None

    def add_drawing(self,visio_file_path,drawing_name):
        drawing = VisioDrawing(self,visio_file_path,drawing_name)
        self.drawings[drawing_name] = drawing
        return drawing
        

class VisioDrawing():
    
    def __init__(self,app,visio_file_path,drawing_name):
        self.app = app
        self.visio_file_path = visio_file_path
        self.drawing_name = drawing_name
        self.w32_drawing = self.get_drawing()
        self.name = self.w32_drawing.Name
        self.pages = {}
        self.shapes = {}
        self.layers = {}
        self.load_pages_shapes_and_layers()
    
    def get_drawing(self):
        if not self.app:
            return None
        w32_app = self.app.w32_app
        drawing_path = '{}\\{}'.format(self.visio_file_path,self.drawing_name)
        if isfile(drawing_path):
            w32_drawing = w32_app.Documents.Open(drawing_path)
        else:
            w32_app.Documents.Add()
            w32_app.ActiveDocument.SaveAs(drawing_path)
            w32_drawing = self.app.ActiveDocument
        if not w32_drawing:
            return None
        else:
            return w32_drawing
    
    def add_page(self,page_name):
        w32_page = self.drawing.Pages.Add()
        w32_page.Name = page_name
        self.pages[page_name] = VisioPage(self,w32_page)

    def load_pages_shapes_and_layers(self):
        current_pages = self.pages.copy()
        self.pages.clear()
        current_shapes = self.shapes.copy()
        self.shapes.clear()
        for w32_page in self.w32_drawing.Pages:
            if w32_page.Name in current_pages:
                self.pages[w32_page.Name] = current_pages[w32_page.Name]
            else:
                self.pages[w32_page.Name] = VisioPage(self,w32_page)
            for w32_shape in w32_page.Shapes:
                if w32_shape.Name in current_shapes:
                    self.shapes[w32_shape.Name] = current_shapes[w32_shape.Name]
                else:
                    self.shapes[w32_shape.Name] = VisioShape(self.pages[w32_page.Name],w32_shape)
            self.pages[w32_page.Name].load_shapes_and_layers()
        
class VisioPage():
    
    def __init__(self,drawing,w32_page):
        self.drawing = drawing
        self.w32_page = w32_page
        self.name = self.w32_page.Name
        self.shapes = {}
        self.layers = {}
 
    def load_shapes_and_layers(self):
        current_shapes = self.shapes.copy()
        self.shapes.clear()
        current_layers = self.layers.copy()
        self.layers.clear()
        for w32_shape in self.w32_page.Shapes:
            if w32_shape.Name in current_shapes:
                self.shapes[w32_shape.Name] = current_shapes[w32_shape.Name]
            else:
                self.shapes[w32_shape.Name] = VisioShape(self,w32_shape)
        for w32_layer in self.w32_page.Layers:
            if w32_layer.Name in current_layers:
                self.layers[w32_layer.Name] = current_layers[w32_layer.Name]
            else:
                self.layers[w32_layer.Name] = VisioLayer(self,w32_layer)
            self.layers[w32_layer.Name].load_shapes()
            
class VisioLayer():
    
    def __init__(self,page,w32_layer):
        self.page = page
        self.w32_layer = w32_layer
        self.name = self.w32_layer.Name
        self.shapes = {}

    def load_shapes(self):
        current_shapes = self.shapes.copy()
        self.shapes.clear()
        for w32_shape in self.w32_layer.Page.Shapes:
            layer_count = w32_shape.LayerCount
            if layer_count > 0:
                for i in range(1,layer_count+1):
                    if w32_shape.Layer(i).Name == self.name:
                        self.shapes[w32_shape.Name] = self.page.shapes[w32_shape.Name]
                
    def assign_shape(self,shape):
        pass

class VisioShape():
    
    def __init__(self,page,w32_shape,layer=None):
        self.page = page
        self.w32_shape = w32_shape
        self.name = self.w32_shape.Name
        self.layer = layer
        
    def _get_float(self,val):
        return float(str(val))
        
    def get_width(self):
        return self.w32_shape.Cells('Width').Result(50)
        
    def get_height(self):
        return self.w32_shape.Cells('Height').Result(50)

    def get_top(self):
#         return self._get_float(self.w32_shape.Cells('PinY'))
        return self.w32_shape.Cells('PinY').Result(50)
        
    def get_left(self):
#         return self._get_float(self.w32_shape.Cells('PinX'))
        return self.w32_shape.Cells('PinX').Result(50)

    def get_top_left(self):
        return self.get_top(), self.get_left()
        
    def copy_shape(self):
        self.w32_shape.Copy()