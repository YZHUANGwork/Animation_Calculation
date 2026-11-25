import numpy as np
import matplotlib
import math
from collections import defaultdict
from types import SimpleNamespace

import os
import cg_plot_fn as cg
import astropy.units as u
import re

import ITEM_animation_functions as ITEM_ANIME
import SCHRODINGER_animation_functions as SCH_ANIME
import SCENE_animation_functions as SCENE_ANIME
import pandas as pd
rng = np.random.default_rng(42)

DOC = 'png'
if DOC == 'png':
    HEX_INDEX = False
elif DOC == 'pdf':
    HEX_INDEX = True
    
z_order_max = 5
DPI = 100
fig, ax, patches, hex_colors, hex_center_coords, hex_rc_arr, pc, detail_info = cg.make_hex_scene(
    IMG_W=1280, IMG_H=720, HEX_R=8, DPI=DPI, hex_index = HEX_INDEX, z_order_max = z_order_max)
IMG_W_SCENE, IMG_H_SCENE, HEX_R, dx_hex_center, dy_hex_center = detail_info
base_hex_colors = hex_colors.copy()
sigma_color = 0.05

center_loc = ((min(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr))//2, 
              (min(c for r,c in hex_rc_arr)+max(c for r,c in hex_rc_arr))//2)



params = {'HEX_R': HEX_R}
params['center_loc'] = center_loc
params['sigma_color'] = sigma_color
params['dtheta'] = 6.

#--------------1_4_2---------------------
[wreaths_1_scene, wreaths_2_scene, wreaths_3_scene] = SCENE_ANIME.draw_animation_scene(hex_rc_arr,detail_info, "1_4" )
wreaths_all_scene = wreaths_1_scene+wreaths_2_scene+wreaths_3_scene
pre_shift = max(c for r,c in hex_rc_arr) - min(c for r,c in wreaths_all_scene)
width = max(c for r,c in wreaths_all_scene) - min(c for r,c in wreaths_all_scene)
print('width', width, "pre_shift", pre_shift)        
params['wreath preshift'] = pre_shift

Phase_1_1_start =0

params['1_1 starting snapshot'] =  Phase_1_1_start


#--------------1_2---------------------

grids = SCH_ANIME.WAVE_anime(center_loc[0], center_loc[1], detail_info,hex_rc_arr,"tunneling right")
_, pillar_edges= grids

width = max(pillar_edges)-min(pillar_edges)
pre_shift =max(c for r,c in hex_rc_arr) - min(pillar_edges)          # pushes the shape's start right to the edge
padded_max_c = max(c for r,c in hex_rc_arr) + width + width   # <-- this was missing
period = padded_max_c - min(c for r,c in hex_rc_arr)   
min_c = min(c for r,c in hex_rc_arr)

col_final = 20
pre_shift = max(c for r,c in hex_rc_arr) - min(pillar_edges)
true_start_pos = pre_shift + center_loc[1]   # pillar's reference is center_loc's own column, not pillar_edges' midpoint

min_c = min(c for r,c in hex_rc_arr)
delta = (true_start_pos - col_final - min_c) % period
speed=1
starting_snapshot_1_2 = 12


grids = SCH_ANIME.WAVE_anime(center_loc[0]-20, col_final, detail_info,hex_rc_arr,"tunneling right")
curve_cells, _= grids

params['1_2 starting snapshot'] =  starting_snapshot_1_2
params['1_2 pillar'] =  pillar_edges
params['1_2 pillar width'] =  width
params['1_2 start_pos'] =  true_start_pos
params['1_2 padded_max_c'] =  padded_max_c
params['1_2 period'] =  period

params['1_2 col_final'] =  col_final
params['1_2 curve_cells'] =  curve_cells


params['1_2 n'+str(int(0))+' final_snapshot'] =  int(starting_snapshot_1_2 + delta/speed + 0*(period/speed)     )

params['1_2 n'+str(int(1))+' final_snapshot'] =  int(starting_snapshot_1_2 + delta/speed + 1*(period/speed)     )
params['1_2 n'+str(int(2))+' final_snapshot'] =  int(starting_snapshot_1_2 + delta/speed + 2*(period/speed)     )
params['1_2 n'+str(int(3))+' final_snapshot'] =  int(starting_snapshot_1_2 + delta/speed + 3*(period/speed)     )
params['1_2 curve_cells'] =  curve_cells

#--------------1_5---------------------
starting_snapshot_1_5 = 0
center_loc_coffin = (center_loc[0], col_final)
grids_FULLtunneling = SCH_ANIME.WAVE_anime(center_loc_coffin[0], center_loc_coffin[1], detail_info,hex_rc_arr,"full tunneling")
curve_cells_1_5, coffin_edges= grids_FULLtunneling


coffin_width = max(coffin_edges)-min(coffin_edges)
pre_shift_coffin =max(c for r,c in hex_rc_arr) - min(coffin_edges)          # pushes the shape's start right to the edge
padded_max_c_coffin = max(c for r,c in hex_rc_arr)# + coffin_width + coffin_width 
period_coffin = padded_max_c_coffin - min(c for r,c in hex_rc_arr)   
true_start_pos_coffin = pre_shift_coffin + min(coffin_edges)
        
delta_coffin = (true_start_pos_coffin - min(coffin_edges) - min_c) % period_coffin

params['1_5 center_loc_coffin'] =  center_loc_coffin
params['1_5 coffin'] =  coffin_edges
params['1_5 coffin width'] =  coffin_width
params['1_5 pre_shift_coffin'] =  pre_shift_coffin
params['1_5 period_coffin'] =  period_coffin
params['1_5 curve_cells'] =  curve_cells_1_5

params['1_5 n'+str(int(0))+' final_snapshot'] =  int(starting_snapshot_1_5 + delta_coffin/speed + 0*(period_coffin/speed)     )
params['1_5 n'+str(int(1))+' final_snapshot'] =  int(starting_snapshot_1_5 + delta_coffin/speed + 1*(period_coffin/speed)     )
params['1_5 n'+str(int(2))+' final_snapshot'] =  int(starting_snapshot_1_5 + delta_coffin/speed + 2*(period_coffin/speed)     )


#--------------1_6---------------------

[_, pre_shift]  = SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_6 left char' )
params['1_6 left char terminal snapshot'] =  pre_shift

# ── SAVE ──────────────────────────────────────────────────────────────────
OUTPUT_FOLDER = './'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, 'params.csv')

print(f"Writing {OUTPUT_FILE} ...")
pd.DataFrame(params.items(), columns=['key','value']).to_csv(OUTPUT_FILE, index=False)
print(f"Saved -> {OUTPUT_FILE}")