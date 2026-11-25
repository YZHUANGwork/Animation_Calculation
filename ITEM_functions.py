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
import cg_draw_figure as cgf
import expected_value as EXP

def draw_ghosts(ghosts_cols, top_line, bottom_line):
    ghosts = []
    
    for ghost_col in ghosts_cols:
        ghosts+= cgd.verticle_line(top_line, ghost_col, bottom_line, bend = 'left'
             )+cgd.verticle_line(top_line, ghost_col, bottom_line, bend = 'right'
             )
    return ghosts
    
def draw_coffin(coffin_edges, arrow_loc, hex_rc_arr, version):
    arrow = draw_arrow(arrow_loc[0], arrow_loc[1], 4, 1, 4, direction = version)
    coffin = [(r,c) for r,c in hex_rc_arr if c>min(coffin_edges) and c<max(coffin_edges)]
            
    if version=='up':
        coffin_left = [(r,c) for r,c in coffin if c<arrow_loc[1]-1]
        coffin_right = [(r,c) for r,c in coffin if (r,c) not in coffin_left]
    elif version=='down':
        coffin_right = [(r,c) for r,c in coffin if c>arrow_loc[1]+1]
        coffin_left = [(r,c) for r,c in coffin if (r,c) not in coffin_right]
                
    return arrow, coffin,coffin_left, coffin_right


def draw_bridge(bridge_start_row, bridge_start_col, pillar_height = 6):
    bridge_left_part0 = cgd.draw_slope_0p5_diagonal(bridge_start_row, bridge_start_col-10, bridge_start_row+6, 
                                                       left_down=True, right_down=False, left_up=False, right_up=False)
        
        
    bridge_left_part1 = cgd.draw_slope_1p5_diagonal(bridge_start_row, bridge_start_col-10, bridge_start_row-6, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                       )+cgd.draw_slope_1p5_diagonal(bridge_start_row, bridge_start_col-10+1, bridge_start_row-6, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                       )
    
    bridge_left_part2 = cgd.draw_slope_8p3_diagonal(min(r for r,c in bridge_left_part1), 
                                                   max(c for r,c in bridge_left_part1 if r==min(r for r,c in bridge_left_part1)),
                                                   min(r for r,c in bridge_left_part1)-5, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                       )+cgd.draw_slope_8p3_diagonal(min(r for r,c in bridge_left_part1), 
                                                   max(c for r,c in bridge_left_part1 if r==min(r for r,c in bridge_left_part1))+1,
                                                   min(r for r,c in bridge_left_part1)-5, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                       )+cgd.draw_slope_8p3_diagonal(min(r for r,c in bridge_left_part1), 
                                                   max(c for r,c in bridge_left_part1 if r==min(r for r,c in bridge_left_part1))+2,
                                                   min(r for r,c in bridge_left_part1)-5, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                       )
    
    bridge_right_part0 = cgd.verticle_line(bridge_start_row, bridge_start_col+10, bridge_start_row+6, bend = 'right')

    
    bridge_right_part1 = cgd.draw_slope_0p5_diagonal(bridge_start_row, bridge_start_col+10, bridge_start_row-6, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True)
    bridge_right_part2 = cgd.draw_slope_1p5_diagonal(min(r for r,c in bridge_right_part1), 
                                                   max(c for r,c in bridge_right_part1 if r==min(r for r,c in bridge_right_part1)),
                                                   min(r for r,c in bridge_right_part1)-5, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                         )+cgd.draw_slope_1p5_diagonal(min(r for r,c in bridge_right_part1), 
                                                   max(c for r,c in bridge_right_part1 if r==min(r for r,c in bridge_right_part1))+1,
                                                   min(r for r,c in bridge_right_part1)-5, 
                                                   left_down=False, right_down=False, left_up=False, right_up=True
                         )
    
    
    bridge_line_left = bridge_left_part0+bridge_left_part1+bridge_left_part2
    bridge_line_right = bridge_right_part0+bridge_right_part1+bridge_right_part2
    
    pillar_rows = [min(r for r,c in bridge_line_right)+1,
                   min(r for r,c in bridge_line_right)+2,
                   min(r for r,c in bridge_line_right)+4, 
                   min(r for r,c in bridge_line_right)+7,
                  min(r for r,c in bridge_line_right)+8]
    pillars = []
    for pillar_row in pillar_rows:
        pillars+=cgd.verticle_line(pillar_row, 
                                max(c for r,c in bridge_line_right if r==pillar_row), 
                                pillar_row+pillar_height, bend = 'left'
             )
    sorted_bridge_line_left = sorted({r: max(c for q, c in bridge_line_left if q == r) for r, c in bridge_line_left}.items())
    
    sorted_bridge_line_right = sorted({r: min(c for q, c in bridge_line_right if q == r) for r, c in bridge_line_right}.items())
    
    steps = cgd.horizontal_lines([( r1, (c1+5, c2)) 
                                        for (r1, c1), (r2, c2) in zip(sorted_bridge_line_left, sorted_bridge_line_right) 
                                  if r1 % 2 == 1])
    
          
    return pillars, steps, bridge_line_left, bridge_line_right


    
