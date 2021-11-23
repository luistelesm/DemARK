# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
# Preliminaries
from HARK.ConsumptionSaving.ConsIndShockModel import (
    IndShockConsumerType
)

from HARK.ConsumptionSaving.tests.test_IndShockConsumerType import (
    dict_harmenberg    
)

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# %% [markdown]
# # Description of the problem
#
# In macroeconomic models with heterogeneous agents, the permanent component of agents' income ($\textbf{P}_t$) often follows a geometric random walk. At any time, these economies include agents with different levels of permanent income. To find an aggregate characteristic of these economies such as aggregate consumption $\bar{\textbf{C}}_t$, one must integrate over permanent income and all the other relevant state variables
#
# \begin{equation*}
# \bar{\textbf{C}}_t = \int \int C(\text{State},\textbf{P}) \times f_t(\text{State},\textbf{P}) \, d\text{State}\, d\textbf{P}, 
# \end{equation*}
#
# where $\text{State}$ denotes any other state variables that consumption might depend on, $C(\cdot,\cdot)$ is the individual consumption function, and $f_t(\cdot,\cdot)$ is the joint density function of permanent income and the other state variables at time $t$.
#
# Models like the traditional Buffer-Stock-Saving agent with CRRA utility [CITE CARROLL 2021] are homothetic in permanent income. This means that one can solve for a normalized policy function $c(\cdot)$ such that
#
# \begin{equation*}
#     C(\text{State},\textbf{P}) = c\left(\frac{1}{\textbf{P}}\times \text{State}\right)\times \textbf{P} \qquad \forall \text{State},\textbf{P}.
# \end{equation*}
#
# In practice, this implies that one can defined a normalized state vector $\widetilde{\text{State}} = \text{State}/\textbf{P}$ and solve for the normalized policy function. This eliminates one dimension of the optimization problem problem, $\textbf{P}$.
#
# While convenient for the solution of the agents' optimization problem, homotheticity has not simplified our aggregation calculations as we still have
#
# \begin{equation*}
# \begin{split}
# \bar{\textbf{C}}_t =& \int \int C(\text{State},\textbf{P}) \times f_t(\text{State},\textbf{P}) \, d\text{State}\, d\textbf{P}\\
# =& \int \int c\left(\frac{1}{\textbf{P}}\times \text{State}\right)\times \textbf{P} \times f_t(\text{State},\textbf{P}) \, d\text{State}\, d\textbf{P}
# \end{split}
# \end{equation*}
#

# %% [markdown]
# # Description of the method

# %% [markdown]
# # Demonstration of HARK's implementation and the gain in efficiency

# %% Experiment setup
burnin = 2000
sample_every = 50
n_sample = 100
max_agents = 10000

sample_periods = np.arange(start=burnin,
                           stop = burnin+sample_every*n_sample,
                           step = sample_every, dtype = int)

# %% Define function to get our stats of interest
def sumstats(sims, sample_periods):
    
    # Sims' columns are different agents and rows are different times.
    # Subset the times at which we'll sample and transpose.
    samples = pd.DataFrame(sims[sample_periods,].T)
    
    # Get rolling averages
    avgs = samples.expanding(1).mean()
    
    # Now get the mean and standard deviations across samples with every
    # number of agents
    means = avgs.mean(axis = 1)
    stds = avgs.std(axis = 1)
    
    # Also return the full last sample
    return {'means':  means, 'stds': stds, 'dist_last': sims[-1,]}


# %% Create and simulate agent
# Simulations
dict_harmenberg.update(
    {'T_sim': max(sample_periods)+1, 'AgentCount': max_agents,
     'track_vars': [ 'mNrm','cNrm','pLvl']}
)

example = IndShockConsumerType(**dict_harmenberg, verbose = 0)
example.cycles = 0

example.solve()

# Base simulation
example.initialize_sim()
example.simulate()

M_base = sumstats(example.history['mNrm'] * example.history['pLvl'],
                  sample_periods)

C_base = sumstats(example.history['cNrm'] * example.history['pLvl'],
                  sample_periods)

# Harmenberg PIN simulation
example.neutral_measure = True
example.update_income_process()
example.initialize_sim()
example.simulate()

M_pin = sumstats(example.history['mNrm'], sample_periods)
C_pin = sumstats(example.history['cNrm'], sample_periods)

# %% Plots
# Plots

nagents = np.arange(1,max_agents+1,1)

# Market resources
fig, axs = plt.subplots(2)
axs[0].plot(nagents, M_base['stds'], label = 'Base')
axs[0].plot(nagents, M_pin['stds'], label = 'Perm. Inc. Neutral')
axs[0].set_yscale('log')
axs[0].set_xscale('log')
axs[0].grid()
axs[0].legend()

axs[1].plot(nagents, M_base['means'], label = 'Base')
axs[1].plot(nagents, M_pin['means'], label = 'Perm. Inc. Neutral')
axs[1].set_xscale('log')
axs[1].set_xlabel('Number of Agents')
axs[1].grid()
plt.show()

# Consumption
fig, axs = plt.subplots(2)
axs[0].plot(nagents, C_base['stds'], label = 'Base')
axs[0].plot(nagents, C_pin['stds'], label = 'Perm. Inc. Neutral')
axs[0].set_yscale('log')
axs[0].set_xscale('log')
axs[0].grid()
axs[0].legend()

axs[1].plot(nagents, C_base['means'], label = 'Base')
axs[1].plot(nagents, C_pin['means'], label = 'Perm. Inc. Neutral')
axs[1].set_xscale('log')
axs[1].set_xlabel('Number of Agents')
axs[1].grid()
plt.show()

# %% [markdown]
# # Comparison of the PIN-measure and the base measure

# %%
mdists = pd.DataFrame({'Base': M_base['dist_last'],
                       'PIN': M_pin['dist_last']})

mdists.plot.kde()
plt.xlim([0,10])
