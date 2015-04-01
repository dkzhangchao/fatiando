"""

"""
import numpy as np
from scipy import interpolate  # linear interpolation of velocity/density


def seismic_convolutional_model(n_samples, n_traces, model, f, dz=1.,
                                dt=2.e-3, rho=1.):
    """
    Calculate the synthetic seismogram of a geological depth model, Vp is
    mandatory while density is optional. The given model in a matrix form is
    considered a mesh of square cells.

    .. warning::

        Since the relative difference between the model is the important, being
        consistent with the units chosen for the parameters is the only
        requirement, whatever the units.

    Parameters:

    * n_samples, n_traces: integers
        The vertical and horizontal grid dimensions
    * model : 2D-array
        Vp values
    * f : float
        Dominant frequency of the ricker wavelet
    * dz : float
        Length of square grid cells
    * dt: float
        Sample time of the ricker wavelet and of the resulting seismogram

    Returns:

    * synth_l : 2D-array
        Resulting seismogram
    * TWT_ts : 1D-array
        Time axis for the seismogram
    """
    dt_dwn = dt/10.
    TWT = np.zeros((n_samples, n_traces))
    TWT[0, :] = 2*dz/model[0, :]
    for j in range(1, n_samples):
        TWT[j, :] = TWT[j-1]+2*dz/model[j, :]
    TMAX = max(TWT[-1, :])
    #
    TMIN = min(TWT[0, :])
# if dt/TMIN
    TWT_rs = np.zeros(np.ceil(TMAX/dt_dwn))
    for j in range(1, len(TWT_rs)):
        TWT_rs[j] = TWT_rs[j-1]+dt_dwn
    vel = np.ones((np.ceil(TMAX/dt_dwn), n_traces))
    for j in range(0, n_traces):
        kk = np.ceil(TWT[0, j]/dt_dwn)
        lim = np.ceil(TWT[-1, j]/dt_dwn)-1
    # linear interpolation
        tck = interpolate.interp1d(TWT[:, j], model[:, j])
        vel[kk:lim, j] = tck(TWT_rs[kk:lim])
    # extension of the model repeats the last value of the true model
        vel[lim:, j] = vel[lim-1, j]
    # first values equal to the first value of the true model
        vel[0:kk, j] = model[0, j]
    # resampling from dt_dwn to dt
    vel_l = np.zeros((np.ceil(TMAX/dt), n_traces))
    TWT_ts = np.zeros((np.ceil(TMAX/dt), n_traces))
    resmpl = int(dt/dt_dwn)
    vel_l[0, :] = vel[0, :]
    for j in range(0, n_traces):
        for jj in range(1, len(TWT_ts)):
            vel_l[jj, j] = vel[resmpl*jj, j]  # 10=dt/dt_new, dt_new=0.002=2ms
    for j in range(1, len(TWT_ts)):
        TWT_ts[j, :] = TWT_rs[resmpl*j]
    # density calculations
    if isinstance(rho, np.ndarray):
        rho2 = np.ones((np.ceil(TMAX/dt_dwn), n_traces))
        for j in range(0, n_traces):
            kk = np.ceil(TWT[0, j]/dt_dwn)
            lim = np.ceil(TWT[-1, j]/dt_dwn)-1
    # linear interpolation
            tck = interpolate.interp1d(TWT[:, j], rho[:, j])
            rho2[kk:lim, j] = tck(TWT_rs[kk:lim])
    # extension of the model repeats the last value of the true model
            rho2[lim:, j] = rho2[lim-1, j]
    # first values equal to the first value of the true model
            rho2[0:kk, j] = rho[0, j]
        # resampling from dt_dwn to dt
        rho_l = np.zeros((np.ceil(TMAX/dt), n_traces))
        resmpl = int(dt/dt_dwn)
        rho_l[0, :] = rho2[0, :]
        for j in range(0, n_traces):
            for jj in range(1, len(TWT_ts)):
                rho_l[jj, j] = rho[resmpl*jj, j]
    # calculate RC
    if ~isinstance(rho, np.ndarray):
        rc = np.zeros(np.shape(vel_l))
        rc[1:, :] = (vel_l[1:, :]-vel_l[:-1, :])/(vel_l[1:, :]+vel_l[:-1, :])
    else:
        rc[1:, :] = (vel_l[1:, :]*rho_l[1:, :]-vel_l[:-1, :]*rho_l[:-1, :])
                    /(vel_l[1:, :]*rho_l[1:, :]+vel_l[:-1, :]*rho_l[:-1, :])
    #
    # wavelet
    w = rickerwave(f, dt)
    #
    # convolution
    synth_l = np.zeros(np.shape(rc))
    for j in range(0, n_traces):
        if np.shape(rc)[0] >= len(w):
            synth_l[:, j] = np.convolve(rc[:, j], w, mode='same')
        else:
            aux = np.floor(len(w)/2.)
            synth_l[:, j] = np.convolve(rc[:, j], w, mode='full')[aux:-aux]
    return synth_l, TWT_ts


def rickerwave(f, dt):
    nw = 2.2/f/dt
    nw = 2*np.floor(nw/2)+1
    nc = np.floor(nw/2)
    w = np.zeros(nw)
    k = np.arange(1, nw+1)
    alpha = (nc-k+1)*f*dt*np.pi
    beta = alpha**2
    w = (1.-beta*2)*np.exp(-beta)
    return w
