#!/usr/bin/env python
# coding: utf-8

# # Directional Coupler EMEPy Tutorial
#
# This tutorial utilizes EMEPy's new feature, the profile monitor, to estimate the coupling length of a standard silicon directional coupler.

# In[1]:


import emepy as em
from emepy.eme import Layer, EME
from emepy.mode import Mode
from emepy.fd import MSEMpy
import numpy as np
from matplotlib import pyplot as plt
from emepy.tools import Si, SiO2
import time

# Geometric parameters
wavelength = 1.55e-6  # Wavelength
width = 0.4e-6  # Width of left waveguide
gap = 0.2e-6  # Gap between waveguides
thickness = 0.22e-6  # Thickness of left waveguide
num_modes = 1  # Number of modes
mesh = 100  # Number of mesh points
core_index = Si(wavelength * 1e6)  # Silicon core
cladding_index = SiO2(wavelength * 1e6)  # Oxide cladding
x = np.linspace(-2e-6, 2e-6, mesh)
n = np.ones(mesh) * cladding_index


# ### Define structure and verify shape

# Create simulation
eme = EME(quiet=True,parallel=True,num_periods=2)

# Create left waveguide
single_left_edge = -gap / 2 - width
single_right_edge = -gap / 2
single_n = np.where((single_left_edge <= x) * (x <= single_right_edge), core_index, n)

single_channel = MSEMpy(
    wavelength,
    width=None,
    thickness=thickness,
    cladding_index=cladding_index,
    num_modes=num_modes,
    mesh=mesh,
    x=x,
    y=x,
    n=single_n,
)

# Create left waveguide
left_edge = -gap / 2 - width
right_edge = -gap / 2
n = np.where((left_edge <= x) * (x <= right_edge), core_index, n)

# Create right waveguide
left_edge = gap / 2
right_edge = gap / 2 + width
n = np.where((left_edge <= x) * (x <= right_edge), core_index, n)

two_channel = MSEMpy(
    wavelength,
    width=None,
    thickness=thickness,
    cladding_index=cladding_index,
    num_modes=num_modes,
    mesh=mesh,
    x=x,
    y=x,
    n=n,
)

for i in range(3):
    eme.add_layer(Layer(single_channel, num_modes, wavelength, 0.5e-6))
# eme.add_layer(Layer(single_channel, num_modes, wavelength, 0.5e-6))
# eme.add_layer(Layer(single_channel, num_modes, wavelength, 0.5e-6))
# eme.add_layer(Layer(single_channel, num_modes, wavelength, 0.5e-6))
# eme.add_layer(Layer(two_channel, num_modes, wavelength, 25e-6))

# draw
# if eme.am_master():
    # plt.figure()
    # eme.draw()
    # plt.show()


# ### Add a monitor

source = em.Source(z=2.3e-6,mode_coeffs=[1],k=-1)
monitor = eme.add_monitor(axes="xz",sources=[source])


# # ### Propagate
t = time.time()
eme.solve_modes()
# if eme.am_master():
#     print("time to solve for 30 modes: {}".format(time.time()-t))
eme.propagate(left_coeffs=[],right_coeffs=[])  # propagate at given wavelength

# # print(np.matmul(eme.s_parameters()[0],np.array([1,0])))
# # print(eme.s_parameters()[0])

# # ### Visualize Monitors

if eme.am_master():
    # plt.figure()
    # monitor.visualize(component="n")
    # plt.colorbar()
    # plt.show()

    plt.figure()
    monitor.visualize(component="Hy")
    plt.colorbar()
    plt.show()

