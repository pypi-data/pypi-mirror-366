# -*- coding: utf-8 -*-
"""
Subroutines for analysis of statistical descriptors of RVEs:
 * original particles (or their inner polyhedra)
 * voxel structure
 * polyhedral grain structure

@author: Alexander Hartmaier
ICAMS, Ruhr University Bochum, Germany
March 2024
"""
import logging
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import ConvexHull
from kanapy.plotting import plot_stats_dict


def arr2mat(mc):
    """
    Converts a numpy array into a symmetric matrix.

    Parameters
    ----------
    mc

    Returns
    -------

    """
    return np.array([[mc[0], mc[5], mc[4]],
                     [mc[5], mc[1], mc[3]],
                     [mc[4], mc[3], mc[2]]])


def con_fun(mc):
    """Constraint: matrix must be positive definite, for symmetric matrix all eigenvalues
    must be positive. Constraint will penalize negative eigenvalues.
    """
    eigval, eigvec = np.linalg.eig(arr2mat(mc))
    return np.min(eigval) * 1000


def find_rot_axis(len_a, len_b, len_c):
    """
    Find the rotation axis of an ellipsoid defined be three semi-axes and return the
    equivalent values for the semi-axes along and transversal to the rotation axis.

    Parameters
    ----------
    len_a
    len_b
    len_c

    Returns
    -------
    rot_ax
    trans_ax

    """
    ar_list = [np.abs(len_a / len_b - 1.0), np.abs(len_b / len_a - 1.0),
               np.abs(len_b / len_c - 1.0), np.abs(len_c / len_b - 1.0),
               np.abs(len_c / len_a - 1.0), np.abs(len_a / len_c - 1.0)]
    minval = np.min(ar_list)
    if minval > 0.15:
        # no clear rotational symmetry, choose the longest axis as rotation axis
        irot = np.argmax([len_a, len_b, len_c])
    else:
        ind = np.argmin(ar_list)  # identify two axes with aspect ratio closest to 1
        if ind in [0, 1]:
            irot = 2
        elif ind in [2, 3]:
            irot = 0
        else:
            irot = 1
    return irot


def get_ln_param(data):
    # sig, loc, sc = lognorm.fit(sdict['eqd'])
    ind = np.nonzero(data > 1.e-5)[0]
    log_data = np.log(data[ind])
    scale = np.exp(np.median(log_data))
    sig = np.std(log_data)
    return sig, scale


def pts_in_ellips(Mcomp, pts):
    """ Check how well points fulfill equation of ellipsoid
    (pts-ctr)^T M (pts-ctr) = 1

    Parameters
    ----------
    Mcomp
    pts

    Returns
    -------

    """
    if Mcomp.shape != (6,):
        raise ValueError(f'Matrix components must be given as array with shape (6,), not {Mcomp.shape}')
    ctr = np.average(pts, axis=0)
    pcent = pts - ctr[np.newaxis, :]
    score = 0.
    for x in pcent:
        mp = np.matmul(arr2mat(Mcomp), x)
        score += np.abs(np.dot(x, mp) - 1.0)
    return score / len(pts)


def get_diameter(pts):
    """
    Get estimate of largest diameter of a set of points.
    Parameters
    ----------
    pts : (N, dim) ndarray
        Point set in dim dimensions

    Returns
    -------
    diameter : (dim)-ndarray

    """
    ind0 = np.argmin(pts, axis=0)  # index of point with lowest coordinate for each Cartesian axis
    ind1 = np.argmax(pts, axis=0)  # index of point with highest coordinate for each Cartesian axis
    v_min = np.array([pts[i, j] for j, i in enumerate(ind0)])  # min. value for each Cartesian axis
    v_max = np.array([pts[i, j] for j, i in enumerate(ind1)])  # max. value for each Cartesian axis
    ind_d = np.argmax(v_max - v_min)  # Cartesian axis along which largest distance occurs
    return pts[ind1[ind_d], :] - pts[ind0[ind_d], :]

def project_pts(pts, ctr, axis):
    """
    Project points (pts) to plane defined via center (ctr) and normal vector (axis).

    Parameters
    ----------
    pts : (N, dim) ndarray
        Point set in dim dimensions
    ctr : (dim)-ndarray
        Center point of the projection plane
    axis : (dim)-ndarray
        Unit vector for plane normal

    Returns
    -------
    ppt : (N, dim) ndarray
        Points projected to plane with normal axis
    """
    dvec = pts - ctr[None, :]  # distance vector b/w points and center point
    pdist = np.array([np.dot(axis, v) for v in dvec])
    ppt = np.zeros(pts.shape)
    for i, p in enumerate(dvec):
        ppt[i, :] = p - pdist[i] * axis
    return ppt


