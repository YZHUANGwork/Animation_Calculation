import numpy as np
import matplotlib
import math
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.colors import LinearSegmentedColormap
import cg_plot_fn as cg
import expected_value as EXP
rng = np.random.default_rng(42)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    
def select_normal_color(select, rgb_mean, rgb_std):
    n_color  = sum(select)
    colors = np.column_stack([
    rng.normal(rgb_mean[0], rgb_std[0], n_color),
    rng.normal(rgb_mean[1], rgb_std[1], n_color),
    rng.normal(rgb_mean[2], rgb_std[2], n_color),
    ]).clip(0, 1)
    return colors


def select_uniform_color(select, rgb_start, rgb_end):
    n_color  = sum(select)
    colors = np.column_stack([
    rng.uniform(rgb_start[0], rgb_end[0], n_color),
    rng.uniform(rgb_start[1], rgb_end[1], n_color),
    rng.uniform(rgb_start[2], rgb_end[2], n_color),
    ]).clip(0, 1)
    return colors

def color_row_gradient(arr, color_i, color_f, hex_rc_arr, hex_colors, sort='row', sigma_color=0.03, end_weight=0.2,
                       period=None, mode='linear', pivot=None, pivot_scope='global'):
    """
    mode: 'sigmoid' (decay toward target) or 'linear' (straight interpolation).
    pivot: None = plain row/col bands. 'min'/'max' = band by distance from an edge instead.
    pivot_scope: 'per_row' = edge found separately per row/col. 'global' = one edge for the whole shape.
    """
    if pivot and pivot_scope == 'global':
        edge = (min if pivot == 'min' else max)(c if sort == 'col' else r for r, c in arr)
        key = (lambda r, c: abs(c - edge)) if sort == 'col' else (lambda r, c: abs(r - edge))

    elif pivot and pivot_scope == 'per_row':
        group_idc, offset_idc = (0, 1) if sort == 'col' else (1, 0)
        vals_by_group = {}
        for pt in arr:
            vals_by_group.setdefault(pt[group_idc], set()).add(pt[offset_idc])

        edge_for = {}
        for g, vals in vals_by_group.items():
            for v in vals:
                lo = v
                while (lo-1) in vals: lo -= 1
                hi = v
                while (hi+1) in vals: hi += 1
                edge_for[(g, v)] = (v - lo) if pivot == 'min' else (hi - v)

        key = (lambda r, c: edge_for[(r, c)]) if sort == 'col' else (lambda r, c: edge_for[(c, r)])

    else:
        key = (lambda r, c: r) if sort == 'row' else (lambda r, c: c)

    sorted_idc = sorted(set(key(r, c) for r, c in arr))
    n_steps = len(sorted_idc)

    if mode == 'sigmoid':
        Y = np.array([[1.0], [0.0]])
        X = cg.steps_to_Q(n_steps, end_weight=end_weight)
    elif mode != 'linear':
        raise ValueError(f"mode must be 'sigmoid' or 'linear', got {mode!r}")

    target = color_f
    color_A, color_B = color_i, color_f
    leg_start = 0
    leg_len = period if period else n_steps
    leg_idx = 0

    for step, i in enumerate(sorted_idc):
        if period and step > 0 and step % period == 0:
            color_i, target = target, color_i
            leg_start = step
            leg_len = min(period, n_steps - step)
            leg_idx += 1

        select = [(r,c) in arr and key(r, c) == i for r, c in hex_rc_arr]

        if mode == 'sigmoid':
            V_input = np.array([color_i,target])
            Color_output, _ = EXP.expected_value(X, Y, V_input)
            color_i = Color_output[0]
        else:
            color_start, color_end = (color_A, color_B) if leg_idx % 2 == 0 else (color_B, color_A)
            t = (step - leg_start) / max(leg_len - 1, 1)
            color_i = (1 - t) * np.array(color_start) + t * np.array(color_end)
    
        hex_colors[select] = select_normal_color(select, color_i, np.ones(3)*sigma_color)   
    
    return hex_colors


def color_hex_gradient(arr, color_i, color_f, hex_rc_arr, hex_colors, center, n_layers,
                        sigma_color=0.03, end_weight=0.2, period=None, mode='sigmoid',
                        start_n=0, end_n=None):
    """
    mode='sigmoid' (default, unchanged behavior) / mode='linear' -- same two
    modes as color_row_gradient, applied per hex ring instead of per row.
 
    start_n / end_n: which rings to include, instead of always starting at
    the center (n=0) and running to n_layers. end_n defaults to n_layers.
    e.g. start_n=2, end_n=5 skips the center and ring 1 entirely, and
    gradients only across rings 2-5.
    """
    row, col = center
    if end_n is None:
        end_n = n_layers
 
    frontiers = []
    for n in range(start_n, end_n + 1):
        if n == 0:
            ring = [center] if center in arr else []
        else:
            _, frontier = cg.hex_neighbours_n(row, col, n=n, return_frontier=True)
            ring = [h for h in frontier if h in arr]
        frontiers.append(ring)

    n_steps = len(frontiers)
 
    if mode == 'sigmoid':
        Y = np.array([[1.0], [0.0]])
        X = cg.steps_to_Q(n_steps, end_weight=end_weight)
    elif mode != 'linear':
        raise ValueError(f"mode must be 'sigmoid' or 'linear', got {mode!r}")
 
    target = color_f
    color_A, color_B = color_i, color_f   # fixed originals (linear mode only), same pattern as color_row_gradient
    leg_start = 0
    leg_len = period if period else n_steps
    leg_idx = 0
 
    for step, frontier in enumerate(frontiers):
        if period and step > 0 and step % period == 0:
            color_i, target = target, color_i   # sigmoid mode: unchanged swap behavior
            leg_start = step
            leg_len = min(period, n_steps - step)
            leg_idx += 1
 
        select = [(r,c) in frontier for r, c in hex_rc_arr]
 
        if mode == 'sigmoid':
            V_input = np.array([color_i, target])
            Color_output, _ = EXP.expected_value(X, Y, V_input)
            color_i = Color_output[0]
        else:   # linear -- always interpolate from the correct fixed endpoint, by leg parity
            color_start, color_end = (color_A, color_B) if leg_idx % 2 == 0 else (color_B, color_A)
            t = (step - leg_start) / max(leg_len - 1, 1)
            color_i = (1 - t) * np.array(color_start) + t * np.array(color_end)
 
        hex_colors[select] = select_normal_color(select, color_i, np.ones(3)*sigma_color)
 
    return hex_colors


