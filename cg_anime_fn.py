import numpy as np
import matplotlib
import math
matplotlib.use('Agg')
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict
from types import SimpleNamespace

import astropy.units as u
import os
import cg_plot_fn as cg
import cg_draw_fn as cgd
import cg_color_fn as cgc
import expected_value as EXP

rng = np.random.default_rng(42)
def sweep_colored_cells(detail_info, pivot, final_line, colored_cells, snapshot, dtheta=6.0,
                         from_final_line=False, to_angle=0.0, invert=False):
    """
    Clock-hand sweep pivoting at `pivot`, two arms growing between a
    reference angle and a target angle (0=+X, 90=up, ccw positive; pixel-y
    increases downward so this is flipped internally).
 
    Call once with snapshot=None (colored_cells unused) to get back the
    total number of frames the sweep needs.
 
    Normal use -- ERASE everything except final_line (e.g. the left
    character sweeping down to a line): leave from_final_line/to_angle/invert
    at their defaults. Both arms start at to_angle (0=+X by default) and
    grow toward final_line's own angle; final_line's cells stay protected
    (always kept) the whole time; returns the cells NOT YET swept.
 
    Reveal use -- GROW OUTWARD from final_line instead (e.g. the right
    character growing out of a line): pass from_final_line=True, to_angle=
    the angle you want the arms to converge on instead (180=-X, say), and
    invert=True. Both arms now start AT final_line's own angle and grow
    toward to_angle; final_line's cells are still always included; returns
    the cells the sweep HAS reached (growing from nothing) instead of the
    cells it hasn't (shrinking from everything).
    """
    piv_x, piv_y = cg.hex_center_pixel(pivot[0], pivot[1], detail_info)
 
    # angle (standard math convention: 0=+x, 90=up, ccw positive; pixel-y
    # increases downward, so it's flipped) of every final_line cell, to get
    # the direction the sweep is anchored to
    final_line_angles = []
    for cell in final_line:
        if cell == pivot:
            continue
        cx, cy = cg.hex_center_pixel(cell[0], cell[1], detail_info)
        final_line_angles.append(math.degrees(math.atan2(-(cy - piv_y), cx - piv_x)))
    final_line_angle = float(np.mean(final_line_angles)) if final_line_angles else 90.0
    final_line_angle %= 360.0
 
    if from_final_line:
        reference_angle = final_line_angle
        target_angle = to_angle % 360.0
    else:
        reference_angle = to_angle % 360.0
        target_angle = final_line_angle
 
    ccw_total = (target_angle - reference_angle) % 360.0   # ccw distance from reference to target
    cw_total = (reference_angle - target_angle) % 360.0    # cw distance from reference to target
 
    if snapshot is None:
        n_frames = int(np.ceil(max(ccw_total, cw_total) / dtheta))
        print('reference_angle', reference_angle, '| target_angle', target_angle,
              '| ccw_total', ccw_total, '| cw_total', cw_total, '| n_frames', n_frames)
        return n_frames
 
    swept_ccw = min((snapshot + 1) * dtheta, ccw_total)
    swept_cw = min((snapshot + 1) * dtheta, cw_total)
 
    protected_cells = set(final_line)   # always included, regardless of invert
    remaining = []
    for cell in colored_cells:
        if cell in protected_cells:
            remaining.append(cell)
            continue
        cx, cy = cg.hex_center_pixel(cell[0], cell[1], detail_info)
        theta = math.degrees(math.atan2(-(cy - piv_y), cx - piv_x)) % 360.0
        ccw_dist = (theta - reference_angle) % 360.0
        cw_dist = (reference_angle - theta) % 360.0
        swept = (ccw_dist <= swept_ccw) or (cw_dist <= swept_cw)
        if invert:
            if swept:
                remaining.append(cell)
        else:
            if not swept:
                remaining.append(cell)
    return remaining


