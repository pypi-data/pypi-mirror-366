""""
Function to create parameter sets from three orthogonal surface slices

NOT PART OF PUBLIC KANAPY!

Authors: Golsa Tooloei Eshlaghi, Alexander Hartmaier
ICAMS, Ruhr University Bochum, Germany

March 2024
"""
import logging
import numpy as np
from scipy.stats import vonmises, lognorm
from scipy.spatial.transform import Rotation as R
from scipy.linalg import eig


def create_ref_ell(eqd_scale, ar_scale, ta_loc, slices=None):
    """
    Create reference Ellispoid from statistical data of three orthogonal surface slices.

    Parameters
    ----------
    eqd_scale
    ar_scale
    ta_loc
    slices

    Returns
    -------
    semi_axs
    euler
    """
    # Set information on sequence of slices
    if slices is None:
        logging.warning('No information about sequence of surface slices given.'
                        'Assuming: "xz", "yz", "xy"')
        slices = ['xz', 'yz', 'xy']
    Nslice = len(slices)
    if Nslice != 3:
        raise ValueError(f'Number of slices must be 3, not {Nslice}.')
    # calculate matrix of 3D ellipsoid
    M_ell = np.zeros((3, 3))
    seq = ''
    for isl, pl in enumerate(slices):
        dinv = 4. / eqd_scale[isl] ** 2
        ca = np.cos(ta_loc[isl])
        sa = np.sin(ta_loc[isl])
        h11 = dinv * (ca ** 2 / ar_scale[isl] + ar_scale[isl] * sa ** 2)
        h22 = dinv * (sa ** 2 / ar_scale[isl] + ar_scale[isl] * ca ** 2)
        h12 = dinv * ca * sa * (1. / ar_scale[isl] - ar_scale[isl])
        # determine normal axis and insert slice matrix into full 3D matrix
        if pl.lower() == 'xy':
            seq += 'z'
            if np.isclose(M_ell[0, 0], 0.):
                M_ell[0, 0] = h11
            else:
                # Two values for M[0,0], Using average
                M_ell[0, 0] = 0.5 * (M_ell[0, 0] + h11)
            if np.isclose(M_ell[1, 1], 0.):
                M_ell[1, 1] = h22
            else:
                # Two values for M[1,1], Using average
                M_ell[1, 1] = 0.5 * (M_ell[1, 1] + h22)
            M_ell[0, 1] = h12
        elif pl.lower() == 'xz':
            seq += 'y'
            if np.isclose(M_ell[0, 0], 0.):
                M_ell[0, 0] = h11
            else:
                # Two values for M[0,0], Using average
                M_ell[0, 0] = 0.5 * (M_ell[0, 0] + h11)
            if np.isclose(M_ell[2, 2], 0.):
                M_ell[2, 2] = h22
            else:
                # Two values for M[2,2], Using average
                M_ell[2, 2] = 0.5 * (M_ell[2, 2] + h22)
            M_ell[0, 2] = h12
        elif pl.lower() == 'yz':
            seq += 'x'
            if np.isclose(M_ell[1, 1], 0.):
                M_ell[1, 1] = h11
            else:
                # Two values for M[1,1], Using average
                M_ell[1, 1] = 0.5 * (M_ell[1, 1] + h11)
            if np.isclose(M_ell[2, 2], 0.):
                M_ell[2, 2] = h22
            else:
                # Two values for M[2,2], Using average
                M_ell[2, 2] = 0.5 * (M_ell[2, 2] + h22)
            M_ell[1, 2] = h12
        else:
            raise ValueError(f'Unknown format for slice, must be "xy", "xz" or "yz", not "{pl}"')

    # fill lower triangle of symmetric matrix
    M_ell[1, 0] = M_ell[0, 1]
    M_ell[2, 0] = M_ell[0, 2]
    M_ell[2, 1] = M_ell[1, 2]

    # extract lengths of semi-axes and their directions
    ev_val, evec = eig(M_ell, right=True)
    if not np.all(np.isclose(np.imag(ev_val), 0.)):
        raise ValueError('Matrix not positive definite, imaginary eigenvalues', ev_val)
    ev_val = np.real(ev_val)
    if any(ev_val <= 0.):
        raise ValueError('Matrix not positive definite, negative eigenvalues', ev_val)
    semi_axs = list(1. / np.sqrt(ev_val))
    rot = R.from_matrix(evec)
    euler = list(rot.as_euler(seq))
    return semi_axs, euler, seq


