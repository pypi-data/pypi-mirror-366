from scipy.linalg import eigh
import numpy as np


def find_psd_U_std(covar, N_std=1) -> np.ndarray:
    """
    for scipy.stats._mutlivariate, simplified
    """
    s, u = eigh(covar, lower=True)
    s_pinv = 1 / s
    U = np.multiply(u, np.sqrt(np.abs(s_pinv)))
    if N_std != 1:
        U = U / N_std
    return U


def find_mahalanobis(covar, X) -> np.ndarray:
    # https://github.com/scipy/scipy/blob/v1.8.0/scipy/stats/_multivariate.py
    # Use Modified Scipy to find Mahalanobis distance Fast
    psd_U = find_psd_U_std(covar, N_std=1)
    maha = np.sqrt(np.sum(np.square(np.dot(X, psd_U)), axis=-1))
    return maha


def maha_dis_to_groups(X, group_mean, group_covar) -> np.ndarray:
    n_points = np.shape(X)[0]
    n_groups = group_mean.shape[0]
    d = np.zeros((n_points, n_groups))
    for i in range(n_groups):
        mean, covar = group_mean[i, :], group_covar[i, :]
        d[:, i] = find_mahalanobis(covar, X - mean[None, :])
    return d


def add_maha_members_labels(X: np.ndarray, group_mean: np.ndarray, group_covar: np.ndarray, max_dis=2.13) -> np.ndarray:
    """
    Returns group labels of the stars.
    Stars below the specified distance cut are labled.
    Stars above are given the fluff label -1
    """
    dis = maha_dis_to_groups(X, group_mean, group_covar)
    labels = np.argmin(dis, axis=1)
    N = dis.shape[0]
    closest_dis = dis[np.arange(N), labels]
    labels[closest_dis > max_dis] = -1
    return labels


def find_Nstd_from_percent(percent, dof) -> float:
    from scipy.stats import chi2

    Nstd = float(np.sqrt(chi2.ppf(percent, dof)))
    return Nstd
