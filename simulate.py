#!/bin/python
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pynetlogo

reports  = ["count bacteria", "avgres", "antibiotic"]
timeunit =  "Minutes"
titles   = ["Bacteria", "Resistance", "Antibiotica"]
units    = ["Count", "", ""]

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

def simulate(netlogo, ticks, n, setup={}, value=[], verbose=False):
	if verbose:
		print('*********** SETUP COMMANDS ***********')
	for prm, val in setup.items():
		if verbose:
			print(f'set {prm} {val}')
		netlogo.command(f'set {prm} {val}')

	vran = range(1)
	data = np.empty((0, len(reports) + 2 if value else len(reports) + 1))
	if value:
		if verbose:
			print(f'***********   TEST VALUE   ***********')
			print(value[0])
			print(f'[{value[1]} -> {value[2]}] in {value[3]} steps')
		vran = np.linspace(*value[1:])

	for x in vran:
		vdata = np.empty((0, len(reports) + 1))
		if value:
			netlogo.command(f'set {value[0]} {x}')
			if verbose:
				print('**************************************')
				print(f'{value[0]} = {x}')

		for i in range(n):
			if verbose:
				np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
				print(f'***********   RUN No. {i+1:3}  ***********')
				if value:
					print(f'set {value[0]} {x}')
				print(f'repeat {ticks} [go]')
			netlogo.command('setup')
			rep = netlogo.repeat_report(reports, ticks, go='go')
			if verbose:
				for r in reports:
					print(f'report {r}')
					tmp = np.array(rep[r])
					if np.all(tmp.astype(int) == tmp):
						print(tmp.astype(int))
					else: print(tmp)
			vdata = np.concatenate([vdata, [[i+1 ,*v] for v in zip(*rep.values())]])
		if value:
			data = np.concatenate([data, np.concatenate([np.full(((ticks+1)*n,1), x), vdata], axis=1)])
		else: data = vdata

	return data

def plot(data, plots=None, img=None, verbose=False):
	if verbose:
		print('***********   PLOT DATA    ***********')
	if plots is None:
		plots = [y for y in range(len(reports))]
	else:
		plots = [int(p)-1 for p in plots]

	if data.shape[1] == len(reports) + 1:
		if verbose:
			print('plot multiple runs...')
		runs = np.unique(data[:,0])
		for i in range(len(plots)):
			ax = plt.subplot(1, len(plots), i+1)
			for r in runs:
				vdata = data[data[:,0] == r][:,plots[i]+1]
				ax.plot(vdata[vdata >= 0], alpha=0.25)
			vdata = np.array([data[data[:,0] == r][:,plots[i]+1] for r in runs])
			print(vdata)
			ax.plot([np.mean(row[row >= 0]) for row in vdata.T], color='black', label='average')
			ax.set_title(titles[plots[i]])
			ax.set_xlabel(timeunit)
			ax.set_ylabel(units[plots[i]])
			ax.legend()
	else:
		if verbose:
			print('plot mean of multiple runs')
		values = np.unique(data[:,0])
		runs = {v: np.unique(data[data[:,0] == v][:,1]) for v in values}
		for i in range(len(plots)):
			ax = plt.subplot(1, len(plots), i+1)
			for v in values:
				vdata = np.array([data[np.logical_and(data[:,0] == v, data[:,1] == r)][:,plots[i]+2] for r in runs[v]])
				ax.plot([np.mean(row[row >= 0]) for row in vdata.T], label=f'{round(v, 3)}')
			ax.set_title(titles[plots[i]])
			ax.set_xlabel(timeunit)
			ax.set_ylabel(units[plots[i]])
			ax.legend()
	plt.gcf().set_size_inches(5*len(plots), 5)
	if img:
		print(f'Save Image to {img}')
		plt.savefig(img)
	else:
		plt.show()
	if verbose:
		print('**************************************')


import argparse
import json
import sys, signal

parser = argparse.ArgumentParser(prog='SimBioSys')
parser.add_argument('mode', choices=['simulate', 'plot'])
parser.add_argument('data')
parser.add_argument('-m', '--model')
parser.add_argument('-c', '--config')
parser.add_argument('-p', '--plots', nargs='+', default=None)
parser.add_argument('-i', '--image')
parser.add_argument('-g', '--gui', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

if (args.mode == 'simulate' and (args.model is None or args.config is None)):
	parser.error('mode "simulate" requires "--model" and "--config"')
	sys.exit(1)

if (args.plots and args.mode != 'plot'):
	parser.error('can only which plot to show while plotting')
	sys.exit(2)

if args.mode == 'simulate':
	with open(args.config) as file:
		dct = json.load(file)
	try:
		nl = start(args.model, args.gui, args.verbose)
		data = simulate(nl, **dct, verbose=args.verbose)
		with open(args.data, 'w') as file:
			if data.shape[1] > len(reports) + 1:
				file.write(dct['value'][0] + ',')
			file.write('Run No.,' + ','.join([f'{x} in {y}' for x,y in zip(titles, units)]) + '\n')
			np.savetxt(file, data, delimiter=',')
	finally:
		if nl: nl.kill_workspace()
else:
	data = np.genfromtxt(args.data, skip_header=1, delimiter=',')
	plot(data, plots=args.plots, img=args.image, verbose=args.verbose)
