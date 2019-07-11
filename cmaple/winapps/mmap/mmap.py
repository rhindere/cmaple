'''
Created on Apr 30, 2018

@author: Ron Hinderer - rhindere@cisco.com
'''
from pprint import pprint
from collections import OrderedDict
from os.path import isfile, join
from cmaple.winapps.win_base import WinBase
import win32com.client
import sys
mc = win32com.client.constants
try:
    test = mc.mmCommandBarExport
except AttributeError as err:
    mc = win32com.client.gencache.EnsureDispatch("MindManager.Application")
    del mc
    mc = win32com.client.constants


class MindManagerApp(WinBase):
    def __init__(self, **kwargs):
        kwarg_defaults = {'verify': False, 'cmd_retries': 5, 'backoff_timer': 30,
                          'persist_responses': True, 'restore_responses': False, 'leaf_dir': None}

        for key, val in kwargs.items():
            kwarg_defaults[key] = val

        self.__dict__.update(kwarg_defaults)

        super(MindManagerApp, self).__init__()

        self.w32_app = self.get_mm_app()

        self.mmaps = {}
        
    def get_mm_app(self):
        try: 
            m = win32com.client.GetActiveObject("MindManager.Application")
    
        except:
            m = win32com.client.Dispatch("MindManager.Application")
        if m:
            m.Visible = True
            return m
        else:
            return None

    def add_mmap(self, mmap_file_path, mmap_name):
        mmap = MindManagerMap(self, mmap_file_path, mmap_name)
        self.mmaps[mmap_name] = mmap
        return mmap


class MindManagerMap:
    
    def __init__(self, app, mmap_file_path, mmap_name):
        self.app = app
        self.mmap_file_path = mmap_file_path
        self.name = mmap_name
        self.w32_mmap = self.get_mmap()
        self.central_topic = MindManagerCentralTopic(self, self.w32_mmap.CentralTopic.Text)
        self.load_topics()
    
    def get_mmap(self):
        if not self.app:
            return None
        w32_app = self.app.w32_app
        mmap_path = '{}\\{}'.format(self.mmap_file_path, self.name)
        print(mmap_path)
        if isfile(mmap_path):
            for w32_mmap in w32_app.AllDocuments:
                if w32_mmap.Name == self.name:
                    return w32_mmap
            w32_app.AllDocuments.Open(mmap_path)
            w32_mmap = w32_app.ActiveDocument
            return w32_mmap
        else:
            w32_app.AllDocuments.Add()
            w32_app.ActiveDocument.SaveAs(mmap_path)
            w32_mmap = w32_app.ActiveDocument
            return w32_mmap
        return None
    
    def clear_mmap(self):
        for w32_topic in self.w32_mmap.CentralTopic.AllSubTopics:
            w32_topic.Delete()
        
    def get_central_topic(self):
        return MindManagerCentralTopic(self, self.w32_mmap.CentralTopic.Text)
    
    def load_topics(self):
        pass


class MindManagerTopic:
    
    def __init__(self, parent_topic, w32_topic, topic_name):
        self.parent_topic = parent_topic
        self.w32_topic = w32_topic
        self.name = topic_name
        self.notes_text = None
        self.sub_topics = []
        self.load_sub_topics()
 
    def load_sub_topics(self):
        for w32_topic in self.w32_topic.AllSubTopics:
            self.sub_topics.append(MindManagerTopic(self, w32_topic, w32_topic.Text))
    
    def add_hyperlink(self, hyperlink):
        w32_topic_hyperlink = self.w32_topic.CreateHyperlink(hyperlink)
        return w32_topic_hyperlink

    def add_hyperlink_to_topic(self, guid):
        w32_topic_hyperlink_to_topic = self.w32_topic.CreateHyperlinkToTopicByGuid(guid)
        return w32_topic_hyperlink_to_topic

    def add_sub_topic(self, topic_name, position=0):
        w32_topic = None
        w32_topic = self.w32_topic.AddSubTopic(topic_name)
        if not position == 0:
            self.w32_topic.AllSubTopics.Insert(w32_topic, 1)
        self.sub_topics.append(MindManagerTopic(self, w32_topic, topic_name))
        return self.sub_topics[-1]

    def add_callout_topic(self, topic_name):
        w32_topic = self.w32_topic.AllCalloutTopics.Add()
        w32_topic.Text = topic_name
        self.sub_topics.append(MindManagerTopic(self, w32_topic, topic_name))
        return self.sub_topics[-1]

    def change_topic_name(self, topic_name):
        self.name = topic_name
        self.w32_topic.Text = topic_name

    def clear_sub_topics(self):
        for w32_topic in self.w32_topic.AllSubTopics:
            w32_topic.Delete()

    def get_sub_topic(self,sub_topic_name):
        for sub_topic in self.sub_topics:
            print(sub_topic_name, sub_topic.name)
            if sub_topic.name == sub_topic_name:
                return sub_topic
        return None
        
    def set_notes(self, notes_text):
        self.w32_topic.Notes.Text = notes_text
        self.notes_text = self.w32_topic.Notes.Text
        return self.notes_text
        
    def paste_topic(self, shape_name):
        pass


class MindManagerCentralTopic(MindManagerTopic):
    
    def __init__(self, mmap, topic_name):
        self.mmap = mmap
        self.w32_central_topic = self.mmap.w32_mmap.CentralTopic
        super().__init__(self, self.w32_central_topic, topic_name)

    def add_balanced_sub_topic(self, topic_name):
        w32_topic = self.w32_central_topic.AddBalancedSubTopic(topic_name)
        self.sub_topics.append(MindManagerTopic(self, w32_topic, topic_name))
        return self.sub_topics[-1]

