import numpy as np
import matplotlib
import math
matplotlib.use('Agg')
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict, Counter
import astropy.units as u
import astropy.constants as const
from scipy.interpolate import interp1d
import os
import cg_plot_fn as cg
import cg_draw_fn as cgd
import cg_color_fn as cgc
import cg_draw_figure as cgf
import cg_anime_fn as cga
import SCENE_animation_functions as SCENE_ANIME
import ITEM_animation_functions as ITEM_ANIME
import ANIMATION_background_functions as ANIME_BKGD
import WAVEINTERFERENCE_animation_functions as WAVE_ANIME

import re

import pandas as pd, ast
df = pd.read_csv('params.csv')


rng = np.random.default_rng(42)

DOC = 'png'
if DOC == 'png':
    HEX_INDEX = False
elif DOC == 'pdf':
    HEX_INDEX = True
    
z_order_max = 5
DPI = 100

fig, ax, patches, hex_colors, hex_center_coords, hex_rc_arr, pc,detail_info = cg.make_hex_scene(
    IMG_W=1280, IMG_H=720, HEX_R=8, DPI=DPI, hex_index = HEX_INDEX, z_order_max = z_order_max)
IMG_W_SCENE, IMG_H_SCENE, HEX_R, dx_hex_center, dy_hex_center = detail_info

sigma_color = ast.literal_eval(df.set_index('key').loc['sigma_color', 'value'])

base_hex_colors = hex_colors.copy()
#------------------------SNAPSHOT PARAMS--------------------------
curve1_bkgd_colors = ANIME_BKGD.draw_animation_background(hex_rc_arr, detail_info, hex_colors, '1_5').copy()

_, dict_1_2b = ANIME_BKGD.get_background_dict(hex_rc_arr, detail_info, hex_colors, '1_5', other_info = None )

n_sweep_frames_1_2= SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_2 sweep left char',
                                                 other_info = dict_1_2b)[-1]
n_curve_cells_1_2 = len(SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_2 curve', 
                                                     other_info = None )[0])
n_travel_frames_1_2 =  SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_2 travel left char', 
                                                    other_info = [dict_1_2b, n_curve_cells_1_2])[-1]



dict_1_6_left_char = SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 
                                                int(ast.literal_eval(df.set_index('key').loc['1_6 left char terminal snapshot', 'value'])),
                                                '1_6 left char')
dict_1_6_right_char = SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 0, '1_6 right char')

n_sweep_frames_1_6= SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_6 sweep left char',
                                                          other_info = dict_1_6_left_char)[-1]
n_curve_cells_1_7 = len(SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_7 curve', other_info = None )[0])
n_travel_frames_1_6 =  SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_6 travel left char', 
                                             other_info = [dict_1_6_left_char, n_curve_cells_1_7])[-1]
n_reveal_frames_1_6= SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_6 reveal right char',
                                                      other_info = dict_1_6_right_char)[-1]


[_, _, N_total_bridge_reveal, N_total_ghosts_reveal, TRANSITION_END_ROW, _, ] = SCENE_ANIME.draw_animation_scene(hex_rc_arr, 
                                                                                                                 detail_info, '2_2')

total_frames_SQUEEZE = 110
total_frames_SQUARE = math.ceil((max(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr)) / 10) * 10
total_frames_SHIFT = total_frames_SQUARE//3
total_frames_transit = total_frames_SQUEEZE+total_frames_SQUARE+total_frames_SHIFT
total_frames_CONST = 100

[_, _, N_total_bridge_reveal, N_total_ghosts_reveal, _, _, ] = SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '2_2')

#_, grid_hex_rc = WAVE_ANIME.WAVE_anime(hex_rc_arr, detail_info, 'square')

#distance = TRANSITION_END_ROW - min(r for r, c in grid_hex_rc)
#TRANSITION_ROW_STEP = max(2, math.ceil(distance / total_frames_SHIFT / 2) * 2)
           
total_frames_TRANS = 50



#------ UPDATE PARAM-----------------------
LONGER_FACTOR = 1
sinking_LONGER_FACTOR = 5

Phase_1_1_start =0
Phase_1_2_start =12*LONGER_FACTOR
Phase_1_3_start =45*LONGER_FACTOR
Phase_1_4_1_start =Phase_1_3_start+100*LONGER_FACTOR 
Phase_1_4_2_start = Phase_1_4_1_start+int(ast.literal_eval(df.set_index('key').loc['wreath preshift', 'value']))*LONGER_FACTOR