def draw_papereffigies(head_center_row, head_center_col, bottom_line, version ):
    if 'small' in version:
        n_size = 1
        head = cg.hex_neighbours_n(head_center_row, head_center_col, n=n_size)
        hair_part1 = cgd.draw_trapezoid(min(r for r,c in head), 
                                        min(c for r,c in head if r==min(r for r,c in head)), 
                                        max(c for r,c in head if r==min(r for r,c in head)), 
                                        head_center_row+n_size, 
                                   slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right')[-2]
        hair_part2 = cgd.draw_trapezoid(max(r for r,c in hair_part1), 
                                        min(c for r,c in hair_part1 if r==max(r for r,c in hair_part1)), 
                                        max(c for r,c in hair_part1 if r==max(r for r,c in hair_part1)),  bottom_line, 
                                   slope_left = 'inf', slope_right = 'inf', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right')[-2]+[(r,c) for r,c in head if r<head_center_row]
        hair = [(r,c) for r,c in hair_part1+hair_part2 if r>=head_center_row]
        face = [(r,c) for r,c in cg.hex_neighbours_n(head_center_row+2, head_center_col, n=n_size) if r>=head_center_row+2]
        
        body = cgd.draw_trapezoid(max(r for r,c in face)+3, 
                                        min(c for r,c in hair if r==max(r for r,c in face)+3), 
                                        max(c for r,c in hair if r==max(r for r,c in face)+3),  bottom_line, 
                                   slope_left = 'inf', slope_right = 'inf', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right')[-2]
        collar = cgd.draw_slope_0p5_diagonal(max(r for r,c in face)+2, 
                                             min(c for r,c in hair if r==max(r for r,c in face)+2), max(r for r,c in face)+5, 
                                             left_down=False, right_down=True, left_up=True, right_up=True
                )+cgd.draw_slope_0p5_diagonal(max(r for r,c in face)+2, 
                                             max(c for r,c in hair if r==max(r for r,c in face)+2), max(r for r,c in face)+10, 
                                             left_down=True, right_down=False, left_up=True, right_up=True
                )
        if 'front' in version:
            keys = ["hair", "face", "body","collar",]
        elif 'back' in version:
            keys = ["hair", "body",]
    
    elif 'mid' in version:
        n_size = 3
        jaw_row = head_center_row
        face= cgd.draw_trapezoid(jaw_row, head_center_col-n_size, head_center_col+n_size, bottom_line-5, 
                                   slope_left = '0.5 shift', slope_right = '0.5 shift', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right',shift_gap_left = 5, shift_amount_left = -1, 
                  shift_gap_right = 5, shift_amount_right = -1,  )[-2]
        hair = cgd.draw_trapezoid(jaw_row-2, head_center_col-n_size, head_center_col+n_size, bottom_line, 
                                   slope_left = '0.5 shift', slope_right = '0.5 shift', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right',shift_gap_left = 4, shift_amount_left = 1, 
                  shift_gap_right = 4, shift_amount_right = 1,  )[-2]
       
        hair_front = cgd.draw_trapezoid(max(r for r,c in face)-8, 
                                        min(c for r,c in face if r==max(r for r,c in face)-8),
                                        max(c for r,c in face if r==max(r for r,c in face)-8), bottom_line, 
                                   slope_left = '1.5 shift', slope_right = '1.5 shift', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right',shift_gap_left = 3, shift_amount_left = -1, 
                  shift_gap_right = 3, shift_amount_right = -1,  )[-2]
        
        eye_row = max(r for r,c in face)-5
        cheek_row = max(r for r,c in face)-8
        mouth_row =jaw_row+8
        mouth = [(r,c) for r,c in cg.hex_neighbours_n(mouth_row,head_center_col, n=5, keep_origin =False , return_frontier=True)[-1]
                 if r<mouth_row-1]
      
        
        eyes = [pt for pt in cg.hex_neighbours_n(eye_row, min(c for r,c in face if r==eye_row)+3, n=2
                    , keep_origin =False , return_frontier=True
                                                )[-1]+cg.hex_neighbours_n(eye_row, max(c for r,c in face if r==eye_row)-3, n=2
                    , keep_origin =False , return_frontier=True)[-1] if pt in face]
        
        cheeks = [pt for pt in cg.hex_neighbours_n(cheek_row, min(c for r,c in face if r==cheek_row), n=2
                    )+cg.hex_neighbours_n(cheek_row, max(c for r,c in face if r==cheek_row), n=2
                    ) if pt in face]
        
        if 'front' in version:
            keys = ["hair", "hair_front", "face","cheeks", "eyes", "mouth"]
        elif 'back' in version:
            keys = ["hair", ]

    elif 'big' in version:
        
        n_size = bottom_line-head_center_row
        face = cg.hex_neighbours_n(head_center_row, head_center_col, n=n_size)
        
        n_eye = 4
        eye_row = head_center_row+n_eye+1
        cheek_row = eye_row+7
        n_cheek = 3
        
        mouth_row = max(r for r,c in face)-4
        
        left_eye_center = (eye_row, min(c for r,c in face if r==eye_row)+8)
        right_eye_center = (eye_row, max(c for r,c in face if r==eye_row)-8)
        
        eyes =[(r,c) for r,c in  cg.hex_neighbours_n(left_eye_center[0], left_eye_center[1], n=n_eye, 
                                                      keep_origin =False , return_frontier=True
                            )[-1]+cg.hex_neighbours_n(right_eye_center[0], right_eye_center[1], n=n_eye, 
                                                      keep_origin =False , return_frontier=True
                                                )[-1] if  (r,c) in face
              ]
        
        eyeball = cg.hex_neighbours_n(left_eye_center[0], left_eye_center[1], n=1
                 )+cg.hex_neighbours_n(right_eye_center[0], right_eye_center[1], n=1
                 )
        paint = cgd.verticle_line(max(r for r,c in eyeball), 
                                  max(c for r,c in eyeball  if r==max(r for r,c in eyeball)), bottom_line+7, bend = 'right')
        
        
        eye_socket = [(r,c) for r,c in  cg.hex_neighbours_n(left_eye_center[0], left_eye_center[1], n=n_eye-1
                                       )+cg.hex_neighbours_n(right_eye_center[0], right_eye_center[1], n=n_eye-1) 
                      if  (r,c) in face
              ]
        
        cheek = [pt for pt in cg.hex_neighbours_n(cheek_row, min(c for r,c in face if r==cheek_row)+1, n=n_cheek
                    )+cg.hex_neighbours_n(cheek_row, max(c for r,c in face if r==cheek_row)-1, n=n_cheek
                    ) if pt in face and pt  not in eyes+eye_socket]
        
                
        hair_left = cgd.draw_trapezoid(head_center_row, min(c for r,c in face)-6, head_center_col, bottom_line, 
                                   slope_left = '0.5', slope_right = 'inf', direction = 'lr',
                                   bend_left = 'left', bend_right = 'right')[-2]
        hair_right = cgd.draw_trapezoid(head_center_row, head_center_col,  max(c for r,c in face)+6, bottom_line, 
                                   slope_left = 'inf', slope_right ='0.5' , direction = 'lr',
                                   bend_left = 'left', bend_right = 'right')[-2]

        hand_part1 = cgd.draw_trapezoid(bottom_line-3, min(c for r,c in hair_left if r==bottom_line-3)+8,
                                  min(c for r,c in hair_left if r==bottom_line-3)+18, bottom_line, 
                                  slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                                  bend_left = 'left', bend_right = 'right')[-2]
        hand_part2 = cgd.draw_trapezoid(max(r for r,c in hand_part1), min(c for r,c in hand_part1 if r==max(r for r,c in hand_part1)),
                                  max(c for r,c in hand_part1 if r==max(r for r,c in hand_part1)),max(r for r,c in hand_part1)+2, 
                                  slope_left = '8/3', slope_right = '8/3', direction = 'rl',
                                  bend_left = 'left', bend_right = 'right')[-2]
        
        hand = hand_part1+hand_part2
        
        finger_skeleton = cgd.draw_block((max(r for r,c in hand_part1), 
                                          (max(c for r,c in hand_part1 if r==max(r for r,c in hand_part1))-3,
                                          max(c for r,c in hand_part1 if r==max(r for r,c in hand_part1))-3)), bottom_line+5)
        finger = []
        for loc in finger_skeleton:
            finger+=cg.hex_neighbours_n(loc[0], loc[1], n=1)
            
        
        if 'front' in version:
            keys = ["hair_left", "hair_right", 
                    "face", "cheek", "eyes","eye_socket", "eyeball", "paint", "hand","finger","left_eye_center", "right_eye_center",
                   ]
        elif 'back' in version:
            keys = ["hair_left", "hair_right", ]

    local_vars = locals()
    return [local_vars[k] for k  in keys]


def draw_shape(center_row, center_col, n_size=6):
    shape = cg.hex_neighbours_n(center_row,center_col, n=n_size, keep_origin = False, return_frontier=True
                                       )[-1]
    shape_row2_temp = cg.hex_neighbours_n(center_row,center_col, n=n_size+1, keep_origin = False, return_frontier=True
                               )[-1]
    remove_shape_row2 = [(center_row, center_col-(n_size+1)), (center_row, center_col+(n_size+1)),
           (max(r for r,c in shape_row2_temp), min(c for r,c in shape_row2_temp if r==max(r for r,c in shape_row2_temp))),
           (max(r for r,c in shape_row2_temp), max(c for r,c in shape_row2_temp if r==max(r for r,c in shape_row2_temp))),
           (min(r for r,c in shape_row2_temp), min(c for r,c in shape_row2_temp if r==min(r for r,c in shape_row2_temp))),
           (min(r for r,c in shape_row2_temp), max(c for r,c in shape_row2_temp if r==min(r for r,c in shape_row2_temp)))    ]
    shape_row2 = [(r,c) for r,c in shape_row2_temp if (r,c) not in remove_shape_row2]
    shape+=shape_row2
    
    return shape

def draw_photo(frame_center_row, frame_center_col, size, flip = False):
    if size == 'big':    
        n_size = 6
        head_center_row = frame_center_row-2
        head_raw, raw_body, line_dict, head_dict, neck, torso_dict, upperlimb_joint_dict, botlimb_joint_dict, thigh_dict, calf_dict, feet_dict, upperarm_dict, forearm_dict, hand_dict, plot_temp = cgf.draw_human_body(head_center_row ,frame_center_col, version="7")

        frame = draw_shape(frame_center_row, frame_center_col, n_size=n_size)
        photo  = cg.hex_neighbours_n(frame_center_row, frame_center_col, n=n_size-1)
        
        valid_frame = [(r,c) for r,c in frame if (r,c) not in photo]
        if flip:
            valid_body = [(2*head_center_row-r,c) for r,c in raw_body if (r,c)in photo]
        else:
            valid_body = [(r,c) for r,c in raw_body if (r,c)in photo]
    elif size == 'mid':  
        n_size = 3
        raw_body = cg.hex_neighbours_n(frame_center_row, frame_center_col, n=1)
        frame = draw_shape(frame_center_row, frame_center_col, n_size=n_size)
        photo  = cg.hex_neighbours_n(frame_center_row, frame_center_col, n=n_size-1)
        if flip:
            raw_body+=[(r,c) for r,c in photo if r== min(row for row,col in photo)]
        else:
            raw_body+=[(r,c) for r,c in photo if r== max(row for row,col in photo)]
        valid_frame = [(r,c) for r,c in frame if (r,c) not in photo]
        valid_body = [(r,c) for r,c in raw_body if (r,c)in photo]
    elif size == 'small':  
        n_size = 2
        frame = draw_shape(frame_center_row, frame_center_col, n_size=n_size)
        photo  = cg.hex_neighbours_n(frame_center_row, frame_center_col, n=n_size-1)
        if flip:
            raw_body=[(r,c) for r,c in photo if r== min(row for row,col in photo)]+[(frame_center_row, frame_center_col)]
        else:
            raw_body=[(r,c) for r,c in photo if r== max(row for row,col in photo)]+[(frame_center_row, frame_center_col)]
        
        valid_body = [(r,c) for r,c in raw_body if (r,c)in photo]
        valid_frame = [(r,c) for r,c in frame if (r,c) not in photo]
        
    return valid_body, photo, valid_frame

def draw_spiderlily(center_row, center_col, version):
    if 'side' in version:
        flower_center = cg.hex_neighbours_n(center_row, center_col, n=1)
        stem = [(center_row+2,center_col)]
        temp = cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row-2,
                                           left_down=False, right_down=False, left_up=True, right_up=True
                   )+cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row+2,
                                           left_down=True, right_down=True, left_up=True, right_up=True
                   )
        flower_in_raw =flower_center+[(r,c) for r,c in temp if r<=center_row]
        flower_out = cgd.draw_slope_0p5_diagonal(max(r for r,c in flower_center), 
                              min(c for r,c in flower_center if r==max(r for r,c in flower_center))-1, 
                              min(r for r,c in flower_center),
                              left_down=False, right_down=False, left_up=True, right_up=False
                   )+cgd.draw_slope_1p5_diagonal(max(r for r,c in flower_center), 
                              min(c for r,c in flower_center if r==max(r for r,c in flower_center))-1, 
                              center_row,
                              left_down=False, right_down=False, left_up=True, right_up=False
                   )+cgd.draw_slope_0p5_diagonal(max(r for r,c in flower_center), 
                              max(c for r,c in flower_center if r==max(r for r,c in flower_center))+1, 
                              min(r for r,c in flower_center),
                              left_down=False, right_down=False, left_up=False, right_up=True
                   )+cgd.draw_slope_1p5_diagonal(max(r for r,c in flower_center), 
                              max(c for r,c in flower_center if r==max(r for r,c in flower_center))+1, 
                              center_row,
                              left_down=False, right_down=False, left_up=False, right_up=True
                   )+[(r,c) for r,c in temp if r>center_row]
        flower_in = [(r,c) for r,c in flower_in_raw if (r,c) not in flower_out]
        return stem, flower_in, flower_out
    elif 'top' in version:    
        size = 3
        flower_in = [(center_row, center_col)]
        flower_raw = cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row-size,
                              left_down=False, right_down=False, left_up=True, right_up=True
                   )+cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row+size,
                              left_down=True, right_down=True, left_up=False, right_up=False
                   )+cgd.horizontal_lines([(center_row, (center_col-size, center_col+size))])
        flower_out = [(r,c) for r,c in flower_raw if (r,c) not in flower_in+cg.get_hex_corners(center_row, center_col, 1)[::2]+cg.get_hex_corners(center_row, center_col, 2)[1::2]]
            
        return flower_in, flower_out

