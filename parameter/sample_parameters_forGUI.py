# -*- coding: utf-8 -*-
"""実験で用いるパラメータ / Parameters used in the experiment"""

# JB06
PARAMETERS_FILE_PATH = __file__
ZCU111_IP_ADDRESS = "192.168.1.3"  # ZCU111のIPアドレス / ip address of ZCU111
DAC_CHANNEL = "dac229_t1_ch2"  # 出力に使用するチャンネル / a channel used for output
ADC_CHANNEL = "adc224_t0_ch0"  # 観測に使用するチャンネル / a channel used for observation
ADC_SF = 4.096e9  # unit : sps / ADCのサンプリングレート / sampling rate of ADC
DAC_SF = 4.096e9  # unit : sps / DACのサンプリングレート / sampling rate of DAC
NCO_FREQUENCY = 1536e6  # unit : Hz / NCOの周波数 / frequency of NCO
NCO_PHASE = 0.0  # unit : ° / NCOの位相 / phase of NCO
NYQUISTFACTOR = 2  # ナイキストファクタ
# NUM_LOOP = 1000 # 積算回数 / averaging times
# PULSE_DELAY = 20e-3  # unit : s / パルスシーケンスが終わってから次のパルスシーケンスが始まるまでの時間 / time between the end of a pulse sequence and the start of the next pulse sequence
DAC_LATENCY = 0.0  # unit : s / DACのレイテンシ / latency of DAC
ADC_LATENCY = 200e-9  # unit : s / ADCのレイテンシ / latency of ADC
LOGIC_LATENCY = 0.0  # unit : s / ロジック信号のレイテンシ / latency of logic signal
CUTOFF_FREQUENCY = 2e7  # unit : Hz / SMファイル作成時のカットオフ周波数 / cutoff frequency for SM file creation


def set_sampleparameters(xilinx_zcu111_server, PULSE_DELAY=20e-3, NUM_LOOP=1000):
    xilinx_zcu111_server.ClearWaveform()  # データのクリア
    xilinx_zcu111_server.SetIPAddress(ZCU111_IP_ADDRESS)  # IPアドレスの設定
    xilinx_zcu111_server.SetADCSamplingFrequency(ADC_SF)  # ADCのサンプリングレートの設定
    xilinx_zcu111_server.SetDACSamplingFrequency(DAC_SF)  # DACのサンプリングレートの設定
    xilinx_zcu111_server.SetADCNCOFrequency(NCO_FREQUENCY)  # NCOの周波数の設定
    xilinx_zcu111_server.SetADCNCOPhase(NCO_PHASE)  # NCOの位相の設定
    xilinx_zcu111_server.SetDACNCOFrequency(NCO_FREQUENCY)  # NCOの周波数の設定
    xilinx_zcu111_server.SetDACNCOPhase(NCO_PHASE)  # NCOの位相の設定
    xilinx_zcu111_server.SetNyquistFactor(DAC_CHANNEL, NYQUISTFACTOR)  # チャンネルのナイキストファクタの設定
    xilinx_zcu111_server.SetNyquistFactor(ADC_CHANNEL, NYQUISTFACTOR)  # チャンネルのナイキストファクタの設定
    xilinx_zcu111_server.SetADCChannelList([ADC_CHANNEL,])  # 使用するADCのチャンネルのリストの送信
    xilinx_zcu111_server.SetDACLatency(DAC_LATENCY)  # DAC Latency
    xilinx_zcu111_server.SetADCLatency(ADC_LATENCY)  # ADC Latency
    xilinx_zcu111_server.SetLOGICLatency(LOGIC_LATENCY)  # LOGIC Latency
    xilinx_zcu111_server.SetAveragingTimes(NUM_LOOP)  # 積算回数の設定
    xilinx_zcu111_server.SetPulseDelay(PULSE_DELAY)  # パルス間隔の設定
