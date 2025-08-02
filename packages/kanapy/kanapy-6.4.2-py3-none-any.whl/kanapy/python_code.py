import numpy as np
import time
import scipy.sparse as sp
import scipy.io as sio
from mtex2numpy import mtex2numpy as m2n  # Alternative: pyMTEX-Bibliothek
import os

def texture_reconstruction(ns, **kwargs):
    """
    This function systematically reconstructs the ODF by a smaller number of
    orientations.
    
    Parameters:
    -----------
    ns : int
        Number of reduced orientations/grains in RVE
    
    **kwargs : keyword arguments
        'ebsd_mat_file' : str
            Path to EBSD data saved as .mat file (should contain only one phase/mineral)
        'ebsd' : object
            EBSD object (should contain only one phase/mineral)
        'orientation' : object
            Orientation object
        'grains_mat_file' : str
            Path to grains data saved as .mat file (should contain only one phase/mineral)
        'grains' : object
            Grains object (should contain only one phase/mineral)
        'kernel' : object
            Kernel object (only deLaValeePoussinKernel)
        'kernel_shape' : float
            Kernel shape parameter kappa in degrees, default is 5
    
    Returns:
    --------
    orired_f : object
        Reduced orientation set
    odfred_f : object
        ODF calculated from reduced orientation set
    ero : float
        L1 error
    varargout : optional
        Additional outputs if requested
    """
    # Set progress output flag
    mtex_progress = 1  # Avoid progress output
    
    options = ['ebsd_mat_file', 'ebsd', 'orientation']
    flag = 1
    grains = []
    
    # Process input parameters for orientations
    for option in options:
        if option in kwargs and flag >= 0:
            if option == 'ebsd_mat_file':
                # Load EBSD data from MAT file
                mat_data = sio.loadmat(kwargs[option])
                # Get the variable name from the mat file
                ebsd_var = list(mat_data.keys())[-1]  # Simplified approach to get the main variable
                ebsd = mat_data[ebsd_var]
                
                # Check if EBSD has only one phase
                assert len(np.unique(ebsd.phase_id)) == 1, "EBSD has multiple phases"
                ori = ebsd.orientations
                flag -= 1
                
            elif option == 'ebsd':
                ebsd = kwargs[option]
                # Check if EBSD has only one phase
                assert len(np.unique(ebsd.phase_id)) == 1, "EBSD has multiple phases"
                ori = ebsd.orientations
                flag -= 1
                
            elif option == 'orientation':
                ori = kwargs[option]
                flag -= 1
    
    flag = 1
    
    # Process input parameters for grains or kernel
    options = ['grains_mat_file', 'grains', 'kernel', 'kernel_shape']
    
    for option in options:
        if option in kwargs and flag >= 0:
            if option == 'grains_mat_file':
                # Load grains data from MAT file
                mat_data = sio.loadmat(kwargs[option])
                # Get the variable name from the mat file
                grains_var = list(mat_data.keys())[-1]  # Simplified approach to get the main variable
                grains = mat_data[grains_var]
                
                # Check if grains has only one phase
                assert len(np.unique(grains.phase_id)) == 1, "Grains has multiple phases"
                print("Optimum kernel estimated from mean orientations of grains")
                psi = calc_kernel(grains.mean_orientation)
                flag -= 1
                
            elif option == 'grains':
                grains = kwargs[option]
                # Check if grains has only one phase
                assert len(np.unique(grains.phase_id)) == 1, "Grains has multiple phases"
                print("Optimum kernel estimated from mean orientations of grains")
                psi = calc_kernel(grains.mean_orientation)
                flag -= 1
                
            elif option == 'kernel':
                # Check if kernel is of type deLaValleePoussinKernel
                # This check needs to be adjusted based on the Python equivalent
                assert is_de_la_vallee_poussin_kernel(kwargs[option]), "Invalid kernel, use deLaValleePoussinKernel"
                psi = kwargs[option]
                flag -= 1
                
            elif option == 'kernel_shape':
                # Create deLaValleePoussinKernel with given halfwidth
                psi = de_la_vallee_poussin_kernel(halfwidth=kwargs[option])
                flag -= 1
    
    assert flag >= 0, "Multiple options for same input"
    
    if flag == 1:
        psi = de_la_vallee_poussin_kernel(halfwidth=0.08726646259971647)  # 5 degrees in radians
        print(f"Default initial kernel shape factor: {5} degree")
    
    # ODF calculation and L1 minimization setup
    odf = calc_kernel_odf(ori, kernel=psi)
    
    # Ensure ori is properly shaped
    if ori.shape[1] > ori.shape[0]:
        ori = ori.reshape(len(ori), 1)
    
    ll = 10
    hl = 55
    step = 1
    ero = 100
    e_mod = []
    lim = 10
    hh = []
    kappa = psi.halfwidth * 180 / np.pi  # initial kernel shape
    
    # Start timing
    start_time = time.time()
    
    for hw in range(ll, hl + 1, step):
        # Create an equispaced grid in SO3
        S3G = equispaced_so3_grid(ori.CS, ori.SS, resolution=(hw/2)*(np.pi/180))
        
        weights = np.ones(len(ori))
        # Find indices of orientations in the grid
        indices = find_orientations_in_grid(S3G, ori)
        M = sp.csr_matrix((weights, (np.arange(len(ori)), indices)), 
                          shape=(len(ori), len(S3G)))
        
        weights = np.array(M.sum(axis=0)).flatten()
        weights = weights / np.sum(weights)
        
        # Subgrid selection
        non_zero = weights != 0
        S3G = S3G[non_zero]
        weights = weights[non_zero]
        
        # Integer approximation
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
        co = 0
        
        while diff > 0:
            if screen[weights_loc[co]] > 0:
                screen[weights_loc[co]] -= 1
                diff = np.sum(screen) - ns
            co += 1
        
        fval = screen[screen > 0]
        
        # Mean orientation estimation and kernel optimization
        rows, cols = M.nonzero()
        ytun = np.unique(cols)
        ytfreq = np.bincount(cols, minlength=len(S3G))
        
        # Split orientations into cells based on their grid association
        oriseq = []
        start_idx = 0
        for freq in ytfreq:
            if freq > 0:
                oriseq.append(ori[rows[start_idx:start_idx+freq]])
                start_idx += freq
            else:
                oriseq.append([])
        
        # Select orientations where screen > 0
        oriseq = [oriseq[i] for i in range(len(screen)) if screen[i] > 0]
        
        ori_f = S3G[screen == 1]
        
        oriseq_p = [oriseq[i] for i in range(len(fval)) if fval[i] > 1]
        ind = [int(fval[i]) for i in range(len(fval)) if fval[i] > 1]
        
        # Split mean calculation for orientations
        pend_list = []
        for i in range(len(oriseq_p)):
            pend_list.extend(split_mean(oriseq_p[i], ind[i]))
        
        ori_f = np.concatenate([ori_f, pend_list])
        
        # Estimate ODF and calculate error
        odfred, h = odf_est(ori_f, np.ones(ns), kappa, odf)
        hh.append(h)
        er = calc_error(odf, odfred)
        
        if er < ero:
            orired_f = ori_f
            odfred_f = odfred
            ohw = h
            ero = er
        
        e_mod.append(er)
        
        # Check convergence
        if len(e_mod) > lim:
            min_idx = np.argmin(e_mod)
            if len(e_mod) - min_idx > lim:
                break
    
    # Project to fundamental region
    orired_f = project_to_fundamental_region(orired_f)
    
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    
    return orired_f, odfred_f, ero

