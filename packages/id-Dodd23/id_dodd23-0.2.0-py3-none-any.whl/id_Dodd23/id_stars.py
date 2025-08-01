from .dynamics import dynamics_calc_H99, calc_vtoomre
from .mahalanobis_funcs import add_maha_members_labels
from .load_data import group_mean, group_covar, named_Groups
import numpy as np


def groups_from_xyz(xyz: np.ndarray, max_maha_dis=2.13) -> np.ndarray:
    """Galactocentric xyz"""

    vec_ELzLp = dynamics_calc_H99(xyz)
    v_toomre = calc_vtoomre(xyz)
    groups = groups_from_dynamics(vec_ELzLp, v_toomre, max_maha_dis)
    return groups


def groups_from_dynamics(ELz_Vec: np.ndarray, v_toomre: np.ndarray, max_maha_dis=2.13) -> np.ndarray:
    """
    Returns group labels of the stars.
    Stars below the specified distance cut are labled.
    Stars above are given the fluff label -1
    """
    labels = add_maha_members_labels(ELz_Vec, group_mean, group_covar, max_dis=max_maha_dis)
    groups = named_Groups[labels]
    groups[labels == -1] = "Other"
    disc_filt = v_toomre < 210
    groups[disc_filt] = "Disc"
    return groups
