# Guide to basic configuration for Mars on PSG

## Introduction

This simple guide should help a beginner user to setup the basic configuration for Mars radiative simulation using Planetary Spectrum Generator. The initial configuration should be done using the web interface at <https://psg.gsfc.nasa.gov/index.php>. After the whole procedure the configuration file can be downloaded and used for run the program locally.

## Initial step and premises

To proceed with the configuration, connect to <https://psg.gsfc.nasa.gov/index.php>. To avoid to consider previous setup click the ***Reset*** button before starting a new configuration (unless you know what are you doing).

## Change Object

The first thing to set is the object we want to simulate, for this, let us start using the ***Change Object*** button.

Select ***Planet*** >> ***Mars***, choose a date and click ***Ephemeris*** to confirm. Note that specifically on Mars the choice of the date plays a very important role in the composition of the atmosphere. The winter atmosphere and the summer one are very different among each other. In fact, during winters, clouds of CO<sub>2</sub> form near the poles, while during summers a lot of dust is released into the atmosphere, especially over the equatorial zone. For the initial configuration we suggest the default date (08/04/2020).

Concerning the *View geometry*, we suggest to begin with ***Nadir*** *from* ***User-defined*** observation point. Select *Longitude* and *Latitude* (for this example 100.00 and 0.00) and the altitude (*Distance*) (here 400.00 km).

Finally, to proceed, click on ***Save settings***.

## Change Composition

Now, it is time to deal with atmospheric composition. For initial simulation on Mars, we are going to use a tabulated standard atmosphere. Select *Atmosphere* >> ***Atmospheric template*** >> ***Mars Climate Database (MCD)*** and click ***Load***. This will import atmospheric profiles for the most important gases present in the Martian atmosphere. Among the voice *Processes*, one can add or remove the computation of different things. Since we are interested in the Infrared part of the spectrum we will remove the computation of **Rayleigh** scattering and **UV_all**. We add **Layering** for the computation of the Optical Depths, **Contribution** for ... 

For now we leave the *Surface* part untouched. Also in this case we click on ***Save settings***.

## Change Instrument

For the instrument, select ***User defined***. The chose spectral range is the one of FORUM: from 100 cm<sup>-1</sup> to 1600 cm<sup>-1</sup>, with a spectral resolution of 0.4 cm<sup>-1</sup>. The selected function for the convolution is the ***Boxcar***. Also the *spectrum intensity unit* can be set to ***W/sr/m2/cm-1***.

***Save settings*** after this.

## Download configuration and generate the spectrum

Now we can download the config file and generate the spectrum.