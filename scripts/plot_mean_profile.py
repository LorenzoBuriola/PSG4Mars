import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('mean_profile.csv')

#plots
T = data.Temperature.to_numpy()
P = data.Pressure.to_numpy()
hh = data.Altitude.to_numpy()  # Altitude in km
sdT = std.Temperature.to_numpy()

fig,ax = plt.subplots(figsize=(8, 6))
ax.set_yscale('log')
ax.plot(T, P, color = 'firebrick', marker='o', label='Mean T profile')
ax.plot(T+60, P, color = 'firebrick', linestyle='--', label=r'Mean T profile $\pm$ 60 K')
ax.plot(T-60, P, color = 'firebrick', linestyle='--')
ax.fill_betweenx(P, T-2*sdT, T+2*sdT, color = 'indianred', alpha = 0.5, label=r'2$\sigma$')
ax.invert_yaxis()
ax.set_xlabel('T [K]', fontsize=20)
ax.set_ylabel('P [bar]', fontsize=20)
ax.legend(fontsize = 14)
plt.tick_params(axis='both', which='major', labelsize=18)
ax_h = ax.twinx()
ax_h.plot(T, hh, alpha = 0)
ax_h.set_ylabel('Altitude [km]', fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=18)

fig.savefig('T_prof.png', dpi=300, bbox_inches='tight')

listnames = ['H2O', 'CO', 'CO2', 'O3']
fig2,ax2 = plt.subplots(figsize=(8, 6))
cc = ['blue', 'green', 'red', 'orange']
for i,obj in enumerate(listnames):
    mean = data[obj].to_numpy()
    sd = std[obj].to_numpy()
    fig,ax = plt.subplots()
    ax.plot(mean, P, color = 'darkorange', marker='o', label=listnames[i])
    ax.fill_betweenx(P, np.maximum(mean-2*sd,0), mean+2*sd, color = 'navajowhite', alpha = 0.5)
    ax.invert_yaxis()
    ax.set_yscale('log')
    ax.set_ylabel('P [bar]')
    ax.set_xlabel(f'{obj} VMR')
    fig.savefig(f'{obj}_profiles.png', dpi=300, bbox_inches='tight')
    ax2.plot(mean, P, label=listnames[i], color = cc[i], marker='.')
plt.close(fig)
ax2.plot(data['HCl'], P, label='HCl', color = 'purple', marker='.')
ax2.invert_yaxis()
ax2.set_yscale('log')
ax2.set_ylabel('P [bar]', fontsize=20)
ax2.set_xlabel('VMR', fontsize=20)
ax2.set_xscale('log')
ax2.legend(fontsize=16)
ax2.tick_params(axis='both', which='major', labelsize=18)
fig2.savefig('mean_profiles.png', dpi=300, bbox_inches='tight')