"""Plotting functions."""

import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

small_size = 15
medium_size = 25
bigger_size = 30
plt.rc('font', size=small_size)          # controls default text sizes
plt.rc('axes', titlesize=small_size)    # fontsize of the axes title
plt.rc('axes', labelsize=small_size)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=small_size)    # fontsize of the tick labels
plt.rc('ytick', labelsize=small_size)    # fontsize of the tick labels
plt.rc('legend', fontsize=small_size)    # legend fontsize
plt.rc('figure', titlesize=small_size)  # fontsize of the figure title
plt.rc('text', usetex = False)


def plot_sensitivity(sensitivity_mask, ax=None, xlabels=None, ylabels=None):

    if xlabels is not None and ylabels is not None:
       sensitivity_mask = pd.DataFrame(sensitivity_mask, index=xlabels, columns=ylabels)

    ax = sns.heatmap( sensitivity_mask, ax=ax, cmap='Blues')
    ax.set(title='Sensitivity heatmap')


def plot_sensitivity_mask(sensitivity_mask, ax=None, xlabels=None, ylabels=None):
    # define the colors
    cmap = mpl.colors.ListedColormap(['lightgrey', 'tab:blue'])

    # create a normalize object the describes the limits of
    # each color
    bounds = [-.5, 0.5, 1.5]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    if xlabels is not None and ylabels is not None:
       sensitivity_mask = pd.DataFrame(sensitivity_mask, index=xlabels, columns=ylabels)

    ax = sns.heatmap(
        sensitivity_mask, ax=ax, cmap=cmap, norm=norm, 
        cbar_kws={"ticks": [0, 1]}
      )
    ax.collections[0].colorbar.set_ticklabels(["not sensitive", "sensitive"], rotation=90)
    ax.set(title='Sensitivity mask')


def plot_1to1_scatter(r, iy=0, ax=None, train_or_test='test', model='', y_var=''):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5,4))
    n_ens = r['ens predict'][train_or_test].shape[0]
    for k in range(n_ens):
        ax.scatter(r['true'][train_or_test][...,iy], r['ens predict'][train_or_test][k,...,iy], 
                      color='lightgrey', label='ensemble' if k ==0 else None)
    ax.scatter(r['true'][train_or_test][...,iy], r['weighted mean predict'][train_or_test][...,iy], 
                color='black', label='weighted mean')
    ax.set(xlabel='True', ylabel='Prediction', title=f"{model}: {y_var}")
    ax.legend()
    return ax


def plot_1to1_uncertainty(r, iy=0, ax=None, train_or_test='test', model='', y_var=''):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(5,4))
    x = r['true'][train_or_test][...,iy]
    y = r['weighted mean predict'][train_or_test][...,iy]
    std = r['weighted std predict'][train_or_test][...,iy]
    bias = r['weighted bias'][train_or_test][iy]
    uncertainty = r['weighted relative uncertainty'][train_or_test][iy]
    ax.errorbar(x, y, std, color='black', linestyle='None', fmt='o', markersize=2, capsize=2)
    lim = ax.get_ylim()
    ax.plot(lim, lim, '--', color='tab:blue')
    ax.set(xlim=lim, ylim=lim, xlabel='True', ylabel='Prediction', 
            title=f"{model}: {y_var} \n (bias: {bias:.3f}; uncertainty: {uncertainty:.3f})")
    return ax
