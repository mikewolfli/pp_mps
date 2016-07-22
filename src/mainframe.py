#!/usr/bin/env python
#coding:utf-8
"""
  Author:   10256603<mikewolf.li@tkeap.com>
  Purpose: 
  Created: 2016/3/14
"""

from global_list import *
from ldap3 import Server, Connection, SIMPLE, SYNC, ALL, SASL, NTLM

global login_info

import_headers = {'prod_order':'工单','batch_id':'批次','plant':'工厂','mat_no':'物料号',
                 'mat_name':'物料名称','wbs_no_box':'项目号/STO','mrp_controller':'MRP控制者',
                 'prod_scheduler':'生产计划','lift_type_d':'梯型','spn_date':'SPN日期','req_qty':'数量','receive_qty':'收货数量',
                 'start_date':'开始日期','fin_date':'完成日期','order_status':'订单状态','order_type':'工单类型',
                 'remarks':'文本'}
                 
tree_items=['工单导入']

class LoginForm(Toplevel):
    def __init__(self, parent, title=None):
        Toplevel.__init__(self, parent)

        self.withdraw()
        if parent.winfo_viewable():
            self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if self.parent is not None:
            #center(self.parent)
            self.geometry("+%d+%d" % (self.parent.winfo_rootx()+50,self.parent.winfo_rooty()+50))

        self.deiconify() # become visible now

        self.initial_focus.focus_set()

        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        
        #self.grab_set()
        
        self.wait_window(self) 
            
    def body(self, master):
        self.label1 = Label(master,text='用户名')
        self.label1.grid(row=0, column=0, sticky=W)
        self.uid_entry= Entry(master)
        self.uid_entry.grid(row=0, column=1, columnspan=2,  sticky=EW)       
        self.label2 = Label(master, text='密码')
        self.label2.grid(row=1, column=0, sticky=W)
        self.pwd_entry = Entry(master, show='*')
        self.pwd_entry.grid(row=1, column=1, columnspan=2, sticky=EW)
        self.msg_str=StringVar()
        self.label_message = Label(master, textvariable=self.msg_str).grid(row=2, column=0, columnspan=3, sticky=W)
        return self.uid_entry

    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="登陆", width=10, command=self.ok, default=ACTIVE)
        w.pack( side=LEFT, padx=5, pady=5)
        w = Button(box, text="取消", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
        
    def validate(self):  
        login_info['uid'] = self.uid_entry.get()
        login_info['pwd'] = self.pwd_entry.get()
        
        if len(login_info['uid'].strip())==0:
            self.msg_str.set('用户名不能为空')
            self.initial_focus=self.uid_entry
            self.initial_focus.focus_set()
            return 0
            
        s = Server('tkeasia.com', get_info=ALL)
        c = Connection(s, user="tkeasia\\"+login_info['uid'], password=login_info['pwd'], authentication=NTLM)
        ret = c.bind()
        if ret:
            login_info['status'] = True
            self.get_permission()
            self.log_login()
            return 1
        else:
            self.msg_str.set('登陆失败！')
            messagebox.showerror('错误', c.last_error)
            return 0
        
    def destroy(self):
        self.initial_focus = None
        Toplevel.destroy(self)    
        
    def cancel(self, event=None):
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()
        
        if pg_db.get_conn():
            pg_db.close()
            
        if mps_db.get_conn():          
            mps_db.close()
            
        sys.exit()
        
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()        
        self.destroy()
        
    def log_login(self):
        if not mps_db.get_conn():
            mps_db.connect()
              
        login_record = login_log.select().where((login_log.employee==login_info['uid'])&(login_log.log_status==True))
        if len(login_record) >0:   
            log_loger = login_log.update(log_status=False).where((login_log.employee==login_info['uid'])&(login_log.log_status==True))
            log_loger.execute()
        
        
        log_loger = login_log.insert(employee=login_info['uid'], log_status=True, login_time=datetime.datetime.now())
        log_loger.execute()
    
    def get_permission(self):
        try:
            perm = op_permission.get(op_permission.employee==login_info['uid'])
            login_info['perm']= perm.perm_code
        except op_permission.DoesNotExist:
            pass

class mainframe(Frame):
    import_tab = None
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        pg_db.connect()          
        if not mps_db.get_conn():
            mps_db.connect()
                                    
    def createWidgets(self):
        self.ntbook = ttk.Notebook(self)
        self.ntbook.grid(row=0, column=2, rowspan=2, sticky=NSEW)
        
        self.tree = ttk.Treeview(self,columns=('col0'), displaycolumns=(),selectmode='browse')
        self.tree.column('#0', width=150)
        self.tree.column('col0',width=0)
        self.tree.heading('#0', text='')
        self.tree.heading('col0', text='')
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.grid(row=0, column=0, sticky=NS)
        ysb.grid(row=0, column=1, sticky=NS)
        xsb.grid(row=1,column=0, sticky=EW)
        
        tree_root = self.tree.insert('','end', text='操作列表', open =True)
        for item in tree_items:
            self.tree.insert(tree_root, 'end', text=item, values=(-1), open=False)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.ntbook.rowconfigure(0, weight=1)
        self.ntbook.columnconfigure(0, weight=1)
        self.grid()
        self.tree.bind('<<TreeviewSelect>>', self.select_func)
        self.ntbook.bind('<<NotebookTabChanged>>', self.tab_changed)
                
    def tab_changed(self, event):
        if not login_info['status']:
            return
        
        i_sel = int(self.ntbook.index(CURRENT))
        root = self.tree.get_children()
        if not root :
            return
        ch_items = self.tree.get_children(root)
        for item in ch_items:
            if i_sel == int(self.tree.item(item, 'values')[0]):
                self.tree.selection_set(item)
                return    
        
    def select_func(self,event=None):
        if not login_info['status']:
            return
        
        select = self.tree.selection()        
        if not select :
            return
               
        sel=select[0]
        i_per = int(self.tree.item(sel, 'values')[0])
        s_perm = login_info['perm']
                      
        i_sel = self.ntbook.index(END)
        
        if i_per==-1:
            nt_title=self.tree.item(sel, 'text')
            i_index=tree_items.index(nt_title)
            if i_index==0:
                if not self.import_tab and int(s_perm[i_index])>0:
                    self.import_tab = import_pane(self) 
                    self.ntbook.add(self.import_tab, text=nt_title, sticky=NSEW)
                    self.tree.set(sel, 'col0', i_sel)
                    self.ntbook.select(i_sel)
                else:
                    return
        else:
            if int(s_perm[i_per]) <= 0:
                return
                
            self.ntbook.select(i_per)
            
class import_pane(Frame):
    '''
    权限
    1 - VIEW
    2 - 导入工单
    3 - 
    '''
    def __init__(self, master=None):
        Frame.__init__(self, master)
        wg_group1=Frame(self)
        wg_group1.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        
        self.import_order = Button(wg_group1, text="导入工单")
        self.import_order.grid(row=0, column=0)
        self.import_order['command']=self.import_pd_order
        
        table_panel= Frame(self)
        model = TableModel(rows=0, columns=0)
        self.mat_table = Table(table_panel, model, editable=False)
        self.mat_table.show()
        
        self.mat_table.grid(row=0, column=0, rowspan=2, columnspan=2, sticky=NSEW)
        table_panel.columnconfigure(1, weight=1)
        table_panel.rowconfigure(1, weight=1)
        table_panel.grid(row=2, column=0, rowspan=6, columnspan=6, sticky=NSEW)
        self.grid(row=0, column=0, sticky=NSEW)
        self.columnconfigure(5, weight=1)
        self.rowconfigure(2, weight=1)           
        
    def import_pd_order(self):
        file_name = filedialog.askopenfilename(title="导入工单", filetypes=[('excel file','.xls'),('excel file','.xlsx'),('excel file','.xlsm')]) 
        if not file_name:
            return
        
        df = pd.read_excel(file_name,sheetname=0)
        model = TableModel(dataframe=df)
        self.mat_table.updateModel(model) 
        return
        
class Application():
    def __init__(self, root):
        main_frame = mainframe(root)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.grid(row=0, column=0, sticky=NSEW)
        LoginForm(main_frame,'用户登陆')
   
        root.protocol("WM_DELETE_WINDOW", self.quit_func)

    def quit_func(self):
        if pg_db.get_conn():
            pg_db.close()
            
        if mps_db.get_conn() and login_info['status']:
            log_loger = login_log.update(logout_time = datetime.datetime.now(), log_status=False).where((login_log.employee==login_info['uid'])&(login_log.log_status==True))
            log_loger.execute()            
            mps_db.close()
        root.destroy()
                
if __name__ == '__main__':   
    root=Tk() 
    #root.resizable(0,    
    #root.attributes("-zoomed", 1) # this line removes the window managers bar
                
    try:                                   # Automatic zoom if possible
        root.wm_state("zoomed")
    except TclError:                    # Manual zoom
        # get the screen dimensions
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        # borm: width x height + x_offset + y_offset
        geom_string = "%dx%d+0+0" % (width, height)
        root.wm_geometry(geom_string)
        
    root.title('钣金喷涂MPS')
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=10)  
    root.option_add("*Font", default_font)
    Application(root)
    root.geometry('800x600')
    root.mainloop()