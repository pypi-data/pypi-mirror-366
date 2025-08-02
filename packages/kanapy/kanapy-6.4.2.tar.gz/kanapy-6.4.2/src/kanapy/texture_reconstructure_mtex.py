import numpy as np
from scipy.special import legendre, beta
from scipy.optimize import fminbound
from scipy.integrate import quad
from scipy.spatial import cKDTree
from orix.quaternion import Orientation
from abc import ABC
import matplotlib.pyplot as plt
import kanapy as knpy


class Kernel(ABC):
    def __init__(self, A=None):
        self.A = np.array(A).flatten() if A is not None else np.array([])

    @property
    def bandwidth(self):
        return len(self.A) - 1

    @bandwidth.setter
    def bandwidth(self, L):
        self.A = self.A[:min(L + 1, len(self.A))]

    def __str__(self):
        return f"custom, halfwidth {np.degrees(self.halfwidth()):.2f}°"

    def __eq__(self, other):
        L = min(self.bandwidth, other.bandwidth)
        return np.linalg.norm(self.A[:L + 1] - other.A[:L + 1]) / np.linalg.norm(self.A) < 1e-6

    def __mul__(self, other):
        L = min(self.bandwidth, other.bandwidth)
        l = np.arange(L + 1)
        return Kernel(self.A[:L + 1] * other.A[:L + 1] / (2 * l + 1))

    def __pow__(self, p):
        l = np.arange(self.bandwidth + 1)
        return Kernel(((self.A / (2 * l + 1)) ** p) * (2 * l + 1))

    def norm(self):
        return np.linalg.norm(self.A ** 2)

    def cutA(self, fft_accuracy=1e-2):
        epsilon = fft_accuracy / 150
        A_mod = self.A / (np.arange(1, len(self.A) + 1) ** 2)
        idx = np.where(A_mod[1:] <= max(min([np.min(A_mod[1:]), 10 * epsilon]), epsilon))[0]
        if idx.size > 0:
            self.A = self.A[:idx[0] + 2]

    def halfwidth(self):
        def error_fn(omega):
            return (self.K(1) - 2 * self.K(np.cos(omega / 2))) ** 2

        return fminbound(error_fn, 0, 3 * np.pi / 4)

    def K(self, co2):
        co2 = np.clip(co2, -1, 1)
        omega = 2 * np.arccos(co2)
        return self._clenshawU(self.A, omega)

    def K_orientations(self, orientations_ref, orientations):
        misangles = orientations.angle_with(orientations_ref)
        co2 = np.cos(misangles / 2)
        return self.K(co2)

    def RK(self, d):
        d = np.clip(d, -1, 1)
        return self._clenshawL(self.A, d)

    def RRK(self, dh, dr):
        dh = np.clip(dh, -1, 1)
        dr = np.clip(dr, -1, 1)
        L = self.bandwidth
        result = np.zeros((len(dh), len(dr)))

        if len(dh) < len(dr):
            for i, dh_i in enumerate(dh):
                Plh = [legendre(l)(dh_i) for l in range(L + 1)]
                result[i, :] = self._clenshawL(np.array(Plh) * self.A, dr)
        else:
            for j, dr_j in enumerate(dr):
                Plr = [legendre(l)(dr_j) for l in range(L + 1)]
                result[:, j] = self._clenshawL(np.array(Plr) * self.A, dh)
        result[result < 0] = 0
        return result

    def _clenshawU(self, A, omega):
        omega = omega / 2
        res = np.ones_like(omega) * A[0]
        for l in range(1, len(A)):
            term = np.cos(2 * l * omega) + np.cos(omega) * np.cos((2 * l - 1) * omega) + \
                   (np.cos(omega) ** 2)
            res += A[l] * term
        return res

    def _clenshawL(self, A, x):
        b_next, b_curr = 0.0, 0.0
        x2 = 2 * x
        for a in reversed(A[1:]):
            b_next, b_curr = b_curr, a + x2 * b_curr - b_next
        return A[0] + x * b_curr - b_next

    def calc_fourier(self, L, max_angle=np.pi, fft_accuracy=1e-2):
        A = []
        small = 0
        for l in range(L + 1):
            def integrand(omega):
                return self.K(np.cos(omega / 2)) * np.sin((2 * l + 1) * omega / 2) * np.sin(omega / 2)

            coeff, _ = quad(integrand, 0, max_angle, limit=2000)
            coeff *= 2 / np.pi
            A.append(coeff)
            if abs(coeff) < fft_accuracy:
                small += 1
            else:
                small = 0
            if small == 10:
                break
        return np.array(A)

    def plot_K(self, n_points=200):
        omega = np.linspace(0, np.pi, n_points)
        co2 = np.cos(omega / 2)
        values = self.K(co2)
        plt.figure()
        plt.plot(np.degrees(omega), values)
        plt.xlabel("Misorientation angle (degrees)")
        plt.ylabel("K(cos(omega/2))")
        plt.title("Kernel Function")
        plt.grid(True)
        plt.show()


