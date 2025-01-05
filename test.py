# sources:
# https://pynetlogo.readthedocs.io/en/latest/_docs/introduction.html
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pynetlogo

def plot(data, cmd, bc, rs):
	bc.plot(data[cmd[0]], label='Bacteria')
	bc.set_xlabel('Ticks')
	bc.set_ylabel('Counts')
	bc.legend()

	rs.plot(data[cmd[1]], color='r', label='Average Resistance')
	rs.set_xlabel('Ticks')
	rs.set_ylabel('Resistance in %')
	rs.legend()

netlogo = pynetlogo.NetLogoLink(
#	gui=True,
#	jvm_path='/usr/lib/jvm/java-23-openjdk/lib/libjli.so',
	netlogo_home='/opt/netlogo'
)

netlogo.load_model('model.nlogo')
netlogo.command('setup')
#netlogo.command('repeat 100 [go]')

cmd = ['count bacteria', 'mean [resistance] of bacteria']

n = 5

fig, axs = plt.subplots(n, 2)
data = []
for i in range(n):
	rep = netlogo.repeat_report(cmd, 500, go='go')
	data += [pd.DataFrame(rep)]
	plot(data[-1], cmd, axs[i, 0], axs[i, 1])
netlogo.kill_workspace()
print(data)
plt.show()