Phase_pillar_stop = int(ast.literal_eval(df.set_index('key').loc['1_2 n1 final_snapshot', 'value']))*LONGER_FACTOR

Phase_curve_start_1_2 =Phase_pillar_stop+10#int(ast.literal_eval(df.set_index('key').loc['1_2 n1 final_snapshot', 'value']))*LONGER_FACTOR# 400 5
Phase_curve_end_1_2 = Phase_curve_start_1_2+n_curve_cells_1_2


Phase_sweep_start_1_2 = Phase_curve_start_1_2+15
Phase_sweep_end_1_2 = Phase_sweep_start_1_2+n_sweep_frames_1_2

Phase_travel_start_1_2 = Phase_sweep_end_1_2
Phase_travel_end_1_2 = Phase_travel_start_1_2+n_travel_frames_1_2

total_frames_tunneling_1_2 =max(Phase_travel_end_1_2, Phase_curve_end_1_2)
Phase_pillarleave_start = total_frames_tunneling_1_2-50*LONGER_FACTOR# personal choice

Phase_1_6_start = total_frames_tunneling_1_2
Phase_coffin_start = total_frames_tunneling_1_2+10   # personal choice


Phase_coffin_end = Phase_coffin_start+int(ast.literal_eval(df.set_index('key').loc['1_5 n0 final_snapshot', 'value'])+1)*LONGER_FACTOR

Phase_curve_start_1_7 = Phase_coffin_end
Phase_curve_end_1_7 = Phase_curve_start_1_7+n_curve_cells_1_7

Phase_sweep_start_1_6 = Phase_curve_start_1_7
Phase_sweep_end_1_6 = Phase_sweep_start_1_6+n_sweep_frames_1_6

Phase_travel_start_1_6 = Phase_sweep_end_1_6
Phase_travel_end_1_6 = Phase_travel_start_1_6+n_travel_frames_1_6

Phase_reveal_start_1_6 = Phase_curve_end_1_7
Phase_reveal_end_1_6 = Phase_reveal_start_1_6+n_reveal_frames_1_6
 
total_tunneling_frames_1_7 = max(Phase_travel_end_1_6, Phase_reveal_end_1_6)
    
Phase_up_pot_start = total_frames_tunneling_1_2+(Phase_travel_end_1_6-total_frames_tunneling_1_2)//2
Phase_down_pot_start = Phase_curve_start_1_7

Phase_SQUEEZE_start = total_tunneling_frames_1_7
Phase_SQUEEZE_end = Phase_SQUEEZE_start+total_frames_SQUEEZE

Phase_SQUARE_start = Phase_SQUEEZE_end
Phase_SQUARE_end = Phase_SQUARE_start+total_frames_SQUARE

Phase_TRANS_start = Phase_SQUARE_end
Phase_TRANS_end = Phase_TRANS_start+total_frames_TRANS


Phase_CONST_start = Phase_TRANS_end

Phase_bridge_ghost_start = Phase_CONST_start+10
Phase_bridge_ghost_end = Phase_bridge_ghost_start+N_total_bridge_reveal+N_total_ghosts_reveal

                                                    
Phase_small_moving_true = Phase_bridge_ghost_start+(Phase_bridge_ghost_end-Phase_bridge_ghost_start)//3*2

Phase_small_moving = 3
Phase_previous = Phase_small_moving_true-Phase_small_moving


snapshot_small_turning = 16

Phase_mid_growing = snapshot_small_turning
snapshot_mid_grow = 5
nth_mid_reveal_start = 2             # n = 2 is the third
extra_shift_mid_reveal_start = -10
snapshot_mid_reveal = snapshot_mid_grow+max(c for r,c in hex_rc_arr)*nth_mid_reveal_start+extra_shift_mid_reveal_start

Phase_mid_reveal_start = snapshot_mid_reveal
Phase_mid_end = Phase_mid_reveal_start+max(c for r,c in hex_rc_arr)