class DeLaValleePoussinKernel(Kernel):
    def __init__(self, kappa=None, halfwidth=None, bandwidth=None):
        if halfwidth is not None:
            kappa = 0.5 * np.log(0.5) / np.log(np.cos(halfwidth / 2))
        elif kappa is None:
            kappa = 90

        self.kappa = kappa
        L = bandwidth if bandwidth is not None else round(kappa)
        C = beta(1.5, 0.5) / beta(1.5, kappa + 0.5)
        self.C = C

        A = np.ones(L + 1)
        A[1] = kappa / (kappa + 2)

        for l in range(1, L - 1):
            A[l + 1] = ((kappa - l + 1) * A[l - 1] - (2 * l + 1) * A[l]) / (kappa + l + 2)

        for l in range(0, L + 1):
            A[l] *= (2 * l + 1)

        super().__init__(A)
        self.cutA()

    def K(self, co2):
        co2 = np.clip(co2, -1, 1)
        return self.C * co2 ** (2 * self.kappa)

    def DK(self, co2):
        return -self.C * self.kappa * np.sqrt(1 - co2 ** 2) * co2 ** (2 * self.kappa - 1)

    def RK(self, t):
        return (1 + self.kappa) * ((1 + t) / 2) ** self.kappa

    def DRK(self, t):
        return self.kappa * (1 + self.kappa) * ((1 + t) / 2) ** (self.kappa - 1) / 2

    def halfwidth(self):
        return 2 * np.arccos(0.5 ** (1 / (2 * self.kappa)))


def mtex_to_orix(euler_angles_deg, crystal_symmetry=None):
    """
    Convert a list or array of MTEX-style Euler angles (in degrees) to orix Orientation objects.
    Expected input shape: (N, 3) with angles in degrees.
    """
    euler_rad = np.radians(euler_angles_deg)
    return Orientation.from_euler(euler_rad[:, 0], euler_rad[:, 1], euler_rad[:, 2], degrees=False)


# Helper stubs
def xnum2str(x):
    return f"{x:.3f}"


