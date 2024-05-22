# SNSPD testing on Montana II

#########################################
### Setup counter
#########################################
### Scan counter trigger levels - Make sure trigger voltage is well above noise level

Ib = 4.9e-6  # indicate bias current here
SRS.set_voltage(Ib * R_srs)
SRS.set_output(False)
sleep(0.5)
SRS.set_output(True)

trigger_v, count_rate = counter.scan_trigger_voltage(
    [-0.1, 0.1], counting_time=0.2, num_pts=100
)
data_dict = {"trigger_v": trigger_v, "count_rate": count_rate, "Ib": Ib}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="trigger_level",
    test_name=test_name,
    filedir=filedirectry,
    zip_file=True,
)
plt.semilogy(trigger_v * 1e3, count_rate, "o")
plt.xlabel("trigger level (mV)")
plt.ylabel("count rate (cps)")
plt.savefig(file_path + ".png")
plt.show()


###################################################
# Dark count measurement
###################################################
currents1 = np.arange(0e-6, 4e-6, 1e-6)
currents2 = np.arange(4e-6, 15e-6, 0.2e-6)
currents = np.concatenate([currents1, currents2])
counting_time = 1

comments = "trigger_50mV"

DCR = count_rate_curve(currents, counting_time=counting_time)

data_dict = {"DCR": DCR, "currents": currents, "trigger_level": trigger_level}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="DCR",
    test_name=test_name + comments,
    filedir=filedirectry,
    zip_file=True,
)

# plt.semilogy(1e6*currents, LCR, 'o', label='Laser count rate (LCR)')
plt.semilogy(1e6 * currents, DCR, "o", label="Dark count rate (DCR)")
# plt.semilogy(1e6*currents, LCR-DCR, 'o', label='LCR - DCR')
plt.legend(loc="upper left")
plt.xlabel("Bias current (uA)")
plt.ylabel("Counts (Hz)")
plt.title("Counts vs Bias\n" + sample_name)
plt.savefig(file_path + ".png")
plt.show()


###################################################
# Background count measurement
###################################################
currents1 = np.arange(0e-6, 4e-6, 1e-6)
currents2 = np.arange(4e-6, 15e-6, 0.2e-6)
currents = np.concatenate([currents1, currents2])
counting_time = 1

BCR = count_rate_curve(currents, counting_time=counting_time)

data_dict = {"BCR": BCR, "currents": currents, "trigger_level": trigger_level}
file_path, file_name = save_data_dict(
    data_dict, test_type="BCR", test_name=test_name, filedir=filedirectry, zip_file=True
)

# plt.semilogy(1e6*currents, LCR, 'o', label='Laser count rate (LCR)')
plt.semilogy(1e6 * currents, DCR, "o", label="Background count")
# plt.semilogy(1e6*currents, LCR-DCR, 'o', label='LCR - DCR')
plt.legend(loc="upper left")
plt.xlabel("Bias current (uA)")
plt.ylabel("Counts (Hz)")
plt.title("Counts vs Bias\n" + sample_name)
plt.savefig(file_path + ".png")
plt.show()


###################################################
# Laser count measurement
###################################################
currents1 = np.arange(0e-6, 4e-6, 1e-6)
currents2 = np.arange(4e-6, 15e-6, 0.2e-6)
currents = np.concatenate([currents1, currents2])
counting_time = 1

laser_power = 220e-6
OD = "OD3"

comments = ""

LCR = count_rate_curve(currents, counting_time=counting_time)
data_dict = {
    "OD": OD,
    "laser_power": laser_power,
    "LCR": LCR,
    "currents": currents,
    "trigger_level": trigger_level,
}
file_path, file_name = save_data_dict(
    data_dict,
    test_type="LCR",
    test_name=test_name + comments,
    filedir=filedirectry,
    zip_file=True,
)

plt.semilogy(1e6 * currents, LCR, "o", label="Laser count")
# plt.semilogy(1e6*currents, LCR-DCR, 'o', label='LCR - DCR')
plt.legend(loc="upper left")
plt.xlabel("Bias current (uA)")
plt.ylabel("Counts (Hz)")
plt.title("Counts vs Bias\n" + sample_name)
plt.savefig(file_path + ".png")
plt.show()
