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
import expected_value as EXP

import re

import ITEM_functions as ITEM_F
import ITEM_animation_functions as ITEM_ANIME
import SCHRODINGER_animation_functions as SCH_ANIME
import WAVEINTERFERENCE_animation_functions as WAVE_ANIME
import ANIMATION_background_functions as ANIME_BKGD

import pandas as pd, ast
df = pd.read_csv('params.csv')

rng = np.random.default_rng(42)


def draw_animation_scene(hex_rc_arr, detail_info, version, other_info = None  ):
    if '1_1' in version:
        bodies_scene, photos_scene, frames_scene = [],[],[]
        step_mid = 16
        rows_mid = np.arange(min(r for r,c in hex_rc_arr), max(r for r,c in hex_rc_arr)//2, step_mid)
        cols_mid = np.arange(min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), step_mid)
               
        rows_small = np.arange(min(r for r,c in hex_rc_arr)+step_mid//2, max(r for r,c in hex_rc_arr)//2, step_mid)
        cols_small = np.arange(min(c for r,c in hex_rc_arr)+step_mid//2, max(c for r,c in hex_rc_arr), step_mid)
        
        
        for row_mid in rows_mid:
            for col_mid in cols_mid:
                body, photo, frame = ITEM_F.draw_photo(row_mid, col_mid, 'mid', flip = False)
                
                bodies_scene+=body
                photos_scene+=photo
                frames_scene+=frame
         
        for row_small in rows_small:
            for col_small in cols_small:
                body, photo, frame = ITEM_F.draw_photo(row_small, col_small, 'small', flip = False)
                bodies_scene+=body
                photos_scene+=photo
                frames_scene+=frame
        if version == '1_1':
            scene_list = [bodies_scene, photos_scene, frames_scene]
            
        elif version == '1_1 flip':
            flip_row = (min(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr))//2
            bodies_scene_flip = [(2*flip_row-r, c) for r,c in bodies_scene]  
            photos_scene_flip = [(2*flip_row-r, c) for r,c in photos_scene]  
            frames_scene_flip = [(2*flip_row-r, c) for r,c in frames_scene]  
            scene_list = [bodies_scene_flip, photos_scene_flip, frames_scene_flip]
        elif version == '1_1 center':
            scene_list = [rows_small, cols_small, rows_mid, cols_mid]
        elif version == '1_1 flip center':    
            flip_row = (min(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr))//2
            rows_small_flip = 2*flip_row -  rows_small  
            rows_mid_flip = 2*flip_row -  rows_mid  
            scene_list = [rows_small_flip, cols_small, rows_mid_flip, cols_mid]    
            
    elif version == '1_2':
        pillar_edges = ast.literal_eval(df.set_index('key').loc['1_2 pillar', 'value'])
        width = max(pillar_edges)-min(pillar_edges)
        
        pillar = [(r,c) for r,c in hex_rc_arr if c>min(pillar_edges) and c<max(pillar_edges)]
        pre_shift =max(c for r,c in hex_rc_arr) - min(pillar_edges)          # pushes the shape's start right to the edge
        pillar_scene = [(r, c+pre_shift) for r,c in pillar]
        
        center_loc = ast.literal_eval(df.set_index('key').loc['center_loc', 'value'])
        body, photo, frame = ITEM_F.draw_photo(center_loc[0]-20, center_loc[1], 'big', flip = False)
        body_scene  = [(r, c+pre_shift) for r,c in body]
        photo_scene = [(r, c+pre_shift) for r,c in photo]
        frame_scene = [(r, c+pre_shift) for r,c in frame]
        
        scene_list = [body_scene, photo_scene, frame_scene, pillar_scene, width]
    
    elif version == '1_2 curve':
        initial_pivot = (ast.literal_eval(df.set_index('key').loc['center_loc', 'value'])[0]-20, 
                 int(ast.literal_eval(df.set_index('key').loc['1_2 col_final', 'value'])))
        
        curve_cells_scene =ast.literal_eval(df.set_index('key').loc['1_2 curve_cells', 'value'])
        
        scene_list = [curve_cells_scene]
        
    elif version == '1_2 sweep left char':
        dict_left_char = other_info
        dtheta = ast.literal_eval(df.set_index('key').loc['dtheta', 'value'])

        initial_pivot = (ast.literal_eval(df.set_index('key').loc['center_loc', 'value'])[0]-20, 
                 int(ast.literal_eval(df.set_index('key').loc['1_2 col_final', 'value'])))
        final_lines_left = cgd.draw_slope_0p5_diagonal(initial_pivot[0], initial_pivot[1], 0,
                                                left_down=False, right_down=False, left_up=True, right_up=False)
        n_sweep_frames = cga.sweep_colored_cells(detail_info, initial_pivot, final_lines_left, None, None, dtheta=dtheta)
        
        flat_1_2_body_cells = [pt for key in dict_left_char for pt in dict_left_char[key][0]]
        final_line_kept_cells_left = [cell for cell in final_lines_left if cell in list(set(flat_1_2_body_cells))]
        
        piv_x, piv_y = cg.hex_center_pixel(initial_pivot[0], initial_pivot[1], detail_info)
        def _cell_dist_from_pivot(cell):
            r, c = cell
            cx, cy = cg.hex_center_pixel(r, c, detail_info)
            return (cx - piv_x) ** 2 + (cy - piv_y) ** 2
        final_line_kept_cells_left.sort(key=_cell_dist_from_pivot)
        if not final_line_kept_cells_left:
            curve_cells_scene =ast.literal_eval(df.set_index('key').loc['1_2 curve_cells', 'value'])
            final_line_kept_cells_left = curve_cells_scene[:1]
            
        scene_list = [initial_pivot, final_lines_left, dtheta, final_line_kept_cells_left, n_sweep_frames]
    elif  version == '1_2 travel left char':
        [dict_left_char, curve_reveal_count] = other_info
        final_line_kept_cells_left = draw_animation_scene(hex_rc_arr, detail_info, '1_2 sweep left char', dict_left_char)[3]
        curve_cells_scene_full = draw_animation_scene(hex_rc_arr, detail_info, '1_2 curve')[0]
        curve_cells_scene = curve_cells_scene_full[:curve_reveal_count]   # only what's actually been revealed so far
 
        combined_cells = list(reversed(final_line_kept_cells_left)) + curve_cells_scene
        len_final_left = len(final_line_kept_cells_left)
        travel_positions = (len(combined_cells) - len_final_left) + 1
 
        scene_list = [combined_cells, len_final_left, travel_positions]
    
    
    elif version == '1_3':
        word_top_row = max(r for r,c in hex_rc_arr)//3*2
        Funeral_loc = (max(r for r,c in hex_rc_arr)-3, 5)
        Funeral_dict = ITEM_F.draw_word(Funeral_loc, 'Funeral', word_top_row)
        Funeral_word_scene = [item for sublist in list(Funeral_dict.values())  for item in sublist] 
        
        Museum_loc = (max(r for r,c in hex_rc_arr)-8, max(c for r,c in Funeral_word_scene)+18)
        
        Museum_dict = ITEM_F.draw_word(Museum_loc, 'Museum', word_top_row)
        Museum_word_scene = [item for sublist in list(Museum_dict.values() )  for item in sublist] 
        
        title_word_scene = Funeral_word_scene+Museum_word_scene
        scene_list = [Funeral_word_scene, Museum_word_scene, title_word_scene]
        
    if '1_4' in version:
    
        step_wreath = 12
        wreaths_1, wreaths_2, wreaths_3 = [], [], []
        n_wreath = 5
        rows_wreath = np.arange(max(r for r,c in hex_rc_arr)//2+8, max(r for r,c in hex_rc_arr), step_wreath)
        cols_wreath = np.arange(min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), step_wreath)
        for r, row_wreath in enumerate(rows_wreath):
            if r %2==0:
                cols_wreath_modified = cols_wreath[::2]
            else:
                cols_wreath_modified = cols_wreath[1::2]
            
            for c, col_wreath in enumerate(cols_wreath_modified):
                
                
                wreath_1 = cg.hex_neighbours_n(row_wreath, col_wreath, n=n_wreath, keep_origin =False , return_frontier=True
                        )[-1]
                wreath_2 = cg.hex_neighbours_n(row_wreath, col_wreath, n=n_wreath-1, keep_origin =False , return_frontier=True
                        )[-1]
                wreath_3 = cg.hex_neighbours_n(row_wreath, col_wreath, n=n_wreath-3, keep_origin =False , return_frontier=True
                        )[-1]
                wreaths_1 += wreath_1
                wreaths_2 += wreath_2
                wreaths_3 += wreath_3
        
        if version == '1_4':
            scene_list = [wreaths_1, wreaths_2, wreaths_3]
            
        elif version == '1_4 flip':
            flip_row = (min(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr))//2
            wreaths_1_flip = [(2*flip_row-r, c) for r,c in wreaths_1]  
            wreaths_2_flip = [(2*flip_row-r, c) for r,c in wreaths_2]  
            wreaths_3_flip = [(2*flip_row-r, c) for r,c in wreaths_3]  
            scene_list = [wreaths_1_flip, wreaths_2_flip, wreaths_3_flip]
        elif version == '1_4 center':
            scene_list = [rows_wreath, cols_wreath]
        elif version == '1_4 flip center':    
            flip_row = (min(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr))//2
            rows_wreath_flip = 2*flip_row -  rows_wreath  
            #print("rows_wreath", rows_wreath, "rows_wreath_flip",  rows_wreath_flip)
            cols_wreath_flip = cols_wreath
            scene_list = [rows_wreath_flip, cols_wreath_flip]
            
    elif "1_5" in version:
        coffin_edges = ast.literal_eval(df.set_index('key').loc['1_5 coffin', 'value'])
        width = max(coffin_edges)-min(coffin_edges)
        
        coffin = [(r,c) for r,c in hex_rc_arr if c>min(coffin_edges) and c<max(coffin_edges)]
        #coffin_edges_scene = coffin_edges+pre_shift
        
        center_loc = ast.literal_eval(df.set_index('key').loc['center_loc', 'value'])
        flip_row = (min(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr))//2

        arrow_center_row = center_loc[0]-20-1
        arrow_center_col = int(np.mean([c for r,c in coffin if r==arrow_center_row] ))
       
        pre_shift =max(c for r,c in hex_rc_arr) - min(coffin_edges)          
        coffin_scene = [(r, c+pre_shift) for r,c in coffin]
        
        print('pre_shift', pre_shift)
        
        if 'up' in version:
            arrow_loc = (arrow_center_row,     arrow_center_col)
            
        elif 'down' in version:
            arrow_loc = (2*flip_row-arrow_center_row,     arrow_center_col)
        scene_list = [coffin_edges, arrow_loc, pre_shift]
            
            
    elif version == "1_6 left char" or version == "1_6 right char" or version == "1_6 right sinking char"  :
        curve_cells =ast.literal_eval(df.set_index('key').loc['1_5 curve_cells', 'value'])
        n_head = 3
        if 'left' in version:
            center_loc = curve_cells[0]

            head_center_row= center_loc[0] - n_head - n_head - n_head - n_head - n_head
            head_center_col= center_loc[1]- n_head- n_head- n_head+2
            
            char = ITEM_F.draw_mainchar(head_center_row, head_center_col, face_direction=None, version = '5')[0]
            pre_shift =max(c for r,c in char)-min(c for r,c in hex_rc_arr) 
            print('char pre_shift', pre_shift)


            scene_list = [char, pre_shift]
        elif 'right' in version:
            center_loc = curve_cells[-1]
            head_center_row = center_loc[0] - n_head - n_head - n_head - n_head+1
            head_center_col = center_loc[1]+ n_head+ n_head-1
            character_body, character_joints, head = ITEM_F.draw_mainchar(head_center_row, head_center_col, 
                                                                          face_direction='right', version = '3')
            
            scene_list = [character_body, character_joints, head]
            if 'sinking' in version:
                sinking_line = center_loc[0]
                scene_list = [character_body, character_joints, head, sinking_line]
                
    elif version == '1_6 sweep left char':
        dict_left_char = other_info
        dtheta = ast.literal_eval(df.set_index('key').loc['dtheta', 'value'])

        
        curve_cells_scene =ast.literal_eval(df.set_index('key').loc['1_5 curve_cells', 'value'])
        initial_pivot = curve_cells_scene[0]
        final_lines_left = cgd.verticle_line(initial_pivot[0], initial_pivot[1], 0, bend = 'left')
        n_sweep_frames = cga.sweep_colored_cells(detail_info, initial_pivot, final_lines_left, None, None, dtheta=dtheta)
        
        flat_1_2_body_cells = [pt for key in dict_left_char for pt in dict_left_char[key][0]]
        final_line_kept_cells_left = [cell for cell in final_lines_left if cell in list(set(flat_1_2_body_cells))]
        
        piv_x, piv_y = cg.hex_center_pixel(initial_pivot[0], initial_pivot[1], detail_info)
        def _cell_dist_from_pivot(cell):
            r, c = cell
            cx, cy = cg.hex_center_pixel(r, c, detail_info)
            return (cx - piv_x) ** 2 + (cy - piv_y) ** 2
        final_line_kept_cells_left.sort(key=_cell_dist_from_pivot)
        if not final_line_kept_cells_left:
            curve_cells_scene =ast.literal_eval(df.set_index('key').loc['1_5 curve_cells', 'value'])
            final_line_kept_cells_left = curve_cells_scene[:1]
            
        scene_list = [initial_pivot, final_lines_left, dtheta, final_line_kept_cells_left, n_sweep_frames]
    
    elif  version == '1_6 travel left char':
        [dict_left_char, curve_reveal_count] = other_info
        final_line_kept_cells_left = draw_animation_scene(hex_rc_arr, detail_info, '1_6 sweep left char', dict_left_char)[3]
        curve_cells_scene_full = draw_animation_scene(hex_rc_arr, detail_info, '1_7 curve')[0]
        curve_cells_scene = curve_cells_scene_full[:curve_reveal_count]   # only what's actually been revealed so far
 
        combined_cells = list(reversed(final_line_kept_cells_left)) + curve_cells_scene
        len_final_left = len(final_line_kept_cells_left)
        travel_positions = (len(combined_cells) - len_final_left) + 1
 
        scene_list = [combined_cells, len_final_left, travel_positions]
    elif  version == '1_6 reveal right char':
        
        dict_right_char = other_info
        dtheta = ast.literal_eval(df.set_index('key').loc['dtheta', 'value'])

        
        curve_cells_scene =ast.literal_eval(df.set_index('key').loc['1_5 curve_cells', 'value'])
        
        final_pivot = curve_cells_scene[-1]
        print(final_pivot, max(c for r,c in hex_rc_arr))
        final_lines_right = cgd.draw_slope_0p5_diagonal(final_pivot[0], final_pivot[1], 0,
                                                left_down=False, right_down=False, left_up=False, right_up=True)
 
        n_reveal_frames = cga.sweep_colored_cells(detail_info, final_pivot, final_lines_right, None, None, dtheta=dtheta,
                                           from_final_line=True, to_angle=180.0, invert=True)
 
        flat_1_6_body_cells = [pt for key in dict_right_char for pt in dict_right_char[key][0]]
        final_line_kept_cells_right = [cell for cell in final_lines_right if cell in list(set(flat_1_6_body_cells))]
 
        piv_x, piv_y = cg.hex_center_pixel(final_pivot[0], final_pivot[1], detail_info)
        def _cell_dist_from_pivot_right(cell):
            r, c = cell
            cx, cy = cg.hex_center_pixel(r, c, detail_info)
            return (cx - piv_x) ** 2 + (cy - piv_y) ** 2
        final_line_kept_cells_right.sort(key=_cell_dist_from_pivot_right)
        if not final_line_kept_cells_right:
            final_line_kept_cells_right = curve_cells_scene[-1:]
 
        scene_list = [final_pivot, final_lines_right, dtheta, final_line_kept_cells_right, n_reveal_frames]
    
    elif version == '1_7 curve':
        
        curve_cells_scene =ast.literal_eval(df.set_index('key').loc['1_5 curve_cells', 'value'])
        
        scene_list = [curve_cells_scene]
        
    
    
    elif "1_8" in version: #plant pot flower top
        source_version = version.replace('8','4')+' center'
        
        [center_rows, center_cols] = draw_animation_scene(hex_rc_arr, detail_info, source_version )
        #print(center_rows, center_cols)
        light_locs, dark_locs = [], []
        for r, center_row in enumerate(center_rows):
            center_cols_modified = center_cols[r % 2::2]
            for c, center_col_modified in enumerate(center_cols_modified):
                loc = (center_row, center_col_modified)
                (light_locs if (r + c) % 2 == 0 else dark_locs).append(loc)
       
        scene_list = [light_locs, dark_locs]
    
    elif "1_9" in version: #plant pot flower side and pot
        source_version = version.replace('9','1')+' center'
        
        [center_rows_flower, center_cols_flower, center_rows_pot, center_cols_pot] = draw_animation_scene(hex_rc_arr, detail_info, 
                                                                                                          source_version )
        
        light_flower_locs, dark_flower_locs = [], []
        for r, center_row_flower in enumerate(center_rows_flower):
            for c, center_col_flower in enumerate(center_cols_flower):
                loc_flower = (center_row_flower, center_col_flower)
                (light_flower_locs if (r + c) % 2 == 0 else dark_flower_locs).append(loc_flower)
        
        light_soil_locs, dark_soil_locs = [], []
        for r, center_row_pot in enumerate(center_rows_pot):
            for c, center_col_pot in enumerate(center_cols_pot):
                loc_pot = (center_row_pot, center_col_pot)
                (dark_soil_locs  if (r + c) % 2 == 0 else light_soil_locs).append(loc_pot)

                
        scene_list = [light_flower_locs, dark_flower_locs, light_soil_locs, dark_soil_locs]
    
    elif '2_0' in version:# wave superpose squeeze 
        total_frames = other_info
        if 'squeeze' in version: #transition background
            t_span = np.array([round(t, 5) for t in np.linspace(0, 15, total_frames)])
            alpha_span = np.linspace(0, 1, total_frames)
        elif 'square' in version:#solid background
            t_last_end = 15
            
            t_span = np.array([round(t, 5) for t in np.linspace(t_last_end, 45, total_frames)])
            alpha_span = np.ones(t_span.shape)

        elif 'shift' in version:#shift transition
            t_last_end = 45
            
            t_span = np.array([round(t, 5) for t in np.linspace(t_last_end, 55, total_frames)])
            alpha_span = np.ones(t_span.shape)
        elif 'constant' in version:#shift transition
            t_last_end = 55
            
            t_span = np.array([round(t, 5) for t in np.linspace(t_last_end, 100, total_frames)])
            alpha_span = np.ones(t_span.shape)
        elif 'final' in version:#shift transition
            t_last_end = 100
            
            t_span = np.array([round(t, 5) for t in np.linspace(t_last_end, 110, total_frames)])
            alpha_span = np.ones(t_span.shape)
        scene_list = [total_frames, t_span, alpha_span]

        
    elif '2_1' in version:#PPL FLOWER
        alpha = 0.8
        cols_raw = np.arange(min(c for r,c in hex_rc_arr)+10, max(c for r,c in hex_rc_arr)+10, 20)
        cols = cols_raw[0::2]
        flip_cols = cols_raw[1::2]
        scene_list = [cols, flip_cols, alpha]
    

    elif '2_2' in version:#bridge ghost
        river_line = max(r for r,c in hex_rc_arr)//3
        bridge_start_loc = (max(r for r,c in hex_rc_arr)//2, max(c for r,c in hex_rc_arr)//2)
        pillars, steps, bridge_line_left, bridge_line_right = ITEM_F.draw_bridge(bridge_start_loc[0], bridge_start_loc[1])
        
        N_pillars = len(set(r for r, c in pillars))
        N_bridge  = len(set(r for r, c in bridge_line_left))   # assumes left/right span the same rows
        N_steps   = len(set(c for r, c in steps))

        N_total_bridge_reveal = max(N_pillars, N_bridge, N_steps)
        
        bridge_raw = bridge_line_left+bridge_line_right
        ghosts_cols =np.arange(max(c for r,c in bridge_raw if r==river_line)+1, max(c for r,c in hex_rc_arr), 3)
        ghosts = ITEM_F.draw_ghosts(ghosts_cols, river_line, river_line-2)
        
        N_total_ghosts_reveal   = len(set(c for r, c in ghosts))
    
        scene_list = [bridge_start_loc, ghosts_cols, N_total_bridge_reveal, N_total_ghosts_reveal, river_line, bridge_raw, ]
    elif '2_3' in version:#papereffigies
        [bridge_start_loc, ghosts_cols, _, _, river_line, bridge_raw] = draw_animation_scene(hex_rc_arr, detail_info, '2_2' )
        if 'small' in version:
            head_center_rows = [river_line-10, 5]
            head_center_cols = np.arange(0, max(c for r,c in hex_rc_arr), 4)

            locs_dark , locs_light = [], []
            for r, head_center_row in enumerate(head_center_rows):
                head_center_cols_modified = head_center_cols[r % 2::2]

                if head_center_row == min(head_center_rows):
                    locs_dark += [(head_center_row, c) for c in head_center_cols_modified]
                if head_center_row == max(head_center_rows):
                    locs_light += [(head_center_row, c) for c in head_center_cols_modified]

            scene_list = [locs_dark, locs_light, river_line]
        elif 'mid' in version:
            loc_center = (-2, bridge_start_loc[1])
            scene_list = [loc_center, river_line]
        elif 'big' in version:
            loc_center = (0, bridge_start_loc[1])
            scene_list = [loc_center, river_line]
    elif  '2_4' in version:
        [bridge_start_loc, _, _, _, _, bridge_raw] = draw_animation_scene(hex_rc_arr, detail_info, '2_2' )
        head_start_loc = (max(r for r,c in hex_rc_arr)-15, 30)
        
        trajectory_part1 = cgd.draw_slope_0p5_diagonal(bridge_start_loc[0], bridge_start_loc[1], max(r for r,c in bridge_raw)+1, 
                                                       left_down=True, right_down=False, left_up=False, right_up=False)
        trajectory_part2 = cgd.draw_slope_1p5_diagonal(max(r for r,c in trajectory_part1), 
                                                       max(c for r,c in trajectory_part1 if r==max(r for r,c in trajectory_part1)), 
                                                       head_start_loc[0], 
                                                       left_down=True, right_down=False, left_up=False, right_up=False)
        trajectory_part3 = cgd.verticle_line(max(r for r,c in trajectory_part2), 
                                                       max(c for r,c in trajectory_part2 if r==max(r for r,c in trajectory_part2))
                                             , max(r for r,c in hex_rc_arr)+2, bend = 'left')
        trajectory = trajectory_part1+trajectory_part2+trajectory_part3
        trajectory_sorted = sorted(trajectory, key=lambda rc: -rc[0])
        
        scene_list = [trajectory_sorted]

       
    return scene_list

def draw_animation(hex_rc_arr, detail_info, snapshot, version, other_info = None ):
    if '1_1' in version:# mid small frame, photo
        
        bkgd = hex_rc_arr
        
        [bodies_scene, photos_scene, frames_scene] = draw_animation_scene(hex_rc_arr, detail_info, version )

        bodies = cga.scroll_drawn_grid(bodies_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), snapshot, speed=1)
        photos = cga.scroll_drawn_grid(photos_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), snapshot, speed=1)
        frames = cga.scroll_drawn_grid(frames_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), snapshot, speed=1)
        
        if version == '1_1':
            bkdg_COLOR = [[0.2,0.2,0.2], 'sigmafactor=0.2']

            bodies_COLOR = [[1,1,1]]
            photos_COLOR = [[0.3, 0.3, 0.3]]
            frames_COLOR = [cgc.hex_to_rgb("#c8c473")]       
        elif version == '1_1 flip':
            bkdg_COLOR = [[0., 0., 0.], 'sigmafactor=0.2']

            bodies_COLOR = [cgc.hex_to_rgb("#025771")] 
            photos_COLOR = [[1,0,0]]
            frames_COLOR = [cgc.hex_to_rgb("#13e7ae")] 
           
        keys = ["bkgd",  "frames","photos",  "bodies"]

        colors = [bkdg_COLOR, frames_COLOR,photos_COLOR, bodies_COLOR, ]
        
    elif version == '1_2':# pillar, big frame, photo
        [body_scene, photo_scene, frame_scene, pillar_scene, width] = draw_animation_scene(hex_rc_arr, detail_info, version)
        body_COLOR = [[1,1,1], 'sigmafactor=1.5']
        photo_COLOR = [[0.3, 0.3, 0.3], 'sigmafactor=1.2']
        frame_COLOR = [cgc.hex_to_rgb("#c8c473"), 'sigmafactor=1.2']       
        
        padded_max_c = max(c for r,c in hex_rc_arr) + width + width   # <-- this was missing

        pillar = cga.scroll_drawn_grid(pillar_scene, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
        body = cga.scroll_drawn_grid(body_scene, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
        photo = cga.scroll_drawn_grid(photo_scene, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
        frame = cga.scroll_drawn_grid(frame_scene, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
        pillar_COLOR = [[0,0,0], 'sigmafactor=0.2']
        
        keys = ["pillar", "frame","photo",  "body"
               ]
        
        colors = [pillar_COLOR,frame_COLOR,photo_COLOR, body_COLOR, ]
    
    elif version == '1_2 curve':
        
        [curve_cells_scene] = draw_animation_scene(hex_rc_arr, detail_info, version )
        
        visible_curve_cells = curve_cells_scene[:snapshot + 1]
        visible_curve_cells_COLOR = [[1,1,1], cgc.hex_to_rgb("#b56e10"), 'sigmafactor=2.5', 'col']       
        keys = ["visible_curve_cells"
               ]
        
        colors = [visible_curve_cells_COLOR]
        
    elif version == '1_2 sweep left char':
        dict_left_char = other_info
        [initial_pivot, final_lines_left, dtheta, _, _] = draw_animation_scene(hex_rc_arr, detail_info, version, dict_left_char )
 
        keys = []
        colors = []
        for key in dict_left_char.keys():
            part = dict_left_char.get(key)[0]
            part_colors = dict_left_char.get(key)[1]
            remaining_part = cga.sweep_colored_cells(
                        detail_info, initial_pivot, final_lines_left, part, snapshot, dtheta=dtheta)
            exec(f"{key}_remaining = remaining_part")
            keys.append(key + '_remaining')
            colors.append(part_colors)
    elif  version== '1_2 travel left char':
        [combined_cells, len_final_left, travel_positions] = draw_animation_scene(hex_rc_arr, detail_info, version, other_info)
 
        start_idx = min(snapshot, travel_positions - 1)
        traveling_cells = combined_cells[start_idx: start_idx + len_final_left]
        remaining_curve_cells = combined_cells[start_idx + len_final_left:] 
 
        keys = ["remaining_curve_cells", "traveling_cells"]
        colors = [[[1,1,1], cgc.hex_to_rgb("#b56e10"), 'sigmafactor=2.', 'col']     , [[1,1,1]]]

        
    elif version == '1_3':# title
        [Funeral_word_scene, Museum_word_scene, title_word_scene] = draw_animation_scene(hex_rc_arr, detail_info, version)
        pre_shift = max(c for r,c in hex_rc_arr) - min(c for r,c in title_word_scene)
        Funeral_word = [(r, c+pre_shift-snapshot) for r,c in Funeral_word_scene]
        Museum_word = [(r, c+pre_shift-snapshot) for r,c in Museum_word_scene]


        Funeral_word_COLOR = [[1,1,1], 'sigmafactor=2.']       
        Museum_word_COLOR = [cgc.hex_to_rgb("#c8c473"), 'sigmafactor=2.']       
        keys = ["Funeral_word", "Museum_word", ]
        
        colors = [Funeral_word_COLOR, Museum_word_COLOR]
    
    elif "1_4" in version:# wreaths
        if 'flip' in version:
            wreaths_1_COLOR = [cgc.hex_to_rgb("#8bffdf")]
            wreaths_2_COLOR = [[1,0,0]]
            wreaths_3_COLOR = [cgc.hex_to_rgb("#4ed5ff")]
            [wreaths_1_scene, wreaths_2_scene, wreaths_3_scene] = draw_animation_scene(hex_rc_arr, detail_info, "1_4 flip" )
            
        elif "flip" not in version:
            wreaths_1_COLOR = [cgc.hex_to_rgb("#ede995")]
            wreaths_2_COLOR = [[1,1,1]]
            wreaths_3_COLOR = [cgc.hex_to_rgb("#d6bf28")]
            [wreaths_1_scene, wreaths_2_scene, wreaths_3_scene] = draw_animation_scene(hex_rc_arr, detail_info, "1_4" )
        
        if  version== '1_4_1':
            wreaths_all_scene = wreaths_1_scene+wreaths_2_scene+wreaths_3_scene
            pre_shift = max(c for r,c in hex_rc_arr) - min(c for r,c in wreaths_all_scene)
            width = max(c for r,c in wreaths_all_scene) - min(c for r,c in wreaths_all_scene)
            print('width', width, "pre_shift", pre_shift)
            wreaths_1 = [(r, c+pre_shift) for r,c in wreaths_1_scene]
            wreaths_2 = [(r, c+pre_shift) for r,c in wreaths_2_scene]
            wreaths_3 = [(r, c+pre_shift) for r,c in wreaths_3_scene]

            padded_max_c = max(c for r,c in hex_rc_arr) + width + width

            wreaths_1_scroll = cga.scroll_drawn_grid(wreaths_1, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
            wreaths_2_scroll = cga.scroll_drawn_grid(wreaths_2, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
            wreaths_3_scroll = cga.scroll_drawn_grid(wreaths_3, min(c for r,c in hex_rc_arr), padded_max_c, snapshot, speed=1)
            keys = ["wreaths_1_scroll", "wreaths_2_scroll", "wreaths_3_scroll"]
        
        elif '1_4_2' in version:    
            wreaths_1 = cga.scroll_drawn_grid(wreaths_1_scene, 
                                              min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), snapshot, speed=1)
            wreaths_2 = cga.scroll_drawn_grid(wreaths_2_scene, 
                                              min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), snapshot, speed=1)
            wreaths_3 = cga.scroll_drawn_grid(wreaths_3_scene, 
                                              min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), snapshot, speed=1)
            keys = ["wreaths_1", "wreaths_2", "wreaths_3"]
        
        
        
        colors = [wreaths_1_COLOR,wreaths_2_COLOR, wreaths_3_COLOR ]
    
    elif '1_5' in version:# coffin
        [coffin_snapshot] = other_info
        if 'up' in version:
            [coffin_edges_scene, arrow_loc_scene, pre_shift]= draw_animation_scene(hex_rc_arr, detail_info, '1_5 up'  )
        elif 'down' in version:
            [coffin_edges_scene, arrow_loc_scene, pre_shift]= draw_animation_scene(hex_rc_arr, detail_info, '1_5 down' )
        
        if 'enter' in version:
            offset = max(pre_shift - snapshot, 0)
        elif 'leave' in version:
            shift_out = max(coffin_edges_scene) - min(c for r, c in hex_rc_arr) + 2
            offset = -min(snapshot, shift_out)
        print('offset', offset)
        arrow_loc = (arrow_loc_scene[0], arrow_loc_scene[1]+offset)
        
        coffin_edges = np.array(coffin_edges_scene)+offset
        if 'up' in version:
            dict_item = ITEM_ANIME.draw_coffin_anime(coffin_edges, arrow_loc, 'up', hex_rc_arr, snapshot=coffin_snapshot)
        elif 'down' in version:
            dict_item = ITEM_ANIME.draw_coffin_anime(coffin_edges, arrow_loc, 'down', hex_rc_arr, snapshot=coffin_snapshot)
            
        return dict_item
        
    elif version == "1_6 left char" or version == "1_6 right char" or version == "1_6 right sinking char"  :
        if 'left' in version:
            [left_char_scene, pre_shift]  = draw_animation_scene(hex_rc_arr, detail_info, version )
            left_char_COLOR = [cgc.hex_to_rgb("#dd8216"), 'sigmafactor=3.']
            left_char = [(r, c + min(snapshot - pre_shift, 0)) for r,c in left_char_scene]

            keys = ["left_char", ]
            colors = [left_char_COLOR,]
        elif 'right' in version:
            right_char_body_COLOR = [cgc.hex_to_rgb("#bdded3")]
            right_char_joints_COLOR = [cgc.hex_to_rgb("#95b2a9"), 'sigmafactor=1.5']
            right_char_head_COLOR = [cgc.hex_to_rgb("#adadad")]
            
            
            if "sinking" not in version:
                [right_char_body_scene, right_char_joints_scene, right_char_head_scene]=draw_animation_scene(hex_rc_arr, 
                                                                                                             detail_info, version)
                right_char_body = [(r, c+snapshot) for r,c in right_char_body_scene]
                right_char_joints = [(r, c+snapshot) for r,c in right_char_joints_scene]
                right_char_head = [(r, c+snapshot) for r,c in right_char_head_scene]

                keys = ["right_char_body", "right_char_joints", "right_char_head"]
                colors = [right_char_body_COLOR,right_char_joints_COLOR, right_char_head_COLOR]
            
            
            elif "sinking" in version:
                alpha = 0.4
                [right_char_body_scene, right_char_joints_scene, right_char_head_scene, sinking_line]=draw_animation_scene(hex_rc_arr, 
                                                                                                             detail_info, version)
                row_min = min(r for r, c in right_char_body_scene + right_char_joints_scene + right_char_head_scene)
                row_max = max(r for r, c in right_char_body_scene + right_char_joints_scene + right_char_head_scene)
                disappearing_line = row_max

                N_A = row_max - sinking_line              # Phase A: sweep transparency boundary down to the sinking line
                N_B = (row_max - row_min) + 1               # Phase B: shift down until everything passes the disappearing line

                snapshot_A = min(snapshot, N_A)
                snapshot_B = min(max(snapshot - N_A, 0), N_B)

                shift_down = snapshot_B
                threshold_row = row_max - snapshot_A   # settles at sinking_line_row once Phase A finishes
                
                right_char_body_shifted = [(r + shift_down, c) for r, c in right_char_body_scene]
                right_char_body_solid = [(r, c) for r, c in right_char_body_shifted if r < threshold_row]
                right_char_body_transparent = [(r, c) for r, c in right_char_body_shifted if threshold_row <= r < disappearing_line]

                right_char_joints_shifted = [(r + shift_down, c) for r, c in right_char_joints_scene]
                right_char_joints_solid = [(r, c) for r, c in right_char_joints_shifted if r < threshold_row]
                right_char_joints_transparent = [(r, c) for r, c in right_char_joints_shifted if threshold_row <= r < disappearing_line]
                
                wiggle_pattern = [0, -1, -2, -1]
                col_wiggle = wiggle_pattern[snapshot % 4]

                right_char_head_shifted = [(r + shift_down, c + col_wiggle) for r, c in right_char_head_scene]
                right_char_head_solid = [(r, c) for r, c in right_char_head_shifted if r < threshold_row]
                right_char_head_transparent = [(r, c) for r, c in right_char_head_shifted if threshold_row <= r < disappearing_line]
                
                right_char_body_TRANSCOLOR = cgc.add_alpha(right_char_body_COLOR, alpha)
                right_char_joints_TRANSCOLOR = cgc.add_alpha(right_char_joints_COLOR, alpha)
                right_char_head_TRANSCOLOR = cgc.add_alpha(right_char_head_COLOR, alpha)
                
                keys = ["right_char_body_solid", "right_char_joints_solid", "right_char_head_solid",
                       "right_char_body_transparent", "right_char_joints_transparent", "right_char_head_transparent"
                       ]
                colors = [right_char_body_COLOR,right_char_joints_COLOR, right_char_head_COLOR,
                         right_char_body_TRANSCOLOR, right_char_joints_TRANSCOLOR, right_char_head_TRANSCOLOR]
            
                
               
                
    elif version == '1_6 sweep left char':
        dict_left_char = other_info
        [initial_pivot, final_lines_left, dtheta, _, _] = draw_animation_scene(hex_rc_arr, detail_info, version, dict_left_char )
 
        keys = []
        colors = []
        for key in dict_left_char.keys():
            part = dict_left_char.get(key)[0]
            part_colors = dict_left_char.get(key)[1]
            remaining_part = cga.sweep_colored_cells(
                        detail_info, initial_pivot, final_lines_left, part, snapshot, dtheta=dtheta)
            exec(f"{key}_remaining = remaining_part")
            keys.append(key + '_remaining')
            colors.append(part_colors)
    elif  version== '1_6 travel left char':
        [combined_cells, len_final_left, travel_positions] = draw_animation_scene(hex_rc_arr, detail_info, version, other_info)
 
        start_idx = min(snapshot, travel_positions - 1)
        traveling_cells = combined_cells[start_idx: start_idx + len_final_left]
        remaining_curve_cells = combined_cells[start_idx + len_final_left:] 
 
        keys = ["remaining_curve_cells", "traveling_cells"]
        colors = [[cgc.hex_to_rgb("#b56e10"),cgc.hex_to_rgb("#bdded3"),  'sigmafactor=2.5', 'col']    , 
                  [cgc.hex_to_rgb("#b56e10")]]
    
    elif  version == '1_6 reveal right char':
        dict_right_char = other_info
        [final_pivot, final_lines_right, dtheta, _, _] = draw_animation_scene(hex_rc_arr, detail_info, version, dict_right_char)
 
        keys = []
        colors = []
        for key in dict_right_char.keys():
            part = dict_right_char.get(key)[0]
            
            part_colors = dict_right_char.get(key)[1]
            visible_part = cga.sweep_colored_cells(
                        detail_info, final_pivot, final_lines_right, part, snapshot, dtheta=dtheta,
                        from_final_line=True, to_angle=180.0, invert=True)
            exec(f"{key}_visible = visible_part")
            keys.append(key + '_visible')
            colors.append(part_colors)        
    elif version == '1_7 curve':
        
        [curve_cells_scene] = draw_animation_scene(hex_rc_arr, detail_info, version )
        
        visible_curve_cells = curve_cells_scene[:snapshot + 1]
        visible_curve_cells_COLOR = [cgc.hex_to_rgb("#b56e10"),cgc.hex_to_rgb("#bdded3"),  'sigmafactor=2.5', 'col']       
        keys = ["visible_curve_cells"
               ]
        
        colors = [visible_curve_cells_COLOR]
        
    elif "1_8" in version: #plant pot flower top
        light_sub_snapshot, dark_sub_snapshot = other_info
        [light_locs_scene, dark_locs_scene]= draw_animation_scene(hex_rc_arr, detail_info, version )
        
        light_locs = cga.scroll_drawn_grid(light_locs_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                                  snapshot, speed=1)
        dark_locs = cga.scroll_drawn_grid(dark_locs_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                                  snapshot, speed=1)
        
        
        dict_loc = {}
        for light_loc in light_locs:
            loc_result = ITEM_ANIME.draw_plant_pot_anime(light_loc[0], light_loc[1], "spider lily top white", snapshot=light_sub_snapshot)
            for k, (value, color) in loc_result.items():
                dict_loc[f"{light_loc}_{k}"] = [value, color]
        for dark_loc in dark_locs:
            loc_result = ITEM_ANIME.draw_plant_pot_anime(dark_loc[0], dark_loc[1], "spider lily top red", snapshot=dark_sub_snapshot)
            for k, (value, color) in loc_result.items():
                dict_loc[f"{dark_loc}_{k}"] = [value, color]
        
        return dict_loc
        
    elif "1_9" in version: #plant pot flower side body frame flip
        [light_flower_sub_snapshot, dark_flower_sub_snapshot, light_soil_sub_snapshot, dark_soil_sub_snapshot] = other_info
        [light_flower_locs_scene, dark_flower_locs_scene, light_soil_locs_scene, dark_soil_locs_scene] = draw_animation_scene(hex_rc_arr,
                                                                                                                              detail_info, 
                                                                                                                              version )
        light_flower_locs = cga.scroll_drawn_grid(light_flower_locs_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                                  snapshot, speed=1)
        dark_flower_locs = cga.scroll_drawn_grid(dark_flower_locs_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                                  snapshot, speed=1)
        light_soil_locs = cga.scroll_drawn_grid(light_soil_locs_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                                  snapshot, speed=1)
        dark_soil_locs = cga.scroll_drawn_grid(dark_soil_locs_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                                  snapshot, speed=1)
        
        dict_loc = {}
        for light_flower_loc in light_flower_locs:
            loc_result = ITEM_ANIME.draw_plant_pot_anime(light_flower_loc[0], light_flower_loc[1], 
                                                         "spider lily side white", snapshot=light_flower_sub_snapshot)
            for k, (value, color) in loc_result.items():
                dict_loc[f"{loc_result}_{k}"] = [value, color]
        
        for dark_flower_loc in dark_flower_locs:
            loc_result = ITEM_ANIME.draw_plant_pot_anime(dark_flower_loc[0], dark_flower_loc[1], 
                                                         "spider lily side red", snapshot=dark_flower_sub_snapshot)
            for k, (value, color) in loc_result.items():
                dict_loc[f"{dark_flower_loc}_{k}"] = [value, color]
        
        for light_soil_loc in light_soil_locs:
            loc_result = ITEM_ANIME.draw_plant_pot_anime(light_soil_loc[0], light_soil_loc[1], 
                                                         "spider lily pot white", snapshot=light_soil_sub_snapshot)
            for k, (value, color) in loc_result.items():
                dict_loc[f"{light_soil_loc}_{k}"] = [value, color]

                
        for dark_soil_loc in dark_soil_locs:
            loc_result = ITEM_ANIME.draw_plant_pot_anime(dark_soil_loc[0], dark_soil_loc[1], 
                                                         "spider lily pot red", snapshot=dark_soil_sub_snapshot)
            for k, (value, color) in loc_result.items():
                dict_loc[f"{dark_soil_loc}_{k}"] = [value, color]

        return dict_loc
    
    elif '2_0' in version: 
        [current_hex_colors, weight_by_value, total_frames] = other_info
        
        [total_frames, t_span, alpha_span] = draw_animation_scene(hex_rc_arr, detail_info, version, other_info = total_frames)
        if 'squeeze' in version:
            wave_version = 'squeeze'
            COLORMAP = [
                            (0.0,  '#000000'),  
                            (0.6, '#d10013'),
                            (0.8, '#ff0054'),
                            (0.85, '#60ffd4'),
                            (0.9, '#ffcfdf'), 
                            (0.95,  '#b0ffea'),
                            (1.0,  '#ffffff'), 
                        ]
        elif 'square' in version:
            wave_version = 'square'
            COLORMAP = [
                (0.0,  '#000000'),  
                (0.6, '#7d0035'),
                (0.8, '#d10013'),
                (0.85, '#60ffd4'),
                (0.9, '#ffcfdf'), 
                (0.95,  '#b0ffea'),
                (1.0,  '#ffffff'), 
            ]
            
        elif 'shift' in version:
            wave_version = 'square'
            COLORMAP = [
                (0.0,  '#000000'),  
                (0.6, '#7d0035'),
                (0.8, '#d10013'),
                (0.85, '#60ffd4'),
                (0.9, '#ffcfdf'), 
                (0.95,  '#b0ffea'),
                (1.0,  '#ffffff'), 
            ]
        elif 'constant' in version:
            wave_version = 'square'
            COLORMAP = [
                (0.0,  '#47001e'),  
                (0.6, '#5c0027'),
                (0.8, '#7d0035'),
                (0.85, '#577e73'),
                (0.9, '#a78792'), 
                (0.95,  '#8aa7a0'),#9ebeb7
                (1.0,  '#b0d5cc'), 
            ]
        elif 'final' in version:
            wave_version = 'square'
            COLORMAP = [
                (0.0,  '#47001e'),  
                (0.6, '#5c0027'),
                (0.8, '#7d0035'),
                (0.85, '#577e73'),
                (0.9, '#a78792'), 
                (0.95,  '#b0ffea'),#9ebeb7
                (1.0,  '#ffffff'), 
            ]
        current_ALPHA = alpha_span[min(snapshot, total_frames - 1)]
        current_TIME = t_span[min(snapshot, total_frames - 1)]
        
        WAVE, grid_hex_rc = WAVE_ANIME.WAVE_anime(hex_rc_arr, detail_info, wave_version)
        VALUE = WAVE.field_at(current_TIME).ravel()
        
        [_, _, river_line] = draw_animation_scene(hex_rc_arr, detail_info,  '2_3 small' )
        TRANSITION_END_ROW = river_line+1
        min_row_base = min(r for r, c in grid_hex_rc) 
        FINAL_OFFSET = (TRANSITION_END_ROW - min_row_base) // 2 * 2    
         
        if 'shift' in version:
            print(wave_version)
            SNAPSHOTS_PER_ROW_STEP = 1
            
            steps_taken = (snapshot - 0) // SNAPSHOTS_PER_ROW_STEP
            distance = TRANSITION_END_ROW - min_row_base
            TRANSITION_ROW_STEP = max(2, math.ceil(distance / total_frames / 2) * 2)
           
            
            offset = min(max(steps_taken, 0) * TRANSITION_ROW_STEP, FINAL_OFFSET)
            
            print(wave_version, version, offset)
            
            grid_hex_rc_input = [(r + offset, c) for r, c in grid_hex_rc] if offset > 0 else grid_hex_rc
            shift =  max(0, min(TRANSITION_END_ROW - min(r for r,c in grid_hex_rc_input), TRANSITION_END_ROW))
            blended_color = ANIME_BKGD.draw_animation_background(hex_rc_arr, detail_info, current_hex_colors, '2_2 full', 
                                                                 other_info = shift )
            
            print('TRANSITION_ROW_STEP', TRANSITION_ROW_STEP, 'shift', shift)
            
            select_part, blended_shifted = cg.average_grid_to_hex_scene(
                grid_hex_rc_input, hex_rc_arr, VALUE, current_hex_colors, COLORMAP, alpha=1.0, weight_by_value=False
                                                                )
            blended_color[select_part] = blended_shifted


            print('len(select_part)', len(select_part), 'len(blended_shifted)', len(blended_shifted), 'len(hex_rc_arr)', len(hex_rc_arr) )
            dict_loc = {'wave_'+str(round(current_TIME, 5)): [hex_rc_arr, blended_color]}
        elif 'constant' in version or 'final' in version:
            grid_hex_rc_terminal = [(r + FINAL_OFFSET, c) for r, c in grid_hex_rc] 
            blended_color = ANIME_BKGD.draw_animation_background(hex_rc_arr, detail_info, current_hex_colors, '2_2 sky', 
                                                                 other_info = None )
            
            
            select_part, blended_terminal = cg.average_grid_to_hex_scene(
                grid_hex_rc_terminal, hex_rc_arr, VALUE, current_hex_colors, COLORMAP, alpha=1.0, weight_by_value=False
                                                                )
            blended_color[select_part] = blended_terminal
            dict_loc = {'wave_'+str(round(current_TIME, 5)): [hex_rc_arr, blended_color]}
            
        else:

            select_part, blended_color = cg.average_grid_to_hex_scene(
                grid_hex_rc, hex_rc_arr,VALUE, current_hex_colors, COLORMAP, alpha=current_ALPHA, weight_by_value=weight_by_value)


            dict_loc = {'wave_'+str(round(current_TIME, 5)): [hex_rc_arr, blended_color]}
        return dict_loc
    
    elif '2_1' in version:#flower ppl
        [flower_snapshot]= other_info
        [body_cols, body_flip_cols, alpha]= draw_animation_scene(hex_rc_arr, detail_info,  version )
        body_COLOR =      cgc.add_alpha([np.array([0.2,0.2,0.2]),([0.1,0.1,0.1],cgc.hex_to_rgb("#a3ad54")), 'stripe'], alpha)
        body_flip_COLOR = cgc.add_alpha([np.array([0.2,0.2,0.2]),(cgc.hex_to_rgb("#a26c55"), [0.1,0.1,0.1]),'stripe'], alpha)
        
        row_snapshot = snapshot-max(r for r,c in hex_rc_arr)
        rowflip_snapshot = max(r for r,c in hex_rc_arr)+max(r for r,c in hex_rc_arr)-snapshot
        dict_item = {}
        char_dict_item = {}
        bodies, bodies_flip = [], []
        for c,col in enumerate(body_cols):
            body, locs = ITEM_F.draw_body_flower((row_snapshot, col), '7', flip=False)
            bodies+=body
            char_dict_item[f"ghost plant side up left_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('left leg')[0], locs.get('left leg')[1], "ghost plant side up left", snapshot=flower_snapshot)
            char_dict_item[f"ghost plant side down right_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('right leg')[0], locs.get('right leg')[1], "ghost plant side down right", snapshot=flower_snapshot)
            char_dict_item[f"ghost plant top_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('botton')[0], locs.get('botton')[1], "ghost plant top", snapshot=flower_snapshot+5)
            char_dict_item[f"jimsonweed side hand_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('left hand')[0], locs.get('left hand')[1], "jimsonweed side", snapshot=flower_snapshot)
            char_dict_item[f"jimsonweed side wrist_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('right wrist')[0], locs.get('right wrist')[1], "jimsonweed side", snapshot=flower_snapshot+5)
            char_dict_item[f"jimsonweed top_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('chest')[0], locs.get('chest')[1], "jimsonweed top", snapshot=flower_snapshot)
            
        for c,col in enumerate(body_flip_cols):
            body, locs = ITEM_F.draw_body_flower((rowflip_snapshot, col), '7', flip=True)
            bodies_flip+=body
            
            char_dict_item[f"ghost plant side up right_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('right arm')[0], locs.get('right arm')[1], "ghost plant side up right", snapshot=flower_snapshot)
            char_dict_item[f"ghost plant side down left_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('left arm')[0], locs.get('left arm')[1], "ghost plant side down left", snapshot=flower_snapshot)
            char_dict_item[f"ghost plant top flipped_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('chest')[0], locs.get('chest')[1], "ghost plant top", snapshot=flower_snapshot)
            char_dict_item[f"spider lily top_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('botton')[0], locs.get('botton')[1], "spider lily top", snapshot=flower_snapshot)
            char_dict_item[f"spider lily side foot_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('left foot')[0]-2, locs.get('left foot')[1], "spider lily side", snapshot=flower_snapshot)
            char_dict_item[f"spider lily side knee_{c}"] = ITEM_ANIME.draw_flower_anime(
                locs.get('right knee')[0], locs.get('right knee')[1], "spider lily side", snapshot=flower_snapshot+5)
            
        dict_item["bodies"] = [bodies, body_COLOR]
        dict_item["bodies_flip"] = [bodies_flip, body_flip_COLOR]
        return dict_item, char_dict_item
      
        
    elif '2_2' in version:#bridge ghost
        
        [bridge_start_loc, ghosts_cols, N_total_bridge_reveal, N_total_ghosts_reveal, river_line,_] = draw_animation_scene(hex_rc_arr, 
                                                                                                                           detail_info, 
                                                                                                                         version )
        if snapshot <=N_total_bridge_reveal:
            bridge_dict   = ITEM_ANIME.draw_bridge_anime(bridge_start_loc[0], bridge_start_loc[1], 'reveal', snapshot=snapshot)
        elif snapshot>N_total_bridge_reveal:
            bridge_dict = ITEM_ANIME.draw_bridge_anime(bridge_start_loc[0], bridge_start_loc[1], 'transparent', snapshot=snapshot)

        if snapshot <= N_total_bridge_reveal:
            ghost_dict = {}
        elif snapshot <= N_total_bridge_reveal + N_total_ghosts_reveal:
            ghost_dict = ITEM_ANIME.draw_ghost_anime(ghosts_cols, river_line, river_line-2, 'reveal',
                                                      snapshot=snapshot - N_total_bridge_reveal)
        else:
            ghost_dict = ITEM_ANIME.draw_ghost_anime(ghosts_cols, river_line, river_line-2, 'transparent', snapshot=snapshot)

        dict_item = {**bridge_dict, **ghost_dict}
        return dict_item
    
    elif  '2_3' in version:# effigy
        
        if 'small' in version:
            [reveal_start_snapshot]= other_info
            [locs_dark_scene, locs_light_scene, river_line] = draw_animation_scene(hex_rc_arr, detail_info,  '2_3 small' )
            dict_loc = {}
            locs_dark = cga.scroll_drawn_grid(locs_dark_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                              snapshot, speed=1)
            locs_light= cga.scroll_drawn_grid(locs_light_scene, min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                              snapshot, speed=1)

            sub_snapshot = max(snapshot - reveal_start_snapshot, 0)
            spacing = 2   # snapshots between each loc's start
            all_locs = [(loc, 'dark') for loc in locs_dark] + [(loc, 'light') for loc in locs_light]
            all_locs = [(loc, kind) for loc, kind in all_locs if min(c for r,c in hex_rc_arr) <= loc[1] <= max(c for r,c in hex_rc_arr)]
            
            all_locs_sorted = sorted(all_locs, key=lambda x: x[0][1])   # current column order, left to right
            
            
            for rank, (loc, kind) in enumerate(all_locs_sorted):
                loc_sub_snapshot = max(sub_snapshot - rank * spacing, 0)

                name = 'small dark left' if kind == 'dark' else 'small light right'
                loc_result = ITEM_ANIME.draw_papereffigies_anime(loc[0], loc[1], river_line, name, snapshot=loc_sub_snapshot)
                for k, (value, color) in loc_result.items():
                    dict_loc[f"{loc}_{k}"] = [value, color]
        
        elif 'mid' in version:
            [grow_start_snapshot, reveal_start_snapshot]= other_info
            [loc_center_scene, river_line] = draw_animation_scene(hex_rc_arr, detail_info,  version )
            min_c = min(c for r,c in hex_rc_arr)
            max_c = max(c for r,c in hex_rc_arr)

            if snapshot < reveal_start_snapshot:
                locs_center = cga.scroll_drawn_grid([loc_center_scene], min_c, max_c, snapshot, speed=1)
            else:
                locs_at_reveal = cga.scroll_drawn_grid([loc_center_scene], min_c, max_c, reveal_start_snapshot, speed=1)
                loc_visible = [(r, c) for r, c in locs_at_reveal if min_c <= c <= max_c][0]
                locs_center = [(loc_visible[0], loc_visible[1] - (snapshot - reveal_start_snapshot))]
    
    
            #locs_center= cga.scroll_drawn_grid([loc_center_scene], min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
            #                                  snapshot, speed=1)
            
            sub_snapshot_grow   = min(max(snapshot - grow_start_snapshot, 0), reveal_start_snapshot - grow_start_snapshot)
            sub_snapshot_reveal = max(snapshot - reveal_start_snapshot, 0)
            dict_loc = {}
            
            
            if snapshot < grow_start_snapshot:
                version_mid = 'mid grow'
                sub_snapshot = 0
            elif snapshot >= grow_start_snapshot and snapshot < reveal_start_snapshot:
                version_mid = 'mid grow'
                sub_snapshot = sub_snapshot_grow
                
            elif snapshot >= reveal_start_snapshot:
                version_mid = 'mid reveal'
                sub_snapshot = sub_snapshot_reveal
                print('version_mid', version_mid, 'sub_snapshot', sub_snapshot)
            for loc_center in locs_center:   
                loc_center_result = ITEM_ANIME.draw_papereffigies_anime(loc_center[0], loc_center[1], river_line, version_mid,
                                                                           snapshot=sub_snapshot)
                
                for k, (value, color) in loc_center_result.items():
                    dict_loc[f"{loc_center}_{k}"] = [value, color]
        elif 'big' in version:     
            [grow_start_snapshot, reveal_start_snapshot]= other_info
            [loc_center_scene, river_line] = draw_animation_scene(hex_rc_arr, detail_info,  version )
            
            locs_center= cga.scroll_drawn_grid([loc_center_scene], min(c for r,c in hex_rc_arr), max(c for r,c in hex_rc_arr), 
                                              snapshot, speed=1)
            sub_snapshot_grow   = min(max(snapshot - grow_start_snapshot, 0), reveal_start_snapshot - grow_start_snapshot)
            sub_snapshot_reveal = max(snapshot - reveal_start_snapshot, 0)
            dict_loc = {}
            
            
            if snapshot < grow_start_snapshot:
                version_big = 'big grow'
                sub_snapshot = 0
            elif snapshot >= grow_start_snapshot and snapshot < reveal_start_snapshot:
                version_big = 'big grow'
                sub_snapshot = sub_snapshot_grow
                
            elif snapshot >= reveal_start_snapshot:
                version_big = 'big reveal'
                sub_snapshot = sub_snapshot_reveal
                
            for loc_center in locs_center:   
                loc_center_result = ITEM_ANIME.draw_papereffigies_anime(loc_center[0], loc_center[1], river_line, version_big,
                                                                           snapshot=sub_snapshot)
                
                for k, (value, color) in loc_center_result.items():
                    dict_loc[f"{loc_center}_{k}"] = [value, color]
        
        return dict_loc 
   
    elif  '2_4' in version:# char moving
        alpha = 0.5
        [trajectory] =draw_animation_scene(hex_rc_arr, detail_info,  '2_4' )
        
        current_snapshot = min(snapshot, len(trajectory) - 1)
        current_loc = trajectory[current_snapshot]
        character_body, character_joints, head = ITEM_F.draw_mainchar(current_loc[0], current_loc[1], 
                                                                          face_direction='back', version = '3')
        transparent_line_start = max(r for r,c in character_body)
        terminal_line = trajectory[-1][0]
        rows_moved = trajectory[0][0] - current_loc[0]
        factor = 3   # every `factor` rows moved, transparent_line drops by 1
        transparent_line = max(transparent_line_start - rows_moved // factor, terminal_line)
        
        character_body_transparent   = [pt for pt in character_body if pt[0] > transparent_line]
        character_body_solid         = [pt for pt in character_body if pt[0] <= transparent_line]

        character_joints_transparent = [pt for pt in character_joints if pt[0] > transparent_line]
        character_joints_solid       = [pt for pt in character_joints if pt[0] <= transparent_line]

        head_transparent              = [pt for pt in head if pt[0] > transparent_line]
        head_solid                    = [pt for pt in head if pt[0] <= transparent_line]

        character_body_COLOR = [cgc.hex_to_rgb("#bdded3")]
        character_joints_COLOR =[cgc.hex_to_rgb("#95b2a9")]
        head_COLOR = [cgc.hex_to_rgb("#95b2a9")]
        
        character_body_TRANSCOLOR = cgc.add_alpha(character_body_COLOR, alpha)
        character_joints_TRANSCOLOR = cgc.add_alpha(character_joints_COLOR, alpha)
        head_TRANSCOLOR = cgc.add_alpha(head_COLOR, alpha)
        
        keys = ["character_body_solid", "character_joints_solid", "head_solid",
               "character_body_transparent", "character_joints_transparent", "head_transparent"
               ]
        colors = [character_body_COLOR,character_joints_COLOR, head_COLOR,
                 character_body_TRANSCOLOR, character_joints_TRANSCOLOR, head_TRANSCOLOR]
        
    if '1_5' not in version and "1_8" not in version and "1_9" not in version and "2_0" not in version and "2_2" not in version and "2_3" not in version  and "2_1" not in version:
        local_vars = locals()
        if "1_6 right sinking char" not in version:
            return {k: [local_vars[k], c] for k, c in zip(keys, colors)}
        else:
            return cgc.keep_top_color({k: [local_vars[k], c] for k, c in zip(keys, colors)})