def bbox(pts, return_vector=False, two_dim=False):
    # Approximate smallest rectangular cuboid around points of grains
    # to analyse prolate (aspect ratio > 1) and oblate (a.r. < 1) particles correctly
    dia = get_diameter(pts)  # approx. of largest diameter of grain
    ctr = np.mean(pts, axis=0)  # approx. center of grain
    len_a = np.linalg.norm(dia)  # length of largest side
    if len_a < 1.e-3:
        logging.warning(f'Very small grain at {ctr} with max. diameter = {len_a}')
        if len_a < 1.e-8:
            raise ValueError(f'Grain of almost zero dimension at {ctr} with max. diameter = {len_a}')
    ax_a = dia / len_a  # unit vector along longest side
    ppt = project_pts(pts, ctr, ax_a)  # project points onto central plane normal to diameter
    trans1 = get_diameter(ppt)  # largest side transversal to long axis
    len_b = np.linalg.norm(trans1)  # length of second-largest side
    ax_b = trans1 / len_b  # unit vector of second axis (normal to diameter)
    if two_dim:
        if return_vector:
            return 0.5 * len_a, 0.5 * len_b, ax_a, ax_b
        else:
            return 0.5 * len_a, 0.5 * len_b
    ax_c = np.cross(ax_a, ax_b)  # calculate third orthogonal axes of rectangular cuboid
    lpt = project_pts(ppt, np.zeros(3), ax_b)  # project points on third axis
    pdist = np.array([np.dot(ax_c, v) for v in lpt])  # calculate distance of points on third axis
    len_c = np.max(pdist) - np.min(pdist)  # get length of shortest side
    if return_vector:
        return 0.5*len_a, 0.5*len_b, 0.5*len_c, ax_a, ax_b, ax_c
    else:
        return 0.5*len_a, 0.5*len_b, 0.5*len_c


def calc_stats_dict(a, b, c, eqd):
    arr_a = np.sort(a)
    arr_b = np.sort(b)
    arr_c = np.sort(c)
    arr_eqd = np.sort(eqd)
    a_sig, a_sc = get_ln_param(arr_a)
    b_sig, b_sc = get_ln_param(arr_b)
    c_sig, c_sc = get_ln_param(arr_c)
    e_sig, e_sc = get_ln_param(arr_eqd)
    irot = find_rot_axis(a_sc, b_sc, c_sc)
    if irot == 0:
        arr_ar = 2.0 * np.divide(arr_a, (arr_b + arr_c))
        ar_sc = 2.0 * a_sc / (b_sc + c_sc)
    elif irot == 1:
        arr_ar = 2.0 * np.divide(arr_b, (arr_a + arr_c))
        ar_sc = 2.0 * b_sc / (a_sc + c_sc)
    elif irot == 2:
        arr_ar = 2.0 * np.divide(arr_c, (arr_b + arr_a))
        ar_sc = 2.0 * c_sc / (b_sc + a_sc)
    else:
        logging.error(f'Wrong index of rotation axis: irot = {irot}')
        arr_ar = -1.
        ar_sc = -1.
    # print(f'  ***   AR Median: {np.median(arr_ar)}, {ar_sc}', irot)
    sd = {
        'a': arr_a,
        'b': arr_b,
        'c': arr_c,
        'eqd': arr_eqd,
        'a_sig': a_sig,
        'b_sig': b_sig,
        'c_sig': c_sig,
        'eqd_sig': e_sig,
        'a_scale': a_sc,
        'b_scale': b_sc,
        'c_scale': c_sc,
        'eqd_scale': e_sc,
        'ind_rot': irot,
        'ar': np.sort(arr_ar),
        'ar_scale': ar_sc,
        'ar_sig': np.std(arr_ar)
    }
    return sd


