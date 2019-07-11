'''
Created on Apr 30, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''
from pprint import pprint
import win32com.client
import sys
from string import printable
import re
from ppt_to_mmap_main.helpers import remove_control_characters,\
    is_control_character
import string

pc = win32com.client.constants
try:
    test = pc.ppLayoutCustom
except AttributeError as err:
    pt = win32com.client.gencache.EnsureDispatch("PowerPoint.Application")
    del pt
    pc = win32com.client.constants
from collections import OrderedDict
from os.path import isfile, join


class PowerPointApp():
    def __init__(self):
        self.w32_app = self.get_ppt_app()
        self.presentations = {}
        
    def get_ppt_app(self):
        try: 
            p = win32com.client.GetActiveObject("PowerPoint.Application")
    
        except:
            p = win32com.client.Dispatch("PowerPoint.Application")
        if p:
            p.Visible = True
            return p
        else:
            return None

    def add_presentation(self,powerpoint_file_path,presentation_name):
        presentation = PowerPointPresentation(self,powerpoint_file_path,presentation_name)
        self.presentations[presentation_name] = presentation
        return presentation
        

class PowerPointPresentation():
    
    def __init__(self,app,presentation_file_path,presentation_name):
        self.app = app
        self.presentation_file_path = presentation_file_path
        self.presentation_name = presentation_name
        self.w32_presentation = self.get_presentation()
        self.name = self.w32_presentation.Name
        self.slides = {}
        self.shapes = {}
        self.sections = {}
        self.load_slides()
        self.slide_height = None
        self.slide_width = None
    
    def get_slide_height(self):
        self.slide_height = self.w32_presentation.PageSetup.SlideHeight
        return self.slide_height
    
    def get_slide_width(self):
        self.slide_width = self.w32_presentation.PageSetup.SlideWidth
        return self.slide_width
    
    def get_presentation(self):
        if not self.app:
            return None
        w32_app = self.app.w32_app
        presentation_path = '{}\\{}'.format(self.presentation_file_path,self.presentation_name)
        print(presentation_path)
        if isfile(presentation_path):
            for w32_presentation in w32_app.Presentations:
                if w32_presentation.Name == self.presentation_name:
                    return w32_presentation
            w32_app.Presentations.Open(presentation_path)
            return w32_app.ActivePresentation
        else:
            w32_app.Presentations.Add()
            return w32_app.ActivePresentation
        return None
    
    def clear_presentation(self):
        for w32_slide in self.w32_presentation.Slides:
            w32_slide.Delete()
        section_count = self.w32_presentation.SectionProperties.Count
        for i in range(1,section_count+1):
            self.w32_presentation.SectionProperties.Delete(1,True)
        self.load_slides()
        
    def add_slide(self,slide_name,section_name=None):
        slide_count = self.w32_presentation.Slides.Count
        w32_slide = self.w32_presentation.Slides.Add(slide_count+1,pc.ppLayoutCustom)
        self.slides[slide_name] = PowerPointSlide(self,w32_slide,section_name)
        return self.slides[slide_name]

    def add_section(self,section_name):
        section_count = self.w32_presentation.SectionProperties.Count
        section_index = self.w32_presentation.SectionProperties.AddSection(section_count+1,section_name)
        self.sections[section_name] = PowerPointSection(self,section_index,section_name)
        return self.sections[section_name]

    def is_shape_in_box(self,shape,top,left,bottom,right):
        shape_top,shape_left,shape_bottom,shape_right = shape.get_shape_box()
        if shape_top >= top:
            if shape_left >= left:
                if shape_bottom <= bottom:
                    if shape_right <= right:
                        return True
        return False

    def load_slides(self):
        self.slides.clear()
        slide_name_qualifiers = {}
        for w32_slide in self.w32_presentation.Slides:
            if w32_slide.Name in self.slides:
                slide_name_qualifiers[w32_slide.Name] += 1
                w32_slide.Name = '{}_{}'.format(w32_slide.Name,slide_name_qualifiers[w32_slide.Name])
            else:
                slide_name_qualifiers[w32_slide.Name] = 0
            self.slides[w32_slide.Name] = PowerPointSlide(self,w32_slide)
            self.slides[w32_slide.Name].load_shapes()
        
class PowerPointSlide():
    
    def __init__(self,presentation,w32_slide,section_name=None):
        self.presentation = presentation
        self.w32_slide = w32_slide
        self.name = self.w32_slide.Name
        self.notes_text = None
        self.shapes = {}
 
    def load_shapes(self):
        self.shapes.clear()
        shape_name_qualifiers = {}
        shape_count = self.w32_slide.Shapes.Count
        for i in range(1,shape_count+1):
            w32_shape = self.w32_slide.Shapes(i)
            if w32_shape.Name in self.shapes:
                shape_name_qualifiers[w32_shape.Name] += 1
                w32_shape.Name = '{}_{}'.format(w32_shape.Name,shape_name_qualifiers[w32_shape.Name])
            else:
                shape_name_qualifiers[w32_shape.Name] = 0
            self.shapes[w32_shape.Name] = PowerPointShape(self,w32_shape,i)

    def get_hyperlinks(self,hyperlinks_dict):
        print('Getting hyperlinks for slide',self.name)
        for w32_hyperlink in self.w32_slide.Hyperlinks:
            try:
                display_text = ''
                display_text_temp = w32_hyperlink.TextToDisplay
                for character in display_text_temp:
                    if ord(character) > 31 and ord(character) < 127:
#                     if re.match('[\w .,:/@]',character):
                        display_text += character
                address = ''
                address_temp = w32_hyperlink.Address
                for character in address_temp:
                    if ord(character) > 31 and ord(character) < 127:
#                     if character in string.printable:
#                     if re.match('[\w .,:/@]',character):
                        address += character
                hyperlinks_dict[display_text] = address
            except:
                print('Error getting this hyperlink...')
                return
            
    def is_hidden(self):
        return self.w32_slide.SlideShowTransition.Hidden

    def add_shape(self,shape_name):
        w32_shape = self.w32_slide.Shapes.Add()
        w32_shape.Name = shape_name
        self.shapes[shape_name] = PowerPointShape(self,w32_shape)
        self.presentation.shapes[shape_name] = self.shapes[shape_name]
        
    def export_bit_map(self,format='BMP'):
        file_name = '{}\\{}_{}_{}'.format(self.presentation.presentation_file_path,
                                                    self.presentation.presentation_name,
                                                    self.name,
                                                    'temp.image')
        self.w32_slide.Export(file_name, format)
        return file_name
        
    
    def paste_shape(self,shape_name):
        w32_shape_range = self.w32_slide.Shapes.Paste()
        w32_shape = w32_shape_range.Item(1)
        w32_shape.Name = shape_name
        self.shapes[shape_name] = PowerPointShape(self,w32_shape)
        self.presentation.shapes[shape_name] = self.shapes[shape_name]
        return self.shapes[shape_name]
    
    def get_notes_text(self):
        notes_text = ''
        for w32_shape in self.w32_slide.NotesPage.Shapes:
            if not w32_shape.Type == 14:
                continue
            if w32_shape.PlaceholderFormat.Type == pc.ppPlaceholderBody:
                if w32_shape.HasTextFrame and w32_shape.TextFrame.HasText:
                    paragraph_count = w32_shape.TextFrame.TextRange.Paragraphs().Count
                    for i in range(1,paragraph_count+1):
                        w32_paragraph = w32_shape.TextFrame.TextRange.Paragraphs(i)
                        character_count = w32_paragraph.Characters().Count
                        for j in range(1,character_count+1):
                            character = w32_paragraph.Characters(j).Text
                            if ord(character) > 31 and ord(character) < 127:
#                             if re.match('[\w .,:/@]',character):
#                             if character in string.printable:
                                notes_text += character
                            else:
                                print('what is this character???',character,ord(character))
                        notes_text += '\n'
        self.notes_text = notes_text
        return self.notes_text
        
class PowerPointSection():
    
    def __init__(self,presentation,section_index,section_name):
        self.presentation = presentation
        self.section_index = section_index
        self.name = section_name
        self.slides = {}
 
    def load_slides(self):
        #Under construction
        pass

    def add_member_slide(self,slide_name,slide):
        self.slides[slide_name] = slide
        
class PowerPointShape():
    
    def __init__(self,slide,w32_shape,index):
        self.slide = slide
        self.w32_shape = w32_shape
        self.index = index
        self.name = self.w32_shape.Name
        self.text = None
         
    def get_text(self):
        if self.w32_shape.HasTextFrame:
            if self.w32_shape.TextFrame.HasText:
                self.text = self.w32_shape.TextFrame.TextRange.Text
        return self.text
        
    def get_top(self):
        return self.w32_shape.Top
        
    def get_left(self):
        return self.w32_shape.Left

    def get_height(self):
        return self.w32_shape.Height

    def get_width(self):
        return self.w32_shape.Width
        
    def get_top_left(self):
        return self.get_top(), self.get_left()
        
    def get_shape_text(self,text_dict):

        def get_text(w32_shape,text_dict,shape_path):
            shape_text= ''
            if w32_shape.HasTextFrame:
                if w32_shape.TextFrame.HasText:
                    paragraph_count = w32_shape.TextFrame.TextRange.Paragraphs().Count
                    for i in range(1,paragraph_count+1):
                        w32_paragraph = w32_shape.TextFrame.TextRange.Paragraphs(i)
                        character_count = w32_paragraph.Characters().Count
                        shape_text = ''
                        for j in range(1,character_count+1):
                            character = w32_paragraph.Characters(j).Text
                            print(character)
                            if len(character) == 1 and ord(character) > 31 and ord(character) < 127:
#                             if character in string.printable:
                                shape_text += character
                    text_dict[shape_path] = shape_text

        def recurse_groups(w32_shape,text_dict,shape_path):
            try:
                shape_path = '{}~{}'.format(shape_path,w32_shape.Name)
            except:
                print('got exception for shape path =',shape_path)
                return
            get_text(w32_shape,text_dict,shape_path)
            shape_count = 0
            try:
                shape_count = w32_shape.GroupItems.Count
            except:
                return
            if shape_count > 0:
                for i in range(1,shape_count+1):
                    w32_group_shape = w32_shape.GroupItems.Item(i)
                    recurse_groups(w32_group_shape,text_dict,shape_path)

        recurse_groups(self.w32_shape,text_dict,str(self.slide.w32_slide.SlideID))

    def get_shape_box(self):
        top = self.get_top()
        left = self.get_left()
        height = self.get_height()
        width = self.get_width()
        return top, left, top+height, left+width
        
    def set_top(self,top):
        self.w32_shape.Top = top
        
    def set_left(self,left):
        self.w32_shape.Left = left

    def set_top_left(self,top,left):
        self.set_top(top)
        self.set_left(left)

    def set_width(self,width):
        self.w32_shape.Width = width
        
    def set_height(self,height):
        self.w32_shape.Height = height

