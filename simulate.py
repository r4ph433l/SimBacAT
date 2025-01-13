#!/bin/python
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
		print('**************************************\n')
	return netlogo

def simulate(netlogo, report, ticks, n, setup={}, value=[], verbose=False):
	if verbose:
		print('*********** SETUP COMMANDS ***********')
	for prm, val in setup.items():
		if verbose:
			print(f'set {prm} {val}')
		netlogo.command(f'set {prm} {val}')

	vran = range(1)
	data = np.empty((0, len(report) + 2 if value else len(report) + 1))
	if value:
		print(f'***********  TEST VALUE   ***********')
		print(value[0])
		print(f'[{value[1]} -> {value[2]}] in {value[3]} steps')
		vran = np.linspace(*value[1:])

	for x in vran:
		vdata = np.empty((0, len(report) + 1))
		if value:
			netlogo.command(f'set {value[0]} {x}')
			print('**************************************')
			print(f'set {value[0]} {x:.2f}')

		for i in range(n):
			if verbose:
				np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
				print(f'***********   RUN No. {i+1:3}  ***********')
				if value:
					print(f'set {value[0]} {x:.2f}')
				print(f'repeat {ticks} [go]')
			netlogo.command('setup')
			rep = netlogo.repeat_report(report, ticks, go='go')
			if verbose:
				for r in report:
					print(f'report {r}')
					tmp = np.array(rep[r])
					if np.all(tmp.astype(int) == tmp):
						print(tmp.astype(int))
					else: print(tmp)
			vdata = np.concatenate([vdata, [[i+1 ,*v] for v in zip(*rep.values())]])

		if verbose:
			print('*********** POSTSIMULATION ***********')
			print('Determine most representative Data...')
		# select most representative data
		err = np.zeros(n)
		for i in range(ticks-1):
			means = [np.mean(vdata[i::ticks, x+1]) for x in range(len(report))]
			vars  = [np.var(vdata[i::ticks, x+1]) for x in range(len(report))]
			for k in range(n):
				err[k] += sum([((vdata[k*ticks + i][x+1] - means[x]) / vars[x])**2 for x in range(len(report)) if vars[x] != 0])
			err -= min(err)
		m = np.argmin(err)
		vdata[:,0][vdata[:,0] == m] = 0
		if verbose:
			print(f'Run No.{m+1} is most representative')
			print(vdata[vdata[:,0] == 0][:,1:])
			print('**************************************\n')

		if value:
			data = np.concatenate([data, np.concatenate([np.full(((ticks+1)*n,1), x), vdata], axis=1)])
		else: data = vdata

	return data

def plot(data, timeunit, ylabels, titles, suptitle=None, outimg=None, verbose=False):
	if verbose:
		print('***********   PLOT DATA    ***********')
		if suptitle:
			print(suptitle)
		print('Draw Lines...')
	runs = data.shape[1] - 1
	n = np.unique(data[:,0])
	n[::-1].sort()
	fig, axs = plt.subplots(1, runs)
	for k in range(runs):
		for i in n:
			if i == 0:
				axs[k].plot(data[data[:,0] == i][:,k+1], color='black', alpha=1, markevery=20)
			axs[k].plot(data[data[:,0] == i][:,k+1], alpha=0.25, markevery=5)
		axs[k].set_xlabel(timeunit)
		axs[k].set_title(titles[k])
		axs[k].set_ylabel(ylabels[k])
	fig.set_size_inches(runs * 5, 5)
	if suptitle:
		fig.suptitle(suptitle, size='xx-large', weight='bold')
	if verbose:
		print('Highlight most representative Run...')
	if outimg:
		print(f'Save Image to {outimg}')
		fig.savefig(outimg)
	else:
		plt.show()
	if verbose:
		print('**************************************')


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
	vtest = data.shape[1] > len(dct['simulate']['report']) + 1
	if args.outcsv:
		with open(args.outcsv, 'w') as file:
			if vtest:
				file.write(dct['simulate']['value'][0] + ',')
			file.write('Run No. [0 = most representative],' + ','.join([f'{x} in {y}' for x,y in zip(dct['plot']['titles'], dct['plot']['ylabels'])]) + '\n')
			np.savetxt(file, data, delimiter=',')
	if vtest:
		for v in np.unique(data[:,0]):
			plot(data[data[:,0] == v][:,1:], **dct['plot'], suptitle=f'{dct["simulate"]["value"][0]} = {v:.2f}', outimg=args.outimg + str(v) if args.outimg else None, verbose=args.verbose)
	else:
		plot(data, **dct['plot'], outimg=args.outimg, verbose=args.verbose)
finally:
	if nl: nl.kill_workspace()
