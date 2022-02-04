# -*- coding: utf-8 -*-


import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as dialog
import tkinter.messagebox as messagebox
import tkinter.font as font
import numpy

import utility_ima.tkintertool_ima as tkima
import utility_ima.read_sequence as read_
import utility_ima.write_sequence as write_

# 単体用
# import tkintertool_ima as tkima
# import read_sequence as read_
# import write_sequence as write_

__author__ = "Hiroki Imawaka <u801286h@ecs.osaka-u.ac.jp>"

#パスが書いてあるファイル
PATH_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/foldersettings.txt'

#GUI用の定数
PORT_a = ['ch0', 'ch1', 'ch2', 'ch3']
PORT_l = ['logic0', 'logic1', 'logic2', 'logic3', 'logic4', 'logic5', 'logic6', 'logic7']
bgCOLOR = 'white'
analogCOLOR = 'pink'
logicCOLOR = 'LightSkyBlue'
ITEMS_PARATAB = ["NUM_LOOP", "PULSE_DELAY"]
EXPERIMENT = ["'stepwise'", "'once'", "'array'", "'voltage_only'"]
VARIABLE = ["start", "stop", "span"]
PORT10 = [str(i) for i in range(1, 11)]
PORT4 = [str(i) for i in range(1, 5)]


def is_num(s):
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

def rejectLF(list):
    '''
    listの各要素の右端にある改行を取り払う
    '''
    result = [line.rstrip('\n') for line in list]
    return result

def bool_to_str01(b):
    if b:
        return '1'
    elif b == False:
        return '0'
        
def str01_to_bool(s):
    if s == '0':
        return False
    elif s == '1':
        return True

class Settings(dict):
    '''
    辞書型
    '''
    def __init__(self):
        self["experiment"] = "'stepwise'" # 実験の種類
        self["var"] = "'T_90'" # 2つめの変数の有無(0 or 1)
        self["stepwise_start"] = '9.2' # stepwiseの際のstart
        self["stepwise_stop"] = '6.6' # stepwiseの際のstop
        self["stepwise_span"] = '0.01' # stepwiseの際のspan
        self["var_start"] = '10' # varのstart
        self["var_stop"] = '120' # varのstop
        self["var_span"] = '10' # varのspan

        self["DAC229_T1_CH2_AMPLITUDE"] = '1.0'
        self["DAC229_T1_CH2_PHASE"] = '0.0 * numpy.pi'
        self["POWER_SUPPLY_VOLTAGE"] = '6.8'
        self["NUM_LOOP"] = '1000'
        self["PULSE_DELAY"] = '20e-3'
        self["DAC_LATENCY"] = '000.0e-9'
        self["ADC_LATENCY"] = '200e-9'
        self["LOGIC_LATENCY"] = '0.0'
        self["DAC229_T1_CH2_AMPLITUDE"] = '1.0'
        self["DAC229_T1_CH2_PHASE"] = '0.0 * numpy.pi'

class Sequences():
    def __init__(self):
        self.analog = dict()
        for i in range(4):
            self.analog['ch'+str(i)] = []
        self.logic = dict()
        for i in range(8):
            self.logic['logic'+str(i)] = []
        self.analog_use = ['0'] * 4
        self.logic_use = ['0'] * 8
        self.names = dict()
        self.paras = dict()
        self.sequence = []
        self.vartexts = dict()

class Pathes():
    def __init__(self):
        self.projectname = ''
        self.settingname = ''
        self.dir_setting = ''
        self.dir_data = ''
        self.nowopening = ''

