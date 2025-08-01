from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
import numpy as np


def draw_ellipse(position, covariance, ax=None, c="r", alpha=0.3, nsig=2.13):
    """Draw an ellipse with a given position and covariance"""
    ax = ax or plt.gca()

    # Convert covariance to principal axes
    if covariance.shape == (2, 2):
        U, s, Vt = np.linalg.svd(covariance)
        angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        angle = 0
        width, height = 2 * np.sqrt(covariance)

    # Draw the Ellipse
    ax.add_patch(
        Ellipse(position, nsig * width, nsig * height, angle=angle, color="none", ec=c, linewidth=4, alpha=alpha)
    )
    ax.scatter(*position, c=c, marker="+", s=100)

    return


g_colours = {
    "13": np.array([[0.0, 1.0, 0.0]]),
    "8": np.array([[1.0, 0.0, 1.0]]),
    "ED-5": np.array([[0.0, 0.5, 1.0]]),
    "Gaia Enceladus": np.array([[1.0, 0.5, 0.0]]),
    "Hot Thick Disk": np.array([[0.5, 0.75, 0.5]]),
    "L-RL3": np.array([[0.32552069, 0.01834657, 0.63061281]]),
    "Sequoia": np.array([[0.86452207, 0.00352848, 0.14999182]]),
    "Thamnos 1+2": np.array([[0.14135315, 0.99754929, 0.92938808]]),
    "Other": "light_grey",
    "Disc": "red",
}
label_dic = {}
for xkey in ["x", "y", "z", "R", "r"]:
    label_dic[xkey] = rf"${xkey}$, kpc"
    label_dic[f"v{xkey}"] = rf"$v_{{{xkey}}}$, km/s"
label_dic["dist"] = r"Distance, kpc"
label_dic["vT"] = r"$v_{T}$, km/s"
label_dic["vP"] = r"$\sqrt{\left(v_{R}^{2}+v_{Z}^{2}\right)}$, km/s"
label_dic["v_toomre"] = r"$v_{\mathrm{Toomre}}$, km/s"


label_dic["En"] = r"En, ${{\mathrm{km}}^2/\mathrm{s}}^2$"
label_dic["Lz"] = r"$L_{z}$, kpc km/s"
label_dic["Lp"] = r"$L_{\perp}$, kpc km/s"

Lzmax = 3e3
lims = {"Lz": [-Lzmax, Lzmax], "Lp": [0, 3e3], "Dist": [0, 13], "En": [-1.7e5, -0.4e5], "v_toomre": [0, 500]}
