# sources:
# https://pynetlogo.readthedocs.io/en/latest/_docs/introduction.html
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pynetlogo

def plot(data, cmd):
	fig = plt.figure()

	bc = fig.add_subplot(1,2,1)
	bc.plot(data[cmd[0]], label='Bacteria')
	bc.set_xlabel('Ticks')
	bc.set_ylabel('Counts')
	bc.legend()

	rs = fig.add_subplot(1,2,2)
	av = [np.mean(x) for x in data[cmd[1]]]
	rs.plot(av, color='r', label='Average Resistance')
	bc.set_xlabel('Ticks')
	bc.set_ylabel('Resistance in %')
	rs.legend()
	plt.show()


netlogo = pynetlogo.NetLogoLink(
#	gui=True,
#	jvm_path='/usr/lib/jvm/java-23-openjdk/lib/libjli.so',
	netlogo_home='/opt/netlogo'
)

netlogo.load_model('model.nlogo')
netlogo.command('setup')
#netlogo.command('repeat 100 [go]')

cmd = ['count bacteria', '[resistance] of bacteria']
data = netlogo.repeat_report(cmd, 200, go='go')
data = pd.DataFrame(data)
netlogo.kill_workspace()

plot(data, cmd)

