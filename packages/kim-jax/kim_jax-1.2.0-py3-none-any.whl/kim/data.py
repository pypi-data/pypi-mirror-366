"""The general data class."""

# Author: Peishi Jiang <shixijps@gmail.com>

import numpy as np

import json
import pickle
from pathlib import Path, PosixPath

from typing import Optional

from .pre_analysis import analyze_interdependency
from .utils import get_scaler

from jaxtyping import Array

    # Attributes
    # ----------
    # xdata (array-like): the copy of xdata
    # ydata (array-like): the copy of ydata
    # Ns (int): the number of samples
    # Nx (int): the number of predictors
    # Ny (int): the number of predictands
    # xscaler_type (str): the type of xdata scaler, either 'minmax', 'normalize', 'standard', or 'log'
    # yscaler_type (str): the type of ydata scaler, either 'minmax', 'normalize', 'standard', or 'log'
    # xscaler (str): the xdata scaler
    # yscaler (str): the ydata scaler
    # sensitivity_config (dict): the sensitivity analysis configuration
    # sensitivity_done (bool): whether the sensitivity analysis is performed
    # sensitivity (array-like): the calculated sensitivity with shape (Nx, Ny)
    # sensitivity_mask (array-like): the calculated sensitivity mask with shape (Nx, Ny)
    # cond_sensitivity_mask (array-like): the calculated conditional sensitivity mask with shape (Nx, Ny)

