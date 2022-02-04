# -*- coding: utf-8 -*-
"""Xilinx ZCU111用LabRAD Serverを用いてESR実験を行うプログラムのサンプルです.
This is a sample program for conducting ESR experiments using LabRAD Server for Xilinx ZCU111.
最終更新日:2021/3/3
"""

import numpy as np
import math
import time

import labrad
from utility import *
from utility.constants import *
from utility.file_manager import *
from utility.graph_utility import *
from utility.logging_utility import *
from utility.others import *
from utility.read_write import *
from utility.waveform_processing import *
from pulse.pulse_sequence import *
from pulse.pulse_source import *
from parameter.sample_parameters_forGUI import *
# from waveform.sample_waveform_fpga import *


# 実行したいパルスプログラムをインポート
from PulseProgramFiles.test import *
import importlib

COM_PORT = "COM4"  # シリアル通信のポート / serial communication port
POWER_SUPPLY_CHANNEL = 2  # CCVで用いるチャンネル / channel of power supply for CCV
TIME_WAIT = 0


class run_ESR():
    def __init__(self, set, seq, set10V, path):
        self.set = set
        self.seq = seq
        self.set10V = set10V
        self.path = path

        cxn = labrad.connect(username="", password="")
        self.gpdx303s_server = cxn.gw_instek_gpdx303s

        if self.set['experiment'] != "'voltage_only'":
            self.xilinx_zcu111_server = cxn.xilinx_zcu111
            self.esr_init()
            self.pulse_start_point_dac_dict = {}
            self.pulse_end_point_dac_dict = {}
            self.pulse_start_point_adc_dict = {}
            self.pulse_end_point_adc_dict = {}
            self.signal_start_point_dict = {}
            self.signal_end_point_dict = {}
        else:
            self.gpdx303s_server.Connect(COM_PORT)
            if self.gpdx303s_server.GetOutputStatus() == 0:
                self.gpdx303s_server.TurnOff()
                self.gpdx303s_server.On()


    def run(self):
        if self.set10V:
            self.gpdx303s_server.SetVoltage(POWER_SUPPLY_CHANNEL, 10.)

        if self.set['experiment'] == "'stepwise'":
            self.run_mfs()
        elif self.set['experiment'] == "'array'":
            self.run_array()
        elif self.set['experiment'] == "'once'":
            self.run_once()
        elif self.set['experiment'] == "'voltage_only'":
            self.run_voltage_only()
        
    def run_mfs(self):
        var_list = np.arange(float(self.set['stepwise_start']), float(self.set['stepwise_stop'])-0.001, -float(self.set['stepwise_span']))
        for var in var_list:
            self.gpdx303s_server.SetVoltage(POWER_SUPPLY_CHANNEL, var)
            self.esr(index=math.floor(var*1000))
            print(str(round(var, 3)) + 'V finished')
            time.sleep(TIME_WAIT)
        self.esr_finalize()

    def run_array(self):
        self.gpdx303s_server.SetVoltage(POWER_SUPPLY_CHANNEL, float(self.set['POWER_SUPPLY_VOLTAGE']))
        var_list = np.arange(int(self.set['var_start']), int(self.set['var_stop'])+1, int(self.set['var_span']))
        
        for var in var_list:
            d = dict()
            v = self.set['var'].replace("'", "")
            d[v] = str(int(var)) + '*MINIMUM_PULSE_LENGTH_STEP'
            for key, value in self.seq.names.items():
                if v in value:
                    d[key] = value
            self.esr(index=int(var), vartexts=d)
            print(str(int(var)) + 'mpls finished')
            print(str((int(var)*3.0 / (2.0 * 768e6)*1e9)) + 'ns')
            time.sleep(TIME_WAIT)
            del d
        self.esr_finalize()

    def run_once(self):
        self.gpdx303s_server.SetVoltage(POWER_SUPPLY_CHANNEL, float(self.set['POWER_SUPPLY_VOLTAGE']))
        self.esr(index=1)
        self.esr_finalize()
    
    def run_voltage_only(self):
        self.gpdx303s_server.SetVoltage(POWER_SUPPLY_CHANNEL, float(self.set['POWER_SUPPLY_VOLTAGE']))
        self.gpdx303s_server.Close()

    def esr_init(self):
        '''
        arrayやstepwiseで回す際、毎回実行しなくていいもの

        note
            self.path_return:
                clientGUIでつかうために作った
        '''
        # parameters
        MAIN_FILE_DIRECTORY_PATH = self.path.dir_data + '/' + self.path.projectname

        # constants / データの保存先を設定
        CURRENT_TIME = get_time()
        self.LOG_PATH = "{0}\\{1}_{2}\\LOG".format(MAIN_FILE_DIRECTORY_PATH, PROGRAM_NAME, CURRENT_TIME)
        self.JSON_PATH = "{0}\\{1}_{2}\\JSON".format(MAIN_FILE_DIRECTORY_PATH, PROGRAM_NAME, CURRENT_TIME)
        self.ADC_PATH = "{0}\\{1}_{2}\\ADC".format(MAIN_FILE_DIRECTORY_PATH, PROGRAM_NAME, CURRENT_TIME)
        self.DAC_PATH = "{0}\\{1}_{2}\\DAC".format(MAIN_FILE_DIRECTORY_PATH, PROGRAM_NAME, CURRENT_TIME)

        self.path_return = "{0}\\{1}_{2}".format(MAIN_FILE_DIRECTORY_PATH, PROGRAM_NAME, CURRENT_TIME)


        # initialize
        self.logger = get_file_output_logger(logger_name=PROGRAM_NAME, log_file_path=self.LOG_PATH, log_file_name="{0}_{1}".format(get_program_name(__file__), CURRENT_TIME))
        write_json(json_data={}, json_path=self.JSON_PATH, json_name=PROGRAM_NAME, logger=self.logger)
        self.json_data = {}
        self.json_data["ADC Sampling Rate"] = ADC_SF
        self.json_data["DAC Sampling Rate"] = DAC_SF
        self.json_data["Center Frequency"] = DAC229_T1_CH2_FREQUENCY
        write_json(json_data=self.json_data, json_path=self.JSON_PATH, json_name=PROGRAM_NAME, logger=self.logger)

        # recording
        copy_file(__file__, self.LOG_PATH)
        copy_file(PARAMETERS_FILE_PATH, self.LOG_PATH)
        copy_file(WAVEFORM_FILE_PATH, self.LOG_PATH)

        # set parameters
        set_sampleparameters(self.xilinx_zcu111_server, PULSE_DELAY=float(self.set["PULSE_DELAY"]), NUM_LOOP=int(self.set["NUM_LOOP"]))

        # connect
        self.gpdx303s_server.Connect(COM_PORT)
        if self.gpdx303s_server.GetOutputStatus() == 0:
            self.gpdx303s_server.TurnOff()
            self.gpdx303s_server.On()
        # self.gpdx303s_server.SetVoltage(POWER_SUPPLY_CHANNEL, POWER_SUPPLY_VOLTAGE)
        self.xilinx_zcu111_server.Connect()  # FPGAに接続


        # calibration
        if self.xilinx_zcu111_server.GetCalibrationStatus() == 0:
            input("キャリブレーションする必要があります. / You need calibratiion.\n以下のとおりSMAケーブルを接続してください. / Please connect the SMA cable as follows.\n\n         ADC       |       DAC\n    -------------------------------\n    ADC224_T0_CH0  |  DAC229_T1_CH2\n    ADC224_T0_CH1  |  DAC229_T1_CH3\n    ADC225_T1_CH0  |  DAC229_T1_CH0\n    ADC225_T1_CH1  |  DAC229_T1_CH1\n\n終わりましたらEnterキーを押してください. / Please press a Enter key when you are finished.")
            self.xilinx_zcu111_server.Calibration()
            input("キャリブレーションが終わりました. / The calibration is done. \nSMAケーブルを実験を行えるように接続し直してください. / Please reconnect the SMA cable so that the experiment can take place.\n接続し直しましたらEnterキーを押してください./Press a Enter key after reconnecting.")

    def esr(self, index=1, vartexts={}):
        '''
        各測定を行う関数

        args
            index:
                各データのタイトルに入るもの
                int型
            vartexts:
                arrayなどで回す際に変更しなければいけないものを、
                {'定数名':'式(str型)'}
                の形で格納したもの
                定数名 = eval(式)
                のようになるよう、ソースコードには書かれている
        '''
        # run and save data
        beep()

        pulse_sequence = PulseSequence(logger=self.logger)  # PulseSequence()のインスタンスの作成
        pulse_program(pulse_sequence, vartexts=vartexts)  # パルスデータの構築
        self.xilinx_zcu111_server.SetWaveformByCode(pulse_sequence.encode())  # エンコードされたデータをFPGAにセット

        file_name = DAC_CHANNEL + "_" + str(index)
        self.json_data[file_name] = index
        self.pulse_start_point_dac_dict[file_name] = round(DAC_SF * (pulse_sequence.setting["pulse start"] + 100e-9))
        self.pulse_end_point_dac_dict[file_name] = round(DAC_SF * (pulse_sequence.setting["pulse end"] - 100e-9))
        self.json_data["Pulse Start Point DAC"] = self.pulse_start_point_dac_dict
        self.json_data["Pulse End Point DAC"] = self.pulse_end_point_dac_dict
        write_json(json_data=self.json_data, json_path=self.JSON_PATH, json_name=PROGRAM_NAME, logger=self.logger)
        set_waveform = self.xilinx_zcu111_server.GetWaveform(DAC_CHANNEL)
        write_binary_file(binary_data=set_waveform, binary_path=self.DAC_PATH, binary_name=file_name, format_character="f", logger=self.logger)

        self.xilinx_zcu111_server.SetUp()  # FPGAのセットアップ
        self.xilinx_zcu111_server.WriteDataToMemory()  # データの書き込み
        self.xilinx_zcu111_server.Run()  # 出力及び観測
        self.xilinx_zcu111_server.ReadDataFromMemory()  # データの読み込み

        file_name = ADC_CHANNEL + "_" + make_str_int(index, 4)
        self.json_data[file_name] = index
        adc_decimation_factor = self.xilinx_zcu111_server.GetDUCDDCFactor()
        self.json_data["ADC Decimation Factor"] = adc_decimation_factor
        self.pulse_start_point_adc_dict[file_name] = round((ADC_SF / adc_decimation_factor) * (pulse_sequence.setting["pulse start"] + 50e-9))
        self.pulse_end_point_adc_dict[file_name] = round((ADC_SF / adc_decimation_factor) * (pulse_sequence.setting["pulse end"] + 250e-9))
        self.signal_start_point_dict[file_name] = round((ADC_SF / adc_decimation_factor) * pulse_sequence.setting["signal start"])
        self.signal_end_point_dict[file_name] = self.signal_start_point_dict[file_name] + 2048
        self.json_data["Pulse Start Point ADC"] = self.pulse_start_point_adc_dict
        self.json_data["Pulse End Point ADC"] = self.pulse_end_point_adc_dict
        self.json_data["Signal Start Point"] = self.signal_start_point_dict
        self.json_data["Signal End Point"] = self.signal_end_point_dict
        write_json(json_data=self.json_data, json_path=self.JSON_PATH, json_name=PROGRAM_NAME, logger=self.logger)
        observed_waveform = self.xilinx_zcu111_server.GetWaveform(ADC_CHANNEL)
        write_binary_file(binary_data=observed_waveform, binary_path=self.ADC_PATH, binary_name=file_name, format_character="f", logger=self.logger)

        del pulse_sequence
    
    def esr_finalize(self):
        # finalize
        write_json(json_data=self.json_data, json_path=self.JSON_PATH, json_name=PROGRAM_NAME, logger=self.logger)
        self.gpdx303s_server.Close()
        self.xilinx_zcu111_server.Close()  # FPGAとの接続を切断
        kill_loggers()
        beep(times=2)
