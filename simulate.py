#!/bin/python
# sources:
# https://pynetlogo.readthedocs.io/en/latest/_docs/introduction.html
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
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
		data += [[i+1,*v] for v in zip(*rep.values())]

	data = np.array(data)

	# select most representative data
	err = np.zeros(n)
	for i in range(ticks-1):
		means = [np.mean(data[i::ticks, x+1]) for x in range(len(report))]
		vars  = [np.var(data[i::ticks, x+1]) for x in range(len(report))]
		for k in range(n):
			err[k] += sum([((data[k*ticks + i][x+1] - means[x]) / vars[x])**2 for x in range(len(report)) if vars[x] != 0])
		err -= min(err)
	m = np.argmin(err)
	print(m)
	data[:,0][data[:,0] == m] = 0

	return data

def plot(data, timeunit, ylabels, titles, outimg=None):
	runs = data.shape[1] - 1
	n = np.unique(data[:,0])
	n[::-1].sort()
	fig, axs = plt.subplots(1,runs)
	for k in range(runs):
		for i in n:
			if i == 0:
				axs[k].plot(data[data[:,0] == i][:,k+1], color='black', alpha=1)
			axs[k].plot(data[data[:,0] == i][:,k+1], linestyle='-.', alpha=0.25)
		axs[k].set_xlabel(timeunit)
		axs[k].set_title(titles[k])
		axs[k].set_ylabel(ylabels[k])
	fig.set_size_inches(runs * 5, 5)
	if outimg:
		fig.savefig(outimg)
	else:
		plt.show()


import argparse
import json
import sys, signal

parser = argparse.ArgumentParser(prog='simulate')
parser.add_argument('model')
parser.add_argument('config')
parser.add_argument('-o', '--outcsv')
parser.add_argument('-i', '--outimg')
parser.add_argument('-g', '--gui', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

with open(args.config) as file:
	dct = json.load(file)

try:
	nl = start(args.model, args.gui)
	data = simulate(nl, **dct['simulate'])
	if args.verbose: print(data)
	if args.outcsv:
		with open(args.outcsv, 'w') as file:
			file.write('Run No. [0 = most representative],' + ','.join([f'{x} in {y}' for x,y in zip(dct['plot']['titles'], dct['plot']['ylabels'])]) + '\n')
			np.savetxt(file, data, delimiter=',')
	plot(data, **dct['plot'], outimg=args.outimg)
finally:
	if nl: nl.kill_workspace()
