"""
Various types of Time-Frequency estimators.
"""

from pathlib import Path
import argparse
import scipy.io.wavfile as wavio
import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np


def create_sti(filename, nfft, decimation, secoffset):
    """This does the calculation for the STI plot

    Creates the spectral time intensity plot of the whole file. Outputs the sti in dB/Hz. Array is frequency x time.

    Parameters
    ----------
    filename : str
        Name of the wav file.
    nfft : int
        Number of fft bins after decimation.
    decimation : int
        Decimation factor.
    secoffset : float
        Number of seconds to offset the time vector.
    Returns
    -------
    freq : array_like
        Vector of frequency values in Hz
    t_ar : array_like
        Time array in seconds.
    len_s : float
        Number of seconds of data in file.
    Sxxlist : list
        List of the spectrogram arrays in dB/Hz.
    """
    rate, data = wavio.read(filename)
    len_s = float(data.shape[0]) / rate
    freq = np.fft.rfftfreq(nfft, 1.0 / rate)
    if data.ndim == 1:
        if decimation != 1:
            data = sig.decimate(data, decimation)
            rate = rate / decimation

        ntime = data.shape[0] // nfft
        t_ar = (np.arange(ntime) + 0.5) * nfft / rate
        datamat = data[: ntime * nfft].reshape(ntime, nfft)
        Sxx0 = np.abs(np.fft.rfft(datamat, axis=1)) ** 2 / rate
        # freq, t_ar, Sxx0 = sig.spectrogram(data, rate, nfft=nfft, scaling="density")
        Sxx0db = 10 * np.log10(Sxx0.transpose() + 1e-6)
        Sxxlist = [Sxx0db]
    elif data.ndim == 2:
        nchan = data.shape[1]
        Sxxlist = []
        if decimation != 1:
            data = sig.decimate(data, decimation, axis=0)
            rate = rate / decimation
        for ichan in range(nchan):
            ntime = data.shape[0] // nfft
            t_ar = (np.arange(ntime) + 0.5) * nfft / rate
            datamat = data[: ntime * nfft, ichan].reshape(ntime, nfft)
            Sxx0 = np.abs(np.fft.rfft(datamat, axis=1)) ** 2 / rate
            # freq, t_ar, Sxx0 = sig.spectrogram(
            #     data[:, ichan], rate, nfft=nfft, scaling="density"
            # )
            Sxx0db = 10 * np.log10(Sxx0.transpose() + 1e-12)
            Sxxlist.append(Sxx0db)
    t_ar = t_ar + secoffset
    return freq, t_ar, len_s, Sxxlist


# %% Lag Functions