class Data(object):
    """The Data object.

    Attributes
    ----------
    xdata : array-like
        the copy of xdata
    ydata : array-like
        the copy of ydata
    Ns : int
        the number of samples
    Nx : int
        the number of predictors
    Ny : int
        the number of predictands
    xscaler_type : str
        the type of xdata scaler, either 'minmax', 'normalize', 'standard', or 'log'
    yscaler_type : str
        the type of ydata scaler, either 'minmax', 'normalize', 'standard', or 'log'
    xscaler : str
        the xdata scaler
    yscaler : str
        the ydata scaler
    sensitivity_config : dict
        the sensitivity analysis configuration
    sensitivity_done : bool
        whether the sensitivity analysis is performed
    sensitivity : array-like
        the calculated sensitivity with shape (Nx, Ny)
    sensitivity_mask : array-like
        the calculated sensitivity mask with shape (Nx, Ny)
    cond_sensitivity_mask : array-like
        the calculated conditional sensitivity mask with shape (Nx, Ny)

    """

    def __init__(self, xdata: Optional[Array]=None, ydata: Optional[Array]=None, 
                 fdata: Optional[PosixPath]=None, xscaler_type: str='', yscaler_type: str=''):
        """Initialization function.

        Args:
            xdata (array-like): the predictors with shape (Ns, Nx)
            fdata (PosixPath): the root path where an existing data instance will be loaded
            ydata (array-like): the predictands with shape (Ns, Ny)
            xscaler_type (str): the type of xdata scaler, either `minmax`, `normalize`, `standard`, `log`, or ``
            yscaler_type (str): the type of ydata scaler, either `minmax`, `normalize`, `standard`, `log`, or ``
        """
        if fdata is not None:
           self.sensitivity_done = True
           self.load(fdata, check_xy=False, overwrite=True) 
        
        elif xdata is None or ydata is None:
            raise Exception("xdata and ydata are not given!")
        
        else:
            # Data array
            self.xdata = xdata
            self.ydata = ydata

            # Data dimensions
            assert xdata.shape[0] == ydata.shape[0], \
                "xdata and ydata must be the same number of samples"
            self.Ns = xdata.shape[0]
            self.Nx = xdata.shape[1]
            self.Ny = ydata.shape[1]

            # Create the transformer of the data
            self.xscaler_type = xscaler_type.lower()
            self.yscaler_type = yscaler_type.lower()
            self.xscaler = get_scaler(self.xdata, self.xscaler_type)
            self.yscaler = get_scaler(self.ydata, self.yscaler_type)

            # Data sensitivity
            self.sensitivity_config = {
                "method": None,
                "metric": None,
                "sst": None,
                "ntest": None,
                "alpha": None,
                "bins": None,
                "k": None,
                "n_jobs": None,
                "seed_shuffle": None,
            }
            self.sensitivity = np.zeros([self.Nx, self.Ny])
            self.sensitivity_mask = np.zeros([self.Nx, self.Ny], dtype='bool')
            self.cond_sensitivity_mask = np.zeros([self.Nx, self.Ny], dtype='bool')
            self.sensitivity_done = False
            self.loaded_from_other_sources = False
    

    def calculate_sensitivity(
        self, method: str='gsa', metric: str='it-bins', 
        sst: bool=False, ntest: int=100, alpha: float=0.05, 
        bins: int=10, k: int=5, n_jobs=-1, seed_shuffle: int=1234,
        verbose: int=0
    ):
        """Calculate the sensitivity between `self.xdata` and `self.ydata` using either `pairwise_analysis` or `pc` method.
           The results are updated in `self.sensitivity_done`, `self.sensitivity`, `self.sensitivity_mask`, and `self.cond_sensitivity_mask`.
        
        Args:
            method (str): The preliminary analysis method, including:
                `gsa`: the pairwise global sensitivity analysis
                `pc`: a modified PC algorithm that include conditional indendpence test after gsa
                Defaults to `gsa`.
            metric (str): The metric calculating the sensitivity, including:
                `it-bins`: the information-theoretic measures (MI and CMI) using binning approach
                `it-knn`: the information-theoretic measures (MI and CMI) using knn approach
                `corr`: the correlation coefficient
                Defaults to `corr`.
            sst (bool): Whether to perform the statistical significance test or the shuffle test. Defaults to False.
            ntest (int): The number of shuffled samples in sst. Defaults to 100.
            alpha (float): The significance level. Defaults to 0.05.
            bins (int): The number of bins for each dimension when metric == "it-bins". Defaults to 10.
            k (int): The number of nearest neighbors when metric == "it-knn". Defaults to 5.
            n_jobs (int): The number of processers/threads used by joblib.Parallel. Defaults to -1.
            seed_shuffle (int): The random seed number for doing shuffle test. Defaults to 5.
            verbose (int): The verbosity level (0: normal, 1: debug). Defaults to 0.
        """
        sensitivity_config = self.sensitivity_config
        # xdata, ydata = self.xdata, self.ydata
        xdata_scaled, ydata_scaled = self.xdata_scaled, self.ydata_scaled
        # Calculate sensitivity
        sensitivity, sensitivity_mask, cond_sensitivity_mask = analyze_interdependency(
            xdata_scaled, ydata_scaled, method, metric, sst, 
            ntest, alpha, bins, k, n_jobs, seed_shuffle, verbose=verbose
        )

        # Update the configuration
        sensitivity_config['method'] = method
        sensitivity_config['metric'] = metric
        sensitivity_config['sst'] = sst
        sensitivity_config['ntest'] = ntest
        sensitivity_config['alpha'] = alpha
        sensitivity_config['bins'] = bins
        sensitivity_config['k'] = k
        sensitivity_config['n_jobs'] = n_jobs
        sensitivity_config['seed_shuffle'] = seed_shuffle
        self.sensitivity_config = sensitivity_config

        # Update the analysis result
        self.sensitivity_done = True
        self.sensitivity = sensitivity
        self.sensitivity_mask = sensitivity_mask
        self.cond_sensitivity_mask = cond_sensitivity_mask
    
    @property
    def xdata_scaled(self):
        """Perform normalization on `self.xdata` based on the given normalization type `self.xscaler_type`.
        
        Returns:
            array-like: the scaled `self.xdata`
        """
        return self.xscaler.transform(self.xdata)

    @property
    def ydata_scaled(self):
        """Perform normalization on `self.ydata` based on the given normalization type `self.yscaler_type`.

        Returns:
            array-like: the scaled `self.ydata`
        """
        return self.yscaler.transform(self.ydata)
    
    def save(self, rootpath: PosixPath=Path("./")):
        """Save data and sensitivity analysis results to specified location, including:
            - data (x, y) and scaler
            - sensitivity analysis configuration
            - sensitivity analysis results

        Args:
            rootpath (PosixPath): the root path where data will be saved

        """
        if not self.sensitivity_done:
            raise Exception("Sensitivity analysis is not done yet.")

        if not rootpath.exists():
            rootpath.mkdir(parents=True)

        # xdata and ydata
        f_x, f_y = rootpath / "x.npy", rootpath / "y.npy"
        np.save(f_x, self.xdata)
        np.save(f_y, self.ydata)

        # x and y scalers
        f_scaler = rootpath / "scaler.pkl"
        scaler = {"x": self.xscaler, "y": self.yscaler, 
                  "xtype": self.xscaler_type, "ytype": self.yscaler_type}
        with open(f_scaler, "wb") as f:
            pickle.dump(scaler, f)
        
        # sensitivity configurations
        f_sensitivity_config = rootpath / "sens_configs.json"
        with open(f_sensitivity_config, "w") as f:
            json.dump(self.sensitivity_config, f)

        # sensitivity results
        f_s = rootpath / "sensitivity.npy"
        f_mask = rootpath / "sensitivity_mask.npy"
        f_cond_mask = rootpath / "cond_sensitivity_mask.npy"
        np.save(f_s, self.sensitivity)
        np.save(f_mask, self.sensitivity_mask)
        np.save(f_cond_mask, self.cond_sensitivity_mask)
    
    def load(self, rootpath: PosixPath=Path("./"), check_xy: bool=True, overwrite: bool=False):
        """load data and sensitivity analysis results from specified location, including:
            - data (x, y) and scaler
            - sensitivity analysis configuration
            - sensitivity analysis results

        Args:
            rootpath (PosixPath): the root path where data will be loaded

        """
        if self.sensitivity_done and not overwrite:
            raise Exception("Sensitivity analysis has been performed.")
        
        # Load xdata and ydata
        f_x, f_y = rootpath / "x.npy", rootpath / "y.npy"
        xdata = np.load(f_x)
        ydata = np.load(f_y)
        if check_xy:
            assert np.allclose(xdata, self.xdata)
            assert np.allclose(ydata, self.ydata)
        self.xdata, self.ydata = xdata, ydata
        self.Ns = xdata.shape[0]
        self.Nx = xdata.shape[1]
        self.Ny = ydata.shape[1]

        # x and y scalers
        f_scaler = rootpath / "scaler.pkl"
        with open(f_scaler, "rb") as f:
            scaler = pickle.load(f)
        self.xscaler = scaler['x']
        self.yscaler = scaler['y']
        self.xscaler_type = scaler['xtype']
        self.yscaler_type = scaler['ytype']
        
        # sensitivity configurations
        f_sensitivity_config = rootpath / "sens_configs.json"
        with open(f_sensitivity_config, "r") as f:
            self.sensitivity_config = json.load(f)

        # sensitivity results
        f_s = rootpath / "sensitivity.npy"
        f_mask = rootpath / "sensitivity_mask.npy"
        f_cond_mask = rootpath / "cond_sensitivity_mask.npy"
        sensitivity = np.load(f_s)
        sensitivity_mask = np.load(f_mask)
        cond_sensitivity_mask = np.load(f_cond_mask)
        assert sensitivity.shape == (self.Nx, self.Ny)
        assert sensitivity_mask.shape == (self.Nx, self.Ny)
        assert cond_sensitivity_mask.shape == (self.Nx, self.Ny)
        self.sensitivity = sensitivity
        self.sensitivity_mask = sensitivity_mask
        self.cond_sensitivity_mask = cond_sensitivity_mask

        self.loaded_from_other_sources = True
        self.sensitivity_done = True