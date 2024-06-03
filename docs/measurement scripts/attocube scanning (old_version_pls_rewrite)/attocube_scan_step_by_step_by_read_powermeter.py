#%%
import pyvisa
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import style
import os, sys, time
import matplotlib.animation as animation
from datetime import datetime 
import smtplib, ssl

sys.path.append('C:\Users\ICE\Desktop\git-repo\qnn-lab-instr-python')


from qnnpy.functions.save_data_vs_param import *
from qnnpy.instruments.thorlabs_pm100d import ThorlabsPM100D
from qnnpy.instruments.attocube_anc150 import AttocubeANC150
from qnnpy.instruments.attocube_anc300 import AttocubeANC300



pm = ThorlabsPM100D(u'USB0::0x1313::0x8078::PM002229::0::INSTR')
ac = AttocubeANC150('ASRL12::INSTR')
#ar = AttocubeANC300('ASRL16::INSTR')

#%% some useful functions
def nstep(axis = 2, steps = 10, direction = 'up', scan_voltage = 20, scan_frequency = 20):
    ac.setm(axis, 'stp')
    ac.setv(axis, scan_voltage)
    ac.setf(axis, scan_frequency)
    power = []
    
    if direction == 'up':
        for i in range(steps):
            ac.stepu(axis, 1)
            sleep(0.1+1/scan_frequency)
            power.append(pm.get_power())
    else:
        for i in range(steps):
            ac.stepd(axis, 1)
            sleep(0.1+1/scan_frequency)
            power.append(pm.get_power())
    steps = range(1, steps+1)
    return steps, power    

def curve_classification(y):
    ydiff = []
    up = 0
    down = 0
    for i in range(len(y)-1):
        if y[i+1]>=y[i]:
            ydiff.append(1)
            up= up+1
        else:
            ydiff.append(-1)
            down = down+1
    if up>=(len(y)*3/4):
        return 'monotonic_up'
    else:
        if max(w2dbm(y))<-70:
                return 'signal_low'
        else:
            if down>=(len(y)*3/4):
                return 'monotonic_down'
            else:
                return 'nonlinear'


def look_for_max(axis = 2, starting_direction = 0, starting_steps = 10, voltage = 20, freq = 20):
    #optmization process
#    if pm.get_power()<1e-7:
#        print('signal too low')
#        return 0,0,0
    move_direction=[]; steps=[]; powers = [] 
    move_direction.append(starting_direction)
    steps.append(starting_steps)
    direction_option = ['up', 'down'] #0 is up, 1 is down.
    #start with 10 steps, up
    temp, power = nstep(axis = axis, steps = steps[-1], direction = direction_option[move_direction[-1]], scan_voltage = voltage, 
                         scan_frequency = freq)
    powers = power
    
    print(10*np.log10(np.array(power)/1e-3))
    while (steps[-1]>=2) & (sum(steps)<300):
        shape = curve_classification(power)
        print(shape)
        if shape=='monotonic_down':
            steps.append(int(round(steps[-1]/2.0)))# #reduce steps 
            move_direction.append((move_direction[-1]+1)%2) #change direction
            temp, power = nstep(axis = axis, steps = steps[-1], direction = direction_option[move_direction[-1]], scan_voltage = voltage, 
                             scan_frequency = freq)
        if shape=='monotonic_up':
            steps.append(steps[-1]) #keep  the same number of steps
            move_direction.append(move_direction[-1])
            temp, power = nstep(axis = axis, steps = steps[-1], direction = direction_option[move_direction[-1]], scan_voltage = voltage, 
                             scan_frequency = freq)
        if shape =='nonlinear':
            steps.append(int(round(steps[-1]/2.0))) #reduce steps by half
            move_direction.append((move_direction[-1]+1)%2) #change direction
            temp, power = nstep(axis = axis, steps = steps[-1], direction = direction_option[move_direction[-1]], scan_voltage = voltage, 
                     scan_frequency = 20)
        if shape == 'signal_low':
            print('signal too low')
            break
        print(10*np.log10(np.array(power)/1e-3))
        powers = powers+power
    return powers, move_direction, steps
            
    

def w2dbm(x):
    return 10*np.log10(np.array(x)/1e-3)

#%%
#def email_remind():
#    port = 465  # For SSL
#    smtp_server = "smtp.gmail.com"
#    sender_email = "dizhu.lab@gmail.com"  # Enter your address
#    receiver_email = "paddy.dizhu@gmail.com"  # Enter receiver address
#    password = 'sharedpassword'
#    message = """\
#    Subject: Error during cooldown
#        
#    This is a python generated email."""
#
#    context = ssl.create_default_context()
#    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#        server.login(sender_email, password)
#        server.sendmail(sender_email, receiver_email, message)
#        

#%%
steps, power = nstep(axis = 3, steps = 5, direction = 'up', scan_voltage = 35, 
                     scan_frequency = 20)
plt.plot(steps, w2dbm(power))

curve_classification(power)

#%%
#set the attocube scan parameters
scan_voltage = 30
scan_frequency = 10
#ac.reset()
for i in range(1, 3):
    ac.setm(i, 'stp')
    ac.setv(i, scan_voltage)
    ac.setf(i, scan_frequency)
    
ac.setm(1, 'gnd')
    
    
#ar.setm(1, 'stp')
#ar.setv(1, scan_voltage)
#ar.setf(1, scan_frequency)


#%%


