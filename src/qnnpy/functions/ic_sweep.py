# Ic measurement code
# Run add_path.py first
import sys

sys.path.append(r"Q:\qnnpy\qnnpy")

import time

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import fmin


def setup_ic_measurement(
    lecroy,
    freq_gen,
    vpp=1,
    repetition_hz=100,
    trigger_level=0.1,
    trigger_slope="Positive",
    coupling_ch1="DC1M",
    coupling_ch2="DC1M",
):
    # Setup frequency generator to have heartbeat shape for Ic sweeping --'\,---
    freq_gen.set_load(high_z=True)
    # freq_gen.select_arb_wf(name = 'HEARTBEA')
    freq_gen.write("APPL:SIN 1000 HZ, 1 VPP, 0 V")

    # Change repetition rate and voltage amplitude
    freq_gen.set_freq(repetition_hz)
    freq_gen.set_vpp(vpp)
    freq_gen.set_output(True)

    # Setup LeCroy scope:
    lecroy.set_coupling(channel="C1", coupling=coupling_ch1)
    lecroy.set_coupling(channel="C2", coupling=coupling_ch2)
    lecroy.set_bandwidth(channel="C1", bandwidth="20MHz")
    lecroy.set_bandwidth(channel="C2", bandwidth="20MHz")
    lecroy.label_channel(channel="C1", label="AWG input waveform")
    lecroy.label_channel(channel="C2", label="Device output")
    lecroy.label_channel(channel="F1", label="Per-sweep Ic values")
    lecroy.label_channel(channel="F2", label="Ic values histogram")
    lecroy.set_vertical_scale(channel="C1", volts_per_div=500e-3, volt_offset=0)
    lecroy.set_vertical_scale(channel="C2", volts_per_div=100e-3, volt_offset=0)
    lecroy.set_horizontal_scale(
        time_per_div=(1.0 / repetition_hz) / 10.0, time_offset=0
    )
    lecroy.set_trigger(source="C2", volt_level=trigger_level, slope=trigger_slope)
    lecroy.set_trigger_mode(trigger_mode="Normal")
    lecroy.set_parameter(
        parameter="P1", param_engine="Mean", source1="C1", source2=None
    )
    lecroy.setup_math_trend(math_channel="F1", source="P1", num_values=10e3)
    lecroy.setup_math_histogram(math_channel="F2", source="P1", num_values=300)
    lecroy.set_parameter(
        parameter="P2", param_engine="LevelAtX", source1="C1", source2=None
    )
    lecroy.set_parameter(
        parameter="P3", param_engine="HistogramMedian", source1="F2", source2=None
    )
    lecroy.set_parameter(
        parameter="P4", param_engine="HistogramSdev", source1="F2", source2=None
    )
    lecroy.set_parameter(
        parameter="P5",
        param_engine="FullWidthAtHalfMaximum",
        source1="F2",
        source2=None,
    )
    lecroy.set_display_gridmode(gridmode="Single")


def run_ic_sweeps(lecroy, num_sweeps):
    lecroy.clear_sweeps()
    time.sleep(0.1)
    while lecroy.get_num_sweeps(channel="F1") < num_sweeps + 1:
        time.sleep(0.1)
    x, ic_values = lecroy.get_wf_data(channel="F1")
    while len(ic_values) < num_sweeps:
        x, ic_values = lecroy.get_wf_data(channel="F1")
        time.sleep(0.05)
    return ic_values[:num_sweeps]  # will occasionally return 1-2 more than num_sweeps


def gumbel_pdf(theta, x):
    a = theta[0]
    b = theta[1]
    return 1.0 / b * np.exp((x - a) / b - np.exp((x - a) / b))


def gumbel_dist_error_fun(theta, data, min_prob=1e-2):
    pdf_fun = gumbel_pdf
    prob = pdf_fun(theta=theta, x=data)
    prob[prob < min_prob] = (
        min_prob  # Otherwise any datapoint with probability zero returns log(P(x)=0) = -Inf
    )
    log_likelihood = np.sum(np.log(prob))
    return -log_likelihood


def analyze_ic_values(ic_values):
    theta0 = [np.median(ic_values), np.std(ic_values) * 10]
    thetaopt = fmin(gumbel_dist_error_fun, theta0, [ic_values])
    ic = thetaopt[0]
    delta_ic = thetaopt[1]
    return ic, delta_ic


def calc_ramp_rate(vpp, R, repetition_hz, wf="HEARTBEAT"):
    if wf.upper() == "HEARTBEAT":
        T = 1.0 / repetition_hz
        T_ramp = T / 8.0
        I_max = (vpp / 2.0) / R
        return I_max / T_ramp
    elif wf.upper() == "SINE":
        return (vpp / 2.0) / R * (2 * np.pi * repetition_hz)
    else:
        print('Incorrect waveform (must be "sine" or "heartbeat")')
        return 0


def data_list_to_histogram_list(
    data_list, num_bins=100, range_min=None, range_max=None, plotme=False
):
    hist_list = []
    for data in data_list:
        if range_min is None:
            range_min = np.min(data_list)
        if range_max is None:
            range_max = np.max(data_list)
        bin_vals, bin_edges = np.histogram(
            data, bins=num_bins, range=(range_min, range_max)
        )
        bin_centers = bin_edges[:-1] + (bin_edges[1] - bin_edges[0]) / 2.0
        hist_list.append(bin_vals)
    return hist_list, bin_centers


def quick_ic_test(lecroy, num_sweeps=1000, R=50):
    ic_data = run_ic_sweeps(lecroy, num_sweeps=num_sweeps) / R
    print("Median Ic = %0.2f uA / Std. dev Ic = %0.2f uA") % (
        np.median(ic_data * 1e6),
        np.std(ic_data * 1e6),
    )


def quick_retrap_test(lecroy, num_sweeps=1000, trigger_level=0.1, R=50):
    ic_data = run_ic_sweeps(lecroy, num_sweeps=num_sweeps) / R
    print("Median Iretrap = %0.2f uA / Std. dev Iretrap = %0.2f uA") % (
        np.median(ic_data * 1e6),
        np.std(ic_data * 1e6),
    )
    lecroy.set_trigger(source="C2", volt_level=trigger_level, slope="Positive")


def fit_ic_histogram(ic_values, bins=100, binrange=None, plot=False):
    ic_hist, bin_edges = np.histogram(a=ic_values, bins=bins)
    ic_hist_x = bin_edges[:-1] + (bin_edges[1] - bin_edges[0]) / 2.0

    ic, delta_ic = analyze_ic_values(ic_values)
    ic_hist_fit_x = np.linspace(min(ic_values), max(ic_values), bins)
    ic_hist_fit = gumbel_pdf([ic, delta_ic], ic_hist_fit_x)
    ic_hist_fit = ic_hist_fit / float(np.max(ic_hist_fit))
    ic_hist = ic_hist / float(np.max(ic_hist))
    if plot:
        plt.bar(ic_hist_x, ic_hist, width=(ic_hist_x[1] - ic_hist_x[0]))
        plt.plot(ic_hist_x, ic_hist_fit, "r")
        plt.show()
    return ic_hist_x, ic_hist, ic_hist_fit
