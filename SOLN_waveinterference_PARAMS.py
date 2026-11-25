
import numpy as np
import astropy.units as u

import SOLN_waveinterference as SOLN_WAVE

rng = np.random.default_rng(seed=0)
n_drops = 30

xs = rng.uniform(-7, 7, n_drops)
ys = rng.uniform(-10, -4, n_drops)
sources_ripple = tuple(np.array([x, y]) * u.m for x, y in zip(xs, ys))


wavelength_ripple =(0.8,) * n_drops * u.m
amplitude_ripple = tuple(rng.uniform(2., 3., n_drops) *u.m) # (2.5,) * n_drops * u.m
freq_ripple = tuple(rng.uniform(1., 2., n_drops) *u.Hz)
kick_time_ripple = tuple(np.sort(rng.uniform(0, 10, n_drops)) * u.s)#np.arange(1, 18, 1.2)[:n_drops]* u.s

kick_time_ripple2 = tuple(np.sort(rng.uniform(16, 26, n_drops)) * u.s)#np.arange(1, 18, 1.2)[:n_drops]* u.s

#
decay_tau_ripple = tuple(rng.uniform(0.2, 1, n_drops) * u.s)

is_ripple_ripple = (True,) * n_drops

sources_constant_center = ([2, -10] * u.m, [0, -10] * u.m, [ -2, -10] * u.m)
wavelength_constant_center =(3.0 * u.m, 3.0 * u.m, 3.0 * u.m)
amplitude_constant_center = (1.0 * u.m, 1.0 * u.m, 1.0 * u.m)
freq_constant_center = (3.0 * u.Hz, 3.0 * u.Hz, 3.0 * u.Hz)
kick_time_constant_center = (45. * u.s,45. * u.s, 45. * u.s)
is_ripple_constant_center =(False, False, False)
decay_tau_constant_center =(None, None,None)


sources_constant_side = ([5, -10] * u.m, [ -5, -10] * u.m)
wavelength_constant_side =(1.0 * u.m, 1.0 * u.m)
amplitude_constant_side = (3.0 * u.m, 3.0 * u.m)
freq_constant_side = (3.0 * u.Hz, 3.0 * u.Hz)
kick_time_constant_side = (50. * u.s,50. * u.s)
is_ripple_constant_side =(False, False)
decay_tau_constant_side =(None, None)

sources_constant = ([5, -10] * u.m, [2, -10] * u.m, [0, -10] * u.m, [ -2, -10] * u.m, [ -5, -10] * u.m)
wavelength_constant = (1.0 * u.m,3.0 * u.m, 3.0 * u.m, 3.0 * u.m, 1.0 * u.m)
amplitude_constant = (3.0 * u.m, 1.0 * u.m, 1.0 * u.m, 1.0 * u.m, 3.0 * u.m)
freq_constant = (1.0 * u.Hz, 1.0 * u.Hz, 1.0 * u.Hz, 1.0 * u.Hz, 1.0 * u.Hz)
kick_time_constant =(10. * u.s, 45. * u.s,45. * u.s, 45. * u.s,10. * u.s)
is_ripple_constant = (False, False, False, False, False)
decay_tau_constant = (None, None,None,None,None)


sources_constant_final = ([-2.8, 9.5] * u.m, [-0.1, 9.5] * u.m)
wavelength_constant_final =(1.0 * u.m, 1.0 * u.m)
amplitude_constant_final = (5 * u.m, 5 * u.m)
freq_constant_final = (1.0 * u.Hz, 1.0 * u.Hz)
kick_time_constant_final = (100. * u.s,100. * u.s)
is_ripple_constant_final =(True, True)
decay_tau_constant_final =(None, None)



WAVE_GRID_SIZE = 300
WAVE_X_RANGE   = [-6, 6] * u.m
WAVE_Y_RANGE   = [-10, 10] * u.m
WAVE_SOURCES    = tuple(sources_ripple)+tuple(sources_ripple
                                             )+tuple(sources_constant_center)+tuple(sources_constant_side)+tuple(sources_constant_final)
WAVE_WAVELENGTH = tuple(wavelength_ripple)+tuple(wavelength_ripple)+tuple(wavelength_constant_center
                                                                         )+tuple(wavelength_constant_side)+tuple(wavelength_constant_final)
WAVE_AMPLITUDE  = tuple(amplitude_ripple)+tuple(amplitude_ripple)+tuple(amplitude_constant_center
                                                                       )+tuple(amplitude_constant_side)+tuple(amplitude_constant_final)
WAVE_FREQ       = tuple(freq_ripple)+tuple(freq_ripple)+tuple(freq_constant_center)+tuple(freq_constant_side)+tuple(freq_constant_final)

WAVE_KICK_TIME  = tuple(kick_time_ripple)+tuple(kick_time_ripple2)+tuple(kick_time_constant_center
                                                                        )+tuple(kick_time_constant_side)+tuple(kick_time_constant_final)
WAVE_IS_RIPPLE  = tuple(is_ripple_ripple)+tuple(is_ripple_ripple)+tuple(is_ripple_constant_center
                                                                       )+tuple(is_ripple_constant_side)+tuple(is_ripple_constant_final)
WAVE_DECAY_TAU  = tuple(decay_tau_ripple)+tuple(decay_tau_ripple)+tuple(decay_tau_constant_center
                                                                       )+tuple(decay_tau_constant_side)+tuple(decay_tau_constant_final)


def get_wave(GRID_SIZE=None, X_RANGE=None, Y_RANGE=None, SOURCES=None,
             WAVELENGTH=None, AMPLITUDE=None, FREQ=None,
             KICK_TIME=None, IS_RIPPLE=None, DECAY_TAU=None):
   
    GRID_SIZE  = WAVE_GRID_SIZE  if GRID_SIZE  is None else GRID_SIZE
    X_RANGE    = WAVE_X_RANGE    if X_RANGE    is None else X_RANGE
    Y_RANGE    = WAVE_Y_RANGE    if Y_RANGE    is None else Y_RANGE
    SOURCES    = WAVE_SOURCES    if SOURCES    is None else SOURCES
    WAVELENGTH = WAVE_WAVELENGTH if WAVELENGTH is None else WAVELENGTH
    AMPLITUDE  = WAVE_AMPLITUDE  if AMPLITUDE  is None else AMPLITUDE
    FREQ       = WAVE_FREQ       if FREQ       is None else FREQ
    KICK_TIME  = WAVE_KICK_TIME  if KICK_TIME  is None else KICK_TIME
    IS_RIPPLE  = WAVE_IS_RIPPLE  if IS_RIPPLE  is None else IS_RIPPLE
    DECAY_TAU  = WAVE_DECAY_TAU  if DECAY_TAU  is None else DECAY_TAU

    sim = SOLN_WAVE.WaveInterference2D(
        grid_size=GRID_SIZE,
        x_range=X_RANGE, y_range=Y_RANGE,
        sources=SOURCES,
        wavelength=WAVELENGTH,
        amplitude=AMPLITUDE,
        freq=FREQ,
        kick_time=KICK_TIME,
        is_ripple=IS_RIPPLE,
        decay_tau=DECAY_TAU,
    )
    return sim