def draw_jimsonweed(center_row, center_col, version):
    if 'side' in version:
        stem = cgd.verticle_line(center_row, center_col, center_row+2, bend = 'left'
                 )+cgd.verticle_line(center_row, center_col, center_row+2, bend = 'right'
                 )
        flower_bot = cgd.draw_triangle(max(r for r,c in stem), center_col,  max(r for r,c in stem)+2, 
                                     slope_left = '0.5', slope_right = '0.5', direction = 'lr', 
                                     bend_left = 'left', bend_right = 'right')[-2]
        flower_mid = cgd.draw_triangle(max(r for r,c in flower_bot), center_col,  max(r for r,c in flower_bot)+3, 
                                     slope_left = '0.5', slope_right = '0.5', direction = 'lr', 
                                     bend_left = 'left', bend_right = 'right')[-2]
        flower_top_raw = cgd.draw_slope_1p5_diagonal(max(r for r,c in flower_mid), 
                                                   min(c for r,c in flower_mid if r== max(r for r,c in flower_mid)), 
                                                   max(r for r,c in flower_mid)+1, 
                                                 left_down=True, right_down=False, left_up=False, right_up=True
                   )+cgd.draw_slope_0p5_diagonal(max(r for r,c in flower_mid), 
                                                   min(c for r,c in flower_mid if r== max(r for r,c in flower_mid)), 
                                                   max(r for r,c in flower_mid)+1, 
                                                 left_down=True, right_down=False, left_up=False, right_up=True
                   )+cgd.draw_slope_1p5_diagonal(max(r for r,c in flower_mid), 
                                                   max(c for r,c in flower_mid if r== max(r for r,c in flower_mid)), 
                                                   max(r for r,c in flower_mid)+1, 
                                                 left_down=False, right_down=True, left_up=False, right_up=True
                   )+cgd.draw_slope_0p5_diagonal(max(r for r,c in flower_mid), 
                                                   max(c for r,c in flower_mid if r== max(r for r,c in flower_mid)), 
                                                   max(r for r,c in flower_mid)+1, 
                                                 left_down=False, right_down=True, left_up=False, right_up=True
                   )+[(max(r for r,c in flower_mid)+1, center_col)]
        flower_top = [(r,c) for r,c in flower_top_raw if (r,c) not in flower_mid]
        
        return stem, flower_bot, flower_mid, flower_top
    elif 'top' in version:
        size = 3
        flower_in = cg.hex_neighbours_n(center_row, center_col, n=1 )
        flower_raw = cg.hex_neighbours_n(center_row, center_col, n=size-1
                   )+cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row-size,
                              left_down=False, right_down=False, left_up=True, right_up=True
                   )+cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row+size,
                              left_down=True, right_down=True, left_up=False, right_up=False
                   )+cgd.horizontal_lines([(center_row, (center_col-size, center_col+size))])
        flower_out = [(r,c) for r,c in flower_raw if (r,c) not in flower_in
                     ]+cg.hex_neighbours_n(center_row, center_col, n=1 , keep_origin =False , return_frontier=True)[-1]
        return flower_in, flower_out
        