def calc_kernel_odf(orientations, halfwidth=np.radians(10), weights=None, kernel=None, exact=False):
    """
    Estimate an Orientation Distribution Function (ODF) from individual orientations
    using kernel density estimation.

    Parameters
    ----------
    orientations : orix.quaternion.Orientation
        Input orientation set.
    halfwidth : float, optional
        Halfwidth of the kernel in radians (default: 10 degrees).
    weights : array-like, optional
        Weights for each orientation. If None, weights are uniform.
    kernel : Kernel instance, optional
        Kernel function to use. If None, DeLaValleePoussinKernel is used.
    exact : bool, optional
        If False and orientation count > 1000, approximate using grid.

    Returns
    -------
    odf : dict
        A dictionary with 'orientations', 'weights', 'kernel', and 'halfwidth'.
    """
    if orientations.size == 0:
        return {'orientations': [], 'weights': [], 'kernel': kernel, 'halfwidth': halfwidth}

    if weights is None:
        weights = np.ones(len(orientations))

    # Remove NaNs if present
    valid = ~np.isnan(orientations.as_quat().view(np.ndarray)).any(axis=1)
    orientations = orientations[valid]
    weights = weights[valid]
    weights = weights / np.sum(weights)

    # Set up kernel
    if kernel is None:
        kernel = DeLaValleePoussinKernel(halfwidth=halfwidth)
    hw = kernel.halfwidth()

    # Gridify if too many orientations and not exact
    if len(orientations) > 1000 and not exact:
        # Placeholder: replace with proper gridify function if needed
        # Currently using simple thinning and weighting
        step = max(1, len(orientations) // 1000)
        orientations = orientations[::step]
        weights = weights[::step]
        weights = weights / np.sum(weights)

    return {
        'orientations': orientations,
        'weights': weights,
        'kernel': kernel,
        'halfwidth': hw
    }


def equispaced_so3_grid(cs, n_points=10000, max_angle=np.pi, resolution=None, center=None):
    """
    Define an approximately equispaced orientation grid on SO(3).

    Parameters
    ----------
    n_points : int, optional
        Approximate number of points to generate.
    max_angle : float, optional
        Maximum misorientation angle from center in radians.
    resolution : float, optional
        Resolution of the grid (overrides n_points if given).
    center : orix.quaternion.Orientation, optional
        Orientation to center the grid around (defaults to identity).

    Returns
    -------
    orientations : orix.quaternion.Orientation
        Generated orientation grid.
    """

    if resolution is None:
        resolution = 2 / (n_points / (np.pi * np.pi)) ** (1 / 3)

    n_beta = int(np.ceil(np.pi / resolution))
    beta = np.linspace(0, np.pi, n_beta)

    n_alpha = int(np.ceil(2 * np.pi / resolution))
    alpha = np.linspace(0, 2 * np.pi, n_alpha)

    n_gamma = int(np.ceil(2 * np.pi / resolution))
    gamma = np.linspace(0, 2 * np.pi, n_gamma)

    alpha_grid, beta_grid, gamma_grid = np.meshgrid(alpha, beta, gamma, indexing='ij')

    alpha_flat = alpha_grid.ravel()
    beta_flat = beta_grid.ravel()
    gamma_flat = gamma_grid.ravel()
    euler = np.array([alpha_flat, beta_flat, gamma_flat]).T

    orientations = Orientation.from_euler(euler, symmetry=cs, degrees=False)

    if center is not None:
        mis_angle = orientations.angle_with(center)
        orientations = orientations[mis_angle <= max_angle]

    return orientations


def find_orientations_fast(ori1: Orientation, ori2: Orientation, tol: float = 1e-3) -> np.ndarray:
    """
    Find closest matches in ori1 for each orientation in ori2 using KDTree.

    Parameters
    ----------
    ori1 : Orientation
        Orientation database (e.g., EBSD orientations).
    ori2 : Orientation
        Orientations to match (e.g., grain mean orientations).
    tol : float
        Angular tolerance in radians.

    Returns
    -------
    matches : np.ndarray
        Array of indices in ori1 matching each entry in ori2; -1 if no match found.
    """
    # Get quaternions
    q1 = ori1.data
    q2 = ori2.data

    # KDTree in 4D quaternion space
    tree = cKDTree(q1)
    dists, indices = tree.query(q2, distance_upper_bound=2 * np.sin(tol / 2))

    # Check actual angle using orix.angle_with
    matches = []
    for i, (idx, dist) in enumerate(zip(indices, dists)):
        if idx < ori1.size:
            mis = ori2[i].angle_with(ori1[idx])
            if mis < tol:
                matches.append(idx)
            else:
                matches.append(-1)
        else:
            matches.append(-1)

    return np.array(matches)


def textureReconstruction(ns, *args):
    """
    This function sysytematically reconstructs an ODF by a given number of
    orientations (refer .....)
    also the misorientation distribution is  reproduced


    Syntax:
    [ori,odf,e]=texture_reconstruction_algo(n,'ebsdMatfile',ebsdfile)
    [ori,odf,e]=texture_reconstruction_algo(n,'ebsd',ebsd)
    [ori,odf,e]=texture_reconstruction_algo(n,'ebsdMatfile',ebsdfile,
            'grainsMatfile',grainsfile)
    [ori,odf,e]=texture_reconstruction_algo(n,'ebsd',ebsd,'grains',...
            'grains')
    [ori,odf,e]=texture_reconstruction_algo(n,'orientations',ori)
    [ori,odf,e]=texture_reconstruction_algo(n,'orientations',ori,...
            'kernel',psi)
    [ori,odf,e]=texture_reconstruction_algo(n,'orientations',ori,...
            'kernelShape','kappa')

    Inputs:

    1) n: number of reduced orientations/grains in RVE
    2) Either path+filename of ebsd data saved as *.mat file (it should
      contain only one phase/mineral) or ebsd(single phase)/orientations
    3) Either path+filename of the estiamted grains from above
      EBSD saved as *.mat file (it should contain only one phase/mineral)
      or kernel(only deLaValeePoussinKernel)/kernelshape, if nothing
      mentioned then default value kappa = 5 (degree) is assumed.

    Output: reduced orientation set, ODF and L1 error

   input fields and checks
    Parameters
    ----------
    ns
    args

    Returns
    -------

    """
    if 'ebsdMatFile' in args:
        raise ValueError('Option "ebsdMatFile" is not yet supported.')
        # ind = args.index('ebsdMatFile') + 1
        # ebsd = loadmat(args[ind])
        # ebsd_var = list(ebsd.keys())[0]
        # ebsd = ebsd[ebsd_var]
        # assert len(np.unique(ebsd.phaseId)) == 1, 'EBSD has multiple phases'
        # ori = ebsd.orientations
    elif 'ebsd' in args:
        ind = args.index('ebsd') + 1
        ebsd = args[ind]
        assert len(np.unique(ebsd.phaseId)) == 1, 'EBSD has multiple phases'
        ori = ebsd.orientations
    elif 'orientation' in args:
        ind = args.index('orientation') + 1
        ori = args[ind]

    if len(args) > 2:
        if 'grainsMatFile' in args:
            raise ValueError('Option "grainsMatFile" is not yet supported.')
            # ind = args.index('grainsMatFile') + 1
            # grains = loadmat(args[ind])
            # grains_var = list(grains.keys())[0]
            # grains = grains[grains_var]
            # assert len(np.unique(grains.phaseId)) == 1, 'Grains has multiple phases'
            # print('Optimum kernel estimated from mean orientations of grains')
            # psi = calcKernel(grains.meanOrientation)
        elif 'grains' in args:
            raise ValueError('Option "grains" is not yet supported.')
            #ind = args.index('grains') + 1
            #grains = args[ind]
            #assert len(np.unique(grains.phaseId)) == 1, 'Grains has multiple phases'
            #print('Optimum kernel estimated from mean orientations of grains')
            #psi = calcKernel(grains.meanOrientation)
        elif 'kernel' in args:
            ind = args.index('kernel') + 1
            assert isinstance(args[ind], DeLaValleePoussinKernel), 'Invalid kernel use deLaValeePoussinKernel'
            psi = args[ind]
        elif 'kernelShape' in args:
            ind = args.index('kernelShape') + 1
            psi = DeLaValleePoussinKernel(halfwidth=np.radians[ind])
    else:
        psi = DeLaValleePoussinKernel(halfwidth=np.radians(5))
        print(f'Default initial kernel shape factor: {5} degree')

    odf = calc_kernel_odf(ori, kernel=psi)

    if ori.shape[1] > ori.shape[0]:
        ori = np.reshape(ori, (len(ori), 1))

    ll = 10
    hl = 55
    step = 1
    ero = 100
    e_mod = []
    lim = 10
    hh = []
    kappa = psi.halfwidth() * 180 / np.pi  # initial kernel shape

    for hw in np.arange(ll, hl + step, step):
        S3G = equispaced_so3_grid(ori.CS, resolution=np.radians(0.5*hw))  # ori.SS not considered (structure symmetry)

        weights = np.ones(len(ori))
        M = find_orientations_fast(ori, S3G, tol=np.radians(0.5))
        # coo_array((weights, (np.arange(len(ori)), find(S3G, ori))), shape=(len(ori), len(S3G)))

        weights = np.array(M.sum(axis=0)).flatten()
        weights = weights / np.sum(weights)

        S3G = subGrid(S3G, weights != 0)
        weights = weights[weights != 0]

        lval = 0
        hval = float(ns)
        ifc = 1.0
        ihval = np.sum(np.round(hval * weights))

        while (hval - lval > hval * 1e-15 or ihval < ns) and ihval != ns:
            if ihval < ns:
                hvalOld = hval
                hval = hval + ifc * (hval - lval) / 2.0
                lval = hvalOld
                ifc = ifc * 2.0
                ihval = np.sum(np.round(hval * weights))
            else:
                hval = (lval + hval) / 2.0
                ifc = 1.0
                ihval = np.sum(np.round(hval * weights))

        screen = np.round(weights * hval)
        diff = np.sum(screen) - ns

        weights_loc = np.argsort(weights)
        co = 1

        while diff > 0:
            if screen[weights_loc[co]] > 0:
                screen[weights_loc[co]] = screen[weights_loc[co]] - 1
                diff = np.sum(screen) - ns
            co = co + 1

        fval = screen[screen > 0]

        # mean orientation estimation and kernel optimization

        xt, yt = M.nonzero()
        ytun = np.unique(yt)
        ytfreq = np.histogram(yt, bins=ytun)[0]
        oriseq = np.split(ori[xt], np.cumsum(ytfreq)[:-1])

        oriseq = [ori for ori, screen in zip(oriseq, screen) if screen > 0]

        ori_f = S3G[screen == 1]

        oriseq_p = [ori for ori, fval in zip(oriseq, fval) if fval > 1]

        ind = [fval for fval in fval if fval > 1]
        pendList = [splitMean(ori, int(fval)) for ori, fval in zip(oriseq_p, ind)]

        ori_f = np.concatenate([ori_f] + pendList)

        odfred, h = odfEst(ori_f, np.ones(ns), kappa, odf)
        hh.append(h)
        er = calcError(odf, odfred)

        if er < ero:
            orired_f = ori_f
            odfred_f = odfred
            ohw = h
            ero = er

        e_mod.append(er)

        if len(e_mod) - np.argmin(e_mod) > lim:
            break

    orired_f = project2FundamentalRegion(orired_f)

    return orired_f, odfred_f, ero


# Unit test example
if __name__ == "__main__":
    degree = np.pi / 180  # Assuming MATLAB's 'degree' was in radians
    mtexdegchar = "°"  # Placeholder
    # Generate orientations
    ori_ref = Orientation.from_euler([0., 0., 0.])
    N = 100

    vf_min = 0.03  # minimum volume fraction of phases to be considered
    max_angle = 5.0  # maximum misorientation angle within one grain in degrees
    min_size = 10.0  # minim grain size in pixels
    connectivity = 8  # take into account diagonal neighbors
    fname = '../../examples/EBSD_analysis/ebsd_316L_500x500.ang'  # name of ang file to be imported

    # read EBSD map and evaluate statistics of microstructural features
    ebsd = knpy.EBSDmap(fname, vf_min=vf_min, gs_min=min_size, show_plot=False,
                        connectivity=connectivity, show_grains=False, show_hist=False)
    ms_data = ebsd.ms_data[0]

    angles_deg = np.linspace(0, 90, 100)
    angles_rad = np.zeros((N, 3))
    angles_rad[:, 0] = np.radians(angles_deg)
    orientations = Orientation.from_euler(angles_rad)

    # Kernel instance and evaluation
    kernel = DeLaValleePoussinKernel(halfwidth=np.radians(15))
    values = kernel.K_orientations(ori_ref, orientations)

    # Plot
    plt.plot(angles_deg, values)
    plt.xlabel("Misorientation Angle (degrees)")
    plt.ylabel("Kernel Value")
    plt.title("De la Vallée Poussin Kernel Evaluation")
    plt.grid(True)
    plt.show()

    grid = equispaced_so3_grid(cs=ms_data['cs'], n_points=5000, max_angle=np.radians(20))
    print(f"Generated grid with {grid.size} orientations")

    # Simulate 10,000 orientations
    # ori1 = Orientation.random(shape=10000)

    matched_indices = find_orientations_fast(ms_data['ori'], grid, tol=np.radians(3))
    print("Match indices:", matched_indices)

