# -*- coding: utf-8 -*-
import numpy
DAC229_T1_CH2_FREQUENCY = 768e6  # 周波数(単位:Hz) / frequency(unit : Hz)
MINIMUM_PULSE_LENGTH_STEP = 3.0 / (2.0 * DAC229_T1_CH2_FREQUENCY)

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

def list_to_str(ls):
    res = ''
    for i in range(len(ls)):
        res += ls[i] + '\n'
    return res

def create_list_settings(set):
    res = []
    for key, value in set.items():
        if key[0].isupper():
            s = key + ' = ' + value
            res.append(s)
    res.append('')
    for key, value in set.items():
        if key[0].islower():
            s = key + ' = ' + value
            res.append(s)
    res += ['', '']
    return res

def create_list_pulse_sequence(set, seq):
    ls = []
    if set['experiment'] == "'array'":
        var = set['var'].replace("'", "")
        ls.append(var)
        for key, value in seq.names.items():
            if var in value:
                ls.append(key)        
    res = []
    for key, value in seq.names.items():
        if key in ls:
            s = '# ' + key + ' = ' + value
        else:
            s = key + ' = ' + value 
        res.append(s)
    res += ['', '']
    return res

def create_list_ppg(set, seq):
    res = []
    res.append('    print(vartexts)')
    if set['experiment'] == "'array'":
        var = set['var'].replace("'", "")
        s = '    ' + var + ' = ' + "eval(vartexts['" + var + "'])"
        res.append(s)
        for key, value in seq.names.items():
            if var in value:
                s = '    ' + key + ' = ' + "eval(vartexts['" + key + "'])"
                res.append(s)
    for key, value in seq.paras.items():
        s = '    pulse_sequence.set_parameter(' + key + ', ' + value + ')'
        res.append(s)
    psindex = []
    for i in reversed(range(len(seq.sequence))):
        for j in range(4):
            if seq.analog["ch"+str(j)][i] == '1':
                psindex.append(i + 1)
    for i in range(psindex[0]):
        s = '    pulse_sequence.add_sequence(' + seq.sequence[i]
        for j in range(4):
            if seq.analog["ch"+str(j)][i] == '1':
                s += ', dac229_t1_ch' + str(j) + '=Rect(DAC229_T1_CH' + str(j) + '_AMPLITUDE, DAC229_T1_CH' + str(j) + '_PHASE)'
        for j in range(8):
            if seq.logic["logic"+str(j)][i] == '1':
                s += ', logic' + str(j) + '=TTL_high()'
        s += ')'
        res.append(s)
    s = ('    pulse_sequence.set_phasestandard()')
    res.append(s)
    for i in range(psindex[0], len(seq.sequence)):
        s = '    pulse_sequence.add_sequence(' + seq.sequence[i]
        for j in range(8):
            if seq.logic["logic"+str(j)][i] == '1':
                s += ', logic' + str(j) + '=TTL_high()'
        s += ')'
        res.append(s)
    res += ['', '']
    return res

def insert_settings(set, pyfile):
    f = False
    for i in range(len(pyfile.ls_law)):
        if pyfile.ls_law[i] == '# settings' and f == False: 
            index_start = i + 1
            f = True
        elif pyfile.ls_law[i] != '' and f == True:
            if pyfile.ls_law[i][0] == '#':
                index_end = i
                break
    dummy = pyfile.ls_law[:index_start]
    dummy += create_list_settings(set)
    dummy += pyfile.ls_law[index_end:]
    pyfile.ls_law = dummy

def insert_pulse_sequence(set, seq, pyfile):
    f = False
    for i in range(len(pyfile.ls_law)):
        if pyfile.ls_law[i] == '# Pulse sequence' and f == False:
            index_start = i + 1
            f = True
        elif 'def pulse_program(pulse_sequence' in pyfile.ls_law[i] and f == True:
            index_end = i
            break
    dummy = pyfile.ls_law[:index_start]
    dummy += create_list_pulse_sequence(set, seq)
    dummy += pyfile.ls_law[index_end:]
    pyfile.ls_law = dummy

def insert_ppg(set, seq, pyfile):
    f = False
    for i in range(len(pyfile.ls_law)):
        if 'def pulse_program(pulse_sequence' in pyfile.ls_law[i] and f == False:
            index_start = i + 1
            f = True
        elif pyfile.ls_law[i] == 'if __name__ == "__main__":' and f == True:
            index_end = i
            break
    dummy = pyfile.ls_law[:index_start]
    dummy += create_list_ppg(set, seq)
    dummy += pyfile.ls_law[index_end:]
    pyfile.ls_law = dummy

def main(set, seq, path, pyfile):
    insert_settings(set, pyfile)
    insert_pulse_sequence(set, seq, pyfile)
    insert_ppg(set, seq, pyfile)
    with open(path,'w', encoding="utf-8") as f:
        f.write(list_to_str(pyfile.ls_law))





if __name__ == "__main__":
    pass