def draw_ghostplant(center_row, center_col, version):
    
    if 'top' in version:
        flower_in = [(center_row, center_col)]
        if 'left' in version:
            flower_mid = cg.get_hex_corners(center_row, center_col, 1)[::2]
        elif 'right' in version:
            flower_mid = cg.get_hex_corners(center_row, center_col, 1)[1::2]
        flower_out_raw = cg.hex_neighbours_n(center_row, center_col, n=2)
        
        flower_out = [(r,c) for r,c in flower_out_raw if (r,c) not in flower_in+flower_mid]  
        return flower_in, flower_mid, flower_out 
    elif 'side down' in version:
        stem_center = [(r,c) for r, c in cg.hex_neighbours_n(center_row, center_col, n=1, keep_origin = False, return_frontier=True 
                                  )[-1]  if r<=center_row and (r,c) !=(center_row, center_col)]
        if 'left' in version:
            flower_bot = cgd.draw_slope_0p5_diagonal(max(r for r,c in stem_center), 
                                                 min(c for r,c in stem_center if r==max(r for r,c in stem_center)), 
                                                 max(r for r,c in stem_center)+2,
                                           left_down=True, right_down=False, left_up=False, right_up=False)
            stem_side = cgd.verticle_line(max(r for r,c in stem_center), 
                                       max(c for r,c in stem_center if r==max(r for r,c in stem_center)), 
                                       max(r for r,c in stem_center)+6, bend = 'right')
            flower_mid = cg.hex_neighbours_n(max(r for r,c in flower_bot),
                                     min(c for r,c in flower_bot if r==max(r for r,c in flower_bot)), n=1)
            flower_top = [(max(r for r,c in flower_mid), min(c for r,c in flower_mid if r==max(r for r,c in flower_mid)))]
        
        elif 'right' in version:
            flower_bot = cgd.draw_slope_0p5_diagonal(max(r for r,c in stem_center), 
                                                 max(c for r,c in stem_center if r==max(r for r,c in stem_center)), 
                                                 max(r for r,c in stem_center)+2,
                                           left_down=False, right_down=True, left_up=False, right_up=False)
            stem_side = cgd.verticle_line(max(r for r,c in stem_center), 
                                       min(c for r,c in stem_center if r==max(r for r,c in stem_center)), 
                                       max(r for r,c in stem_center)+6, bend = 'left')
            flower_mid = cg.hex_neighbours_n(max(r for r,c in flower_bot),
                                     max(c for r,c in flower_bot if r==max(r for r,c in flower_bot)), n=1)
            flower_top = [(max(r for r,c in flower_mid), max(c for r,c in flower_mid if r==max(r for r,c in flower_mid)))]
        
        stem = stem_center+stem_side
        return stem, flower_bot, flower_mid, flower_top
    elif 'side up' in version:
        if 'left' in version:
            stem = cgd.verticle_line(center_row, center_col, center_row+8, bend = 'right')
            flower_bot_raw = cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row-1,
                                           left_down=False, right_down=False, left_up=True, right_up=False
                        )+cgd.draw_slope_1p5_diagonal(center_row, center_col, center_row-1,
                                           left_down=False, right_down=False, left_up=True, right_up=False
                        )+cgd.draw_slope_8p3_diagonal(center_row, center_col, center_row-1,
                                           left_down=False, right_down=False, left_up=True, right_up=False
                        )
            flower_bot = [(r,c) for r,c in flower_bot_raw if (r,c) not in stem]
            flower_mid_raw = cgd.verticle_line(min(r for r,c in flower_bot) ,
                                           max(c for r,c in flower_bot if r==min(r for r,c in flower_bot)), 
                                           min(r for r,c in flower_bot)-1, bend = 'left'
                           )+cgd.draw_slope_1p5_diagonal(min(r for r,c in flower_bot), 
                                                        max(c for r,c in flower_bot if r==min(r for r,c in flower_bot)), 
                                                        min(r for r,c in flower_bot)+1,
                                           left_down=True, right_down=False, left_up=False, right_up=False
                        )
            flower_mid = [(r,c) for r,c in flower_mid_raw if (r,c) not in flower_bot]
            
        elif 'right' in version:
            stem = cgd.verticle_line(center_row, center_col, center_row+8, bend = 'left')
            flower_bot_raw = cgd.draw_slope_0p5_diagonal(center_row, center_col, center_row-1,
                                           left_down=False, right_down=False, left_up=False, right_up=True
                        )+cgd.draw_slope_1p5_diagonal(center_row, center_col, center_row-1,
                                           left_down=False, right_down=False, left_up=False, right_up=True
                        )+cgd.draw_slope_8p3_diagonal(center_row, center_col, center_row-1,
                                           left_down=False, right_down=False, left_up=False, right_up=True
                        )
            flower_bot = [(r,c) for r,c in flower_bot_raw if (r,c) not in stem]
            flower_mid_raw = cgd.verticle_line(min(r for r,c in flower_bot) ,
                                           min(c for r,c in flower_bot if r==min(r for r,c in flower_bot)), 
                                           min(r for r,c in flower_bot)-1, bend = 'right'
                          )+cgd.draw_slope_1p5_diagonal(min(r for r,c in flower_bot), 
                                                        min(c for r,c in flower_bot if r==min(r for r,c in flower_bot)), 
                                                        min(r for r,c in flower_bot)+1,
                                           left_down=False, right_down=True, left_up=False, right_up=False
                        )
            flower_mid = [(r,c) for r,c in flower_mid_raw if (r,c) not in flower_bot]
            
            
        return stem, flower_bot , flower_mid

