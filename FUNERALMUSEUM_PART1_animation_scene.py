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

import ITEM_functions as ITEM_F
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
global_SNAPSHOT = int(ast.literal_eval(df.set_index('key').loc['1_2 n1 final_snapshot', 'value']))
dict_1_2_snapshot = global_SNAPSHOT - int(ast.literal_eval(df.set_index('key').loc['1_2 starting snapshot','value']))
        
dict_1_6_right_char = SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 0, '1_6 right char')
def draw_particular_scene(hex_rc_arr, hex_colors, detail_info, version):
    if version == '1_7 curve':
        curve_cells_1_7 = SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_7 curve')[0] 
        select_curve_cells_1_7 = cg.select_mask(curve_cells_1_7,hex_rc_arr)
        c0 = np.array(cgc.hex_to_rgb("#b56e10"))
        c1 = np.array(cgc.hex_to_rgb("#d6fff1"))
        
        min_col = min(c for r,c in curve_cells_1_7)
        max_col = max(c for r,c in curve_cells_1_7)


        curve_cells_1_7_COLORS = np.array([
            cgc.select_normal_color([True], c0 + (c1 - c0) * (c - min_col) / (max_col - min_col), np.ones(3) * sigma_color * 2.5)[0]
            for r, c in curve_cells_1_7
        ])

        alpha_span = [(c - min_col) / (max_col - min_col) for r, c in curve_cells_1_7]


        keys = [f"curve_1_7_{i}" for i in range(len(curve_cells_1_7))]
        colors = [[curve_cells_1_7_COLORS[i], f'alpha={alpha_span[i]}'] for i in range(len(curve_cells_1_7))]

        return {k: [[cell], c] for k, cell, c in zip(keys, curve_cells_1_7, colors)}
    elif version == '1_3':
        [Funeral_word, Museum_word, title_word_scene] = SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info, '1_3')
        
        Funeral_word_COLOR = [cgc.add_alpha(cgc.hex_to_rgb("#d6fff1"), 0.6), 'sigmafactor=3.']       
        Museum_word_COLOR = [cgc.add_alpha(cgc.hex_to_rgb("#a4beb5"), 0.6), 'sigmafactor=3.']       
        keys = ["Funeral_word", "Museum_word", ]
        colors = [Funeral_word_COLOR, Museum_word_COLOR]
        local_vars = locals()
        return {k: [local_vars[k], c] for k, c in zip(keys, colors)}
        
hex_colors = base_hex_colors.copy()
current_dict = {'wave bkgd':None,
            '1_2': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, dict_1_2_snapshot, '1_2'),
                 
                
                'wave add':None,
               "1_6 right sinking charS": SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 5, 
                                                                '1_6 right sinking char',other_info = dict_1_6_right_char),
                'CURVE': draw_particular_scene(hex_rc_arr, hex_colors, detail_info, '1_7 curve'),
                #'curve': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 500, '1_7 curve'),
                  '1_3': draw_particular_scene(hex_rc_arr, hex_colors, detail_info, '1_3'),
               }
for char, dict_ in current_dict.items(): 
        
    if char == 'wave bkgd':
        dict_ =SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 0, '2_0_shift', 
                                      other_info = [hex_colors, False, 50]  ) 
    if char == 'wave add':
        dict_ =SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, 90, '2_0_squeeze', 
                                      other_info = [hex_colors, True, 110]  )     
    for key in dict_.keys():
        part_RAW  = dict_.get(key)[0]
        part = [pt for pt in part_RAW if pt in hex_rc_arr]
        

        if len(part)==0:
            continue
        select_part= cg.select_mask(part,hex_rc_arr)
            
        colors = dict_.get(key)[1] 

        m = re.search(r"sigmafactor\s*=\s*([\d.]+)", str(colors))
        sigmafactor = float(m.group(1)) if m else 1.
        
        m_alpha = re.search(r"alpha\s*=\s*([\d.]+)", str(colors))
        alpha = float(m_alpha.group(1)) if m_alpha else 1.
        old_colors = hex_colors.copy()
    
        is_single_with_modifier = len(colors) == 2 and isinstance(colors[1], str) and ('sigmafactor' in colors[1] or 'alpha' in colors[1])

        is_striped = len(colors) == 3 and isinstance(colors[-1], str) and 'stripe' in colors[-1]
        if is_striped:
            stripe_target_colors = cgc.color_stripe(hex_rc_arr, STRIPE_WIDTH=1, 
                                                    STRIPE_PALETTE=[colors[0], colors[1]])
            hex_colors[select_part] =np.array([cgc.select_normal_color([True], c, np.ones(3)*sigma_color*sigmafactor)[0]
                                                  for c in stripe_target_colors[select_part] 
                                                 ])
            
            continue
        if len(colors) == 1 or is_single_with_modifier:
            hex_colors[select_part] = cgc.select_normal_color(select_part, colors[0], np.ones(3)*sigma_color*sigmafactor) 

        else:
            if len(colors) == len(hex_rc_arr):
                #FULLY DEFINED COLORS
                for idx in np.where(select_part)[0]:
                    hex_colors[idx] = cgc.select_normal_color([True], colors[idx], np.ones(3) * sigma_color*sigmafactor)[0]
            else:
                sort_info = colors[-1]
                if 'hex' in str(sort_info):
                    #print('sored by hex')

                    center =sort_info[0]
                    n_layers = sort_info[1]
                    start_n = sort_info[2]
                    end_n=sort_info[3]
                    if 'sigmoid' in str(sort_info):
                        mode = 'sigmoid'
                    else:
                        mode = 'linear'

                    #print(mode)
                    hex_colors = cgc.color_hex_gradient(part,colors[0],colors[1], hex_rc_arr, 
                            hex_colors, center, n_layers,
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
                    print('mode', mode)
                    hex_colors = cgc.color_row_gradient(part, 
                            colors[0],colors[1],
                            hex_rc_arr, hex_colors, sort = 'col', sigma_color = sigma_color*sigmafactor,
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

                    print('mode', mode, 'pivot', pivot)

                    hex_colors = cgc.color_row_gradient(part, 
                            colors[0],colors[1],
                            hex_rc_arr, hex_colors, sort = 'row', sigma_color = sigma_color*sigmafactor, 
                                                        end_weight= 0.01, mode = mode, pivot=pivot )
        
        hex_colors[select_part] = (alpha * hex_colors[select_part]) + ((1 - alpha) * old_colors[select_part])      
pc.set_facecolor(hex_colors)
pc = PatchCollection(patches, facecolor=hex_colors,
                        edgecolor='#bbba90', linewidth=0.4, zorder=z_order_max-1)
ax.add_collection(pc)
pc.set_facecolor(hex_colors)
OUTPUT_FOLDER = 'RESULT'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE   = os.path.join(OUTPUT_FOLDER, 'FUNERALMUSEUM_PART1_animation_scene.'+DOC)

plt.savefig(OUTPUT_FILE, dpi=DPI, bbox_inches='tight')
print('saved')
