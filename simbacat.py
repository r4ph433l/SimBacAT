#!/bin/python
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pynetlogo
import matplotlib
#matplotlib.rc('font', size='12')

reports  = ["count bacteria", "avg-tolerance", "antibiotic"] 	# netlogo commands for bacteria count, average tolerance and antibiotics concentration
timeunit =  r"Zeit [$min$]"					# unit for netlogo ticks
titles   = ["", "", ""]						# plot titles
units    = ["Anzahl Bakterien", "Toleranz", r"Konzentration Ampicillin [$µg/ml$]"] # units for bacteria count, tolerance & and antibiotics concentration

# start netlogo environment
def start(model, gui, verbose=False):
	if verbose:
		print('**********    NetLogo©     ***********')
		print('Starting...')
	netlogo = pynetlogo.NetLogoLink(
		gui=gui,
	#	jvm_path='/usr/lib/jvm/java-23-openjdk/lib/libjli.so',
		netlogo_home='/opt/netlogo' # netlogo folder for linux, comment out if on windows
	)
	if verbose:
		print(f'Load Model {model}')
	netlogo.load_model(model)
	if verbose:
		print('**************************************\n')
	return netlogo

# simulate n runs
def simulate(netlogo, ticks, n, setup={}, value=[], verbose=False):
	if verbose:
		print('*********** SETUP COMMANDS ***********')
	# set global variables
	for prm, val in setup.items():
		if verbose:
			print(f'set {prm} {val}')
		netlogo.command(f'set {prm} {val}')

	vran = range(1)
	data = np.empty((0, len(reports) + 2 if value else len(reports) + 1))
	# if 'value' is set vran = array of values to simulate
	if value:
		if verbose:
			print(f'***********   TEST VALUE   ***********')
			print(value[0])
			print(f'[{min(value[1:])} -> {max(value[1:])}] in {len(value)-1} steps')
		vran = value[1:]
	# iterate over values or do once if 'value' is not set
	for x in vran:
		vdata = np.empty((0, len(reports) + 1))
		# set value
		if value:
			netlogo.command(f'set {value[0]} {x}')
			if verbose:
				print('**************************************')
				print(f'{value[0]} = {x}')
		# do n runs
		for i in range(n):
			if verbose:
				np.set_printoptions(formatter={'float': lambda x: "{0:0.2f}".format(x)})
				print(f'***********   RUN No. {i+1:3}  ***********')
				if value:
					print(f'set {value[0]} {x}')
				print(f'repeat {ticks} [go]')
			# setup and run
			netlogo.command('setup')
			rep = netlogo.repeat_report(reports, ticks, go='go')
			if verbose:
				for r in reports:
					print(f'report {r}')
					tmp = np.array(rep[r])
					if np.all(tmp.astype(int) == tmp):
						print(tmp.astype(int))
					else: print(tmp)
			# add data to array and add run number
			vdata = np.concatenate([vdata, [[i+1 ,*v] for v in zip(*rep.values())]])
		# add runs to data array and add value if 'value' is set
		if value:
			data = np.concatenate([data, np.concatenate([np.full(((ticks+1)*n,1), x), vdata], axis=1)])
		else: data = vdata

	return data