def gen_data_free(pdict, stats):
    """
    Function to generate matrices defining ellipsoid axes and rotations based on data
    from three orthogonal surface slices

    Parameters
    ----------
    pdict
    stats : dictionary

    Returns
    -------
    pdcit

    """
    # Extract descriptors for semi-axes distribution from dict
    sig_sa = stats["Semi axes"]['sig']
    scale_sa = stats["Semi axes"]['scale']
    if 'loc' in stats["Semi axes"].keys():
        logging.warning('Parameter "loc" provided for semi-axes will be ignored.')
    sa_cutoff_min = stats["Semi axes"]["cutoff_min"]
    sa_cutoff_max = stats["Semi axes"]["cutoff_max"]
    if any(np.divide(sa_cutoff_min, sa_cutoff_max) > 0.75):
        raise ValueError('Min/Max values for cutoffs of semi-axes are too close: ' +
                         f'Max: {sa_cutoff_max}, Min: {sa_cutoff_min}')
    # Extract Euler angle statistics for grain tilt from dict
    kappa = stats["Tilt Euler"]['kappa']
    loc_ori = stats["Tilt Euler"]['loc']
    ori_cutoff_min = stats["Tilt Euler"]["cutoff_min"]
    ori_cutoff_max = stats["Tilt Euler"]["cutoff_max"]
    if 'seq' in stats['Tilt Euler'].keys():
        seq = stats['Tilt Euler']['seq']
    else:
        logging.warning('No sequence for Euler angles for ellipsoid tilt provided, assuming "yxz".')
        seq = 'yxz'
    if any(np.divide(ori_cutoff_min, ori_cutoff_max) > 0.75):
        raise ValueError('Min/Max values for cutoffs of orientation of tilt axis are too close: ' +
                         f'Max: {ori_cutoff_max}, Min: {ori_cutoff_min}')

    npart = pdict['Number']  # number of particles for packing
    triple_ta = np.zeros((npart, 3))
    triple_sa = np.zeros((npart, 3))
    # Generate sets of tilt angles and semi_axes corresponding to the data
    # of three orthogonal surface slices
    for i in range(3):
        # Tilt angle statistics, sample from von Mises distribution
        tilt_angle = []
        iter = 0
        while npart - len(tilt_angle) > 0:
            tilt = vonmises.rvs(kappa[i], loc=loc_ori[i], size=npart)
            tilt = 0.5 * (tilt + np.pi)
            index_array = np.where((tilt >= ori_cutoff_min[i]) & (tilt <= ori_cutoff_max[i]))
            TA = tilt[index_array].tolist()
            tilt_angle.extend(TA)
            iter += 1
            if iter > 10000:
                raise StopIteration('Iteration for tilt angles did not converge in 10000 iterations.'
                                    'Increase cutoff range to assure proper generation of particles.')
        triple_ta[:, i] = tilt_angle[0:npart]
        # Aspect ratio statistics, sample from lognormal distribution
        semi_axs = []
        iter = 0
        while npart - len(semi_axs) > 0:
            semi = lognorm.rvs(sig_sa[i], scale=scale_sa[i], size=npart)
            index_array = np.where((semi >= sa_cutoff_min[i]) & (semi <= sa_cutoff_max[i]))
            SA = semi[index_array].tolist()
            semi_axs.extend(SA)
            iter += 1
            if iter > 10000:
                raise StopIteration('Iteration for aspect ratios did not converge in 10000 iterations.'
                                    'Increase cutoff range to assure proper generation of particles.')
        triple_sa[:, i] = 2.0 * np.array(semi_axs[0:npart])
    # Construct list of quaternions from Euler angles of ellipsoid tilt
    quats = []
    for ip in range(npart):
        rot = R.from_euler(seq, triple_ta[ip, :])  # 0.5*(loc_ori + np.pi))
        quats.append(rot.as_quat())

    # Add data to particle data dictionary for further use
    pdict['Major_diameter'] = triple_sa[:, 0].tolist()
    pdict['Minor_diameter1'] = triple_sa[:, 1].tolist()
    pdict['Minor_diameter2'] = triple_sa[:, 2].tolist()
    pdict['Quaternion'] = quats
    return pdict
