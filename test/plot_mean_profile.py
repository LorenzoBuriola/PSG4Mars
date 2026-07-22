import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('../output/mean_profile.csv', header=[0,1])
df_mean = data['Mean'].copy()
df_std = data['StdError'].copy()

Temperature = df_mean['Temperature'].to_numpy()
Pressure = df_mean['Pressure'].to_numpy()
Altitude = df_mean['Altitude'].to_numpy()
sdTemp = df_std['Temperature'].to_numpy()

#plots

fig,ax = plt.subplots(figsize=(8, 6))
ax.set_yscale('log')
ax.plot(Temperature, Pressure, color = 'firebrick', marker='o', label='Mean T profile')
ax.plot(Temperature+60, Pressure, color = 'firebrick', linestyle='--', label=r'Mean T profile $\pm$ 60 K')
ax.plot(Temperature-60, Pressure, color = 'firebrick', linestyle='--')
ax.fill_betweenx(Pressure, Temperature-2*sdTemp, Temperature+2*sdTemp, color = 'indianred', alpha = 0.5, label=r'2$\sigma$')
ax.invert_yaxis()
ax.set_xlabel('T [K]', fontsize=20)
ax.set_ylabel('P [bar]', fontsize=20)
ax.legend(fontsize = 14)
plt.tick_params(axis='both', which='major', labelsize=18)
ax_h = ax.twinx()
ax_h.plot(Temperature, Altitude, alpha = 0)
ax_h.set_ylabel('Altitude [km]', fontsize=20)
plt.tick_params(axis='both', which='major', labelsize=18)

fig.savefig('../fig/T_prof.png', dpi=300, bbox_inches='tight')

listnames = ['H2O', 'CO', 'CO2', 'O3']
fig2,ax2 = plt.subplots(figsize=(8, 6))
cc = ['blue', 'green', 'red', 'orange']
for i,obj in enumerate(listnames):
    mean = df_mean[obj].to_numpy()
    sd = df_std[obj].to_numpy()
    fig,ax = plt.subplots()
    ax.plot(mean, Pressure, color = 'darkorange', marker='o', label=listnames[i])
    ax.fill_betweenx(Pressure, np.maximum(mean-2*sd,0), mean+2*sd, color = 'navajowhite', alpha = 0.5)
    ax.invert_yaxis()
    ax.set_yscale('log')
    ax.set_ylabel('P [bar]')
    ax.set_xlabel(f'{obj} VMR')
    fig.savefig(f'../fig/{obj}_profiles.png', dpi=300, bbox_inches='tight')
    ax2.plot(mean, Pressure, label=listnames[i], color = cc[i], marker='.')
plt.close(fig)
ax2.plot(df_mean['HCl'], Pressure, label='HCl', color = 'purple', marker='.')
ax2.invert_yaxis()
ax2.set_yscale('log')
ax2.set_ylabel('P [bar]', fontsize=20)
ax2.set_xlabel('VMR', fontsize=20)
ax2.set_xscale('log')
ax2.legend(fontsize=16)
ax2.tick_params(axis='both', which='major', labelsize=18)
fig2.savefig('../fig/mean_profiles.png', dpi=300, bbox_inches='tight')