def lag_product(x_in, nlag, nmean=10, numtype=np.complex64, lagtype="centered"):
    """This function will create a  lag product. It will form each lag along the first dimension and then perform sub integrations (arithmatic mean) and then apply a median across the sub integrations. This will deal with n-dimensional arrays where the first two dimensions are the process overwhich the acf is formed and the second is a set of realizations overwhich it is estimated.

    Parameters
    ----------
    x_in : ndarray
        This is a numpy array where the first two dimensions are NsxNp, where Ns is number of samples that process is varying (i.e. range gates in ISR) and Np is number of process relizations (e.g. pulses in ISR).
    nmean : int
        Number of pulses to be averaged first before median applied.
    nlag : int
        Length of the lag product formation.
    numtype : type
        numerical representaiton of the array.

    lagtype : str
        Can be centered forward or backward.

    Returns
    -------
    acf_cent : ndarray
        This is a NrxNl complex numpy array where Nr is number of range gate and Nl is number of lags.
    rg_keep : ndarray
        Indicies of the samples/range gates that will be kept after the lag formation.
    """
    # The first dimension is the where estimation is formed, the second dimension is integrated over. The other dimensions will left along and just carried through.
    (Nr, Np) = x_in.shape[:2]
    otherdims = x_in.shape[2:]
    med_int = np.arange(0, Np, nmean)
    n_start = med_int[:-1]
    n_end = med_int[1:]
    n_sub = len(n_start)
    # Make masks for each piece of data
    if lagtype == "forward":
        arback = np.zeros(nlag, dtype=int)
        arfor = np.arange(nlag, dtype=int)

    elif lagtype == "backward":
        arback = -np.arange(nlag, dtype=int)
        arfor = np.zeros(nlag, dtype=int)
    else:
        # arex = np.arange(0,N/2.0,0.5);
        arback = -np.floor(np.arange(0, nlag / 2.0, 0.5)).astype(int)
        arfor = np.ceil(np.arange(0, nlag / 2.0, 0.5)).astype(int)

    # figure out how much range space will be kept
    ap = -1 * np.min(arback)
    ep = Nr - np.nanmax(arfor)
    rg_keep = np.arange(ap, ep)
    #    wearr = (1./(N-np.tile((arfor-arback)[:,np.newaxis],(1,Np)))).astype(numtype)
    # acf_cent = np.zeros((ep-ap,N))*(1+1j)
    acf_cent = np.zeros((ep - ap, nlag, *otherdims), dtype=numtype)
    for irng, curange in enumerate(rg_keep):
        rng_ar1 = int(curange) + arback
        rng_ar2 = int(curange) + arfor
        # get all of the acfs across pulses # sum along the pulses
        acf_tmp = np.conj(x_in[rng_ar1, :]) * x_in[rng_ar2, :]  # *wearr
        acf_sub = np.zeros((n_sub, nlag, *otherdims), dtype=numtype)
        for i_ind, (ibeg, iend) in enumerate(zip(n_start, n_end)):
            tmp_acf = acf_tmp[:, slice(ibeg, iend)]
            acf_sub[i_ind] = np.nanmean(tmp_acf, axis=1)
        acf_ave = np.nanmedian(acf_sub, axis=0)

        acf_cent[irng, :] = acf_ave  # might need to transpose this
    return acf_cent, rg_keep


def make_sum_rule(nlag, lagtype="centered", srule=None):
    """This function will return the sum rule.

    Parameter
    ---------
    nlag : int
        Number of lags in the ACF.
    lagtype : str
        Type of lags, centered, forward or backward.

    Returns
    -------
    sumrule : ndarray
        A 2 x nlag numpy array that holds the summation rule.
    """
    if lagtype == "forward":
        arback = -np.arange(nlag, dtype=int)
        arforward = np.zeros(nlag, dtype=int)
    elif lagtype == "backward":
        arback = np.zeros(nlag, dtype=int)
        arforward = np.arange(nlag, dtype=int)
    elif lagtype == "centered":
        arback = -np.ceil(np.arange(0, nlag / 2.0, 0.5)).astype(int)
        arforward = np.floor(np.arange(0, nlag / 2.0, 0.5)).astype(int)
    elif lagtype == "barker":
        arback = np.zeros(1, dtype=int)
        arforward = np.zeros(1, dtype=int)
    sumrule = np.array([arback, arforward])
    return sumrule


def make_acf(
    x_in, nlag, nmean=10, numtype=np.complex64, lagtype="centered", srule="centered"
):
    """Performs the full ACF estimation including application of the summation rule to equalize the lag statistics. This will deal with n-dimensional arrays where the first two dimensions are the process overwhich the acf is formed and the second is a set of realizations overwhich it is estimated.

    Parameters
    ----------
    x_in : ndarray
        This is a numpy array where the first two dimensions are NsxNp, where Ns is number of samples that process is varying (i.e. range gates in ISR) and Np is number of process relizations (e.g. pulses in ISR).
    nmean : int
        Number of pulses to be averaged first before median applied.
    nlag : int
        Length of the lag product formation.
    numtype : type
        numerical representaiton of the array.
    lagtype : str
        Can be centered forward or backward.
    srule : str

    Returns
    -------
    acf_est : ndarray
        This is a NrxNl complex numpy array where Nr is number of range gate and Nl is number of lags.
    rg_keep : ndarray
        Indicies of the samples/range gates that will be kept after the lag formation.
    """
    assert nlag >= 1, "nlag must be greater or equal to than one."

    sumrule = make_sum_rule(nlag, lagtype, srule)
    y_out, rng_k1 = lag_product(x_in, nlag, nmean, numtype, lagtype)
    n_rg = y_out.shape[0]
    otherdims = x_in.shape[2:]
    minrg = -1 * sumrule[0].min()
    maxrg = n_rg - sumrule[1].max()
    n_rg_out = maxrg - minrg
    rng_k2 = rng_k1[minrg:maxrg]
    acf_est = np.zeros((n_rg_out, nlag, *otherdims), dtype=numtype)
    for inum, irg in enumerate(range(minrg, maxrg)):
        for ilag in range(nlag):
            cur_sr = sumrule[:, ilag]
            r_sl = slice(irg + cur_sr[0], irg + cur_sr[1]+1)

            # perform a sum on the lags instead of a averaging otherwise you have to weight a window on the output.
            acf_est[inum,ilag] = np.nansum(y_out[r_sl, ilag], axis=0)
    return acf_est, rng_k2