def draw_plant_pot(center_row, center_col, version):
    if version == 'spider lily top':
        n_pot = 5
        pot_out = cg.hex_neighbours_n(center_row, center_col, n=n_pot, keep_origin =False , return_frontier=True)[-1]
        pot_mid = cg.hex_neighbours_n(center_row, center_col, n=n_pot-1, keep_origin =False , return_frontier=True)[-1]
        pot_in = cg.hex_neighbours_n(center_row, center_col, n=n_pot-3, keep_origin =False , return_frontier=True)[-1]
        flower_in, flower_out = draw_spiderlily(center_row, center_col, 'top')
        flower = flower_in+flower_out
        return pot_in, pot_mid, pot_out, flower
    elif version == 'spider lily side':
        root, soil, pot = draw_photo(center_row, center_col, 'small', flip = True)
        stem, flower_in, flower_out = draw_spiderlily(min(r for r,c in pot)-3, center_col, 'side')
        return root, soil, pot , stem, flower_in, flower_out
    elif version == 'spider lily pot':
        root, soil, pot = draw_photo(center_row, center_col, 'mid', flip = True)
        return root, soil, pot
    
    

def draw_letter(center_loc, letter, add_loc):
    if letter == 'F':
        letter_part1  =cgd.verticle_line(center_loc[0], center_loc[1], add_loc, bend = 'left'
                   )
        letter_part2 = cgd.horizontal_lines([(min(r for r,c in letter_part1), 
                                              (min(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)), 
                                               min(c for r,c in letter_part1 if r==min(r for r,c in letter_part1))+5)),
                                          (min(r for r,c in letter_part1)+6, 
                                              (min(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)+6), 
                                               min(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)+6)+5)),]
                   )
        letter = letter_part1+letter_part2
    elif letter == 'u':
        letter_part1 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1], n=1, 
                                                             keep_origin =False , return_frontier=True)[-1]
                        if r>=center_loc[0]]
        letter_part2 = cgd.verticle_line(min(r for r,c in letter_part1), 
                                         min(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)), 
                                         min(r for r,c in letter_part1)-5, bend = 'left'
                              )+cgd.verticle_line(min(r for r,c in letter_part1), 
                                                  max(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)), 
                                                  min(r for r,c in letter_part1)-5, bend = 'right'
                              )
        letter = letter_part1+letter_part2
    elif letter == 'n':
        letter_part1 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1], n=1, 
                                                             keep_origin =False , return_frontier=True)[-1]
                        if r<=center_loc[0]]
        letter_part2 = cgd.verticle_line(max(r for r,c in letter_part1), 
                                         min(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)), 
                                         max(r for r,c in letter_part1)+5, bend = 'left'
                              )+cgd.verticle_line(max(r for r,c in letter_part1), 
                                                  max(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)), 
                                                  max(r for r,c in letter_part1)+5, bend = 'right'
                              )
        letter = letter_part1+letter_part2
        
        
    elif letter == 'e':
        letter_part1 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1], n=2, 
                                                             keep_origin =False , return_frontier=True)[-1]
                        if r<=center_loc[0]+1]
        letter_part2 = cgd.horizontal_lines([(max(r for r,c in letter_part1),
                                         (min(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)), 
                                          max(c for r,c in letter_part1 if r==max(r for r,c in letter_part1))))]
                   )
        letter_part3 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0]+2, center_loc[1], n=2, 
                                                             keep_origin =False , return_frontier=True)[-1]
                        if c<=max(c for r,c in letter_part2) and r>center_loc[0] and (r,c) !=(center_loc[0]+2, center_loc[1]+2)]
        letter = letter_part1+letter_part2+letter_part3
        
    elif letter == 'r':
        letter_part1 = cgd.verticle_line(center_loc[0], center_loc[1], add_loc, bend = 'right'
                              )
        letter_part2 = cgd.draw_slope_1p5_diagonal(center_loc[0]+1, max(c for r,c in letter_part1 if r==center_loc[0]+1), center_loc[0], 
                                              left_down=False, right_down=False, left_up=False, right_up=True
                 )+cgd.draw_slope_8p3_diagonal(center_loc[0]+1, max(c for r,c in letter_part1 if r==center_loc[0]+1), center_loc[0], 
                                              left_down=False, right_down=False, left_up=False, right_up=True
                 )+[(center_loc[0]+1, max(c for r,c in letter_part1 if r==center_loc[0]+1)+1)]
        letter = letter_part1+letter_part2
    elif letter == 'a':
        letter_part1 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1], n=2, 
                                                        keep_origin =False , return_frontier=True)[-1]
                   if r<=center_loc[0]]+[(r,c) for r,c in cg.hex_neighbours_n(center_loc[0]+2, center_loc[1], n=2, 
                                                                              keep_origin =False , return_frontier=True)[-1]
                   if r>center_loc[0]]
        letter_part2 = cgd.draw_slope_0p5_diagonal(max(r for r,c in letter_part1)-2, 
                                              max(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)-2), 
                                              max(r for r,c in letter_part1), 
                                              left_down=False, right_down=True, left_up=False, right_up=False) 
        letter = letter_part1+letter_part2
        
    elif letter == 'l':
        letter = cgd.verticle_line(center_loc[0], center_loc[1], add_loc, bend = 'left'
                             )+cgd.horizontal_lines([(center_loc[0], (center_loc[1], center_loc[1]+2))])
                   
    elif letter == 's':
        letter_part1 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1], n=2, 
                                                             keep_origin =False , return_frontier=True)[-1]
                   if  r<=center_loc[0]+1 and (r,c) != (center_loc[0], center_loc[1]+2) 
            ]
        letter_part2 = cgd.horizontal_lines([(max(r for r,c in letter_part1),
                                         (min(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)), 
                                          max(c for r,c in letter_part1 if r==max(r for r,c in letter_part1))))]
                   )
        letter_part3 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0]+2, center_loc[1], n=2, 
                                                             keep_origin =False , return_frontier=True)[-1]
                   if  r>=center_loc[0]+2 and (r,c) != (center_loc[0]+2, center_loc[1]-2)
            ]
        letter = letter_part1+letter_part2+letter_part3
    elif letter == 'm':
        letter_part1 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1], n=1, 
                                                             keep_origin =False , return_frontier=True)[-1]
                        if r<=center_loc[0]]
        letter_part2 = cgd.verticle_line(max(r for r,c in letter_part1), 
                                         min(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)), 
                                         max(r for r,c in letter_part1)+5, bend = 'left'
                              )+cgd.verticle_line(max(r for r,c in letter_part1), 
                                                  max(c for r,c in letter_part1 if r==max(r for r,c in letter_part1)), 
                                                  max(r for r,c in letter_part1)+5, bend = 'right'
                              )
        letter_part3 = [(r,c) for r,c in cg.hex_neighbours_n(center_loc[0], center_loc[1]+3, n=1, 
                                                             keep_origin =False , return_frontier=True)[-1]
                        if r<=center_loc[0]]
        letter_part4 = cgd.verticle_line(max(r for r,c in letter_part3), 
                                                  max(c for r,c in letter_part3 if r==max(r for r,c in letter_part3)), 
                                                  max(r for r,c in letter_part3)+5, bend = 'right'
                              )
        letter = letter_part1+letter_part2+letter_part3+letter_part4
        
    elif letter == 'M':    
        letter_part1 = cgd.draw_slope_0p5_diagonal_shift(center_loc[0], center_loc[1], add_loc, 4, shift_amount=-1, 
                                              left_down=False, right_down=False, left_up=False, right_up=True
            )+cgd.draw_slope_0p5_diagonal_shift(center_loc[0], center_loc[1], add_loc, 4, shift_amount=-1, 
                                              left_down=False, right_down=False, left_up=True, right_up=False
            )
        letter_part2 = cgd.verticle_line(min(r for r,c in letter_part1), 
                                    min(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)), center_loc[0]+5, bend = 'left'
                             )+cgd.verticle_line(min(r for r,c in letter_part1), 
                                    max(c for r,c in letter_part1 if r==min(r for r,c in letter_part1)), center_loc[0]+5, bend = 'right'
                             )
        letter = letter_part1+letter_part2
    
    return letter
 

