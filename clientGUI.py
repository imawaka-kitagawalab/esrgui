# -*- coding: utf-8 -*-
from utility_ima import GUI
from utility_ima import write_sequence

import os
import tkinter as tk

import run_ESR_forGUI
import importlib

PATH_SEQUENCE = 'C:/Users/NSakigake-QC/Desktop/KLFP ESRsystem/applications/PulseProgramFiles/test.py'

def list_to_str(ls):
    res = ''
    for i in range(len(ls)):
        res += ls[i] + '\n'
    return res

def main():
    '''
    1. 実行ボタンを押したときの最終確認
    2. GUIから値を得る
    3. run_ESR_forGUIで参照するPulseProgramFile「test.py」を書き換える
    4. run_ESR_forGUIを呼び出す
    5. run
    6. データ格納フォルダを控えたのち、インスタンス削除
    7. 実験終了のprint
    8. memoがあれば保存 
    '''
    importlib.reload(run_ESR_forGUI)

    # 1
    if gui.ukkari() == False:
        return
    # 2
    gui.put_paras_into_classes()
    # 3
    write_sequence.main(set=gui.set, seq=gui.seq, path=PATH_SEQUENCE, pyfile=gui.pyfile)
    # 4
    esr = run_ESR_forGUI.run_ESR(set=gui.set, seq=gui.seq, set10V=gui.set10Vflag.get(), path=gui.path)
    # 5
    esr.run()
    # 6
    if gui.set['experiment'] != "'voltage_only'":
        cdir = esr.path_return
    del esr
    # 7
    if gui.set['experiment'] == "'voltage_only'":
        print('--- voltage set finished')
        return
    else:
        print('--- experiment finished')
    # 8
    if gui.memotext != '':
        p = cdir + '/memo.txt'
        with open(p,'w') as f:
            f.write(gui.memotext)

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI.Application(master=root)
    gui.button_exe.config(command=main)
    root.mainloop()

