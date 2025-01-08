#!/bin/python
# sources:
# https://pynetlogo.readthedocs.io/en/latest/_docs/introduction.html
import matplotlib.pyplot as plt
import numpy as np
import pynetlogo

def start(model, gui):
	netlogo = pynetlogo.NetLogoLink(
		gui=gui,
	#	jvm_path='/usr/lib/jvm/java-23-openjdk/lib/libjli.so',
		netlogo_home='/opt/netlogo'
	)
	netlogo.load_model(model)
	return netlogo

def simulate(netlogo, report, ticks, n, parameters={}):
	for prm, val in parameters.items():
		netlogo.command(f'set {prm} {val}')

	data = []
	for i in range(n):
		netlogo.command('setup')
		rep = netlogo.repeat_report(report, ticks, go='go')
		data += [[i,*v] for v in zip(*rep.values())]

	return np.array(data)

def plot(data, ylabels):
	n = np.unique(data[:,0])
	fig, axs = plt.subplots(1,data.shape[1]-1)
	for k in range(data.shape[1]-1):
		for i in n:
			axs[k].plot(data[data[:,0] == i][:,k+1])
		axs[k].set_xlabel('Ticks')
		axs[k].set_ylabel(ylabels[k])
	plt.show()


import argparse
import json
import sys, signal

parser = argparse.ArgumentParser(prog='simulate')
parser.add_argument('model')
parser.add_argument('config')
parser.add_argument('-o', '--outfile')
parser.add_argument('-g', '--gui', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

with open(args.config) as file:
	dct = json.load(file)

try:
	nl = start(args.model, args.gui)
	data = simulate(nl, **dct['simulate'])
	if args.verbose: print(d)
	if args.outfile: np.savetxt(args.outfile, data, delimiter=',')
	plot(data, **dct['plot'])
finally:
	if nl: nl.kill_workspace()

"""
nl = start()
data = simulate(nl, ['count bacteria', 'avgres', 'antibiotica'], 200, 5, [('ab_init', 2.5)])
print(data)
kill(nl)
plot(data, ['Count', 'Resistance in %', ''])
"""
