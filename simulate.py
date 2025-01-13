#!/bin/python
# sources:
# https://pynetlogo.readthedocs.io/en/latest/_docs/introduction.html
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pynetlogo

def start(model, gui, verbose=False):
	if verbose:
		print('**********    NetLogo©     ***********')
		print('Starting...')
	netlogo = pynetlogo.NetLogoLink(
		gui=gui,
	#	jvm_path='/usr/lib/jvm/java-23-openjdk/lib/libjli.so',
		netlogo_home='/opt/netlogo'
	)
	if verbose:
		print(f'Load Model {model}')
	netlogo.load_model(model)
	if verbose:
		print('**************************************')
	return netlogo

def simulate(netlogo, report, ticks, n, parameters={}, verbose=False):
	if verbose:
		print('*********** SETUP COMMANDS ***********')
	for prm, val in parameters.items():
		if verbose:
			print(f'set {prm} {val}')
		netlogo.command(f'set {prm} {val}')
	if verbose:
		print('**************************************')

	data = []
	for i in range(n):
		if verbose:
			np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
			print(f'************  RUN No.{i+1:3}  ************')
		netlogo.command('setup')
		rep = netlogo.repeat_report(report, ticks, go='go')
		if verbose:
			for r in report:
				print(f'report {r}')
				tmp = np.array(rep[r])
				if np.all(tmp.astype(int) == tmp):
					print(tmp.astype(int))
				else: print(tmp)
			print('**************************************')
		data += [[i+1,*v] for v in zip(*rep.values())]


	data = np.array(data)


	if verbose:
		print('*********** POSTSIMULATION ***********')
		print('Determine most representative Data...')
	# select most representative data
	err = np.zeros(n)
	for i in range(ticks-1):
		means = [np.mean(data[i::ticks, x+1]) for x in range(len(report))]
		vars  = [np.var(data[i::ticks, x+1]) for x in range(len(report))]
		for k in range(n):
			err[k] += sum([((data[k*ticks + i][x+1] - means[x]) / vars[x])**2 for x in range(len(report)) if vars[x] != 0])
		err -= min(err)
	m = np.argmin(err)
	data[:,0][data[:,0] == m] = 0
	if verbose:
		print(f'Run No.{m+1} is most representative')
		print('**************************************')

	return data

def plot(data, timeunit, ylabels, titles, outimg=None, verbose=False):
	runs = data.shape[1] - 1
	n = np.unique(data[:,0])
	n[::-1].sort()
	fig, axs = plt.subplots(1,runs)
	for k in range(runs):
		for i in n:
			if i == 0:
				axs[k].plot(data[data[:,0] == i][:,k+1], color='black', alpha=1, markevery=20)
			axs[k].plot(data[data[:,0] == i][:,k+1], alpha=0.25, markevery=5)
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
	nl = start(args.model, args.gui, args.verbose)
	data = simulate(nl, **dct['simulate'], verbose=args.verbose)
	if args.outcsv:
		with open(args.outcsv, 'w') as file:
			file.write('Run No. [0 = most representative],' + ','.join([f'{x} in {y}' for x,y in zip(dct['plot']['titles'], dct['plot']['ylabels'])]) + '\n')
			np.savetxt(file, data, delimiter=',')
	plot(data, **dct['plot'], outimg=args.outimg, verbose=args.verbose)
finally:
	if nl: nl.kill_workspace()
