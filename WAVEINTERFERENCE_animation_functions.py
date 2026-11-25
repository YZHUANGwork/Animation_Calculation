import numpy as np
import math
import cg_plot_fn as cg
import  SOLN_waveinterference_PARAMS as SOLN_P

rng = np.random.default_rng(seed=0)
def WAVE_anime(hex_rc_arr, detail_info, version):
    WAVE = SOLN_P.get_wave()
    X = WAVE.X.ravel()
    Y = WAVE.Y.ravel()

    
    if version == 'squeeze':
        grid_hex_rc= cg.fn2grid(
                X, Y,
                DOMAIN_W_SCALE=0.95, DOMAIN_H_SCALE=0.95,
                PIVOT_ROW=min(r for r,c in hex_rc_arr), PIVOT_COL=(min(c for r,c in hex_rc_arr) + max(c for r,c in hex_rc_arr)) // 2,
                PIVOT_ROW_X=0, PIVOT_COL_Y=Y.max(),
                detail_info=detail_info, square_H=False, square_W =False , return_DOMAIN = False
            )

    elif version == 'square':
        grid_hex_rc= cg.fn2grid(
                X, Y,
                DOMAIN_W_SCALE=0.95, DOMAIN_H_SCALE=0.95,
                PIVOT_ROW=max(r for r,c in hex_rc_arr), PIVOT_COL=(min(c for r,c in hex_rc_arr) + max(c for r,c in hex_rc_arr)) // 2,
                PIVOT_ROW_X=0, PIVOT_COL_Y=Y.min(),
                detail_info=detail_info, square_H=False, square_W =True , return_DOMAIN = False
            )
    return WAVE, grid_hex_rc
