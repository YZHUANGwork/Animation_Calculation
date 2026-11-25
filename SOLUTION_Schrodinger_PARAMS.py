import numpy as np
import astropy.units as u
import astropy.constants as const
from functools import lru_cache

import SOLUTION_Schrodinger as SOLN

# ── 1) Free particle: plane wave phi(x, t=0) ────────────────────────────────
FREE_M     = const.m_e * const.c ** 2   # electron rest energy, real units (J, via m_e and c)
FREE_X_MIN = -2.0 * u.nm
FREE_X_MAX = 0.0 * u.nm
FREE_NGRID = 200
FREE_T     = 0.0 * u.fs
FREE_E     = 5.0 * u.eV
FREE_A     = 1.0
FREE_B     = 0.0

@lru_cache(maxsize=None)
def get_free(M=None, X_MIN=None, X_MAX=None, NGRID=None, T=None, E=None, A=None, B=None):
    
    M      = FREE_M      if M      is None else M
    X_MIN  = FREE_X_MIN  if X_MIN  is None else X_MIN
    X_MAX  = FREE_X_MAX  if X_MAX  is None else X_MAX
    NGRID  = FREE_NGRID  if NGRID  is None else NGRID
    T      = FREE_T      if T      is None else T
    E      = FREE_E      if E      is None else E
    A      = FREE_A      if A      is None else A
    B      = FREE_B      if B      is None else B

    sol = SOLN.PlaneWave(
        m=M.to(SOLN.mass_UNIT),
        x=np.linspace(X_MIN.to(SOLN.len_UNIT), X_MAX.to(SOLN.len_UNIT), NGRID),
        t=T.to(SOLN.time_UNIT),
        E=E.to(SOLN.energy_UNIT), A=A, B=B,
    )
    phi = sol.solve(t=T.to(SOLN.time_UNIT))
    return sol, phi

# ── 2) FiniteBarrier: scattering solution phi(x, t=0) ───────────────────────
BARRIER_M     = const.m_e * const.c ** 2   # electron rest energy, real units
BARRIER_X_MIN = -3.0 * u.nm
BARRIER_X_MAX = 3.0 * u.nm
BARRIER_NGRID = 400
BARRIER_T     = 0.0 * u.fs
BARRIER_E     = 1.0 * u.eV
BARRIER_A     = 1.0
BARRIER_L     = 1.0 * u.nm
BARRIER_V0    = 1.05 * u.eV

@lru_cache(maxsize=None)
def get_FiniteBarrier(M=None, X_MIN=None, X_MAX=None, NGRID=None, T=None, E=None, A=None, L=None, V0=None):
    
    M      = BARRIER_M      if M      is None else M
    X_MIN  = BARRIER_X_MIN  if X_MIN  is None else X_MIN
    X_MAX  = BARRIER_X_MAX  if X_MAX  is None else X_MAX
    NGRID  = BARRIER_NGRID  if NGRID  is None else NGRID
    T      = BARRIER_T      if T      is None else T
    E      = BARRIER_E      if E      is None else E
    A      = BARRIER_A      if A      is None else A
    L      = BARRIER_L      if L      is None else L
    V0     = BARRIER_V0     if V0     is None else V0

    sol = SOLN.FiniteBarrier(
        m=M.to(SOLN.mass_UNIT),
        x=np.linspace(X_MIN.to(SOLN.len_UNIT), X_MAX.to(SOLN.len_UNIT), NGRID),
        t=T.to(SOLN.time_UNIT),
        E=E.to(SOLN.energy_UNIT), A=A, L=L.to(SOLN.len_UNIT), V0=V0.to(SOLN.energy_UNIT),
    )
    phi, A_, B_, C_, D_, F_ = sol.solve(t=T.to(SOLN.time_UNIT))

    x_val = sol.x.to_value(SOLN.len_UNIT)
    Lv = sol.L.to_value(SOLN.len_UNIT)
    k_ext = sol.energy_to_k(sol.E, V=0 * SOLN.energy_UNIT)
    kv_tr = k_ext.to_value(SOLN.k_UNIT)
    k2_ext = sol.energy_to_k(sol.E, V=sol.V0)
    k2v_tr = k2_ext.to_value(SOLN.k_UNIT)

    incident = np.zeros(len(x_val), dtype=complex)
    reflected = np.zeros(len(x_val), dtype=complex)
    transmitted = np.zeros(len(x_val), dtype=complex)
    evanescent = np.zeros(len(x_val), dtype=complex)
    left = x_val < 0
    mid = (x_val >= 0) & (x_val <= Lv)
    right = x_val > Lv
    incident[left] = A_ * np.exp(1j * kv_tr * x_val[left])
    reflected[left] = B_ * np.exp(-1j * kv_tr * x_val[left])
    transmitted[right] = F_ * np.exp(1j * kv_tr * x_val[right])
    evanescent[mid] = C_ * np.exp(1j * k2v_tr * x_val[mid]) + D_ * np.exp(-1j * k2v_tr * x_val[mid])

    return sol, (phi, A_, B_, C_, D_, F_, incident, reflected, transmitted, evanescent)

# ── 3) Infinite potential well: eigenfunctions psi_n(x) ─────────────────────
WELL_M     = const.m_e * const.c ** 2 
WELL_X_MIN = -0.5 * u.nm
WELL_X_MAX = 1.5 * u.nm
WELL_NGRID = 300
WELL_T     = 0.0 * u.fs
WELL_L     = 1.0 * u.nm
WELL_N_MAX = 3

@lru_cache(maxsize=None)
def get_InfiniteBarrier(M=None, X_MIN=None, X_MAX=None, NGRID=None, T=None, L=None, N_MAX=None):
    
    M      = WELL_M      if M      is None else M
    X_MIN  = WELL_X_MIN  if X_MIN  is None else X_MIN
    X_MAX  = WELL_X_MAX  if X_MAX  is None else X_MAX
    NGRID  = WELL_NGRID  if NGRID  is None else NGRID
    T      = WELL_T      if T      is None else T
    L      = WELL_L      if L      is None else L
    N_MAX  = WELL_N_MAX  if N_MAX  is None else N_MAX

    sol = SOLN.InfiniteWell(
        m=M.to(SOLN.mass_UNIT),
        x=np.linspace(X_MIN.to(SOLN.len_UNIT), X_MAX.to(SOLN.len_UNIT), NGRID),
        t=T.to(SOLN.time_UNIT),
        L=L.to(SOLN.len_UNIT), n_max=N_MAX,
    )
    result = sol.solve(t=T.to(SOLN.time_UNIT))
    return sol, result