def get_stats_part(part, iphase=None, ax_max=None,
                   minval=1.e-5, show_plot=True,
                   verbose=False, save_files=False):
    """ Extract statistics about the microstructure from particles. If inner structure is contained
    by fitting a 3D ellipsoid to each structure.

    Parameters
    ----------
    part
    minval
    show_plot
    verbose
    ax_max

    Returns
    -------

    """
    if ax_max is not None:
        minval = max(minval, 1. / ax_max ** 2)
    cons = ({'type': 'ineq', 'fun': con_fun})  # constraints for minimization
    opt = {'maxiter': 200}  # options for minimization
    mc = np.array([1., 1., 1., 0., 0., 0.])  # start value of matrix for minimization
    arr_a = []
    arr_b = []
    arr_c = []
    arr_eqd = []
    for pc in part:
        # decide if phase-specific analysis is performed
        if iphase is not None and iphase != pc.phasenum:
            continue
        if pc.inner is not None:
            pts = pc.inner.points
            rdict = minimize(pts_in_ellips, x0=mc, args=(pts,), method='SLSQP',
                             constraints=cons, options=opt)
            if not rdict['success']:
                if verbose:
                    print(f'Optimization failed for particle {pc.id}')
                    print(rdict['message'])
                continue
            eval, evec = np.linalg.eig(arr2mat(rdict['x']))
            if any(eval <= minval):
                if verbose:
                    print(f'Matrix for particle {pc.id} not positive definite or semi-axes too large. '
                          f'Eigenvalues: {eval}')
                continue
            if verbose:
                print(f'Optimization succeeded for particle {pc.id} after {rdict["nit"]} iterations.')
                print(f'Eigenvalues: {eval}')
                print(f'Eigenvectors: {evec}')
            # Semi-axes of ellipsoid
            ea = 1. / np.sqrt(eval[0])
            eb = 1. / np.sqrt(eval[1])
            ec = 1. / np.sqrt(eval[2])
            eqd = 2.0 * (ea * eb * ec) ** (1.0 / 3.0)
            arr_a.append(ea)
            arr_b.append(eb)
            arr_c.append(ec)
            arr_eqd.append(eqd)
        else:
            eqd = 2.0 * (pc.a * pc.b * pc.c) ** (1.0 / 3.0)
            arr_a.append(pc.a)
            arr_b.append(pc.b)
            arr_c.append(pc.c)
            arr_eqd.append(eqd)

    # calculate statistical parameters
    part_stats_dict = calc_stats_dict(arr_a, arr_b, arr_c, arr_eqd)
    if verbose:
        print('\n--------------------------------------------------')
        print('Statistical microstructure parameters of particles')
        print('--------------------------------------------------')
        print('Median lengths of semi-axes of fitted ellipsoids in micron')
        print(f'a: {part_stats_dict["a_scale"]:.3f}, b: {part_stats_dict["b_scale"]:.3f}, '
              f'c: {part_stats_dict["c_scale"]:.3f}')
        av_std = np.mean([part_stats_dict['a_sig'], part_stats_dict['b_sig'], part_stats_dict['c_sig']])
        print(f'Average standard deviation of semi-axes: {av_std:.4f}')
        print('\nAssuming rotational symmetry in grains')
        print(f'Rotational axis: {part_stats_dict["ind_rot"]}')
        print(f'Median aspect ratio: {part_stats_dict["ar_scale"]:.3f}')
        print('\nGrain size')
        print(f'Median equivalent grain diameter: {part_stats_dict["eqd_scale"]:.3f} micron')
        print(f'Standard deviation of equivalent grain diameter: {part_stats_dict["eqd_sig"]:.4f}')
        print('--------------------------------------------------------')
    if show_plot:
        if part[0].inner is None:
            title = 'Particle statistics'
        else:
            title = 'Statistics of inner particle structures'
        if iphase is not None:
            title += f' (phase {iphase})'
        plot_stats_dict(part_stats_dict, title=title, save_files=save_files)

    return part_stats_dict