class Application():
    '''
    渡すと想定されるもの
    self.set:色々な設定が入っている
    self.seq:シーケンス
    self.path:パスやタイトルなど
    self.pytext:PulseProgramFileの原文をlist化したものなど
    self.memotext:メモ
    self.set10Vflag:10Vにするかどうか
    self.button_exe:実験実行ボタン
    '''
    def __init__(self, master=None):
        self.master = master
        self.master.config(bg=bgCOLOR)
        self.master.geometry("1300x1000")
        self.master.title("ESR")

        self.set = Settings()
        self.seq = Sequences()
        self.path = Pathes()
        self.memotext = ''
        self.set10Vflag = tkima.BooleanVar(set=True)

        self.create_window_init()
        self.create_titleframe_init()
        self.create_tabs_init()
        self.create_sidespace_init()
        self.read_pathsetting()
        self.create_exptab_init()
        self.create_paratab_init()
        self.create_pathtab_init()

    """---------------------init---------------------"""

    def create_window_init(self):
        '''
        メインウインドウの初期状態を作る

        widgets
            self.frame_title:タイトルのウィジェットを置く

            btnframe_l:下2つの親Frame
            savebutton:設定を保存するButton
            openbutton:設定を開くButton

            btnframe_r:下のボタンの親Frame
            exebutton:これを渡すイメージ

        display(self.master)
            row:
                0       空白20
                1       self.frame_title
                2       メインのタブFrame(weight=1)
                3       空白20
                4       btnframe_l, btnframe_r
                5       空白5

            column:
                0       self.frame_title, メインのタブFrame(weight=1)
                1       self.frame_title, メインのタブFrame, btnframe_l
                2       self.frame_title, メインのタブFrame(minsize=400)
                3       self.frame_title, メインのタブFrame, btnframe_r
                4       右のスペース(minsize=250)
        '''
        tkima.grid_config(self.master,  rlist=[[0, 'minsize', 20], [2, 'weight', 1], [3, 'minsize', 20], [5, 'minsize', 5]],
                                        clist=[[0, 'weight', 1], [2, 'minsize', 400], [4, 'minsize', 250]])
        self.frame_title = tkima.Frame(self.master, bg=bgCOLOR, row=1, column=0, columnspan=4, sticky='nsew')
        btnframe_l = tkima.Frame(self.master, bg=bgCOLOR, row=4, column=1, sticky='nsew')
        btnframe_r = tkima.Frame(self.master, bg=bgCOLOR, row=4, column=3, sticky='nsew')
        tkima.Button(btnframe_l, text="save", command=self.save_all, row=0, column=0)
        tkima.Button(btnframe_l, text="open", command=self.open_setting, row=0, column=1)
        self.button_exe = tkima.Button(btnframe_r, text="EXECUTE", row=0, column=0)

    def create_titleframe_init(self):
        '''
        self.frame_titleについて

        widgets
            self.entry_settingname:設定のタイトル
            self.entry_projectname:保存先のタイトル
        '''
        tkima.grid_config(self.frame_title, clist=[[(0, 6), 'weight', 1], [3, 'minsize', 30]])
        tkima.Label(self.frame_title, text="Setting", bg=bgCOLOR, row=0, column=1)
        self.entry_settingname = tkima.Entry(self.frame_title, row=0, column=2)
        tkima.Label(self.frame_title, text="Project", bg=bgCOLOR, row=0, column=4)
        self.entry_projectname = tkima.Entry(self.frame_title, row=0, column=5)

    def create_tabs_init(self):
        '''
        GUIのメインフレーム(タブ)作り

        widgets
            self.nb:大元(タブ付きFrame)
            self.seqtab:
            self.exptab:
            self.paratab:
            self.filetab:
        '''
        self.nb = ttk.Notebook(self.master)
        self.seqtab = tk.Frame(self.nb, bg=bgCOLOR)
        self.exptab = tk.Frame(self.nb, bg=bgCOLOR)
        self.paratab = tk.Frame(self.nb, bg=bgCOLOR)
        self.filetab = tk.Frame(self.nb, bg=bgCOLOR)
        self.nb.add(self.seqtab, text="sequence", padding=2)
        self.nb.add(self.exptab, text="experiment", padding=2)
        self.nb.add(self.paratab, text="parameters", padding=2)
        self.nb.add(self.filetab, text="path", padding=2)
        self.nb.grid(row=2, column=0, columnspan=4, sticky='nsew')

    def create_sidespace_init(self):
        '''
        右側のスペースを作る
        常に置いとくタイプのwidget案あれば

        widgets
            sideframe:下のwidgetたちの親

            self.check_set10V:10VにするかどうかのCheckbutton
            memoframe:'memo'という文字がついているLabelFrame
            self.txtbox_memo:入力Entry

        display
            row:
                0       self.check_set10V
                1       空白20
                2       memoframe
        '''
        sideframe = tkima.Frame(self.master, bg=bgCOLOR, row=2, column=4)
        tkima.grid_config(sideframe, rlist=[[1, 'minsize', 20]])
        self.check_set10V = tkima.Checkbutton(sideframe, text="set10V?", variable=self.set10Vflag, row=0, column=0)
        memoframe = tkima.LabelFrame(sideframe, text="memo", labelanchor="nw", row=2, column=0)
        self.txtbox_memo = tkima.Text(memoframe, height=10, width=20, undo=True, wrap=tk.WORD, bg=bgCOLOR, highlightthickness=0, row=0, column=0)

    def read_pathsetting(self):
        '''
        設定が置いてあるpath、データを保存するpathが書いてあるtextファイルから読み込む
        '''
        with open(PATH_FOLDER, 'r') as f:
            paths = rejectLF(f.readlines())
        self.path.dir_setting = paths[0]
        self.path.dir_data = paths[1]

    def create_exptab_init(self):
        '''
        実験方法のタブ

        self.exwidgetsは、実験方法によって表示の変わるもの
            [0] 固定電圧
            [1] var指定Combo
            [2] Entry(stepwise_start)
            [3] Entry(stepwise_stop)
            [4] Entry(stepwise_span)
            [5] Entry(var_start)
            [6] Entry(var_stop)
            [7] Entry(var_span)
        '''
        tkima.grid_config(self.exptab, rlist=[[(0, 2), 'minsize', 10]], clist=[[0, 'minsize', 10], [2, 'weight', 1]])
        self.frame_experiment = tkima.Frame(self.exptab, row=3, column=2, sticky='news')
        self.combo_experiment = tkima.Combobox(self.exptab, value=tuple(EXPERIMENT), width=10, init=self.set["experiment"], bind_selected=self.combo_experiment_selected, row=1, column=1)
        tkima.grid_config(self.frame_experiment, rlist=[[(0, 2, 4), 'minsize', 10]], clist=[[1, 'minsize', 10]])
        self.frame_var = tkima.Frame(self.frame_experiment)

        l = []
        for key in self.seq.names.keys():
            t = "'" + key + "'"
            l.append(t)

        self.exwidgets = []
        tkima.Entry(self.frame_experiment, width=5, grid=False, init=self.set["POWER_SUPPLY_VOLTAGE"], list=self.exwidgets)
        tkima.Combobox(self.frame_experiment, width=8, grid=False, value=tuple(l), init=self.set["var"], list=self.exwidgets)
        tkima.Entry(self.frame_var, width=5, grid=False, init=self.set["stepwise_start"], list=self.exwidgets)
        tkima.Entry(self.frame_var, width=5, grid=False, init=self.set["stepwise_stop"], list=self.exwidgets)
        tkima.Entry(self.frame_var, width=5, grid=False, init=self.set["stepwise_span"], list=self.exwidgets)
        tkima.Entry(self.frame_var, width=5, grid=False, init=self.set["var_start"], list=self.exwidgets)
        tkima.Entry(self.frame_var, width=5, grid=False, init=self.set["var_stop"], list=self.exwidgets)
        tkima.Entry(self.frame_var, width=5, grid=False, init=self.set["var_span"], list=self.exwidgets)

    def create_pathtab_init(self):
        '''
        pathタブwidget作成

        widgets
            self.setpathlabel:'setting'というLabel
            self.savepathlabel:'data'というLabel

            self.pathentries[]:
                [0]:設定が置いてあるpathのEntry
                [1]:データを保存するpathのEntry

            self.pathbuttons[]:それぞれのディレクトリ変更Button達

            self.newpathbuttons[]:それぞれのディレクトリ作成Button達

        display
            row:
                0       空白(weight=1 with 4)
                1       設定が置いてあるpath
                2       空白50
                3       データを保存するpath
                4       空白(weight=1 with 0)

            column:
                0       空白(weight=1 with 8)
                1       path項目名Label
                2       空白10
                3       path入力Entry
                4       空白5
                5       ディレクトリ変更Button
                6       空白5
                7       ディレクトリ作成Button
                8       空白(weight=1 with 0)
        '''
        tkima.grid_config(self.filetab, rlist=[[(0, 4), 'weight', 1], [2, 'minsize', 50]], clist=[[(0, 8), 'weight', 1], [2, 'minsize', 10], [(4, 6), 'minsize', 5]])

        tkima.Label(self.filetab, text="setting", bg=bgCOLOR, row=1, column=1)
        tkima.Label(self.filetab, text="data", bg=bgCOLOR, row=3, column=1)
        self.pathentries = []
        self.pathbuttons = []
        self.newpathbuttons = []
        dummy = [self.path.dir_setting, self.path.dir_data]
        for i in range(2):
            tkima.Entry(self.filetab, width=50, init=dummy[i], row=2*i+1, column=3, list=self.pathentries)
            tkima.Button(self.filetab, text="change", command=self.change_path(index=i), row=2*i+1, column=5, list=self.pathbuttons)
            tkima.Button(self.filetab, text="make folder", command=self.make_newdir(index=i), row=2*i+1, column=7, list=self.newpathbuttons)

    def create_paratab_init(self):
        '''
        display
            row:
                0       空白10
                1       積算
                2       空白5
                3       REP
                4       空白5

            column:
                0       空白10
                1       項目名
                2       空白20
                3       入力欄
                4       単位あれば
                5       空白(weight=1)
        '''
        n = len(ITEMS_PARATAB)
        tkima.grid_config(self.paratab, rlist=[[0, 'minsize', 10]], clist=[[0, 'minsize', 10], [2, 'minsize', 20], [5, 'weight', 1]])

        for i in range(n):
            tkima.Label(self.paratab, text=ITEMS_PARATAB[i], row=2*i+1, column=1)
            tkima.grid_config(self.paratab, rlist=[[2*i+2, 'minsize', 5]])
            
        self.spin_accumulation = tkima.Spinbox(self.paratab, from_=0, to=100000, increment=100, init=self.set["NUM_LOOP"], width=5, row=1, column=3)
        self.entry_rep_time = tkima.Entry(self.paratab, width=10, init=self.set["PULSE_DELAY"], row=3, column=3)
        tkima.Label(self.paratab, text="s", row=3, column=4)

    """---------------------open, reload---------------------"""

    def open_setting(self):
        '''
        openボタンを押したあと表示する関数まとめ
            1. 設定ファイルのあるフォルダが存在するか
            2. 設定ファイルのあるpathを保存
            3. 開くテキストファイルを選択
            4. 今あるwidgetを一掃
            5. タイトルを更新
            6. 設定をlistに格納
            7. 表示
        '''
        # 1
        res = self.ask_make_settingfolder()
        if res == False:
            print("--- open cancelled")
            return
        # 2
        self.save_paths_into_txtfile_from_entries()
        # 3
        beforefile = self.path.nowopening
        self.select_setting()
        if self.path.nowopening == '':
            print("--- filedialog cancelled")
            self.path.nowopening = beforefile
            return
        # 4
        self.clear_widgets()
        # 5
        self.reload_widgets_on_titleframe()
        # 6
        self.set = Settings()
        self.seq = Sequences()
        self.pyfile = read_.Main(self.path.nowopening, self.set, self.seq)
        # 7
        self.reload_widgets_on_seqtab()
        self.reload_widgets_on_paratab()
        self.reload_widgets_on_exptab()

        print("--- setting opened")
        print("    ( "+self.path.nowopening+" )")

    def select_setting(self):
        '''
        設定ファイル選択

        note
            self.path.nowopening:設定ファイルのpath
        '''
        fTyp = [("", "*.py")] #["", "*.txt"]とすればtxtのみ読み込む
        iDir = self.path.dir_setting
        self.path.nowopening = dialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
        self.path.projectname = os.path.basename(self.path.nowopening).split('.')[0]
        self.path.settingname = os.path.basename(self.path.nowopening).split('.')[0]

    def reload_widgets_on_titleframe(self):
        '''
        タイトルを更新する
        '''
        self.entry_settingname.overwrite(self.path.projectname)
        self.entry_projectname.overwrite(self.path.settingname)

    def reload_widgets_on_exptab(self):
        '''
        self.frame_experimentの1, 3, 5行目に色々配置
        openした時用の部分+_reload_widgets_on_exptab()
        '''
        l = []
        for key in self.seq.names.keys():
            t = "'" + key + "'"
            l.append(t)

        self.exwidgets[0].overwrite(self.set["POWER_SUPPLY_VOLTAGE"])
        self.exwidgets[1].config(value=tuple(l))
        self.exwidgets[1].overwrite(self.set["var"])
        self.exwidgets[2].overwrite(self.set["stepwise_start"])
        self.exwidgets[3].overwrite(self.set["stepwise_stop"])
        self.exwidgets[4].overwrite(self.set["stepwise_span"])
        self.exwidgets[5].overwrite(self.set["var_start"])
        self.exwidgets[6].overwrite(self.set["var_stop"])
        self.exwidgets[7].overwrite(self.set["var_span"])  
        self.combo_experiment.overwrite(self.set["experiment"])
        self._reload_widgets_on_exptab()

    def _reload_widgets_on_exptab(self):
        '''
        self.frame_experimentの1, 3, 5行目に色々配置
        '''
        e = self.combo_experiment.get()
        if e == "'array'":
            tkima.Label(self.frame_experiment, text='voltage', row=1, column=0)
            self.exwidgets[0].grid(row=1, column=2)
            self.exwidgets[1].grid(row=3, column=0)
            self.frame_var.grid(row=3, column=2)
            tkima.grid_config(self.frame_var, clist=[[(2, 5), 'minsize', 5]])
            for i in range(3):
                tkima.Label(self.frame_var, text=VARIABLE[i], row=0, column=3*i)
                self.exwidgets[5+i].grid(row=0, column=3*i+1)
        elif e == "'once'" or e == "'voltage_only'":
            tkima.Label(self.frame_experiment, text='voltage', row=1, column=0)
            self.exwidgets[0].grid(row=1, column=2)
        elif e == "'stepwise'":
            tkima.Label(self.frame_experiment, text='voltage', row=1, column=0)
            self.frame_var.grid(row=1, column=2)
            tkima.grid_config(self.frame_var, clist=[[(2, 5), 'minsize', 5]])
            for i in range(3):
                tkima.Label(self.frame_var, text=VARIABLE[i], row=0, column=3*i)
                self.exwidgets[2+i].grid(row=0, column=3*i+1)

    def reload_widgets_on_seqtab(self):
        '''
        sequenceタブwidget作成

        widgets
            self.combos_seqname:'90pulse'とか、シーケンス名のComboboxのlist

            self.frames_onoff_analog:analogポートのON/OFFを切り替えるボタンのようなFrameのlist[4][n]
            self.blnvars_onoff_analog:それのON/OFFを1/0で保存するBooleanVarのlist[4][n]

            self.frames_onoff_logic:logicポートのON/OFFを切り替えるボタンのようなFrameのlist[8][n]
            self.blnvars_onoff_logic:それのON/OFFを1/0で保存するBooleanVarのlist[8][n]

        display
            row:
                0       空白(weight=1)
                1       self.combos_seqname
                2       何もなし(予備)
                3       空白5
                4       'analog'と言う文字
                2j+5    self.frames_onoff_analog
                2j+6    self.separator
                13      analogを加えるボタン(Nは使うch数)
                14      空白5
                15      'logic'と言う文字
                2j+16   self.frames_onoff_analog
                2j+17   self.separator
                34      logicを加えるボタン(Nは使うch数)
                35      空白5
                36      addボタン、delボタン
                37      空白(weight=1)

            column:
                0       空白30
                1       ch名
                2       空白5
                3+i     シーケンス
                3+n     TIMEボタン
        '''
        n = len(self.seq.sequence)
        tkima.grid_config(self.seqtab, rlist=[[(0, 37), 'weight', 1], [(3, 14, 35), 'minsize', 10]], clist=[[0, 'minsize', 30], [2, 'minsize', 5]])

        self.combos_seqname = []
        for i in range(n):
            tkima.Combobox(self.seqtab, value=tuple(self.seq.sequence), width=6, init=self.seq.sequence[i], row=1, column=3+i, list=self.combos_seqname)
        tkima.Button(self.seqtab, text='TIME', command=self.reload_time, row=1, column=3+n, sticky='w')
        tkima.Frame(self.seqtab, bg='gray', height=2, row=3, column=1, columnspan=n+2, sticky='ew')

        for i in range(4):
            if self.seq.analog_use[i] == '1':
                tkima.Label(self.seqtab, text='ch'+str(i), row=2*i+5, column=1)
        for i in range(8):
            if self.seq.logic_use[i] == '1':
                tkima.Label(self.seqtab, text='logic'+str(i), row=2*i+16, column=1)

        self.frames_onoff_analog = []
        self.blnvars_onoff_analog = []
        tkima.Label(self.seqtab, text='analog', bg=analogCOLOR, row=4, column=1)
        for j in range(4):
            blndummy = []
            framedummy = []
            for i in range(n):
                frame = tkima.Frame(self.seqtab, grid=False, list=framedummy, height=10)
                framedummy[-1].bind("<ButtonRelease-1>", self.switch_on_off(al='a', row=j, column=i))
                tkima.BooleanVar(list=blndummy)
                if self.seq.analog["ch"+str(j)][i] == '1':
                    framedummy[-1].config(bg=analogCOLOR)
                    blndummy[-1].set(True)
                else:
                    framedummy[-1].config(bg=bgCOLOR)
                    blndummy[-1].set(False)
            self.frames_onoff_analog.append(framedummy)
            self.blnvars_onoff_analog.append(blndummy)
        for j in range(4):
            if self.seq.analog_use[j] == '1':
                for i in range(n):
                    self.frames_onoff_analog[j][i].grid(row=2*j+5, column=3+i, sticky='news')
                    tkima.grid_config(self.seqtab, rlist=[[2*j+6, 'minsize', 10]])
                tkima.Frame(self.seqtab, bg=analogCOLOR, height=2, row=2*j+6, column=3, columnspan=n, sticky='new')

        tkima.Button(self.seqtab, text="+", command=self.add_ch(al='a'), row=13, column=1)
        tkima.Frame(self.seqtab, bg='gray', height=2, row=14, column=1, columnspan=n+2, sticky='ew')

        self.frames_onoff_logic = []
        self.blnvars_onoff_logic = []
        tkima.Label(self.seqtab, text='logic', bg=logicCOLOR, row=15, column=1)
        for j in range(8):
            blndummy = []
            framedummy = []
            for i in range(n):
                frame = tkima.Frame(self.seqtab, grid=False, list=framedummy, height=10)
                framedummy[-1].bind("<ButtonRelease-1>", self.switch_on_off(al='l', row=j, column=i))
                tkima.BooleanVar(list=blndummy)
                if self.seq.logic["logic"+str(j)][i] == '1':
                    framedummy[-1].config(bg=logicCOLOR)
                    blndummy[-1].set(True)
                else:
                    framedummy[-1].config(bg=bgCOLOR)
                    blndummy[-1].set(False)              
            self.frames_onoff_logic.append(framedummy)
            self.blnvars_onoff_logic.append(blndummy)
        for j in range(8):
            if self.seq.logic_use[j] == '1':
                for i in range(n):
                    self.frames_onoff_logic[j][i].grid(row=2*j+16, column=3+i, sticky='news')
                    tkima.grid_config(self.seqtab, rlist=[[2*j+17, 'minsize', 10]])
                tkima.Frame(self.seqtab, bg=logicCOLOR, height=2, row=2*j+17, column=3, columnspan=n, sticky='new')

        tkima.Button(self.seqtab, text="+", command=self.add_ch(al='l'), row=34, column=1)

        tkima.Frame(self.seqtab, bg='gray', height=2, row=35, column=1, columnspan=n+2, sticky='ew')
        frame = tkima.Frame(self.seqtab, row=36, column=3, columnspan=n)
        tkima.Button(frame, text="add", command=self.add_sequence, row=0, column=0)
        tkima.Button(frame, text="del", command=self.del_sequence, row=0, column=1)

    def reload_widgets_on_paratab(self):
        self.spin_accumulation.overwrite(self.set["NUM_LOOP"])
        self.entry_rep_time.overwrite(self.set["PULSE_DELAY"])

    """---------------------呼び出される系---------------------"""

    def combo_experiment_selected(self, event):
        if self.seq.sequence == []:
            print('--- no setting')
            return
        tkima.frameforget(self.frame_experiment)
        tkima.frameforget(self.frame_var)
        self._reload_widgets_on_exptab()

    def reload_time(self):
        '''
        名付けられた時間の長さを決定する
        reload_time_okbutton_pushed()とセット
        '''
        n = len(self.seq.sequence)
        for i in range(n):
            if self.seq.sequence[i] != self.combos_seqname[i].get() and is_num(self.combos_seqname[i].get()) == False:
                self.seq.sequence[i] = self.combos_seqname[i].get()
                self.seq.names[self.combos_seqname[i].get()] = '2000*MINIMUM_PULSE_LENGTH_STEP'

        keys = self.seq.names.keys()
        delkeys = []
        for key in keys:
            if key not in self.seq.sequence:
                delkeys.append(key)
        if delkeys != []:
            for key in delkeys:
                del self.seq.names[key]

        m = len(self.seq.paras)
        self.toplevel_time = tkima.Toplevel()
        tkima.grid_config(self.toplevel_time, rlist=[[(n, n+m+1), 'minsize', 10]])

        self.entries_seqtime = []
        dummy = []
        for i in range(n):
            if is_num(self.seq.sequence[i]) == False and self.seq.sequence[i] not in dummy:
                dummy.append(self.seq.sequence[i])
                tkima.Label(self.toplevel_time, text=self.seq.sequence[i], row=i, column=0)
                tkima.Entry(self.toplevel_time, init=self.seq.names[self.seq.sequence[i]], row=i, column=1, list=self.entries_seqtime)
            else:
                self.entries_seqtime.append(False)

        self.entries_seqpara = []
        i = 0
        for key, value in self.seq.paras.items():
            tkima.Label(self.toplevel_time, text=key, row=i+n+1, column=0)
            tkima.Entry(self.toplevel_time, init=value, row=i+n+1, column=1, list=self.entries_seqpara)
            i += 1

        tkima.Button(self.toplevel_time, text='ok', command=self.reload_time_okbutton_pushed, row=n+m+2, column=0, columnspan=2)

    def reload_time_okbutton_pushed(self):
        for i in range(len(self.entries_seqtime)):
            if self.entries_seqtime[i] != False:
                self.seq.names[self.seq.sequence[i]] = self.entries_seqtime[i].get()
        del self.entries_seqtime
        i = 0
        for key in self.seq.paras.keys():
            self.seq.paras[key] = self.entries_seqpara[i].get()
            i += 1
        del self.entries_seqpara
        self.toplevel_time.destroy()
        
    def switch_on_off(self, al=None, row=None, column=None):
        '''
        クリックに応じてポートのON/OFFを切り替える
        alはanalogかlogicか
        self.blnvars_onoff_analogかself.blnvars_onoff_logicを変えて、色を変更
        '''
        def x(event):
            if al == 'a':
                if self.blnvars_onoff_analog[row][column].get():
                    self.blnvars_onoff_analog[row][column].set(False)
                    self.frames_onoff_analog[row][column].config(bg=bgCOLOR)
                else:
                    self.blnvars_onoff_analog[row][column].set(True)
                    self.frames_onoff_analog[row][column].config(bg=analogCOLOR)
            if al == 'l':
                if self.blnvars_onoff_logic[row][column].get():
                    self.blnvars_onoff_logic[row][column].set(False)
                    self.frames_onoff_logic[row][column].config(bg=bgCOLOR)
                else:
                    self.blnvars_onoff_logic[row][column].set(True)
                    self.frames_onoff_logic[row][column].config(bg=logicCOLOR)         
        return x

    def change_path(self, index=None):
        '''
        ディレクトリ変更Buttonを押したら実行される関数
        '''
        def x():
            if index == 0:
                iDir = self.path.dir_setting
                self.path.dir_setting = dialog.askdirectory(initialdir=iDir)
                if self.path.dir_setting == '':
                    print("--- filedialog cancelled")
                    self.path.dir_setting = iDir
                    return
                self.pathentries[0].overwrite(self.path.dir_setting)
            elif index == 1:
                iDir = self.path.dir_data
                self.path.dir_data = dialog.askdirectory(initialdir=iDir)
                if self.path.dir_data == '':
                    print("--- filedialog cancelled")
                    self.path.dir_data = iDir
                    return
                self.pathentries[1].overwrite(self.path.dir_data)
            self.save_paths_into_txtfile_from_entries()
        return x

    def make_newdir(self, index=None):
        '''
        ディレクトリ作成Buttonを押したら実行される関数
        '''
        def x():
            path = self.pathentries[index].get()
            if os.path.isdir(path):
                print("--- this folder already exist")
                return
            os.mkdir(path)
            if index == 0:
                print('--- created new folder for setting file')
            elif index == 1:
                print('--- created new folder for save file')
                print("    ( "+path+" )")

            if index == 0:
                self.path.dir_setting = path
            elif index == 1:
                self.path.dir_data = path

            self.save_paths_into_txtfile_from_entries()
        return x

    def ask_make_datafolder(self):
        '''
        実行時に存在しないフォルダが設定されていた場合に対処する関数

        return
            True:存在したときもしくは新しいのを作成したとき
        '''
        path = self.pathentries[1].get()
        if os.path.isdir(path):
            self.path.dir_data = path
            return True
        res = messagebox.askokcancel("folder for experimental data", path + "\n\ndoes not exist\nmake new folder ?")
        if res == True:
            os.mkdir(path)
            print('--- created new folder for experimental data')
            print("    ( "+path+" )")
            self.path.dir_data = path
        return res

    def ask_make_settingfolder(self):
        '''
        設定保存時に存在しないフォルダが設定されていた場合に対処する関数
        上と同様
        '''
        path = self.pathentries[0].get()
        if os.path.isdir(path):
            self.path.dir_setting = path
            return True
        res = messagebox.askokcancel("folder for setting file", path + "\n\ndoes not exist\nmake new folder ?")
        if res == True:
            os.mkdir(path)
            print('--- created new folder for setting file')
            print("    ( "+path+" )")
            self.path.dir_setting = path
        return res

    def save_all(self):
        '''
        保存の関数まとめ
        '''
        if self.ask_make_settingfolder() == False:
            print("--- save cancelled")
            return
        self.save_paths_into_txtfile_from_entries()
        if self.path.nowopening == '':
            print("--- path saved ( no setting )")
            return
        if self.ask_if_title_changed() == None:
            print("--- cancelled ( only path saved )")
            return
        self.put_paras_into_classes()
        write_.main(self.set, self.seq, self.path.nowopening, self.pyfile)
        print("--- both path and setting saved")
        self.clear_widgets()
        self.reload_widgets_on_seqtab()
        self.reload_widgets_on_exptab()

    def put_paras_into_classes(self):
        '''
        入力欄からパラメータを取得してself.setなどに格納する関数
        仮保存
        '''
        self.set["experiment"] = self.combo_experiment.get()
        self.set["NUM_LOOP"] = self.spin_accumulation.get()
        self.set["POWER_SUPPLY_VOLTAGE"] = self.exwidgets[0].get()
        self.set["var"] = self.exwidgets[1].get()
        self.set["stepwise_start"] = self.exwidgets[2].get()
        self.set["stepwise_stop"] = self.exwidgets[3].get()
        self.set["stepwise_span"] = self.exwidgets[4].get()
        self.set["var_start"] = self.exwidgets[5].get()
        self.set["var_stop"] = self.exwidgets[6].get()
        self.set["var_span"] = self.exwidgets[7].get()
        self.set["PULSE_DELAY"] = self.entry_rep_time.get()

        n = len(self.combos_seqname)
        for i in range(4):
            self.seq.analog['ch'+str(i)] = [bool_to_str01(self.blnvars_onoff_analog[i][j].get()) for j in range(n)]
        for i in range(8):
            self.seq.logic['logic'+str(i)] = [bool_to_str01(self.blnvars_onoff_logic[i][j].get()) for j in range(n)]

        self.seq.analog_use = []
        for i in range(4):
            if '1' in self.seq.analog['ch'+str(i)]:
                self.seq.analog_use.append('1')
            else:
                self.seq.analog_use.append('0')
        self.seq.logic_use = []
        for i in range(8):
            if '1' in self.seq.logic['logic'+str(i)]:
                self.seq.logic_use.append('1')
            else:
                self.seq.logic_use.append('0')

        self.seq.sequence = [self.combos_seqname[i].get() for i in range(n)]
        for i in range(len(self.seq.sequence)):
            if is_num(self.seq.sequence[i][0]) == False and self.seq.sequence[i] not in self.seq.names.keys():
                messagebox.showerror("", 'time of ' + self.seq.sequence[i] + 'is not defined')
                return

        self.path.settingname = self.entry_settingname.get()
        self.path.projectname = self.entry_projectname.get()
        self.path.nowopening = self.path.dir_setting + '/' + self.path.settingname + '.py'

        self.get_memo()

    def save_paths_into_txtfile_from_entries(self):
        '''
        path達をテキストファイルに保存(foldersettings.txtという特定のファイル)
        '''
        dummy = ''
        dummy += self.path.dir_setting + "\n"
        dummy += self.path.dir_data + "\n"
        with open(PATH_FOLDER, 'w') as f:
            f.write(dummy)

    def add_sequence(self):
        '''
        シーケンス編集の際、新たなブロックを挿入するためのきっかけとなる関数
        addbuttonにbindされている
        仮保存のあと、どこに挿入するか聞かれるウインドウが出てくる
        前後に保存ボタンを押さないと動作不安定かも？
        '''
        self.put_paras_into_classes()
        self._add_sequence_where_insert()

    def _add_sequence_where_insert(self):
        '''
        どこに挿入するか聞かれるウインドウを出す
        クリックによって実際に挿入する関数_add_sequence_addに飛ぶ
        '''
        self.addwindow = tkima.Toplevel(title="insert sequence", bg=bgCOLOR, geometry="200x400")
        n = len(self.seq.sequence)
        tkima.grid_config(self.addwindow, rlist=[[(0, 2*n+2), 'weight', 1]], clist=[[(0, 2), 'minsize', 20], [1, 'weight', 1]])
        self.addlabels = []
        for i in range(n):
            tkima.Label(self.addwindow, text="+", bg='salmon', row=2*i+1, column=1, list=self.addlabels, bind_b1_click=self._add_sequence_add(index=i))
            tkima.Label(self.addwindow, text=self.seq.sequence[i], row=2*i+2, column=1)
        tkima.Label(self.addwindow, text="+", bg='salmon', row=2*n+1, column=1, list=self.addlabels, bind_b1_click=self._add_sequence_add(index=-1))

    def _add_sequence_add(self, index=None):
        '''
        実際にシーケンスを挿入し、表示する関数
        仮保存もされないのでsaveすること
        '''
        def x(event):
            self.addwindow.destroy()
            if index == -1:
                for i in range(4):
                    self.seq.analog['ch'+str(i)].append('0')
                for i in range(8):
                    self.seq.logic['logic'+str(i)].append('0')
                self.seq.sequence.append("100")
            else:
                for i in range(4):
                    self.seq.analog['ch'+str(i)].insert(index, '0')
                for i in range(8):
                    self.seq.logic['logic'+str(i)].insert(index, '0')
                self.seq.sequence.insert(index, "100")

            tkima.frameclear(self.seqtab)
            self.reload_widgets_on_seqtab()
        return x

    def clear_widgets(self):
        tkima.frameclear(self.seqtab)
        tkima.frameforget(self.frame_experiment)
        tkima.frameforget(self.frame_var)

    def del_sequence(self):
        '''
        add_sequenceの逆でシーケンスを削るきっかけとなる関数
        delbuttonにbindされている
        どれを消すか聞かれるウインドウが出てくる
        クリックによって実際に削除する関数_del_sequence_delに飛ぶ
        '''
        self.delwindow = tkima.Toplevel(bg=bgCOLOR, geometry="200x400", title="delete sequence")
        n = len(self.seq.sequence)
        tkima.grid_config(self.delwindow, rlist=[[(0, 2*n), 'weight', 1]], clist=[[(0, 2), 'minsize', 20], [1, 'weight', 1]])
        self.dellabels = []
        for i in range(n):
            tkima.grid_config(self.delwindow, rlist=[[2*i, 'minsize', 15]])
            tkima.Label(self.delwindow, text=self.seq.sequence[i], bg='white smoke', bind_b1_click=self._del_sequence_del(index=i), list=self.dellabels, row=2*i+1, column=1)

    def _del_sequence_del(self, index=None):
        '''
        実際にシーケンスを削除し、表示する関数
        仮保存もされないのでsaveすること
        '''
        def x(event):
            self.delwindow.destroy()
            del self.seq.sequence[index]
            for i in range(4):
                del self.seq.analog['ch'+str(i)][index]
            for i in range(8):
                del self.seq.logic['logic'+str(i)][index]
            for i in range(4):
                if '1' not in self.seq.analog['ch'+str(i)]:
                    self.seq.analog_use[i] = '0'
            for i in range(8):
                if '1' not in self.seq.logic['logic'+str(i)]:
                    self.seq.logic_use[i] = '0'
                
            tkima.frameclear(self.seqtab)
            self.reload_widgets_on_seqtab()
        return x

    def ask_if_title_changed(self):
        '''
        保存の際にタイトルが変わっていたときに効果発動
        3択を迫られる:
            yes:別設定として新規保存
            no:タイトルも含めて上書き保存
            canlel:やめる
        '''
        if os.path.basename(self.path.nowopening).split('.')[0] == self.entry_settingname.get():
            return True
        res = messagebox.askyesnocancel("title changed", "title was changed\nsave as other file ?\n(No, change title)")
        if res == False:
            os.rename(self.path.nowopening, self.path.dir_setting + '/' + self.entry_settingname.get() + '.py')
        return res

    def ukkari(self):
        '''
        実行ボタンを押した瞬間、okを押さないと次に進めないウインドウが出てくる
        『Lab Brickはつけた？」というメッセージにしている
        ご自由に設定してください
        '''
        return messagebox.askyesno("confirmation", "Lab Brick (-2304MHz)\n\t...OK?")

    def get_memo(self):
        '''
        メモ欄を読み取る関数
        '''
        self.memotext = self.txtbox_memo.getall()

    def add_ch(self, al=None):
        '''
        出力ポートを足す
        '''
        def x():
            self.put_paras_into_classes()
            self.window_addch = tkima.Toplevel(bg=bgCOLOR, geometry="200x400")
            tkima.grid_config(self.window_addch, rlist=[[(0, 17), 'weight', 1]], clist=[[(0, 2), 'minsize', 20], [1, 'weight', 1]])
            self.add_ch_list = []
            if al == 'a':
                for i in range(4):
                    if self.seq.analog_use[i] == '0':
                        tkima.Label(self.window_addch, bg=analogCOLOR, text=PORT_a[i], bind_b1_click=self._add_ch(al=al, index=i), row=2*i+1, column=1)
                        tkima.grid_config(self.window_addch, rlist=[[2*i+2, 'minsize', 10]])
            if al == 'l':
                for i in range(8):
                    if self.seq.logic_use[i] == '0':
                        tkima.Label(self.window_addch, bg=logicCOLOR, text=PORT_l[i], bind_b1_click=self._add_ch(al=al, index=i), row=2*i+1, column=1)
                        tkima.grid_config(self.window_addch, rlist=[[2*i+2, 'minsize', 10]])
        return x

    def _add_ch(self, al=None, index=None):
        def x(event):
            if al == 'a':
                self.seq.analog_use[index] = '1'
            if al == 'l':
                self.seq.logic_use[index] = '1'
            self.window_addch.destroy()
            tkima.frameclear(self.seqtab)
            self.reload_widgets_on_seqtab()
        return x

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    root.mainloop()
