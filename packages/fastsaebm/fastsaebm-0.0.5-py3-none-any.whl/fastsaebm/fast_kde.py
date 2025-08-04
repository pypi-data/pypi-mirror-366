import numpy as np
from numba import njit
from typing import Dict, Tuple
import math 

EPSILON = 1e-12
SQRT_2PI = math.sqrt(2.0 * math.pi)

@njit(fastmath=True)
def gaussian_kernel(x: float, data_point: float, bw: float) -> float:
    """ data point is one of the measurement in all measurements of a biomarker across all participants
    """
    z = (x - data_point) / bw
    return math.exp(-0.5 * z * z) / (bw * SQRT_2PI)

@njit(fastmath=True)
def calculate_bandwidth(data: np.ndarray, weights: np.ndarray, bw_method:str) -> float:
    """
        - data is all the measurements for a biomarker
        - weights are either the phi or theta weights
    """
    n = len(data)
    if n <= 1:
        return 1.0
    if weights is None or weights.size == 0:
        sigma = max(np.std(data), EPSILON)
    else:
        w_sum = max(np.sum(weights), EPSILON) # lower bound of sigma
        w_mean = np.sum(weights * data) / w_sum
        var = 0.0
        w2_sum = 0.0
        for i in range(n):
            diff = data[i] - w_mean
            var += weights[i] * diff * diff
            w2_sum += weights[i] * weights[i]
        sigma = max(math.sqrt(var / w_sum), EPSILON) # lower bound of sigma
        n_eff = 1.0 / max(w2_sum, EPSILON)
        n = n_eff
    if bw_method == "scott":
        return sigma * n ** (-0.2)
    elif bw_method == "silverman":
        return sigma * (4.0 / (3.0 * n)) ** 0.2

@njit(fastmath=True)
def _compute_pdf(x: float, data: np.ndarray, weights: np.ndarray, bw: float) -> float:
    pdf = 0.0 
    for j in range(len(data)):
        if weights[j] > EPSILON:
            pdf += weights[j] * gaussian_kernel(x, data[j], bw)
    return pdf 

@njit(fastmath=True)
def _compute_ln_likelihood_kde_core(
    p_measurements: np.ndarray, 
    kde_data: np.ndarray,        
    kde_weights: np.ndarray,  
    bw_method: str
) -> float:
    """
    Compute KDE log PDF efficiently using Numba.
    
    Args:
        p_measurements: Biomarker measurements for a specific individual
        kde_data: KDE sample points
        kde_weights: KDE weights
        bw_method
        
    Returns:
        Total log PDF value
    """
    total = 0.0
    n = len(p_measurements)
    for bm in range(n): # index of biomarker and also the corresponding measurement
        x = p_measurements[bm] # this biomarker, this participant
        bm_data = kde_data[bm]  # all the measurements for this bm across all participants
        weights = kde_weights[bm]
        bw = calculate_bandwidth(bm_data, weights, bw_method)
        pdf = _compute_pdf(x, bm_data, weights, bw)
        # Handle numerical stability
        total += np.log(max(pdf, EPSILON))
    return total

@njit(fastmath=True)
def compute_ln_likelihood_kde_fast(
    n_participants:int,
    p_measurements: np.ndarray, # all bm measurements for a specific individual
    S_n: np.ndarray, # the new_order, 1-index, which is the index for bm1 to bmN
    k_j: int, 
    kde_theta_phi: np.ndarray,
    bw_method: str
) -> float:
    """
    Compute ln likelihood for a specific participant's all biomarker measurements 
    
    Args:
        n_participants: number of participants
        bm_measurements: Biomarker measurements for a specific individual
        S_n: the new_order, 1-index, which is the index for bm1 to bmN
        k_j: Stage value
        kde_theta_phi: theta_phi for kde
        bw_method: method for bandwidth selection
        
    Returns:
        Log likelihood value
    """
    assert len(p_measurements) == len(S_n), "Measurements and S_n must have same length"
    assert len(p_measurements) == kde_theta_phi.shape[0], "Measurements must match number of biomarkers"
    assert kde_theta_phi.shape[2] == n_participants, "kde_theta_phi must match n_participants"
    
    # Convert to stage indicators (1 for affected, 0 for non-affected)
    affected_flags = k_j >= S_n

    kde_data = kde_theta_phi[:,0,:]
     # Pre-allocate arrays for Numba
    kde_weights = np.zeros((len(S_n), n_participants))

    # Fill arrays with data
    for bm in range(len(S_n)):
        kde_weights[bm] = kde_theta_phi[bm, 1, :] if affected_flags[bm] else kde_theta_phi[bm, 2, :]
    
    # Compute log likelihood
    return _compute_ln_likelihood_kde_core(
        p_measurements,
        kde_data,
        kde_weights,
        bw_method
    )