def get_stats_vox(mesh, iphase=None, ax_max=None,
                  minval=1.e-5, show_plot=True,
                  verbose=False, save_files=False):
    """
    Get statistics about the microstructure from voxels by analysing nodes at grain boundaries
    and constructing a rectangular bounding box.

    Parameters
    ----------
    mesh
    minval
    show_plot
    verbose
    ax_max

    Returns
    -------

    """
    gfac = 3.0 / (4.0 * np.pi)
    arr_a = []
    arr_b = []
    arr_c = []
    arr_eqd = []
    for igr, vlist in mesh.grain_dict.items():
        # decide if phase-specific analysis is performed
        if iphase is not None and iphase != mesh.grain_phase_dict[igr]:
            continue
        nodes = set()
        for iv in vlist:
            nodes.update(mesh.voxel_dict[iv])
        ind = np.array(list(nodes), dtype=int) - 1
        pts_all = mesh.nodes[ind, :]
        hull = ConvexHull(pts_all)
        eqd = 2.0 * (gfac * hull.volume) ** (1.0 / 3.0)
        pts = hull.points[hull.vertices]  # outer nodes of grain no. igr
        # find bounding box to hull points
        ea, eb, ec = bbox(pts)
        """
        if ax_max is not None:
            minval = max(minval, 1. / ax_max ** 2)
        cons = ({'type': 'ineq', 'fun': con_fun})  # constraints for minimization
        opt = {'maxiter': 200}  # options for minimization
        mc = np.array([1., 1., 1., 0., 0., 0.])  # start value of matrix for minimization
        # find best fitting ellipsoid to points
        rdict = minimize(pts_in_ellips, x0=mc, args=(pts,), method='SLSQP',
                         constraints=cons, options=opt)
        if not rdict['success']:
            if verbose:
                print(f'Optimization failed for grain {igr}')
                print(rdict['message'])
            continue
        eval, evec = np.linalg.eig(arr2mat(rdict['x']))
        if any(eval <= minval):
            if verbose:
                print(f'Matrix for grain {igr} not positive definite or semi-axes too large. '
                      f'Eigenvalues: {eval}')
            continue
        if verbose:
            print(f'Optimization succeeded for grain {igr} after {rdict["nit"]} iterations.')
            print(f'Eigenvalues: {eval}')
            print(f'Eigenvectors: {evec}')
        # Semi-axes of ellipsoid
        ea = 1. / np.sqrt(eval[0])
        eb = 1. / np.sqrt(eval[1])
        ec = 1. / np.sqrt(eval[2])"""

        """# Plot points on hull with fitted ellipsoid -- only for debugging
        import matplotlib.pyplot as plt
        # Points on the outer surface of optimal ellipsoid
        nang = 100
        col = [0.7, 0.7, 0.7, 0.5]
        ctr = np.average(pts, axis=0)
        u = np.linspace(0, 2 * np.pi, nang)
        v = np.linspace(0, np.pi, nang)

        # Cartesian coordinates that correspond to the spherical angles:
        xval = ea * np.outer(np.cos(u), np.sin(v))
        yval = eb * np.outer(np.sin(u), np.sin(v))
        zval = ec * np.outer(np.ones_like(u), np.cos(v))

        # combine the three 2D arrays element wise
        surf_pts = np.stack(
            (xval.ravel(), yval.ravel(), zval.ravel()), axis=1)
        surf_pts = surf_pts.dot(evec.transpose())  # rotate to eigenvector frame
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        x = (surf_pts[:, 0] + ctr[None, 0]).reshape((100, 100))
        y = (surf_pts[:, 1] + ctr[None, 1]).reshape((100, 100))
        z = (surf_pts[:, 2] + ctr[None, 2]).reshape((100, 100))
        ax.plot_surface(x, y, z, rstride=4, cstride=4, color=col, linewidth=0)
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], marker='o')
        plt.show()"""
        arr_a.append(ea)
        arr_b.append(eb)
        arr_c.append(ec)
        arr_eqd.append(eqd)
    # calculate and print statistical parameters
    vox_stats_dict = calc_stats_dict(arr_a, arr_b, arr_c, arr_eqd)
    if verbose:
        print('\n--------------------------------------------------------')
        print('Statistical microstructure parameters in voxel structure')
        print('--------------------------------------------------------')
        print('Median lengths of semi-axes in micron')
        print(f'a: {vox_stats_dict["a_scale"]:.3f}, b: {vox_stats_dict["b_scale"]:.3f}, '
              f'c: {vox_stats_dict["c_scale"]:.3f}')
        av_std = np.mean([vox_stats_dict['a_sig'], vox_stats_dict['b_sig'], vox_stats_dict['c_sig']])
        print(f'Average standard deviation of semi-axes: {av_std:.4f}')
        print('\nAssuming rotational symmetry in grains')
        print(f'Rotational axis: {vox_stats_dict["ind_rot"]}')
        print(f'Median aspect ratio: {vox_stats_dict["ar_scale"]:.3f}')
        print('\nGrain size')
        print(f'Median equivalent grain diameter: {vox_stats_dict["eqd_scale"]:.3f} micron')
        print(f'Standard deviation of equivalent grain diameter: {vox_stats_dict["eqd_sig"]:.4f}')
        print('--------------------------------------------------------')
    if show_plot:
        if iphase is None:
            title = 'Statistics of voxel structure'
        else:
            title = f'Statistics of voxel structure (phase {iphase})'
        plot_stats_dict(vox_stats_dict, title=title, save_files=save_files)

    return vox_stats_dict


