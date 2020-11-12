#real time display of counting rate 
#this is for alignment
#created by Di Zhu on Jul 28,2017
#%%
#set up instrument
import sys
import os
import scipy.io as sio
import matplotlib.pyplot as plt 
import matplotlib.animation as animation
from matplotlib import style
import time
from datetime import datetime

sys.path.append('C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python')


from qnnpy.instruments.agilent_53131a import Agilent53131a




counter = Agilent53131a('GPIB0::30')
counter.basic_setup()
counter.write(':EVEN:HYST:REL 100')
counter.write(':INP:IMP 50')
counter.write(':INP:COUP AC')


counter.set_trigger(0.01)

style.use('fivethirtyeight')

style.use('default')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


counting_time = .2
time_start = time.time()
time_elapse = []
counting_rate = []

def animate(i):
    time_elapse.append(time.time()-time_start)
    counting_rate.append(counter.count_rate(counting_time))
    ax1.clear()
    ax1.plot(time_elapse[-101:-1], counting_rate[-101:-1])

ani = animation.FuncAnimation(fig, animate, interval = 0.5)
#animate(100)
plt.show()


