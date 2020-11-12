from pyvisa import visa
from instruments.ThorlabsPM100_meta import *
from jds_ha9 import *
import numpy as np
from matplotlib import pyplot as plt
from time import sleep

#initiate the power meter
inst = visa.instrument('USB0::0x1313::0x8078::PM002229::INSTR', term_chars='\n', timeout=1)
pm = ThorlabsPM100Meta(inst)
#initiate the optical attenuator
att = JDSHA9('GPIB::5')
att.set_beam_block(False)

attenuation = np.linspace(5,50,20)
#the intial setting takes time
att.set_attenuation_db(attenuation[0])
sleep(1)

power = []
for attn in attenuation:
    att.set_attenuation_db(attn)
    sleep(0.5)
    power.append(pm.read_value())

plt.plot(np.array(attenuation), 10*np.log10(np.array(power)*1000), 'o')
plt.xlabel('Attenuation (dB)')
plt.ylabel('Optical Power (dBm)')
plt.title('Attenuation vs. Power')
plt.show()
