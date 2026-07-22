import numpy as np
import matplotlib.pyplot as plt

p_edges = np.load('../output/p_edges.npy')
print(f'number of pressure levels generated: {p_edges.shape[0]}')
print(f'pressure levels generated in mbar: \n {p_edges*1e3}')

fig,ax = plt.subplots(figsize=(10,6))
ax.plot(np.arange(len(p_edges))+1, p_edges[::-1]*1e3, marker='o', color = 'black')
ax.set_xlabel('# layer')
ax.set_ylabel('Pressure [mbar]')
ax.set_yscale('log')
ax.invert_yaxis()
#horizontal line at 1e-3 bar
ax.axhline(y=1e-5, color='r', linestyle='--')
ax.axhline(y=1, color='r', linestyle='--')
ax.axvline(x=31, color='g', linestyle='--')
ax.axvline(x=51, color='g', linestyle='--')
plt.savefig('../fig/p_edges.png', dpi=300)