def draw_word(word_start_loc, word, WORD_LINE):
    if word == 'Funeral':
        F_letter = draw_letter(word_start_loc, 'F', WORD_LINE)
        
        u_start_loc = (max(r for r,c in F_letter)-1, word_start_loc[1]+6)
        u_letter = draw_letter(u_start_loc, 'u', 0)
        
        n_start_loc = (max(r for r,c in F_letter)-5, u_start_loc[1]+5)
        n_letter = draw_letter(n_start_loc, 'n', 0)
        
        e_start_loc = (min(r for r,c in n_letter)+2, max(c for r,c in n_letter)+4)
        e_letter = draw_letter(e_start_loc, 'e', 0)
        
        r_start_loc = (min(r for r,c in e_letter), max(c for r,c in e_letter)+2)
        r_letter = draw_letter(r_start_loc, 'r', max(r for r,c in F_letter))
        
        a_start_loc = (e_start_loc[0], max(c for row,c in r_letter)+3)
        a_letter = draw_letter(a_start_loc, 'a', 0)
        
        l_start_loc = (max(r for r,c in u_letter), max(c for r,c in a_letter)+2)
        l_letter = draw_letter(l_start_loc, 'l', min(r for r,c in F_letter))
        
        
        WORD_dict  = {'F': F_letter,
                        'u': u_letter,
                        'n': n_letter,
                        'e': e_letter,
                        'r': r_letter,
                        'a': a_letter,
                        'l': l_letter,}
                                  
    elif word == 'Museum':
        M_letter = draw_letter(word_start_loc, 'M', WORD_LINE)
        
        u1_start_loc = (max(r for r,c in M_letter)-1, max(c for r,c in M_letter)+4)
        u1_letter = draw_letter(u1_start_loc, 'u', 0)
        
        s_start_loc = (min(r for r,c in u1_letter)+2, max(c for r,c in u1_letter)+4)
        s_letter = draw_letter(s_start_loc, 's', 0)
        
        e_start_loc = (s_start_loc[0], max(c for r,c in s_letter)+4)
        e_letter = draw_letter(e_start_loc, 'e', 0)
        
        u2_start_loc = (max(r for r,c in e_letter)-1, max(c for r,c in e_letter)+4)
        u2_letter = draw_letter(u2_start_loc, 'u', 0)
        
        m_start_loc = (max(r for r,c in e_letter)-5, max(c for r,c in u2_letter)+4)
        m_letter = draw_letter(m_start_loc, 'm', 0)
        
        WORD_dict  = {'M': M_letter,
                    'u1': u1_letter,
                    's': s_letter,
                    'e': e_letter,
                    'u2': u2_letter,
                    'm': m_letter,}
        
                         
    return WORD_dict