def sub_int(data, nsubs, axis=0):
    """Perform sub integration (mean) and then median on the data.

    Parameters
    ----------
    data : ndarray
        Data array to be averaged over.
    nsubs : int
        Sub integration periods
    axis : int
        Axis over which the data is averaged.

    Returns
    -------
    data_int : ndarray
        Data array after the averaging
    """
    dshape = data.shape
    n_els = dshape[axis]
    tshape = list(dshape)
    tshape[axis] = nsubs
    ar1 = np.linspace(0, n_els, nsubs, dtype=int, endpoint=False)
    ar2 = np.roll(ar1, -1)
    ar2[-1] = n_els
    int_points = np.column_stack((ar1, ar2))
    tmp_data = np.empty(tshape, dtype=data.dtype)

    for i_int, iloc in enumerate(int_points):
        cur_d = data.take(range(*iloc), axis=axis)
        tmp_data[i_int] = np.nanmean(cur_d, axis=axis)
    data_int = np.nanmedian(tmp_data, axis=axis)

    return data_int


# %% Barker Codess
def gen_bark(blen):
    """This function will output a Barker code pulse.

    Parameters
    ----------
    blen : int
        An integer for number of bauds in barker code.

    Returns
    -------
    outar : ndarray
        A blen length numpy array.
    """
    bdict = {
        1: [-1],
        2: [-1, 1],
        3: [-1, -1, 1],
        4: [-1, -1, 1, -1],
        5: [-1, -1, -1, 1, -1],
        7: [-1, -1, -1, 1, 1, -1, 1],
        11: [-1, -1, -1, 1, 1, 1, -1, 1, 1, -1, 1],
        13: [-1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1],
    }
    outar = np.array(bdict[blen])
    outar.astype(np.float64)
    return outar


def barker_lag(x_in, numtype=None, pulse=gen_bark(13)):
    """This will process barker code data by filtering it with a barker code pulse and then sum up the pulses.

    Paramaters
    ----------
    x_in : ndarray
        A complex numpy array size NpxNs where Np is the number of pulses and
    numtype : type
        The type used for processing the data.
    pulse : ndarray
        The barkercode pulse.
    Returns
    -------
    outdata : ndarray
        A Nrx1 size numpy array that holds the processed data. Nr is the number of range gates
    """

    if numtype is None:
        numtype = x_in.dtype

    # It will be assumed the data will be pulses vs rangne
    x_in = x_in.transpose()
    (Nr, Np) = x_in.shape
    pulsepow = np.power(np.absolute(pulse), 2.0).sum()
    # Make matched filter
    filt = np.fft.fft(pulse[::-1] / np.sqrt(pulsepow), n=Nr)
    filtmat = np.repeat(filt[:, np.newaxis], Np, axis=1)
    rawfreq = np.fft.fft(x_in, axis=0)
    outdata = np.fft.ifft(filtmat * rawfreq, axis=0)

    outdata = outdata * outdata.conj()
    outdata = np.sum(outdata, axis=-1)
    # increase the number of axes
    return outdata[len(pulse) - 1 :, np.newaxis]