def optimizexy():
    power_record = []
    power_record.append(pm.get_power())
    sleep(2)
    print('tune axis 2')
    powers, move_direction, steps = look_for_max(axis = 2, starting_steps = 20, 
                                             starting_direction=1, voltage = 32, 
                                             freq = 60)
    power_record = power_record+powers
    print('tune axis 3')
    powers, move_direction, steps = look_for_max(axis = 3, starting_steps = 20, 
                                             starting_direction=0, voltage = 32, 
                                             freq = 60)
    power_record = power_record+powers
    f.write('auto_tuning_start\n')
    
    for p in power_record:
        time_string = datetime.now().isoformat().split('.')[0].replace(':', '')
        
        f.write('{} {:.2f}dBm\n'.format(time_string, w2dbm(p)))
    f.write('auto_tuning_stop\n')
    plt.plot(w2dbm(power_record))
    return power_record[-1]
    

#%%

from datetime import datetime 

date_str = datetime.now().isoformat().split('T')[0]
fname = date_str
directory = r'C:\Users\ICE\Desktop\Di Zhu ICE Oxford\data\optical_power_during_cooldown\20190531_cooldown\\'

mean_power = pm.get_power('dBm')
power_queue = [mean_power]*20

f = open(directory+fname+"warmup.txt", "a")

try:
    while True:
        p = pm.get_power('dBm')
        print('power = {:.2f}dBm'.format(p)),
        power_queue.append(p)
        power_queue.pop(0)
        f.write('{} {:.2f}dBm\n'.format(datetime.now().isoformat().split('.')[0].replace(':', ''),p))
        time.sleep(1)
        rolling_average = np.mean(power_queue)
        if rolling_average < max(mean_power-1, -50):
            if rolling_average< -50:
                print('-50dBm, too low')
                break
            print('rolling average = {:.2f}dBm, mean_power = {:.2f}dBm, tuning start'.format(rolling_average, mean_power))
            final_power = optimizexy()
            mean_power = w2dbm(final_power)
            power_queue = [mean_power]*20
except KeyboardInterrupt:
    print('interrupted!')
    f.write('interrupted\n')
    f.close()
except:
    print('unexpected error!')
    f.write('unexpected error\n')
    f.close()

    





    




#%%
#plt.axis([0, 20])
powers = []
x = range(20)
for i in range(100):
    powers.append(pm.get_power('dBm'))
    if len(powers)<=20:
        plt.plot(range(len(powers)), powers)

    else:
        plt.plot(x, powers[-21:-1])
        
    plt.pause(.5)


plt.show()



#%%
    
#######################################
#set scan parameters
########################################
x_step_size = 1
x_steps =10
#############################
#start the scanning
###############################
powers  = []
for x_step in range(1, x_steps+1):
    ac.stepd(2, x_step_size)
    sleep(0.05+x_step_size/scan_frequency)
    powers.append(pm.get_power())
#powers_down = []
#for x_step in range(1, x_steps+1):
#    ac.stepd(2, x_step_size)
#    sleep(0.05+x_step_size/scan_frequency)
#    powers_down.append(pm.get_power())

plt.close('all')
plt.plot(range(x_steps), 10*np.log10(np.array(powers)/1e-3),'o')
#plt.plot(np.arange(x_steps,0, -1), 10*np.log10(np.array(powers_down)/1e-3), 'o')

#%%

#######################################
#set scan parameters
########################################
z_step_size = 1
z_steps =100
#############################
#start the scanning
###############################
powers  = []
#for z_step in range(1, z_steps+1):
#    ac.stepd(1, z_step_size)
#    sleep(0.05+z_step_size/scan_frequency)
#    powers.append(pm.get_power())
#powers_down = []
for z_step in range(z_steps):
    ac.stepu(1, z_step_size)
    sleep(0.05+z_step_size/scan_frequency)
    powers.append(pm.get_power())


plt.close('all')
plt.plot(range(z_steps), 10*np.log10(powers))
    
    
    
#%%



for y_step in range(1, y_steps+1):
    vol_row = []
    if y_step%2:
        for x_step in range(1, x_steps+1):
            vol_row.append(d.getAIN(0))
            ac.stepu(1,x_step_size)
            sleep(0.05+x_step_size/scan_frequency)        
    else:
        for x_step in range(1, x_steps+1):
            ac.stepd(1,x_step_size)
            sleep(0.05+x_step_size/scan_frequency)
            vol_row.append(d.getAIN(0))
    if y_step ==1:
        vol = np.array(vol_row)
    else:
        if y_step%2:
            vol= np.vstack((vol, np.array(vol_row)))
        else:
            vol= np.vstack((vol, np.array(vol_row)[::-1]))
            
    #sleep(x_steps*x_step_size/scan_frequency) 
    ac.stepu(2, y_step_size)
    sleep(0.05+y_step_size/scan_frequency)

#stop timer
stop = datetime.now()
#stop labjack
#d.streamStop()
d.close()
#attocube travel back to the starting point
ac.stepd(2, y_step_size*y_steps)
sleep(0.05+y_step_size*y_steps/scan_frequency)
if y_steps%2:
    ac.stepd(1, x_steps*x_step_size)
    sleep(0.05+x_step_size/scan_frequency)

plt.imshow(vol, extent=[1,x_steps,1,y_steps], aspect='auto')
#plt.plot(vol)

data_dict = {'x_steps':x_steps, 'y_steps':y_steps, 'x_step_size': x_step_size, 'y_step_size':y_step_size, 'scan_voltage': scan_voltage, 'scan_frequency': scan_frequency, 'photo_diode': vol}

file_path, file_name  = save_data_dict(data_dict, test_type = 'scan_image', test_name = '',
                        filedir = r'C:\Users\ProbeStation\Desktop\Di Zhu - Probe Station\scan_test', zip_file=True)
plt.savefig(file_path + '.png')
plt.show()


def move_to_index(x, y):
    ac.stepu(1, x*x_step_size)
    ac.stepu(2, y*y_step_size)
    
#move_to_index(20,20)