def draw_arrow(arr_tip_row, arr_tip_col, arr_tip_height, 
               width, 
               arr_vertical_height, direction = 'down'):
    
    
    if direction == 'down':
        arr_tip = cgd.draw_triangle(arr_tip_row, arr_tip_col, arr_tip_row-arr_tip_height, 
                                    slope_left = '0.5', slope_right = '0.5', direction = 'lr', 
                 bend_left = 'left', bend_right = 'right')[-2]
        
       
        arr_vertical_locs = [(r,c) for r,c in arr_tip if r==min(row for row,col in arr_tip)]
        arr_vertical_cs = np.array(arr_vertical_locs).T[1]
        
        arr_vertical = cgd.draw_block((min(r for r,c in arr_tip), 
                                       (math.floor(arr_vertical_cs.mean())-width, math.ceil(arr_vertical_cs.mean())+width)), 
                                      min(r for r,c in arr_tip)-arr_vertical_height)
    elif direction == 'up': 
        arr_tip = cgd.draw_triangle(arr_tip_row, arr_tip_col, arr_tip_row+arr_tip_height, 
                                    slope_left = '0.5', slope_right = '0.5', direction = 'lr', 
                 bend_left = 'left', bend_right = 'right')[-2]
        
        arr_vertical_locs = [(r,c) for r,c in arr_tip if r==max(row for row,col in arr_tip)]
        arr_vertical_cs = np.array(arr_vertical_locs).T[1]
        arr_vertical = cgd.draw_block((max(r for r,c in arr_tip), 
                                       (math.floor(arr_vertical_cs.mean())-width, math.ceil(arr_vertical_cs.mean())+width)), 
                                      max(r for r,c in arr_tip)+arr_vertical_height)
    
    arrow = arr_vertical+arr_tip
   
    
    return arrow