# Helper functions

def calc_kernel(orientations):
    """Calculate optimal kernel for given orientations"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return de_la_vallee_poussin_kernel(halfwidth=0.08726646259971647)  # 5 degrees in radians

def is_de_la_vallee_poussin_kernel(kernel):
    """Check if kernel is of type deLaValleePoussinKernel"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return True

def de_la_vallee_poussin_kernel(halfwidth):
    """Create deLaValleePoussinKernel with given halfwidth"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    class Kernel:
        def __init__(self, hw):
            self.halfwidth = hw
    return Kernel(halfwidth)

def calc_kernel_odf(orientations, kernel):
    """Calculate kernel ODF for given orientations and kernel"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return None

def equispaced_so3_grid(cs, ss, resolution):
    """Create equispaced grid in SO3"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return None

def find_orientations_in_grid(grid, orientations):
    """Find indices of orientations in the grid"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return np.zeros(len(orientations), dtype=int)

def split_mean(orientations, count):
    """Split orientations and calculate mean"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return []

def odf_est(orientations, weights, kappa, reference_odf):
    """Estimate ODF from orientations"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return None, kappa

def calc_error(odf1, odf2):
    """Calculate L1 error between two ODFs"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return 0.0

def project_to_fundamental_region(orientations):
    """Project orientations to fundamental region"""
    # Implementation depends on the Python MTEX equivalent
    # This is a placeholder
    return orientations