def gradient_sequence_colors(n_steps, color_i, color_f, end_weight=0.2, period=None, mode='sigmoid'):
    
    if mode == 'sigmoid':
        Y = np.array([[1.0], [0.0]])
        X = cg.steps_to_Q(n_steps, end_weight=end_weight)
    elif mode != 'linear':
        raise ValueError(f"mode must be 'sigmoid' or 'linear', got {mode!r}")
 
    colors = np.zeros((n_steps, 3))
    target = color_f
    color_A, color_B = color_i, color_f
    leg_start = 0
    leg_len = period if period else n_steps
    leg_idx = 0
    c = color_i
 
    for step in range(n_steps):
        if period and step > 0 and step % period == 0:
            c, target = target, c
            leg_start = step
            leg_len = min(period, n_steps - step)
            leg_idx += 1
 
        if mode == 'sigmoid':
            V_input = np.array([c, target])
            Color_output, _ = EXP.expected_value(X, Y, V_input)
            c = Color_output[0]
        else:   # linear
            color_start, color_end = (color_A, color_B) if leg_idx % 2 == 0 else (color_B, color_A)
            t = (step - leg_start) / max(leg_len - 1, 1)
            c = (1 - t) * np.array(color_start) + t * np.array(color_end)
 
        colors[step] = c
 
    return colors

def add_alpha(color_def, alpha):
    if isinstance(color_def[-1], str):
        *colors, sort_info = color_def
        new_sort_info = f"{sort_info} alpha={alpha}"
        return colors + [new_sort_info]
    else:
        return list(color_def) + [f"alpha={alpha}"]
def keep_top_color(parts):
    seen, out = set(), {}
    for k in reversed(parts):
        pts, colors = parts[k]
        out[k] = [[p for p in pts if tuple(p) not in seen], colors]
        seen.update(map(tuple, pts))
    return dict(reversed(out.items()))

def desaturate_matrix(colors, amount=0.5):
    L = np.array([[0.299, 0.587, 0.114]] * 3)   # rank-1 luminance matrix
    M = (1 - amount) * np.eye(3) + amount * L
    return colors @ M.T

def stripe_color_at(row_i, col_i, STRIPE_WIDTH=1, STRIPE_PALETTE=[np.array([0.9, 0.9, 0.9]), hex_to_rgb("#3b6632")], row_range=None):
    
    stripe_idx = (col_i // STRIPE_WIDTH) % len(STRIPE_PALETTE)
    entry = STRIPE_PALETTE[stripe_idx]
    if row_range and isinstance(entry, (list, tuple)):
        t = (row_i - row_range[0]) / max(row_range[1] - row_range[0], 1)
        return (1-t)*np.array(entry[0]) + t*np.array(entry[1])
    return np.array(entry)

def color_stripe(hex_rc_arr, STRIPE_WIDTH = 1 ,STRIPE_PALETTE = [np.array([0.9, 0.9, 0.9]),hex_to_rgb("#3b6632"),]):
    row_range = (min(r for r,c in hex_rc_arr), max(r for r,c in hex_rc_arr))

    stripe_target_colors = np.zeros((len(hex_rc_arr), 3))
    for i, (row_i, col_i) in enumerate(hex_rc_arr):
        stripe_idx = (col_i // STRIPE_WIDTH) % len(STRIPE_PALETTE)
        entry = STRIPE_PALETTE[stripe_idx]
        if isinstance(entry, (list, tuple)):
            t = (row_i - row_range[0]) / max(row_range[1] - row_range[0], 1)
            stripe_target_colors[i] = (1-t)*np.array(entry[0]) + t*np.array(entry[1])
        else:
            stripe_target_colors[i] = entry
    return stripe_target_colors

'''
def stripe_color_at(col_i, STRIPE_WIDTH=1, STRIPE_PALETTE=[np.array([0.9, 0.9, 0.9]), hex_to_rgb("#3b6632")]):
    
    stripe_idx = (col_i // STRIPE_WIDTH) % len(STRIPE_PALETTE)
    return np.array(STRIPE_PALETTE[stripe_idx])

def color_stripe(hex_rc_arr, STRIPE_WIDTH = 1 ,STRIPE_PALETTE = [np.array([0.9, 0.9, 0.9]),hex_to_rgb("#3b6632"),]):
    #STRIPE_WIDTH = 1            
    #STRIPE_PALETTE = [
    #    np.array([0.9, 0.9, 0.9]),   
    #    cgc.hex_to_rgb("#3b6632"),  
    #]

    stripe_target_colors = np.zeros((len(hex_rc_arr), 3))
    for i, (row_i, col_i) in enumerate(hex_rc_arr):
        stripe_idx = (col_i // STRIPE_WIDTH) % len(STRIPE_PALETTE)
        stripe_target_colors[i] = STRIPE_PALETTE[stripe_idx]
    return stripe_target_colors
'''
