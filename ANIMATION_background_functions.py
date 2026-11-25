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
import cg_anime_fn as cga

import cg_draw_figure as cgf


import re
import SCENE_animation_functions as SCENE_ANIME

import ITEM_functions as ITEM_F
import ITEM_animation_functions as ITEM_ANIME

import pandas as pd, ast
df = pd.read_csv('params.csv')

rng = np.random.default_rng(42)


def get_background_dict(hex_rc_arr, detail_info, hex_colors, version, other_info = None ):
    if '1_5' in version:
        
        global_SNAPSHOT = int(ast.literal_eval(df.set_index('key').loc['1_2 n1 final_snapshot', 'value']))
        
        
        dict_1_2_snapshot = global_SNAPSHOT - int(ast.literal_eval(df.set_index('key').loc['1_2 starting snapshot','value']))
        dict_1_1_snapshot = global_SNAPSHOT - int(ast.literal_eval(df.set_index('key').loc['1_1 starting snapshot','value']))
        
        full_1_2 = SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, dict_1_2_snapshot, '1_2')
        dict_1_2a = {k: v for k, v in full_1_2.items() if k in ('pillar','frame','photo')}
        dict_1_2b = {k: v for k, v in full_1_2.items() if k in ( 'body',)}
        char_dict_ =  {'1_1': SCENE_ANIME.draw_animation(hex_rc_arr, detail_info, dict_1_1_snapshot, '1_1'),
                       '1_2': dict_1_2a,
                       }  
   
        return char_dict_, dict_1_2b
    if version =='2_2 full':
        shift_up = int( other_info )
        [locs_dark_scene, locs_light_scene, river_line] = SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info,  '2_3 small' )
        dict_loc = {}    
        if shift_up>=river_line:
            dict_loc['sky'] = [hex_rc_arr, [[0,0,0]]]
        if shift_up>=0 and shift_up<=river_line:
            sky = [(r,c) for r,c in hex_rc_arr if r<= (river_line-shift_up)]
            
            dict_loc['sky'] = [sky, [cgc.hex_to_rgb("#e8dcf4")]]

            for loc in locs_dark_scene:
                loc_result = ITEM_ANIME.draw_papereffigies_anime(loc[0]-shift_up, loc[1], river_line-shift_up, 
                                                                 'small dark left', snapshot=0)
                for k, (value, color) in loc_result.items():
                    dict_loc[f"{loc}_{k}"] = [value, color]
            for loc in locs_light_scene:
                loc_result = ITEM_ANIME.draw_papereffigies_anime(loc[0]-shift_up, loc[1], river_line-shift_up, 
                                                                 'small dark left', snapshot=0)
                for k, (value, color) in loc_result.items():
                    dict_loc[f"{loc}_{k}"] = [value, color]

        return dict_loc
    if version =='2_2 sky':
        [_, _, river_line] = SCENE_ANIME.draw_animation_scene(hex_rc_arr, detail_info,  '2_3 small' )
        sky = [(r,c) for r,c in hex_rc_arr if r<=river_line]
        dict_loc = {}
        dict_loc['sky'] = [sky, [cgc.hex_to_rgb("#e8dcf4"),  'sigmafactor=0.2']]
        return dict_loc
            
    
def draw_animation_background(hex_rc_arr, detail_info, hex_colors, version, other_info = None ):
    sigma_color = ast.literal_eval(df.set_index('key').loc['sigma_color', 'value'])
    
    if '1_5' in version:
        char_dict_, _= get_background_dict(hex_rc_arr, detail_info, hex_colors, version, other_info = other_info)
    if '2_2' in version:
        char_dict_= {'2_2 full':get_background_dict(hex_rc_arr, detail_info, hex_colors, version, other_info = other_info)}
    for char, dict_ in char_dict_.items(): 
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

                        #print('mode', mode, 'pivot', pivot)

                        hex_colors = cgc.color_row_gradient(part, 
                                colors[0],colors[1],
                                hex_rc_arr, hex_colors, sort = 'row', sigma_color = sigma_color*sigmafactor, 
                                                            end_weight= 0.01, mode = mode, pivot=pivot )
            
            hex_colors[select_part] = (alpha * hex_colors[select_part]) + ((1 - alpha) * old_colors[select_part])
    #base_hex_colors = hex_colors.copy()
    return hex_colors