# plot data from csv
def plot(data, plots=None, img=None, verbose=False):
	if verbose:
		print('***********   PLOT DATA    ***********')
	# if 'plots' is not set plot everything
	if plots is None:
		plots = [y for y in range(len(reports))]
	else:
		plots = [int(p)-1 for p in plots]

	# if data has static global values
	if data.shape[1] == len(reports) + 1:
		if verbose:
			print('plot multiple runs...')
		runs = np.unique(data[:,0])
		# do subplots
		for i in range(len(plots)):
			ax = plt.subplot(1, len(plots), i+1)
			# plot every run with 1/4 opacity
			for r in runs:
				vdata = data[data[:,0] == r][:,plots[i]+1]
				ax.plot(vdata[vdata > -1], alpha=0.25)
			# plot average
			vdata = np.array([data[data[:,0] == r][:,plots[i]+1] for r in runs])
			ax.plot([np.mean(row[row > -1]) for row in vdata.T], color='black', label='Durchschnitt')
			ax.set_title(titles[plots[i]])
			ax.set_xlabel(timeunit, size='large')
			ax.set_ylabel(units[plots[i]], size='large')
			ax.legend()
	# if global values were tested plot only average
	else:
		values = np.unique(data[:,0])
		runs = {v: np.unique(data[data[:,0] == v][:,1]) for v in values}
		if verbose:
			plot('plot mean of multiple runs')
		# do subplots
		for i in range(len(plots)):
			ax = plt.subplot(1, len(plots), i+1)
			# plot every value
			for v in values:
				vdata = np.array([data[np.logical_and(data[:,0] == v, data[:,1] == r)][:,plots[i]+2] for r in runs[v]])
				ax.plot([np.mean(row[row > -1]) for row in vdata.T],label=f'{round(v, 3)}')
			ax.set_title(titles[plots[i]])
			ax.set_xlabel(timeunit, size='large')
			ax.set_ylabel(units[plots[i]], size='large')
			ax.legend()

	plt.gcf().set_size_inches(5*len(plots) +2, 5)
	# save to 'img' if set
	if img:
		if verbose:
			print(f'Save Image to {img}')
		plt.savefig(img)
	else:
		plt.margins(0)
		plt.show()
	if verbose:
		print('**************************************')

# some argparse :)
import argparse
import json
import sys, signal

parser = argparse.ArgumentParser(prog='SimBacAT',
				description='Simulation of Bacteria, Antibiotics & Antimicrobial Tolerance',
				epilog='made by Raphael Schoenefeld & Sebastian Droege')
parser.add_argument('mode', choices=['s', 'p'], help='[s] to simulate data, [p] to plot data')
parser.add_argument('data', help='path for .csv data output')
parser.add_argument('-m', '--model', default='model.nlogo', help='path to .nlogo file | default [model.nlogo]')
parser.add_argument('-c', '--config', default='config.json', help='path to .json config file | default [config.json]')
parser.add_argument('-p', '--plots', nargs='+', default=None, help='No. of plots to show | [1] Bacteria, [2] Tolerance, [3] Antibiotics')
parser.add_argument('--value', default=None, help='plot only this value')
parser.add_argument('-i', '--image', help='path for .png image output of plot')
parser.add_argument('-g', '--gui', action='store_true', help='open gui of netlogo')
parser.add_argument('-v', '--verbose', action='store_true', help='display status information')
args = parser.parse_args()

# throw errors
if (args.plots and args.mode != 'p'):
	parser.error('plot selecting requires [p] mode')
	sys.exit(-1)

# for simulating mode
if args.mode == 's':
	# load json
	with open(args.config) as file:
		dct = json.load(file)
	# do the magic
	try:
		nl = start(args.model, args.gui, args.verbose)
		data = simulate(nl, **dct, verbose=args.verbose)
		with open(args.data, 'w') as file:
			if data.shape[1] > len(reports) + 1:
				file.write(dct['value'][0] + ',')
			file.write('Run No.,' + ','.join([f'{x} in {y}' for x,y in zip(titles, units)]) + '\n')
			np.savetxt(file, data, delimiter=',')
	# dont forget to close netlogo
	finally:
		if nl: nl.kill_workspace()
# for plotting mode
else:
	data = np.genfromtxt(args.data, skip_header=1, delimiter=',')
	if (args.value and len(data) < len(reports) + 2):
		parser.error('data does not contain value information')
		sys.exit(-2)
	plot(data[data[:,0] == float(args.value)][:,1:] if args.value else data, plots=args.plots, img=args.image, verbose=args.verbose)