def draw_mainchar(head_char_row, head_char_col, face_direction=None, version = '3'):
    if version == "3" or version=="5" or version=="7":
        _, character_body, _, _, _, _, upperlimb_joint_dict, botlimb_joint_dict, _, _, _, _, _, _, _= cgf.draw_human_body(head_char_row, head_char_col, version = version)
        character_joints = upperlimb_joint_dict["full_joints"]+botlimb_joint_dict["full_joints"]
        if face_direction!=None:
            if 'right' in face_direction:
                head_center = (head_char_row, head_char_col+1)
                n_head = 1
            elif 'left' in face_direction:
                head_center = (head_char_row, head_char_col-1)
                n_head = 1
            elif 'front' in face_direction:
                head_center = (head_char_row, head_char_col)
                n_head = 1
            elif 'back' in face_direction:
                head_center = (head_char_row, head_char_col)
                n_head = 0
            head = cg.hex_neighbours_n(head_center[0], head_center[1], n=n_head, keep_origin = True, return_frontier=False)
            return character_body, character_joints, head
        else:
             return character_body, character_joints

    elif version =="tiny":
        n_head=1
        body_dict, plot_temp = cgf.draw_tiny_body_(head_char_row, head_char_col, n_head)
        raw_body = body_dict['raw_body']
        remove = [(head_char_row+n_head*2+1, min(c for r,c in raw_body if r==head_char_row+n_head*2+1)),
                  (head_char_row+n_head*2+1, max(c for r,c in raw_body if r==head_char_row+n_head*2+1)),
                 ]
        character_body = [(r,c) for r,c in raw_body if (r,c) not in remove]
        
        return character_body


def draw_body_flower(head_loc, version, flip = False):
    body_raw, line_dict = cgf.draw_human_body(head_loc[0], head_loc[1], version = version)[1:3]

    locs_raw = {
        
        'left foot':(max(r for r,c in body_raw) ,min(c for r,c in body_raw if r==max(r for r,c in body_raw))+1),
        'right foot': (max(r for r,c in body_raw),max(c for r,c in body_raw if r==max(r for r,c in body_raw))-1),

        'left leg':(line_dict["gastrocnemius_end_r"],min(c for r,c in body_raw if r==line_dict["gastrocnemius_end_r"])),
        'right leg': (line_dict["gastrocnemius_end_r"],max(c for r,c in body_raw if r==line_dict["gastrocnemius_end_r"])),
        
        'left knee':(line_dict["knee_r"],min(c for r,c in body_raw if r==line_dict["knee_r"])),
        'right knee': (line_dict["knee_r"],max(c for r,c in body_raw if r==line_dict["knee_r"])),
        
        
        'left hand':(line_dict["wrist_r"]+3, min(c for r,c in body_raw if r== line_dict["wrist_r"]+3 and c<head_loc[1])),
        'right hand':(line_dict["wrist_r"]+3, max(c for r,c in body_raw if r== line_dict["wrist_r"]+3 and c>head_loc[1])),
        
        'left wrist':(line_dict["wrist_r"], min(c for r,c in body_raw if r== line_dict["wrist_r"] and c<head_loc[1])),
        'right wrist':(line_dict["wrist_r"], max(c for r,c in body_raw if r== line_dict["wrist_r"] and c>head_loc[1])),
        
        
        'left arm':(line_dict["elbow_r"]+1, min(c for r,c in body_raw if r== line_dict["elbow_r"]+1 and c<head_loc[1])),
        'right arm':(line_dict["elbow_r"]+1, max(c for r,c in body_raw if r== line_dict["elbow_r"]+1 and c>head_loc[1])),
        
        
        'botton':(line_dict["femoral_head_r"]-1, head_loc[1]),
        'chest':(line_dict["breastbone_end_r"]+1 , head_loc[1]),
        
    }
    
    if flip:
        locs = {}
        locs_LIST = []
        for key in locs_raw.keys():
            r, c = locs_raw[key]
            locs[key] = (2*head_loc[0] - r, c)
            locs_LIST.append(locs[key])
        body = [(2*head_loc[0] - r, c) for r, c in body_raw]
        
    else:
        locs = locs_raw
        locs_LIST = list(locs_raw.values())
        body = body_raw
    return body, locs# ,locs_LIST