Phase_big_growing = Phase_mid_end-(max(c for r,c in hex_rc_arr)//5)
snapshot_big_grow = 5
nth_big_reveal_start = 1             # n = 2 is the third
extra_shift_big_reveal_start = +15
snapshot_big_reveal = snapshot_big_grow+max(c for r,c in hex_rc_arr)*nth_big_reveal_start+extra_shift_big_reveal_start
Phase_big_reveal_start = Phase_big_growing+snapshot_big_reveal
Phase_big_end = Phase_big_reveal_start+max(c for r,c in hex_rc_arr)-10


total_frames_CONST = Phase_big_end+Phase_previous-total_frames_TRANS-Phase_TRANS_start
Phase_CONST_end = Phase_CONST_start+total_frames_CONST

Phase_FINAL_start = Phase_CONST_end
total_frames_FINAL = 50
Phase_FINAL_end = Phase_FINAL_start+total_frames_FINAL


total_frames = Phase_FINAL_end

print('Phase_pillar_stop', Phase_pillar_stop, 
      'Phase_curve_end_1_2', Phase_curve_end_1_2, 
      'Phase_travel_end_1_2', Phase_travel_end_1_2,
     'total_frames_tunneling_1_2', total_frames_tunneling_1_2,
     'Phase_pillarleave_start', Phase_pillarleave_start,
      "Phase_curve_end_1_7", Phase_curve_end_1_7, 
      "Phase_travel_end_1_6", Phase_travel_end_1_6, 
      "total_tunneling_frames_1_7", total_tunneling_frames_1_7,
      "Phase_up_pot_start", Phase_up_pot_start, 
      'total_frames_SQUARE', total_frames_SQUARE,
 
      'Phase_CONST_start', Phase_CONST_start,
      'Phase_bridge_ghost_start', Phase_bridge_ghost_start,
      'Phase_bridge_ghost_end', Phase_bridge_ghost_end,
      'Phase_small_moving', Phase_small_moving,
      'Phase_mid_end', Phase_mid_end,
      'total_frames_CONST', total_frames_CONST,
     'total_frames', total_frames
     )

total_seconds =180.
print(total_seconds, total_frames)

def update(snapshot):
    
    print(snapshot)
    current_hex_colors = base_hex_colors.copy()
    
    if snapshot<=total_frames_tunneling_1_2:
        if snapshot>=Phase_1_1_start:
            current_Phase_1_1_snapshot = (snapshot-Phase_1_1_start)//LONGER_FACTOR
            current_dict =  {'1_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_1_snapshot, '1_1')}

        if snapshot>=Phase_1_2_start:
            current_Phase_1_2_snapshot = (snapshot-Phase_1_2_start)//LONGER_FACTOR
            current_dict =  {'1_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_1_snapshot, '1_1'),
                          '1_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_2_snapshot, '1_2')
                          }
        if snapshot>=Phase_1_3_start: 
            current_Phase_1_3_snapshot = (snapshot-Phase_1_3_start)//LONGER_FACTOR
            current_dict =  {'1_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_1_snapshot, '1_1'),
                          '1_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_2_snapshot, '1_2'),
                           '1_3': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_3_snapshot, '1_3')
                          }
        if snapshot>=Phase_1_4_1_start:   
            current_Phase_1_4_1_snapshot = (snapshot-Phase_1_4_1_start)//LONGER_FACTOR
            current_dict =  {'1_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_1_snapshot, '1_1'),
                          '1_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_2_snapshot, '1_2'),
                           '1_3': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_3_snapshot, '1_3'),
                           '1_4_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_1_snapshot, '1_4_1')
                          }
        if snapshot>=Phase_1_4_2_start:
            current_Phase_1_4_2_snapshot = (snapshot-Phase_1_4_2_start)//LONGER_FACTOR
            current_dict =  {'1_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_1_snapshot, '1_1'),
                          '1_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_2_snapshot, '1_2'),
                           '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2')
                          }    
     
        if snapshot>=Phase_pillar_stop: #CURVE TRAVEL 1 
            current_hex_colors = curve1_bkgd_colors.copy()

            if snapshot<=Phase_curve_start_1_2:
                current_dict = {"body": dict_1_2b,
                               '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info,  current_Phase_1_4_2_snapshot, '1_4_2'),
                               }
            if snapshot>Phase_curve_start_1_2 and snapshot<=Phase_curve_end_1_2:
                #curve enter
                current_curve_snapshot_1_2 = snapshot - Phase_curve_start_1_2

                current_dict = {
                    "body": dict_1_2b,
                    'curve': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_curve_snapshot_1_2, '1_2 curve'),
                    '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info,  current_Phase_1_4_2_snapshot, '1_4_2'),
                               }

            if snapshot>Phase_sweep_start_1_2 and snapshot<=Phase_sweep_end_1_2:
                #left char sweep
                current_sweep_snapshot_1_2 = snapshot - Phase_sweep_start_1_2
                current_dict = {
                    "body sweep": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_sweep_snapshot_1_2, '1_2 sweep left char',
                                                                 other_info = dict_1_2b),
                    'curve': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_curve_snapshot_1_2, '1_2 curve'),
                    '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info,  current_Phase_1_4_2_snapshot, '1_4_2'),
                               }

            current_travel_snapshot_1_2 = snapshot - Phase_travel_start_1_2
            if snapshot>Phase_travel_start_1_2 and snapshot<=Phase_travel_end_1_2:   
                #left char travel
                curve_reveal_count_1_2 = min(max(snapshot - Phase_curve_start_1_2 + 1, 0), n_curve_cells_1_2)
                current_dict = {
                    "travel": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_travel_snapshot_1_2, '1_2 travel left char',
                                                         other_info = [dict_1_2b, curve_reveal_count_1_2]),
                  '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info,  current_Phase_1_4_2_snapshot, '1_4_2'),
                               }

            current_leave_snapshot = snapshot - Phase_pillarleave_start
            if snapshot>Phase_pillarleave_start:   

                current_full_1_2 = SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 
                                               ( Phase_pillar_stop-Phase_1_2_start+current_leave_snapshot)//LONGER_FACTOR, '1_2')
                current_dict = {

                    '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                                      (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1'),
                   '1_2': {k: v for k, v in current_full_1_2.items() if k in ('pillar','frame','photo')}, 

                    "travel": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_travel_snapshot_1_2, '1_2 travel left char',
                                                         other_info = [dict_1_2b, curve_reveal_count_1_2]),
                            '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info,  current_Phase_1_4_2_snapshot, '1_4_2'),
                               }
    elif snapshot>total_frames_tunneling_1_2 and snapshot<= total_tunneling_frames_1_7:#
        current_Phase_1_4_2_snapshot = (snapshot-Phase_1_4_2_start)//LONGER_FACTOR
    
        current_leave_snapshot = snapshot - Phase_pillarleave_start
        
        current_Phase_1_6_snapshot = (snapshot-Phase_1_6_start)//LONGER_FACTOR
        if snapshot>Phase_1_6_start:#Phase_1_6_start = total_frames_tunneling_1_2
            #left char enter
            current_dict =  {
               '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                                  (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1'),
               '1_6': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_6_snapshot, "1_6 left char"),
                '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info,  current_Phase_1_4_2_snapshot, '1_4_2'),
                          }
        
        current_Phase_coffin_snapshot = (snapshot-Phase_coffin_start)//LONGER_FACTOR
        if snapshot>Phase_coffin_start and snapshot<= Phase_coffin_end:
            #coffin pillar enter
            GAP = 20  # or 10
            alt = ((snapshot - Phase_coffin_start) // GAP) % 2
            label_1_1 = ['1_1', '1_1 flip'][alt]
            label_1_5 = ['1_5 up enter', '1_5 down enter'][alt]
            label_1_4_2 = ['1_4_2', '1_4_2 flip'][alt]

            current_dict =  {
                '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                           (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, label_1_1),
                '1_6': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_6_snapshot, "1_6 left char"),
                '1_5': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_Phase_coffin_snapshot, label_1_5, 
                                                  other_info = [current_Phase_coffin_snapshot]),

                '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, label_1_4_2),
                }

        
        current_curve_snapshot_1_7 = snapshot - Phase_curve_start_1_7
        if snapshot>Phase_curve_start_1_7 and snapshot<=Phase_curve_end_1_7:
            #curve start
            current_dict =  {
                '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                             (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
                '1_6': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_6_snapshot, "1_6 left char"),
                '1_5': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_Phase_coffin_snapshot, '1_5 down enter', 
                                                  other_info = [current_Phase_coffin_snapshot]),
                 '1_7  curve': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_curve_snapshot_1_7, '1_7 curve'),
                '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
                }

        if snapshot>Phase_sweep_start_1_6 and snapshot<=Phase_sweep_end_1_6:
            #left char sweep
            current_sweep_snapshot_1_6 = snapshot - Phase_sweep_start_1_6
            current_dict = {
                '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                            (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
                '1_5': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_Phase_coffin_snapshot, '1_5 down enter', 
                                                  other_info = [current_Phase_coffin_snapshot]),
                "1_6 sweep left char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_sweep_snapshot_1_6, 
                                                                  '1_6 sweep left char',
                                                             other_info = dict_1_6_left_char),
                 '1_7  curve': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_curve_snapshot_1_7, '1_7 curve'),
                '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
                           }
        
        curve_reveal_count_1_7 = min(max(snapshot - Phase_curve_start_1_7 + 1, 0), n_curve_cells_1_7)
        current_travel_snapshot_1_6 = snapshot - Phase_travel_start_1_6
        current_reveal_snapshot_1_6 = snapshot - Phase_reveal_start_1_6

        if snapshot>Phase_travel_start_1_6:   #(snapshot-Phase_coffin_start)//LONGER_FACTOR
            #left char travel
            
            if snapshot>=Phase_travel_start_1_6+(Phase_travel_end_1_6-Phase_travel_start_1_6)//2:#coffin pillar leave
                current_Phase_coffin_snapshot = snapshot-(Phase_travel_start_1_6+(Phase_travel_end_1_6-Phase_travel_start_1_6)//2)
                label_1_5 = '1_5 down leave'
            else:
                label_1_5 = '1_5 down enter'

            current_dict = {
                    '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                      (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
                    '1_5': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_Phase_coffin_snapshot, label_1_5, 
                                                      other_info = [current_Phase_coffin_snapshot]),
                    "1_6 travel left char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_travel_snapshot_1_6, 
                                                                       '1_6 travel left char',
                                                         other_info = [dict_1_6_left_char, curve_reveal_count_1_7]),
                    '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
                               }

            if snapshot>Phase_reveal_start_1_6 and snapshot<=Phase_reveal_end_1_6:   

                current_dict = {
                    '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                      (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
                    '1_5': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_Phase_coffin_snapshot, label_1_5, 
                                                      other_info = [current_Phase_coffin_snapshot]),
                    "1_6 travel left char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_travel_snapshot_1_6, 
                                                                       '1_6 travel left char',
                                                         other_info = [dict_1_6_left_char, curve_reveal_count_1_7]),
                    "1_6 reveal right char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_reveal_snapshot_1_6, 
                                                                        '1_6 reveal right char',
                                                         other_info = dict_1_6_right_char),
                     '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
                               }


            if snapshot>Phase_reveal_end_1_6:   
                current_dict = {
                '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                  (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
                '1_5': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_Phase_coffin_snapshot, label_1_5, 
                                                  other_info = [current_Phase_coffin_snapshot]),
                "1_6 travel left char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_travel_snapshot_1_6, 
                                                                   '1_6 travel left char',
                                                     other_info = [dict_1_6_left_char, curve_reveal_count_1_7]),
                 "1_6 reveal right char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_reveal_snapshot_1_6, 
                                                                    '1_6 reveal right char',
                                                     other_info = dict_1_6_right_char),
                 '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
                           }

            if snapshot>=Phase_travel_end_1_6:
                current_dict = {
                    '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                      (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
                     "1_6 reveal right char": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_reveal_snapshot_1_6, 
                                                                    '1_6 reveal right char',
                                                     other_info = dict_1_6_right_char),
                     '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
                               }
           
    elif snapshot>total_tunneling_frames_1_7 and snapshot<=Phase_SQUEEZE_end:#Phase_SQUEEZE_start = total_tunneling_frames_1_7
        current_leave_snapshot = snapshot - Phase_pillarleave_start
        current_Phase_1_4_2_snapshot = (snapshot-Phase_1_4_2_start)//LONGER_FACTOR
        
        #add wave and sinking after adding flower pot
        current_dict = {
            '1_1': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                              (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_1 flip'),
             '1_4_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_Phase_1_4_2_snapshot, '1_4_2 flip'),
           
          }
    
    elif snapshot>Phase_SQUARE_start and snapshot<=Phase_SQUARE_end:
        #PPL FLOWER
        stage1_end = (total_frames_SQUEEZE - 1)//10
        current_snapshot = snapshot-Phase_SQUARE_start
        current_sinking_snapshot_1_6 = stage1_end + current_snapshot//2
    
        bodydict_, char_dict_item = SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, current_snapshot, 
                                                               '2_1', other_info=[current_snapshot])
        
        current_dict_basic = { 'wave': None, 
                          "1_6 right sinking charS": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_sinking_snapshot_1_6, 
                                                                    '1_6 right sinking char',
                                                     other_info = dict_1_6_right_char),                 
                           }
        
        current_dict = {**current_dict_basic, **{'body': bodydict_}, **char_dict_item
                       }
        
     
    elif snapshot>=Phase_TRANS_start and snapshot<Phase_TRANS_end:
        current_dict = { 'wave': None, }
    
    elif snapshot>=Phase_CONST_start and snapshot<=total_frames:
        current_bridge_ghost_snapshot = max(snapshot-Phase_bridge_ghost_start, 0) 
        current_char_snapshot = max(snapshot - Phase_CONST_start, 0)//10
    
        if snapshot<=Phase_bridge_ghost_start:#constant 
            current_dict = {
                    'wave': None, 
                 'small': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 0, '2_3 small', 
                                                        other_info = [snapshot_small_turning]),
                  '2_4 char': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_char_snapshot, "2_4"),
                       }
        elif snapshot>Phase_bridge_ghost_start:#bridge start, small effigy static or move 
            if snapshot<Phase_previous:
                current_dict = {
                        'wave': None, 
                     'small': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 0, '2_3 small', 
                                                            other_info = [snapshot_small_turning]),

                    'bridge + ghosts': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_bridge_ghost_snapshot, '2_2'),
                     '2_4 char': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_char_snapshot, "2_4"),
                           }
            else:   
                snapshot_ = snapshot-Phase_previous
                current_small_snapshot = max(snapshot_ - Phase_small_moving, 0)
                current_mid_snapshot = max(snapshot_ - Phase_mid_growing, 0)
                #current_big_snapshot = max(snapshot - Phase_big_growing, 0)
                current_big_snapshot = min(max(snapshot_ - Phase_big_growing, 0), Phase_big_end - Phase_big_growing)

        
                if snapshot_<=Phase_mid_growing:
                    current_dict = {
                            'wave': None, 
                         'small': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_small_snapshot, '2_3 small', 
                                                                other_info = [snapshot_small_turning]),

                        'bridge + ghosts': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_bridge_ghost_snapshot, '2_2'),
                         '2_4 char': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_char_snapshot, "2_4"),
                               }
                elif snapshot_>Phase_mid_growing:
                    print('snapshot_mid_reveal', snapshot_mid_reveal, 'current_mid_snapshot', current_mid_snapshot)

                    if current_mid_snapshot<Phase_mid_reveal_start:
                        current_dict = { 'wave': None, 
                      'mid': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_mid_snapshot, '2_3 mid ', 
                                                          other_info = [snapshot_mid_grow, snapshot_mid_reveal]),
                        'small': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_small_snapshot, '2_3 small', 
                                                            other_info = [snapshot_small_turning]),
                         'bridge + ghosts': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_bridge_ghost_snapshot, '2_2'),
                                        '2_4 char': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_char_snapshot, "2_4"),}

                    else:#mid reveal
                        current_dict_raw = {

                        'mid': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_mid_snapshot, '2_3 mid ', 
                                                          other_info = [snapshot_mid_grow, snapshot_mid_reveal]),}
                        mid_dict = current_dict_raw['mid']

                        hair_back_keys = [k for k in mid_dict if k.endswith('_hair')]
                        hair_front_keys = [k for k in mid_dict if k not in hair_back_keys]

                        #put hair mid at back, then small, then reveal mid at top 
                        current_dict = {'wave': None, 
                           'mid hair back': {k: mid_dict[k] for k in hair_back_keys if k in mid_dict},
                            'small':SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_small_snapshot, '2_3 small', 
                                                            other_info = [snapshot_small_turning]),
                            'mid hair front': {k: mid_dict[k] for k in hair_front_keys if k in mid_dict},
                            'bridge + ghosts': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 
                                                                          current_bridge_ghost_snapshot, '2_2'),
                             '2_4 char': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_char_snapshot, "2_4"),
                        }

                if snapshot_>=Phase_big_growing:   

                    print('current_big_snapshot', current_big_snapshot, 'Phase_big_growing', Phase_big_growing, )
                    big_dict = SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_big_snapshot, '2_3 big ', 
                                                                  other_info = [snapshot_big_grow, snapshot_big_reveal])
                    current_dict['big'] = big_dict 
        
    current_leave_snapshot = snapshot - Phase_pillarleave_start
    current_Phase_1_4_2_snapshot = (snapshot-Phase_1_4_2_start)//LONGER_FACTOR
                
    if snapshot>=Phase_down_pot_start and snapshot<=Phase_SQUEEZE_end:
        #add to 1_1  end at squeeze end
        current_flower_down_snapshot = snapshot-Phase_down_pot_start
        add_current_dict_down = {'flower pot side': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                     (Phase_pillar_stop-Phase_1_1_start+current_leave_snapshot)//LONGER_FACTOR, '1_9 flip', 
                                     other_info=[current_flower_down_snapshot, current_flower_down_snapshot+5,
                                                current_flower_down_snapshot, current_flower_down_snapshot+5]),}
        current_dict.update(add_current_dict_down)
    if snapshot>=Phase_up_pot_start and snapshot<=Phase_SQUEEZE_end:
        #add to 1_4_2, end at squeeze end
        current_flower_up_snapshot = snapshot-Phase_up_pot_start
        add_current_dict_up = {'flower pot top': SCENE_ANIME.draw_animation(hex_rc_arr,  detail_info, 
                                     current_Phase_1_4_2_snapshot, '1_8 flip', 
                                                             other_info=[current_flower_up_snapshot, current_flower_up_snapshot+5]),}
        current_dict.update(add_current_dict_up)    
    
    if snapshot>Phase_SQUEEZE_start and snapshot<=Phase_SQUEEZE_end:#Phase_SQUEEZE_start = total_tunneling_frames_1_7
        current_sinking_snapshot_1_6 = (snapshot-total_tunneling_frames_1_7)//10
        #CHAR SINKING 
        add_current_dict_wave = {'wave': None, 
                        "1_6 right sinking charS": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_sinking_snapshot_1_6, 
                                                                '1_6 right sinking char',other_info = dict_1_6_right_char),}
        current_dict.update(add_current_dict_wave) 
        
        
    for char, dict_ in current_dict.items(): 
        if char == 'wave':
            if snapshot>Phase_SQUEEZE_start and snapshot<=Phase_SQUEEZE_end:
                current_wave_snapshot = snapshot-Phase_SQUEEZE_start
                total_frames_wave = total_frames_SQUEEZE
                wave_version = '2_0_squeeze'
                
            elif snapshot>Phase_SQUARE_start and snapshot<=Phase_SQUARE_end:
                current_wave_snapshot = snapshot-Phase_SQUARE_start
                total_frames_wave = total_frames_SQUARE
                wave_version = '2_0_square'
                
            elif snapshot>Phase_TRANS_start and snapshot<=Phase_TRANS_end:
                current_wave_snapshot = snapshot-Phase_TRANS_start
                total_frames_wave = total_frames_TRANS
                wave_version = '2_0_shift'
                
            elif snapshot>Phase_CONST_start and snapshot<=Phase_CONST_end:
                current_wave_snapshot = snapshot-Phase_CONST_start
                total_frames_wave = total_frames_CONST
                wave_version = '2_0_constant'
            elif snapshot>Phase_FINAL_start and snapshot<=total_frames:
                current_wave_snapshot = snapshot-Phase_FINAL_start
                total_frames_wave = total_frames_FINAL
                wave_version = '2_0_final'
                
            dict_ =SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, current_wave_snapshot, wave_version, 
                                              other_info = [current_hex_colors, False, total_frames_wave] ) 
        for key in dict_.keys():
            part_RAW  = dict_.get(key)[0]
            part = [pt for pt in part_RAW if pt in hex_rc_arr]
            
            if len(part)==0:
                pc.set_facecolor(current_hex_colors)
                continue
            select_part= cg.select_mask(part,hex_rc_arr)
                
            colors = dict_.get(key)[1] 

            m = re.search(r"sigmafactor\s*=\s*([\d.]+)", str(colors))
            sigmafactor = float(m.group(1)) if m else 1.
            
            m_alpha = re.search(r"alpha\s*=\s*([\d.]+)", str(colors))
            alpha = float(m_alpha.group(1)) if m_alpha else 1.
            old_colors = current_hex_colors.copy()
        
            is_single_with_modifier = len(colors) == 2 and isinstance(colors[1], str) and ('sigmafactor' in colors[1] or 'alpha' in colors[1])

            is_striped = len(colors) == 3 and isinstance(colors[-1], str) and 'stripe' in colors[-1]
            if is_striped:
                stripe_target_colors = cgc.color_stripe(hex_rc_arr, STRIPE_WIDTH=1, 
                                                        STRIPE_PALETTE=[colors[0], colors[1]])
                current_hex_colors[select_part] =np.array([cgc.select_normal_color([True], c, np.ones(3)*sigma_color*sigmafactor)[0]
                                                      for c in stripe_target_colors[select_part] 
                                                     ])
                
                pc.set_facecolor(current_hex_colors)
                continue
            if len(colors) == 1 or is_single_with_modifier:
                current_hex_colors[select_part] = cgc.select_normal_color(select_part, colors[0], np.ones(3)*sigma_color*sigmafactor) 

            else:
                if len(colors) == len(hex_rc_arr):
                    #FULLY DEFINED COLORS
                    for idx in np.where(select_part)[0]:
                        current_hex_colors[idx] = cgc.select_normal_color([True], colors[idx], np.ones(3) * sigma_color*sigmafactor)[0]
                else:
                    sort_info = colors[-1]
                    if 'hex' in str(sort_info):
                        print('sored by hex')

                        center =sort_info[0]
                        n_layers = sort_info[1]
                        start_n = sort_info[2]
                        end_n=sort_info[3]
                        if 'sigmoid' in str(sort_info):
                            mode = 'sigmoid'
                        else:
                            mode = 'linear'

                        print(mode)
                        current_hex_colors = cgc.color_hex_gradient(part,colors[0],colors[1], hex_rc_arr, 
                                current_hex_colors, center, n_layers,
                                sigma_color=sigma_color*sigmafactor, end_weight=0.01, period=None, mode=mode,
                                start_n=start_n, end_n=end_n)
                    elif 'col' in sort_info:
                        #print(key)
                        #print('col gradient')
                        if 'max' in sort_info:
                            pivot = 'max'
                        elif 'min' in sort_info:
                            pivot = 'min'
                        else:
                            pivot = None
                        if 'sigmoid' in sort_info:
                            mode = 'sigmoid'
                        else:
                            mode = 'linear'
                        #print('mode', mode)
                        current_hex_colors = cgc.color_row_gradient(part, 
                                colors[0],colors[1],
                                hex_rc_arr, current_hex_colors, sort = 'col', sigma_color = sigma_color*sigmafactor,
                                                            end_weight= 0.01, mode = mode, pivot=pivot ) 

                    else:
                        #print(key)
                        #print('row gradient')

                        if 'sigmoid' in sort_info:
                            mode = 'sigmoid'
                        else:
                            mode = 'linear'

                        if 'max' in sort_info:
                            pivot = 'max'
                        elif 'min' in sort_info:
                            pivot = 'min'
                        else:
                            pivot = None

                        #print('mode', mode, 'pivot', pivot)

                        current_hex_colors = cgc.color_row_gradient(part, 
                                colors[0],colors[1],
                                hex_rc_arr, current_hex_colors, sort = 'row', sigma_color = sigma_color*sigmafactor, 
                                                            end_weight= 0.01, mode = mode, pivot=pivot )
            
            current_hex_colors[select_part] = (alpha * current_hex_colors[select_part]) + ((1 - alpha) * old_colors[select_part])

            pc.set_facecolor(current_hex_colors)
    return (pc,)
 




FPS = (total_frames / (total_seconds * u.s))
time_gap = ((1 / FPS).to(u.ms)).value
ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=time_gap, blit=False)
# ── SAVE ──────────────────────────────────────────────────────────────────
OUTPUT_FOLDER = 'RESULT'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, 'FUNERALMUSEUM_PART1_animation.mp4')
 
print(f"Encoding {OUTPUT_FILE} ...")
writer = animation.FFMpegWriter(
    fps=float(FPS.value), codec='libvpx-vp9',
    extra_args=['-b:v', '0', '-crf', '33', '-deadline', 'good', '-cpu-used', '2'],
)
ani.save(OUTPUT_FILE, writer=writer, dpi=DPI)
print(f"Saved -> {OUTPUT_FILE}")
