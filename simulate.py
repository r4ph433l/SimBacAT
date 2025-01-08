#!/bin/python
# sources:
# https://pynetlogo.readthedocs.io/en/latest/_docs/introduction.html
import matplotlib.pyplot as plt
import numpy as np
import pynetlogo

def start():
	netlogo = pynetlogo.NetLogoLink(
	#	gui=True,
	#	jvm_path='/usr/lib/jvm/java-23-openjdk/lib/libjli.so',
		netlogo_home='/opt/netlogo'
	)
	netlogo.load_model('model.nlogo')
	return netlogo

def simulate(netlogo, cmds, ticks, n, prms=[]):
	for prm, val in prms:
		netlogo.command(f'set {prm} {val}')

	data = []
	for i in range(n):
		netlogo.command('setup')
		rep = netlogo.repeat_report(cmds, ticks, go='go')
		data += [[i,*v] for v in zip(*rep.values())]

	return np.array(data)

def kill(netlogo):
	netlogo.kill_workspace()

def plot(data, ylabels):
	print(data.shape[1])
	n = np.unique(data[:,0])
	fig, axs = plt.subplots(1,data.shape[1]-1)
	for k in range(data.shape[1]-1):
		for i in n:
			axs[k].plot(data[data[:,0] == i][:,k+1])
		axs[k].set_xlabel('Ticks')
		axs[k].set_ylabel(ylabels[k])
	plt.show()



nl = start()
data = simulate(nl, ['count bacteria', 'avgres', 'antibiotica'], 200, 5, [('ab_init', 2.5)])
print(data)
kill(nl)
plot(data, ['Count', 'Resistance in %', ''])