def get_stats_poly(grains, iphase=None, ax_max=None,
                   phase_dict=None,
                   minval=1.e-5, show_plot=True,
                   verbose=False, save_files=False):
    """ Extract statistics about the microstructure from polyhedral grains
        by fitting a 3D ellipsoid to each polyhedron.

        Parameters
        ----------
        geom
        minval
        show_plot
        verbose
        ax_max

        Returns
        -------

        """
    if iphase is not None and phase_dict is None:
        logging.error('Error in get_stats_poly: phase number provided, but no phase_dict present.')
    if ax_max is not None:
        minval = max(minval, 1. / ax_max ** 2)
    cons = ({'type': 'ineq', 'fun': con_fun})  # constraints for minimization
    opt = {'maxiter': 200}  # options for minimization
    mc = np.array([1., 1., 1., 0., 0., 0.])  # start value of matrix for minimization
    arr_a = []
    arr_b = []
    arr_c = []
    arr_eqd = []
    for gid, pc in grains.items():
        # decide if phase-specific analysis is performed
        if iphase is not None and iphase != phase_dict[gid]:
            continue
        pts = pc['Points']
        rdict = minimize(pts_in_ellips, x0=mc, args=(pts,), method='SLSQP',
                         constraints=cons, options=opt)
        if not rdict['success']:
            if verbose:
                print(f'Optimization failed for particle {gid}')
                print(rdict['message'])
            continue
        eval, evec = np.linalg.eig(arr2mat(rdict['x']))
        if any(eval <= minval):
            if verbose:
                print(f'Matrix for particle {gid} not positive definite or semi-axes too large. '
                      f'Eigenvalues: {eval}')
            continue
        if verbose:
            print(f'Optimization succeeded for particle {gid} after {rdict["nit"]} iterations.')
            print(f'Eigenvalues: {eval}')
            print(f'Eigenvectors: {evec}')
        # Semi-axes of ellipsoid
        ea = 1. / np.sqrt(eval[0])
        eb = 1. / np.sqrt(eval[1])
        ec = 1. / np.sqrt(eval[2])
        eqd = 2.0 * (ea * eb * ec) ** (1.0 / 3.0)
        arr_a.append(ea)
        arr_b.append(eb)
        arr_c.append(ec)
        arr_eqd.append(eqd)

    # calculate statistical parameters
    poly_stats_dict = calc_stats_dict(arr_a, arr_b, arr_c, arr_eqd)
    if verbose:
        print('\n----------------------------------------------------------')
        print('Statistical microstructure parameters of polyhedral grains')
        print('----------------------------------------------------------')
        print('Median lengths of semi-axes of fitted ellipsoids in micron')
        print(f'a: {poly_stats_dict["a_scale"]:.3f}, b: {poly_stats_dict["b_scale"]:.3f}, '
              f'c: {poly_stats_dict["c_scale"]:.3f}')
        av_std = np.mean([poly_stats_dict['a_sig'], poly_stats_dict['b_sig'], poly_stats_dict['c_sig']])
        print(f'Average standard deviation of semi-axes: {av_std:.4f}')
        print('\nAssuming rotational symmetry in grains')
        print(f'Rotational axis: {poly_stats_dict["ind_rot"]}')
        print(f'Median aspect ratio: {poly_stats_dict["ar_scale"]:.3f}')
        print('\nGrain size')
        print(f'Median equivalent grain diameter: {poly_stats_dict["eqd_scale"]:.3f} micron')
        print(f'Standard deviation of equivalent grain diameter: {poly_stats_dict["eqd_sig"]:.4f}')
        print('--------------------------------------------------------')
    if show_plot:
        if iphase is None:
            title = 'Statistics of polyhedral grains'
        else:
            title = f'Statistics of polyhedral grains (phase {iphase})'
        plot_stats_dict(poly_stats_dict, title=title, save_files=save_files)

    return poly_stats_dict