def reveal_rows(cells, snapshot, reverse=False):
    unique_rows = sorted(set(r for r, c in cells), reverse=reverse)
    n_visible = snapshot % (len(unique_rows) + 1)
    visible_rows = set(unique_rows[:n_visible])
    return [(r, c) for r, c in cells if r in visible_rows]

def reveal_cols(cells, snapshot, reverse=False):
    unique_cols = sorted(set(c for r, c in cells), reverse=reverse)
    n_visible = snapshot % (len(unique_cols) + 1)
    visible_cols = set(unique_cols[:n_visible])
    return [(r, c) for r, c in cells if c in visible_cols]


def reveal_hex(cells, snapshot, center, end_n, reverse=False, start_n=0):
    cell_set = set(cells)
    frontiers = []
    for n in range(start_n, end_n + 1):
        if n == 0:
            ring = [center] if center in cell_set else []
        else:
            _, frontier = cg.hex_neighbours_n(center[0], center[1], n=n, return_frontier=True)
            ring = [h for h in frontier if h in cell_set]
        frontiers.append(ring)   # included even if empty -- no inference, explicit range only
 
    if reverse:
        frontiers = frontiers[::-1]
 
    n_visible = snapshot % (len(frontiers) + 1)
    return [c for ring in frontiers[:n_visible] for c in ring]

def scroll_cols(cols_base, min_c, max_c, snapshot, draw_fn, draw_args, speed=1):
    span = max_c - min_c
    wrapped_cols = []
    for col0 in cols_base:
        parts = draw_fn(0, col0, *draw_args)
        obj_min_c = min(c for pts in parts for r, c in pts)
        left_offset = col0 - obj_min_c

        wrapped_obj_min_c = min_c + (obj_min_c - min_c - snapshot*speed) % span
        wrapped_cols.append(wrapped_obj_min_c + left_offset)
    return wrapped_cols

def scroll_drawn_grid(shape, min_c, max_c, snapshot, speed=1):
    period = max_c - min_c
    shifted = -snapshot*speed
    wrapped = min_c + (shifted - min_c) % period
    result = []
    for offset in (wrapped - period, wrapped, wrapped + period):
        result += [(r, c+offset) for r, c in shape]
    return result

def scroll_drawn_grid_pad(shape, anchor_c, min_c, max_c, width, snapshot, gap=0, speed=1):
    period = (max_c - min_c) + width + gap
    left_edge = max_c + width          # fixed starting position: fully off-screen right
    shifted = left_edge - snapshot*speed
    wrapped = min_c + (shifted - min_c) % period
    dc = wrapped - anchor_c
    result = []
    for offset in (dc-period, dc, dc+period):
        result += [(r, c+offset) for r, c in shape]
    return result

'''
def draw_scrolling_objects(rows, cols_base, draw_fn, draw_args, min_c, max_c, snapshot, speed=1):
    period = max_c - min_c
    results = None
    for row in rows:
        for col0 in cols_base:
            shifted = col0 - snapshot*speed
            wrapped = min_c + (shifted - min_c) % period  
            for col in (wrapped - period, wrapped, wrapped + period):
                parts = draw_fn(row, col, *draw_args)
                if results is None:
                    results = [[] for _ in parts]
                for acc, pts in zip(results, parts):
                    acc += pts
    return results
'''
def scroll_fill_band(hex_rc_arr, left_edge, width, min_c, max_c, snapshot, gap=0, speed=1):
    period = (max_c - min_c) + width + gap
    shifted = left_edge - snapshot*speed
    wrapped = min_c + (shifted - min_c) % period
    band = []
    for offset in (wrapped - period, wrapped, wrapped + period):
        band += [(r,c) for r,c in hex_rc_arr if offset < c < offset+width]
    return band
'''
def scroll_fill_band(left_edge, width, min_c, max_c, snapshot, speed=1):
    period = max_c - min_c
    shifted = left_edge - snapshot*speed
    band = []
    for edge in (shifted - period, shifted, shifted + period):
        band += [(r,c) for r,c in hex_rc_arr if edge < c < edge+width]
    return band
'''
