# -*- coding: utf-8 -*-
import numpy

def rejectLF(list):
    '''
    listの各要素の右端にある改行を取り払う
    '''
    result = [line.rstrip('\n') for line in list]
    return result

class Main():
    def __init__(self, py, set, seq):
        with open(py, 'r', encoding="utf-8") as f:
            self.ls_law = rejectLF(f.readlines())
        self.ls = [self.ls_law[i].replace(' ', '').replace('\t', '') for i in range(len(self.ls_law)) if self.ls_law[i] != '']
        self.settings = []
        self.pulse_sequence = []
        self.ppg = []
        self.read_settings()
        self.read_pulse_sequence()
        self.read_ppg()
        self.reject_comment()
        self.put_to_dict_settings(set)
        self.put_to_dict_pulse_sequence(seq)
        self.put_to_dict_ppg(seq)
    
    def read_settings(self):
        f = False
        for i in range(len(self.ls)):
            if self.ls[i] == '#settings' and f == False: 
                index_start = i + 1
                f = True
            elif self.ls[i][0] == '#' and f == True:
                index_end = i
                f = 'ok'
                break
        if f == 'ok':
            self.settings = [self.ls[i] for i in range(index_start, index_end)]
        else:
            print('--- cannot read\n\t"# settings" ~ "#"')

    def read_pulse_sequence(self):
        f = False
        for i in range(len(self.ls)):
            if self.ls[i] == '#Pulsesequence' and f == False:
                index_start = i + 1
                f = True
            elif 'defpulse_program(pulse_sequence' in self.ls[i] and f == True:
                index_end = i
                f = 'ok'
                break
        if f == 'ok':
            self.pulse_sequence = [self.ls[i] for i in range(index_start, index_end)]
        else:
            print('--- cannot read\n\t"# Pulse sequence" ~ "def pulse_program(pulse_sequence"')

    def read_ppg(self):
        f = False
        for i in range(len(self.ls)):
            if 'defpulse_program(pulse_sequence' in self.ls[i] and f == False:
                index_start = i + 1
                f = True
            elif self.ls[i] == 'if__name__=="__main__":' and f == True:
                index_end = i
                f = 'ok'
                break
        if f == 'ok':
            self.ppg = [self.ls[i] for i in range(index_start, index_end)]
        else:
            print('--- cannot read\n\t"def pulse_program(pulse_sequence" ~ "if __name__ == "__main__":"')

    def reject_comment(self):
        for i in range(len(self.settings)):
            index = -1
            for j in range(len(self.settings[i])):
                if self.settings[i][j] == '#':
                    index = j
            if index != -1:
                self.settings[i] = self.settings[i][:index]
        for i in range(len(self.pulse_sequence)):
            if '#' in self.pulse_sequence[i]:
                self.pulse_sequence[i] = self.pulse_sequence[i].replace('#', '')
        for i in range(len(self.ppg)):
            index = -1
            for j in range(len(self.ppg[i])):
                if self.ppg[i][j] == '#':
                    index = j
            if index != -1:
                self.ppg[i] = self.ppg[i][:index]
        
    def put_to_dict_settings(self, set):
        for i in range(len(self.settings)):
            key, value = self.settings[i].split('=')
            set[key] = value

    def put_to_dict_pulse_sequence(self, seq):
        for i in range(len(self.pulse_sequence)):
            key, value = self.pulse_sequence[i].split('=')
            seq.names[key] = value
            
    def put_to_dict_ppg(self, seq):
        for i in range(len(self.ppg)):
            if 'pulse_sequence.set_parameter' in self.ppg[i]:
                s = self.ppg[i].replace('pulse_sequence.set_parameter(', '').replace(')', '')
                key, value = s.split(',')
                if 'Frequency' in key:
                    key = key.replace('Frequency', ' Frequency')
                    seq.paras[key] = value
                if 'start' in key:
                    key = key.replace('start', ' start')
                    seq.paras[key] = value
                if 'end' in key:
                    key = key.replace('end', ' end')
                    seq.paras[key] = value
            if 'pulse_sequence.add_sequence' in self.ppg[i]:
                for ch in seq.analog.keys():
                    if ('dac229_t1_' + ch) in self.ppg[i]:
                        seq.analog[ch].append('1')
                    else:
                        seq.analog[ch].append('0')
                for ch in seq.logic.keys():
                    if ch in self.ppg[i]:
                        seq.logic[ch].append('1')
                    else:
                        seq.logic[ch].append('0')
                s = self.ppg[i].replace('pulse_sequence.add_sequence(', '').replace(')', '')
                s = s.split(',')[0]
                seq.sequence.append(s)
        for i in range(4):
            if '1' in seq.analog['ch'+str(i)]:
                seq.analog_use[i] = '1'
            else:
                seq.analog_use[i] = '0'
        for i in range(8):
            if '1' in seq.logic['logic'+str(i)]:
                seq.logic_use[i] = '1'
            else:
                seq.logic_use[i] = '0'

if __name__ == "__main__":
    pass
    # set = Settings()
    # seq = Sequences()
    # a = Main('/Users/imawaka/Desktop/Utility/PulseProgramFiles/test.py', set, seq)
    # print(seq.sequence)