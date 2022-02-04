# -*- coding: utf-8 -*-

import numpy
from pulse.pulse_sequence import *
from pulse.pulse_source import *
from utility.logging_utility import *


WAVEFORM_FILE_PATH = __file__


# settings
DAC229_T1_CH2_AMPLITUDE = 1.0
DAC229_T1_CH2_PHASE = 0.0*numpy.pi
POWER_SUPPLY_VOLTAGE = 10
NUM_LOOP = 100
PULSE_DELAY = 20e-3
DAC_LATENCY = 000.0e-9
ADC_LATENCY = 4000e-9
LOGIC_LATENCY = 0.0

experiment = 'voltage_only'
var = 'T_90'
stepwise_start = 8.5
stepwise_stop = 7
stepwise_span = 0.01
var_start = 5
var_stop = 100
var_span = 5


# 768 MHz
DAC229_T1_CH2_FREQUENCY = 768e6
MINIMUM_PULSE_LENGTH_STEP = 3.0 / (2.0 * DAC229_T1_CH2_FREQUENCY)


# Pulse sequence
T_LASER = 2000*MINIMUM_PULSE_LENGTH_STEP
T_90 = 35*MINIMUM_PULSE_LENGTH_STEP
T_180 = T_90*2
T_TAU = 1200.0*MINIMUM_PULSE_LENGTH_STEP
T_START = 500*MINIMUM_PULSE_LENGTH_STEP
T_END = 100.0*MINIMUM_PULSE_LENGTH_STEP


def pulse_program(pulse_sequence, vartexts={}):
    print(vartexts)
    pulse_sequence.set_parameter("dac229_t1_ch2 Frequency", DAC229_T1_CH2_FREQUENCY)
    pulse_sequence.set_parameter("pulse start", T_LASER+T_START)
    pulse_sequence.set_parameter("pulse end", T_LASER+T_START+T_90+T_TAU+T_180)
    pulse_sequence.set_parameter("signal start", T_LASER+T_START+T_90+T_TAU+T_180+T_TAU)
    pulse_sequence.set_parameter("signal end", T_LASER+T_START+T_90+T_TAU+T_180+T_TAU+1e-6)
    pulse_sequence.add_sequence(T_LASER, logic3=TTL_high())
    pulse_sequence.add_sequence(T_START, logic0=TTL_high(), logic1=TTL_high(), logic2=TTL_high())
    pulse_sequence.add_sequence(T_90, dac229_t1_ch2=Rect(DAC229_T1_CH2_AMPLITUDE, DAC229_T1_CH2_PHASE), logic0=TTL_high(), logic1=TTL_high(), logic2=TTL_high())
    pulse_sequence.add_sequence(T_TAU, logic1=TTL_high(), logic2=TTL_high())
    pulse_sequence.add_sequence(T_180, dac229_t1_ch2=Rect(DAC229_T1_CH2_AMPLITUDE, DAC229_T1_CH2_PHASE), logic0=TTL_high(), logic1=TTL_high(), logic2=TTL_high())
    pulse_sequence.set_phasestandard()
    pulse_sequence.add_sequence(T_END, logic0=TTL_high(), logic1=TTL_high(), logic2=TTL_high())


if __name__ == "__main__":
    pass
    # print("MINIMUM_PULSE_LENGTH_STEP:{} ns".format(1e9 * MINIMUM_PULSE_LENGTH_STEP))
    # print("T_LASER:{} ns".format(1e9 * T_LASER))
    # print("T_90:{} ns".format(1e9 * T_90))
    # print("T_TAU:{} ns".format(1e9 * T_TAU))
    # print("T_START:{} ns".format(1e9 * T_START))
    # print("T_END:{} ns".format(1e9 * T_END))
    # print("total_time:{} ns".format(1e9 * (T_LASER + T_START + T_90 + T_TAU + T_180 + T_END)))
