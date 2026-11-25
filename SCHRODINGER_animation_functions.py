import numpy as np

import math
import astropy.units as u
import os
import cg_plot_fn as cg

import SOLUTION_Schrodinger_PARAMS as SOLN

rng = np.random.default_rng(42)

#------read solution-----------------------

def WAVE_anime(PIVOT_ROW, PIVOT_COL, detail_info, hex_rc_arr, version):
    print(version)
        
    if version == "free":
        sol, phi_free = SOLN.get_free()
        x_free = sol.x.to_value(u.nm)

        X = x_free
        Y = phi_free.real
        
        DOMAIN_W_SCALE = 1.8
        DOMAIN_H_SCALE = 2.
        
        grid_hex_rc = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, PIVOT_ROW, PIVOT_COL, X[0], Y[0], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = False)
        
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        grids = [curve_cells]
    
    if version == "tunneling right":
        sol, soln_details  = SOLN.get_FiniteBarrier(X_MIN=1.*u.nm, X_MAX=6*u.nm, NGRID=600, L=2*u.nm, E=1* u.eV, 
                                                            V0=1.01* u.eV)
        
        (phi_barrier, A, B, C, D, F, incident, reflected, transmitted, evanescent) = soln_details
        x_barrier = sol.x.to_value(u.nm)
        Lv_barrier = sol.L.to_value(u.nm)
        
        X = x_barrier
        Y = phi_barrier.real
        
        x0_ref, xL_ref = 0.0, Lv_barrier

        
        DOMAIN_W_SCALE = 1.2
        DOMAIN_H_SCALE = 2.
        
        idx = np.argmin(np.abs(np.asarray(X-Lv_barrier//2)))
        grid_hex_rc, DOMAIN_W, DOMAIN_H, CANVAS_PHYSICAL_W, CANVAS_PHYSICAL_H = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                                                                        PIVOT_ROW, PIVOT_COL, X[idx], Y[idx], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = True)
        
        grid_hex_rc_barrier = cg.fn2grid(np.array([x0_ref, xL_ref]), np.array([0.0, 0.0]), DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                      PIVOT_ROW, PIVOT_COL, X[idx], 0., detail_info, 
                                      square_H = False,square_W = False, EPS_DOMAIN = 1e-6, 
                                      input_PHYSICAL_size = [CANVAS_PHYSICAL_W, 1.0], return_DOMAIN = False)
        
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        col_x0 = min([grid_hex_rc_barrier[0][1], grid_hex_rc_barrier[1][1]])
        col_xL = max([grid_hex_rc_barrier[0][1], grid_hex_rc_barrier[1][1]])

        grids = [curve_cells, [col_x0, col_xL]]
        
    if version == "full tunneling":
        sol, soln_details  = SOLN.get_FiniteBarrier(X_MIN=-1*u.nm, X_MAX=3*u.nm, NGRID=600,  E=1* u.eV, 
                                                            V0=1.05* u.eV)
        
        (phi_barrier, A, B, C, D, F, incident, reflected, transmitted, evanescent) = soln_details
        x_barrier = sol.x.to_value(u.nm)
        Lv_barrier = sol.L.to_value(u.nm)
        
        X = x_barrier
        Y = phi_barrier.real
        
        x0_ref, xL_ref = 0.0, Lv_barrier

        
        DOMAIN_W_SCALE = 2.
        DOMAIN_H_SCALE = 1.4
        
        
        grid_hex_rc, DOMAIN_W, DOMAIN_H, CANVAS_PHYSICAL_W, CANVAS_PHYSICAL_H = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                                                                        PIVOT_ROW, PIVOT_COL, X[0], Y[0], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = True)
        
        grid_hex_rc_barrier = cg.fn2grid(np.array([x0_ref, xL_ref]), np.array([0.0, 0.0]), DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                      PIVOT_ROW, PIVOT_COL, X[0], 0., detail_info, 
                                      square_H = False,square_W = False, EPS_DOMAIN = 1e-6, 
                                      input_PHYSICAL_size = [CANVAS_PHYSICAL_W, 1.0], return_DOMAIN = False)
        
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        col_x0 = min([grid_hex_rc_barrier[0][1], grid_hex_rc_barrier[1][1]])
        col_xL = max([grid_hex_rc_barrier[0][1], grid_hex_rc_barrier[1][1]])

        grids = [curve_cells, [col_x0, col_xL]]
        
   
    if version == "left incident":
        sol, soln_details  = SOLN.get_FiniteBarrier(X_MIN=-3.55*u.nm, X_MAX=0.1*u.nm, NGRID=600,  E=1* u.eV, 
                                                            V0=1.5* u.eV)
        
        (phi_barrier, A, B, C, D, F, incident, reflected, transmitted, evanescent) = soln_details
        x_barrier = sol.x.to_value(u.nm)
        Lv_barrier = sol.L.to_value(u.nm)
        
        X = x_barrier[::-1]
        Y = incident.real
        
        DOMAIN_W_SCALE = 1.9
        DOMAIN_H_SCALE = 4.
      
        grid_hex_rc, DOMAIN_W, DOMAIN_H, CANVAS_PHYSICAL_W, CANVAS_PHYSICAL_H = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                                                                        PIVOT_ROW, PIVOT_COL, X[0], Y[0], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = True)
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        
        grids = [curve_cells]
        
        
    if version == "right incident":
        sol, soln_details  = SOLN.get_FiniteBarrier(X_MIN=-3.55*u.nm, X_MAX=0.1*u.nm, NGRID=600,  E=1* u.eV, 
                                                            V0=1.5* u.eV)
        
        (phi_barrier, A, B, C, D, F, incident, reflected, transmitted, evanescent) = soln_details
        x_barrier = sol.x.to_value(u.nm)
        Lv_barrier = sol.L.to_value(u.nm)
        
        X = x_barrier
        Y = -incident.real
        
        DOMAIN_W_SCALE = 1.9
        DOMAIN_H_SCALE = 4.
      
        grid_hex_rc, DOMAIN_W, DOMAIN_H, CANVAS_PHYSICAL_W, CANVAS_PHYSICAL_H = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                                                                        PIVOT_ROW, PIVOT_COL, X[0], Y[0], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = True)
        
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        grids = [curve_cells]
        
    if version == "left reflect":
        sol, soln_details  = SOLN.get_FiniteBarrier(X_MIN=-3.55*u.nm, X_MAX=0.1*u.nm, NGRID=600,  E=1* u.eV, 
                                                            V0=1.5* u.eV)
        
        (phi_barrier, A, B, C, D, F, incident, reflected, transmitted, evanescent) = soln_details
        x_barrier = sol.x.to_value(u.nm)
        Lv_barrier = sol.L.to_value(u.nm)
        
        X = x_barrier[::-1]
        Y = reflected.real
        Y_match = incident.real
        
        DOMAIN_W_SCALE = 1.9
        DOMAIN_H_SCALE = 4.
      
        grid_hex_rc, DOMAIN_W, DOMAIN_H, CANVAS_PHYSICAL_W, CANVAS_PHYSICAL_H = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                                                                        PIVOT_ROW, PIVOT_COL, X[0], Y_match[0], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = True)
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        
        grids = [curve_cells]
        
        
    if version == "right reflect":
        sol, soln_details  = SOLN.get_FiniteBarrier(X_MIN=-3.55*u.nm, X_MAX=0.1*u.nm, NGRID=600,  E=1* u.eV, 
                                                            V0=1.5* u.eV)
        
        (phi_barrier, A, B, C, D, F, incident, reflected, transmitted, evanescent) = soln_details
        x_barrier = sol.x.to_value(u.nm)
        Lv_barrier = sol.L.to_value(u.nm)
        
        X = x_barrier
        Y = -reflected.real
        Y_match = -incident.real
        
        DOMAIN_W_SCALE = 1.9
        DOMAIN_H_SCALE = 4.
      
        grid_hex_rc, DOMAIN_W, DOMAIN_H, CANVAS_PHYSICAL_W, CANVAS_PHYSICAL_H = cg.fn2grid(X, Y, DOMAIN_W_SCALE ,DOMAIN_H_SCALE, 
                                                                                        PIVOT_ROW, PIVOT_COL, X[0], Y_match[0], detail_info, 
            square_H = False,square_W = False, EPS_DOMAIN = 1e-6, input_PHYSICAL_size = None, return_DOMAIN = True)
        
        curve_cells = list(dict.fromkeys(
            (r, c) for r, c in grid_hex_rc if (r, c) in hex_rc_arr))
        grids = [curve_cells]
        
        
    return grids

