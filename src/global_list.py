#!/usr/bin/env python
#coding:utf-8
"""
  Author:   10256603<mikewolf.li@tkeap.com>
  Purpose: 
  Created: 2016/3/23
"""
import tkinter
from tkinter import *
from tkinter import simpledialog
from tkinter import font
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog
import datetime
import tkinter.ttk as ttk
from mps_dataset import *
from openpyxl import Workbook, load_workbook, reader
import openpyxl.writer.excel as excel_xlsx
#from tkintertable import *
import pandas as pd
from pandastable import Table, TableModel
import threading
import time
from tkcalendar import *


login_info ={'uid':'','pwd':'','status':False,'perm':'0000'}
'''
界面权限：
0 - 无权限
1 - 只读权限
9 - 管理员权限

2 - 电气自制
3 - 钣金自制
4 - PSM
5 - CO Run
6 - 曳引机自制
'''  

class date_picker(simpledialog.Dialog): 
    result=None
    def body(self, master):
        from_label=Label(master,text='from')
        from_label.grid(row=0, column=0, sticky=EW)
        self.from_var = StringVar()
        self.from_input = Entry(master,textvariable=self.from_var,state='readonly')
        self.from_input.grid(row=0, column=1, columnspan=2, sticky=EW)
        to_label=Label(master, text='to')
        to_label.grid(row=1, column=0, sticky=EW)
        self.to_var = StringVar()
        self.to_input = Entry(master, textvariable=self.to_var, state='readonly')
        self.to_input.grid(row=1, column=1, columnspan=2, sticky=EW)
        self.from_button=Button(master, text='...')
        self.from_button['command']=self.from_click
        self.from_button.grid(row=0, column=3)
        self.to_button=Button(master,text='...')
        self.to_button['command']=self.to_click
        self.to_button.grid(row=1, column=3)
        self.from_var.set(strdate)
        self.to_var.set(strdate)
        return self.from_button
        
    def from_click(self):
        tkCalendar(self, year, month, day, self.from_var )
        
    def to_click(self):
        tkCalendar(self, year, month, day, self.to_var )        
        
    def validate(self):
        self.from_date = str2date(self.from_var.get())
        self.to_date=str2date(self.to_var.get())
        if self.from_date is None or self.to_date is None:
            messagebox.showerror('提示','请务必选择一个日期')
            return 0
        
        if self.from_date > datetime.datetime.today() or self.to_date > datetime.datetime.today():
            messagebox.showerror('提示','请选择早于今天的日期')
            return 0
            
        if self.from_date>self.to_date:
            messagebox.showerror('提示','from日期请务必小于to日期')
            return 0
            
        return 1
        
    def apply(self):        
        self.result={'from':self.from_date, 'to':self.to_date}

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    #i = cols.index(col)

    #l.sort(key=lambda t: t[i], reverse=reverse)
    l.sort(reverse=reverse)
    #      ^^^^^^^^^^^^^^^^^^^^^^^

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col,command=lambda: treeview_sort_column(tv, col, not reverse))
'''       
def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))
'''
    
class ScrolledTextDlg(simpledialog.Dialog):
    def __init__(self, title, method=0, parent=None, initialvalue=None):  
        if not parent:
            parent = tkinter._default_root
        
        self.initialvalue = initialvalue
        self.method=method
        
        simpledialog.Dialog.__init__(self, parent, title)
        
    def body(self, master):
        list_title= Label( master, text='WBS list')
        list_title.pack()
        self.textfield = scrolledtext.ScrolledText( master)
        self.textfield.pack()
        self.textfield.bind_all('<Control-v>', self.copy_ev) 
        self.textfield.bind('<Control-V>', self.copy_ev) 
        self.textfield.bind("<Next>", self.change_line)
        self.textfield.bind("<Alt-L>", self.change_line)
          
        if self.initialvalue is not None:
            self.textfield.delete('1.0',END)
            self.textfield.insert(END, self.initialvalue)
                    
        return self.textfield
    
    def change_line(self, event):
        self.textfield.insert(END,'\n')
        
    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            return 0
        
        res_list = result.split('\n')
        
        res_res=[]
        count=0
        for res in res_list:
            if len(res.rstrip())==0:
                continue
            
            if len(res.rstrip())!=9 and self.method==0:
                messagebox.showwarning("Illegal value", '物料号字符串长度为9位')
                return 0 
                
            if len(res.rstrip())!=14 and self.method==1:
                messagebox.showwarning("Illegal value", 'WBS No字符串长度为14位')
                return 0                 
            
            if self.method==0:
                l = list(res)
                for i in range(len(l) - 1, -1, -1):
                    if not(48 <= ord(l[i]) <= 57): 
                        messagebox.showwarning("Illegal value", '请输入数值')
                        return 0
                    
            count+=1                
            res_res.append(res.rstrip())

        if count==0:
            return 0
                   
        if messagebox.askyesno('是否继续','执行数据数量: '+str(count)+' 条;此操作不可逆，是否继续(YES/NO)?')==NO:
            return 0
        
        self.result=res_res
        return 1
    
    def destroy(self):
        self.textfield=None
        simpledialog.Dialog.destroy(self)        
            
    def getresult(self):
        return self.textfield.get('1.0',END)

    def copy_ev(self, event):
        #self.textfield.delete('1.0',END)
        self.textfield.clipboard_get()
    

def ask_list(title, method=0):
    d=ScrolledTextDlg(title, method)
    return d.result

def value2key(dic, value):
    if not isinstance(dic, dict):
        return None
    
    for key, val in dic.items():
        if val == value:
            return key
    
    return None

def date2str(dt_s):
    if not isinstance(dt_s, datetime.datetime):
        return None
    else:
        return dt_s.strftime("%Y-%m-%d") 

def datetime2str(dt_s):
    if not isinstance(dt_s, datetime.datetime):
        return None
    else:
        return dt_s.strftime("%Y-%m-%d %H:%M:%S") 
    
def str2date(dt_s):
    if dt_s is None or (len(dt_s)==0 and isinstance(dt_s, str)):
        return None
    else:
        return datetime.datetime.strptime(dt_s , '%Y-%m-%d')
    
def str2datetime(dt_s):
    if dt_s is None or (len(dt_s)==0 and isinstance(dt_s, str)) :
        return None
    else:
        return datetime.datetime.strptime(dt_s, "%Y-%m-%d %H:%M:%S") 

def none2str(val):
    if not val:
        return ''
    else:
        return val
        
def get_name(pid):
    if pid=='' or not pid:
        return ''
    try: 
        r_name = s_employee.get(s_employee.employee==pid)
        s_name = r_name.name
    except s_employee.DoesNotExist:
        return 'None'

    return s_name