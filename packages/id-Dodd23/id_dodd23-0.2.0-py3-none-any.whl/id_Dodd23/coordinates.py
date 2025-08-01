from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.coordinates import Galactocentric
from astropy.table import Table, QTable
import numpy as np

u_kms = u.km / u.s
vlsr = 232.8 * u_kms
U, V, W = 11.1 * u_kms, 12.24 * u_kms, 7.25 * u_kms
v_sun = np.asarray([U.value, V.value + vlsr.value, W.value]) * u_kms


def add_units(data: dict | Table | QTable) -> dict | Table | QTable:
    data["ra"] = data["ra"] if isinstance(data["ra"], u.Quantity) else data["ra"] * u.degree
    data["dec"] = data["dec"] if isinstance(data["dec"], u.Quantity) else data["dec"] * u.degree
    data["distance"] = data["distance"] if isinstance(data["distance"], u.Quantity) else data["distance"] * u.kpc
    data["pmra"] = data["pmra"] if isinstance(data["pmra"], u.Quantity) else data["pmra"] * (u.mas / u.yr)
    data["pmdec"] = data["pmdec"] if isinstance(data["pmdec"], u.Quantity) else data["pmdec"] * (u.mas / u.yr)
    data["radial_velocity"] = (
        data["radial_velocity"]
        if isinstance(data["radial_velocity"], u.Quantity)
        else data["radial_velocity"] * (u.km / u.s)
    )
    return data


def coord_transform_icrs_Galacto(data: dict) -> np.ndarray:
    data = add_units(data)
    v_sun = [11.1, 232.8 + 12.24, 7.25] * (u.km / u.s)  # [vx, vy, vz]
    gc_frame = Galactocentric(galcen_distance=8.20 * u.kpc, galcen_v_sun=v_sun, z_sun=0 * u.pc)

    coords = SkyCoord(
        ra=data["ra"],
        dec=data["dec"],
        pm_ra_cosdec=data["pmra"],
        pm_dec=data["pmdec"],
        radial_velocity=data["radial_velocity"],
        distance=data["distance"],
        frame="icrs",
    ).transform_to(gc_frame)
    n_points = len(data["distance"])
    xyz = np.empty((n_points, 6))
    xyz[:, :3] = np.asarray(coords.cartesian.xyz.to(u.kpc)).T
    xyz[:, 3:] = np.asarray(coords.velocity.d_xyz.to(u.km / u.s)).T
    return xyz
