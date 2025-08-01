from .Potential_H99 import H99_potential
import numpy as np
from .coordinates import vlsr


def dynamics_calc_H99(xyz: np.ndarray) -> np.ndarray:
    """
    In: [N,6] np array of [x,y,z,vx,vy,vz]
    Out: [N,3] np array of [E,Lz,Lperp]
    """
    pos, vel = xyz[:, :3], xyz[:, 3:]
    K = 0.5 * np.sum(vel**2, axis=1)
    U = H99_potential(pos)
    En = U + K
    Lvec = np.cross(vel, pos)
    Lz = Lvec[:, 2]
    Lperp = np.sqrt((Lvec[:, :2] ** 2).sum(axis=-1))
    vec_ELzLp = np.column_stack((En, Lz, Lperp))
    return vec_ELzLp


def calc_vtoomre(xyz: np.ndarray) -> np.ndarray:
    vT, vP = calc_vT_vP(xyz)
    vToomre_sq = (vP**2) + ((vT - vlsr.value) ** 2)
    return np.sqrt(vToomre_sq)


def calc_vT_vP(xyz: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    R = np.linalg.norm(xyz[:, :2], axis=-1)
    vT = -((xyz[:, 0] * xyz[:, 4]) - (xyz[:, 1] * xyz[:, 3])) / R
    v_sq = np.sum(xyz[:, 3:] ** 2, axis=-1)
    vP = np.sqrt(v_sq - (vT**2))
    return vT, vP
