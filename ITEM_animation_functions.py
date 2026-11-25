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
import ITEM_functions as ITEM_F


rng = np.random.default_rng(42)


def draw_coffin_anime(coffin_edges, arrow_loc, version, hex_rc_arr, snapshot=0):
        
    arrow, coffin,coffin_left, coffin_right = ITEM_F.draw_coffin(coffin_edges, arrow_loc, hex_rc_arr,version)
    N_coffin_right = len(set(c for r, c in coffin_right))
    N_coffin_left = len(set(c for r, c in coffin_left))
    cycle_len = (N_coffin_left + 1) + (N_coffin_right + 1)+4

    sub_snapshot = snapshot % cycle_len
    
    coffin_COLOR = [[0.5, 0.5, 0.5]]
    if version == 'up':
        if sub_snapshot < N_coffin_right:
            coffin_right_reveal = cga.reveal_cols(coffin_right, sub_snapshot, reverse=True)
            coffin_left_reveal = cga.reveal_cols(coffin_left, 0, reverse=True)
        else:
            coffin_right_reveal = cga.reveal_cols(coffin_right, N_coffin_right, reverse=True)
            coffin_left_reveal = cga.reveal_cols(coffin_left, sub_snapshot - N_coffin_right, reverse=True)

    
        arrow_COLOR = [cgc.hex_to_rgb("#597c70"), 'sigmafactor=1.5']
        coffin_left_COLOR = [cgc.hex_to_rgb("#f4c12b"), 'sigmafactor=1.2']
        coffin_right_COLOR = [cgc.hex_to_rgb("#6d3f15"), 'sigmafactor=1.2']
    elif version == 'down':
        if sub_snapshot < N_coffin_left:
            coffin_left_reveal = cga.reveal_cols(coffin_left, sub_snapshot, reverse=False)
            coffin_right_reveal = cga.reveal_cols(coffin_right, 0, reverse=False)
        else:
            coffin_left_reveal = cga.reveal_cols(coffin_left, N_coffin_left, reverse=False)
            coffin_right_reveal = cga.reveal_cols(coffin_right, sub_snapshot - N_coffin_left, reverse=False)
        
        arrow_COLOR = [cgc.hex_to_rgb("#ff5400"), 'sigmafactor=3.'] 
        coffin_left_COLOR = [cgc.hex_to_rgb("#8b8581"),[0.2,0.2,0.2], 'sigmafactor=1.2', 'col']
        coffin_right_COLOR = [cgc.hex_to_rgb("#ffcf00"), cgc.hex_to_rgb("#ff5400"),'sigmafactor=1.2',  'col']
        
    keys = ["coffin", "coffin_right_reveal", "coffin_left_reveal", "arrow", ]
    colors = [coffin_COLOR, coffin_right_COLOR, coffin_left_COLOR, arrow_COLOR]
        
    local_vars = locals()
    
    return {k: [local_vars[k], c] for k, c in zip(keys, colors)}

    
def draw_ghost_anime(ghosts_cols, top_line, bottom_line, version, snapshot=0):
    ghosts = ITEM_F.draw_ghosts(ghosts_cols, top_line, bottom_line)
    
    N_ghosts   = len(set(c for r, c in ghosts))
    ghosts_COLOR = [cgc.hex_to_rgb("#e8dcf4"), cgc.hex_to_rgb("#8b7692") , 'col']
    
    if version == 'reveal':
        ghosts_reveal  = cga.reveal_cols(ghosts,min(snapshot, N_ghosts),   reverse=False)   # rightmost col -> leftmost col
        
        keys = ["ghosts_reveal", ]
        
        colors = [ghosts_COLOR]
    elif version == 'transparent':
        alpha = round(np.random.default_rng([42, snapshot]).random(), 3)
        ghosts_COLOR           = cgc.add_alpha(ghosts_COLOR, alpha)
       
        keys = ["ghosts", ]
        
        colors = [ghosts_COLOR]
        
    local_vars = locals()
    
    return {k: [local_vars[k], c] for k, c in zip(keys, colors)}


def draw_bridge_anime(bridge_start_row, bridge_start_col, version, snapshot=0):
    
    pillars, steps, bridge_line_left, bridge_line_right = ITEM_F.draw_bridge(bridge_start_row, bridge_start_col, pillar_height = 6)
    pillars_COLOR =  [[0,0,0], cgc.hex_to_rgb("#e90063"), 'row']
    #[[0,0,0], cgc.hex_to_rgb("#7d0035"), 'row']
    steps_COLOR =  [cgc.hex_to_rgb("#f00066"), [0,0,0], 'col' ]
    #[cgc.hex_to_rgb("#7d0035"), [0,0,0], 'col' ]
              
    bridge_line_left_COLOR = [cgc.hex_to_rgb("#f5c3fb"), cgc.hex_to_rgb("#334741"), ['row', 'sigmoid' ]]
    #[cgc.hex_to_rgb("#a98fac"), cgc.hex_to_rgb("#440125"), ['row', 'sigmoid' ]]
    bridge_line_right_COLOR = [cgc.hex_to_rgb("#ffbfd9"), cgc.hex_to_rgb("#0c2c23"), ['row', 'sigmoid' ]]
    #[cgc.hex_to_rgb("#dfbbd6"), [0,0,0], ['row', 'sigmoid' ]]
    
    
    if version == 'reveal':
        N_pillars = len(set(r for r, c in pillars))
        N_bridge  = len(set(r for r, c in bridge_line_left))   # assumes left/right span the same rows
        N_steps   = len(set(c for r, c in steps))

        N_total = max(N_pillars, N_bridge, N_steps)
        s = min(snapshot, N_total)

        pillars_reveal           = cga.reveal_rows(pillars,           min(s, N_pillars), reverse=False)  # top row -> bottom row
        bridge_line_left_reveal  = cga.reveal_rows(bridge_line_left,  min(s, N_bridge),  reverse=True)   # bottom row -> top row
        bridge_line_right_reveal = cga.reveal_rows(bridge_line_right, min(s, N_bridge),  reverse=True)   # bottom row -> top row
        steps_reveal             = cga.reveal_cols(steps,            min(s, N_steps),   reverse=True)   # rightmost col -> leftmost col
        
        
        keys = ["pillars_reveal", "steps_reveal", "bridge_line_left_reveal", "bridge_line_right_reveal"]
        
        colors = [pillars_COLOR,  steps_COLOR, bridge_line_left_COLOR, bridge_line_right_COLOR]
    if version == 'transparent':
        alpha = round(np.random.default_rng([42, snapshot]).random(), 3)

        pillars_COLOR           = cgc.add_alpha(pillars_COLOR, alpha)
        steps_COLOR             = cgc.add_alpha(steps_COLOR, alpha)
        bridge_line_left_COLOR  = cgc.add_alpha(bridge_line_left_COLOR, alpha)
        bridge_line_right_COLOR = cgc.add_alpha(bridge_line_right_COLOR, alpha)

        keys = ["pillars", "steps", "bridge_line_left", "bridge_line_right"]
        
        colors = [pillars_COLOR,  steps_COLOR, bridge_line_left_COLOR, bridge_line_right_COLOR]
    local_vars = locals()
    
    return {k: [local_vars[k], c] for k, c in zip(keys, colors)}

def draw_papereffigies_anime(head_center_row, head_center_col, bottom_line, version, snapshot=0 ):
    if 'small' in version:
        
        hair, face, body,collar= ITEM_F.draw_papereffigies(head_center_row, head_center_col, bottom_line, 'small front' )
        body_hair_set = set(body) | set(hair)
        
        if 'right' in version:
            start_offset = max(c for r, c in body_hair_set) - min(c for r, c in collar + face) + 1
            offset = max(start_offset - snapshot, 0)
        elif 'left' in version:
            start_offset = max(c for r, c in collar + face) - min(c for r, c in body_hair_set) + 1
            offset = -max(start_offset - snapshot, 0)   # negative shift, shrinking toward 0

        collar_reveal = [(r, c + offset) for r, c in collar if (r, c + offset) in body_hair_set]
        face_reveal   = [(r, c + offset) for r, c in face   if (r, c + offset) in body_hair_set]
        
        hair_COLOR = [[0,0,0], cgc.hex_to_rgb("#a58598"), 'row']
        body_COLOR = [[0,0,0], cgc.hex_to_rgb("#894861"), 'row']
        
        if 'dark' in version:
            face_COLOR = [cgc.hex_to_rgb("#a17ca4"), 'sigmafactor=0.5']
            collar_COLOR = [cgc.hex_to_rgb("#687975")]
        elif 'light' in version:
            face_COLOR = [cgc.hex_to_rgb("#cfb8d1"), 'sigmafactor=0.5']
            collar_COLOR = [cgc.hex_to_rgb("#a0ada7")]
        keys = ["hair", "body","face_reveal", "collar_reveal",]
    
        colors = [hair_COLOR ,body_COLOR, face_COLOR, collar_COLOR]
    
    elif 'mid' in version:
        hair, hair_front, face, cheeks, eyes, mouth= ITEM_F.draw_papereffigies(head_center_row, head_center_col, bottom_line, 'mid front' )
        hair_COLOR = [[0,0,0], cgc.hex_to_rgb("#a58598"), 'row', 'sigmafactor=0.5']
        hair_front_COLOR = [[0,0,0], cgc.hex_to_rgb("#894861"), 'row', 'sigmafactor=0.5']
        face_COLOR = [cgc.hex_to_rgb("#ffcde7")]
        cheeks_COLOR = [cgc.hex_to_rgb("#dfa2c2")]
        eyes_COLOR = [[0,0,0]]
        mouth_COLOR = [cgc.hex_to_rgb("#bf156c")]
        
        if 'grow' in version:
            
            N_hair = len(set(r for r, c in hair))
            hair_reveal = cga.reveal_rows(hair, min(snapshot, N_hair), reverse=True)
            keys = ["hair_reveal"]
            colors = [hair_COLOR]
        elif 'reveal' in version:
            start_offset = max(r for r, c in face)+5 - min(r for r, c in hair)
            offset = max(start_offset - snapshot, 0)

            face_reveal   = [(r - offset, c) for r, c in face   ]
            cheeks_reveal = [(r - offset, c) for r, c in cheeks ]
            eyes_reveal   = [(r - offset, c) for r, c in eyes   ]
            mouth_reveal  = [(r - offset, c) for r, c in mouth  ]
            face_bot_line = max(r for r,c in face_reveal)
            if face_bot_line<=min(r for r, c in hair) :
                hair_front_reveal = cgd.draw_block((max(r for r,c in face_reveal), 
                                                    (min(c for r,c in face_reveal if r==max(r for r,c in face_reveal))-2,
                                            max(c for r,c in face_reveal if r==max(r for r,c in face_reveal))+2)), bottom_line)
            elif face_bot_line> min(r for r, c in hair) and face_bot_line <max(r for r,c in face) //3:
                hair_front_reveal = cgd.draw_trapezoid(max(r for r,c in face_reveal)-8, 
                                            min(c for r,c in face_reveal if r==max(r for r,c in face_reveal)-8),
                                            max(c for r,c in face_reveal if r==max(r for r,c in face_reveal)-8), bottom_line, 
                                      slope_left = '0.5', slope_right = '0.5', direction = 'lr',)[-2]

            elif face_bot_line>=max(r for r,c in face) //3 and face_bot_line<max(r for r,c in face) //3*2 :
                hair_front_reveal = cgd.draw_trapezoid(max(r for r,c in face_reveal)-8, 
                                            min(c for r,c in face_reveal if r==max(r for r,c in face_reveal)-8),
                                            max(c for r,c in face_reveal if r==max(r for r,c in face_reveal)-8), 
                                            bottom_line, 
                                       slope_left = '0.5 shift', slope_right = '0.5 shift', direction = 'lr',
                                       bend_left = 'left', bend_right = 'right',shift_gap_left = 4, shift_amount_left = 1, 
                      shift_gap_right = 4, shift_amount_right = 1,  )[-2]


            elif face_bot_line>=max(r for r,c in face) //3*2 and face_bot_line<max(r for r,c in face):
                hair_front_reveal = cgd.draw_trapezoid(max(r for r,c in face_reveal)-8, 
                                            min(c for r,c in face_reveal if r==max(r for r,c in face_reveal)-8),
                                            max(c for r,c in face_reveal if r==max(r for r,c in face_reveal)-8), 
                                            bottom_line, 
                                       slope_left = '0.5 shift', slope_right = '0.5 shift', direction = 'lr',
                                       bend_left = 'left', bend_right = 'right',shift_gap_left =3, shift_amount_left = 1, 
                      shift_gap_right = 3, shift_amount_right = 1,  )[-2]
            else:
                hair_front_reveal = hair_front

            keys = ["hair", "hair_front_reveal", "face_reveal","cheeks_reveal", "eyes_reveal", "mouth_reveal"]

        
            colors = [hair_COLOR ,hair_front_COLOR, face_COLOR, cheeks_COLOR, eyes_COLOR, mouth_COLOR]
    
    elif  'big' in version:
        hair_left,hair_right,face,cheek,eyes,eye_socket,eyeball,paint,hand,finger, left_eye_center, right_eye_center = ITEM_F.draw_papereffigies(head_center_row, 
                                                                                                              head_center_col, 
                                                                                                              bottom_line, 'big front' )
        hair_left_COLOR  =[[0,0,0], cgc.hex_to_rgb("#a58598"), 'col max', 'sigmafactor=0.5']
        hair_right_COLOR = [[0,0,0], cgc.hex_to_rgb("#a58598"), 'col min', 'sigmafactor=0.5']
        face_COLOR = [cgc.hex_to_rgb("#e1c8d5")]
        cheek_COLOR = [cgc.hex_to_rgb("#c65c75")]
        eyes_COLOR = [[0,0,0]]
        eye_socket_COLOR = [cgc.hex_to_rgb("#e8f8f0")]
        eyeball_COLOR = [cgc.hex_to_rgb("#f4003a")]
        paint_COLOR =  [cgc.hex_to_rgb("#f4003a"), [0,0,0], 'row']
        
        hand_COLOR =  [cgc.hex_to_rgb("#cb65a2"), cgc.hex_to_rgb("#d3bde7"), 'row']
        finger_COLOR =  [cgc.hex_to_rgb("#cb65a2"), cgc.hex_to_rgb("#d3bde7"), 'row']
         
            
        if 'grow' in version:
            N_hair_left = len(set(c for r, c in hair_left))
            N_hair_right = len(set(c for r, c in hair_right))
            print('N_hair_right', N_hair_right, 'N_hair_left', N_hair_left)
            hair_left_reveal = cga.reveal_cols(hair_left, min(snapshot, N_hair_left), reverse=True)
            hair_right_reveal = cga.reveal_cols(hair_right, min(snapshot, N_hair_right), reverse=False)

            keys = ["hair_left_reveal", "hair_right_reveal", ]
            colors = [hair_left_COLOR, hair_right_COLOR]
            
        elif 'reveal' in version:
            hair_set = set(hair_left) | set(hair_right)
            face_left = [(r,c) for r,c in face if c<=head_center_col]
            face_right = [(r,c) for r,c in face if c>=head_center_col]
            cheek_left = [(r,c) for r,c in cheek if c<=head_center_col]
            cheek_right = [(r,c) for r,c in cheek if c>=head_center_col]
            eyes_left = [(r,c) for r,c in eyes if c<=head_center_col]
            eyes_right = [(r,c) for r,c in eyes if c>=head_center_col]

            eye_socket_left = [(r,c) for r,c in eye_socket if c<=head_center_col]
            eye_socket_right = [(r,c) for r,c in eye_socket if c>=head_center_col]

            left_group  = face_left  + cheek_left  + eyes_left
            right_group = face_right + cheek_right + eyes_right

            start_offset_left = max(c for r, c in left_group) - min(c for r, c in hair_set) + 1
            offset_left = -max(start_offset_left - snapshot, 0)


            face_left_reveal  = [(r, c + offset_left) for r, c in face_left  if (r, c + offset_left) in hair_set]
            cheek_left_reveal = [(r, c + offset_left) for r, c in cheek_left if (r, c + offset_left) in hair_set]
            eyes_left_reveal  = [(r, c + offset_left) for r, c in eyes_left  if (r, c + offset_left) in hair_set]

            # "_right" parts: enter from the right (positive offset, shrinks toward 0)
            start_offset_right = max(c for r, c in hair_set) - min(c for r, c in right_group) + 1
            offset_right = max(start_offset_right - snapshot, 0)

            face_right_reveal  = [(r, c + offset_right) for r, c in face_right  if (r, c + offset_right) in hair_set]
            cheek_right_reveal = [(r, c + offset_right) for r, c in cheek_right if (r, c + offset_right) in hair_set]
            eyes_right_reveal  = [(r, c + offset_right) for r, c in eyes_right  if (r, c + offset_right) in hair_set]

            eye_socket_left  = [(r, c) for r, c in eye_socket if c <= head_center_col]
            eye_socket_right = [(r, c) for r, c in eye_socket if c >= head_center_col]

            N_eye = len(set(r for r, c in eye_socket))   # single shared count, not split left/right

            reveal_rows_left  = max(N_eye + offset_left,  0)
            reveal_rows_right = max(N_eye - offset_right, 0)

            eye_socket_left_reveal = cga.reveal_rows(
                [(r, c + offset_left) for r, c in eye_socket_left if (r, c + offset_left) in hair_set],
                reveal_rows_left, reverse=False
                )
            eye_socket_right_reveal = cga.reveal_rows(
                [(r, c + offset_right) for r, c in eye_socket_right if (r, c + offset_right) in hair_set],
                reveal_rows_right, reverse=False
                )

            N_finish_slide = max(start_offset_left, start_offset_right)+10
            sub_snapshot_eyeball = max(snapshot - N_finish_slide, 0)   # 0 until slide's done, then starts counting

            N_eyeball = 4
            eyeball_left  = [(r, c) for r, c in eyeball if c <= head_center_col]
            eyeball_right = [(r, c) for r, c in eyeball if c >= head_center_col]

            s_eyeball  = min(sub_snapshot_eyeball, N_eyeball)

            eyeball_left_reveal = cga.reveal_hex(eyeball_left,  s_eyeball,  left_eye_center,  N_eyeball,  reverse=False, start_n=0)
            eyeball_right_reveal = cga.reveal_hex(eyeball_right,s_eyeball,  right_eye_center,  N_eyeball,  reverse=False, start_n=0)

            N_finish_eyeball = N_finish_slide + N_eyeball+10

            sub_snapshot_paint = max(snapshot - N_finish_eyeball, 0)
            N_paint = len(set(r for r, c in paint))
            paint_reveal = cga.reveal_rows(paint, min(sub_snapshot_paint, N_paint), reverse=False)

            sub_snapshot_hand = max(snapshot - N_finish_eyeball, 0)
            hand_above = [(r,c) for r,c in hand if r<=bottom_line]
            hand_below = [(r,c) for r,c in hand if r>=bottom_line]
            N_above = len(set(r for r, c in hand_above))
            N_below = len(set(r for r, c in hand_below))
            N_hand  = max(N_above, N_below)        # one shared pace for both

            s_hand = min(sub_snapshot_hand, N_hand)

            hand_above_reveal = cga.reveal_rows(hand_above, min(s_hand, N_above), reverse=True)   # starts at bottom_line, grows upward
            hand_below_reveal = cga.reveal_rows(hand_below, min(s_hand, N_below), reverse=False)  # starts at bottom_line, grows downward

            N_finish_hand = N_finish_eyeball + N_hand+10
            sub_snapshot_finger = max(snapshot - N_finish_hand, 0)

            N_finger = len(set(r for r, c in finger))
            finger_reveal = cga.reveal_rows(finger, min(sub_snapshot_finger, N_finger), reverse=False)

           
            keys = ["hair_left", "hair_right", 
                    "face_left_reveal","face_right_reveal", 
                    "cheek_left_reveal", "cheek_right_reveal",
                    "eyes_left_reveal", "eyes_right_reveal",
                   "eye_socket_left_reveal", "eye_socket_right_reveal", 
                   "eyeball_left_reveal", "eyeball_right_reveal",
                   "paint_reveal", 
                   "hand_above_reveal", "hand_below_reveal", "finger_reveal" ]

            colors = [hair_left_COLOR ,hair_right_COLOR, face_COLOR, face_COLOR, cheek_COLOR, cheek_COLOR, eyes_COLOR, eyes_COLOR,
                     eye_socket_COLOR, eye_socket_COLOR , eyeball_COLOR, eyeball_COLOR, paint_COLOR, hand_COLOR, hand_COLOR,finger_COLOR]
    local_vars = locals()
    return {k: [local_vars[k], c] for k, c in zip(keys, colors)}

def draw_plant_pot_anime(center_row, center_col, name, snapshot=0):
    if  "spider lily top" in name:
        pot_in, pot_mid, pot_out, flower = ITEM_F.draw_plant_pot(center_row, center_col, "spider lily top")
        center = (center_row, center_col)
        N = 5  
         
        pot_in_stages  = ([cga.reveal_hex(pot_in,  s, center, N, start_n=1) for s in range(N+1)]
                         + [pot_in]*(N+1)
                         + [cga.reveal_hex(pot_in,  s, center, N, start_n=1) for s in range(N, -1, -1)]
                         + [[]]*(N+1))
        pot_mid_stages = ([cga.reveal_hex(pot_mid, s, center, N, start_n=1) for s in range(N+1)]
                         + [pot_mid]*(N+1)
                         + [cga.reveal_hex(pot_mid, s, center, N, start_n=1) for s in range(N, -1, -1)]
                         + [[]]*(N+1))
        pot_out_stages = ([cga.reveal_hex(pot_out, s, center, N, start_n=1) for s in range(N+1)]
                         + [pot_out]*(N+1)
                         + [cga.reveal_hex(pot_out, s, center, N, start_n=1) for s in range(N, -1, -1)]
                         + [[]]*(N+1))
        flower_stages  = ([[] for _ in range(N+1)]
                         + [cga.reveal_hex(flower, s, center, N, start_n=1) for s in range(N+1)]
                         + [flower]*(N+1)
                         + [cga.reveal_hex(flower, s, center, N, start_n=1) for s in range(N, -1, -1)])

        idx = snapshot % len(pot_in_stages)
        #print(len(pot_in_stages))
        pot_in_reveal, pot_mid_reveal, pot_out_reveal, flower_reveal = (
            pot_in_stages[idx], pot_mid_stages[idx], pot_out_stages[idx], flower_stages[idx]
        )

        if "red" in name:
            pot_in_COLOR =[cgc.hex_to_rgb("#15a27c")]
            pot_mid_COLOR =[[1,1,1]]
            pot_out_COLOR =[[1,0,0]]
            flower_COLOR =[cgc.hex_to_rgb("#ff0017"),cgc.hex_to_rgb("#ad0010"), [(center_row, center_col), 3,0,3, 'hex']]
        elif "white" in name:
            pot_in_COLOR =[cgc.hex_to_rgb("#15a27c")]
            pot_mid_COLOR =[[1,0,0]]
            pot_out_COLOR =[[1,1,1]]
            flower_COLOR =[cgc.hex_to_rgb("#fddede"),cgc.hex_to_rgb("#ebe4e4"), [(center_row, center_col), 3,0,3, 'hex']]
            
        keys = ["pot_out_reveal", "pot_mid_reveal", "pot_in_reveal", "flower_reveal"]
        
        colors = [pot_out_COLOR,  pot_mid_COLOR,pot_in_COLOR,flower_COLOR]
    
    elif  "spider lily side" in name:
        root, soil, pot ,stem, spiderlily_in, spiderlily_out = ITEM_F.draw_plant_pot(center_row, center_col, "spider lily side")
        root+=stem
        Stage_grow_out = [(r,c) for r,c in spiderlily_out if r != max(row for row,col in spiderlily_out)]
        Stage_die_out = [(r,c) for r,c in spiderlily_out if r <min(row for row,col in spiderlily_out)+2]
        Stage_die_in = [(r,c) for r,c in spiderlily_out if r >=min(row for row,col in spiderlily_out)+2
                     ]+spiderlily_in
        N_in  = len(set(r for r,c in spiderlily_in))
        N_out = len(set(r for r,c in Stage_grow_out))
        
        N_die_out = len(set(r for r,c in Stage_die_out))
        N_die_in = len(set(r for r,c in Stage_die_in))

        in_stages  = ([[]]*(N_out+1) + [cga.reveal_rows(spiderlily_in, s, reverse=True) for s in range(N_in+1)]
                    + [Stage_die_in]*(N_die_out+1)+ [cga.reveal_rows(Stage_die_in, s, reverse=True) for s in range(N_die_in, -1, -1)])
        out_stages = ([cga.reveal_rows(Stage_grow_out, s, reverse=True) for s in range(N_out+1)] + [spiderlily_out]*(N_in+1)
                    + [cga.reveal_rows(Stage_die_out, s, reverse=True) for s in range(N_die_out, -1, -1)]+ [[]]*(N_die_in+1))

        
        root_reveal = cga.reveal_rows(root, snapshot, reverse=False)
        soil_reveal = cga.reveal_rows(soil, snapshot, reverse=False)
        pot_reveal = cga.reveal_rows(pot, snapshot, reverse=False)
        
        N_root = len(set(r for r,c in root))
        N_soil = len(set(r for r,c in soil))
        N_pot  = len(set(r for r,c in pot))
        N_grow = max(N_root, N_soil, N_pot)   # whichever is tallest sets the pace

        # Phase 1: grow together, row by row. Shorter ones hit their own
        # full count early and just hold there (via min-clamp) while the
        # tallest keeps revealing rows until everyone's full.
        root_grow = [cga.reveal_rows(root, min(s, N_root), reverse=False) for s in range(N_grow+1)]
        soil_grow = [cga.reveal_rows(soil, min(s, N_soil), reverse=False) for s in range(N_grow+1)]
        pot_grow  = [cga.reveal_rows(pot,  min(s, N_pot),  reverse=False) for s in range(N_grow+1)]

        # Phase 2: hold fully revealed for exactly as long as the spiderlily
        # grow/die cycle takes.
        root_hold = [root] * len(out_stages)
        soil_hold = [soil] * len(out_stages)
        pot_hold  = [pot]  * len(out_stages)
        
        root_shrink = [cga.reveal_rows(root, min(s, N_root), reverse=False) for s in range(N_grow, -1, -1)]
        soil_shrink = [cga.reveal_rows(soil, min(s, N_soil), reverse=False) for s in range(N_grow, -1, -1)]
        pot_shrink  = [cga.reveal_rows(pot,  min(s, N_pot),  reverse=False) for s in range(N_grow, -1, -1)]

        root_stages = root_grow + root_hold + root_shrink
        soil_stages = soil_grow + soil_hold + soil_shrink
        pot_stages  = pot_grow  + pot_hold  + pot_shrink
        
        spiderlily_out_stages = [[]]*len(pot_grow) + out_stages + [[]]*len(pot_shrink)
        spiderlily_in_stages  = [[]]*len(pot_grow) + in_stages  + [[]]*len(pot_shrink)

        cycle_len = len(pot_stages)   # == len(root_stages) == len(soil_stages) == len(spiderlily_out_stages) == len(spiderlily_in_stages)
        idx = snapshot % cycle_len

        root_reveal = root_stages[idx]
        soil_reveal = soil_stages[idx]
        pot_reveal  = pot_stages[idx]
        spiderlily_in_reveal  = spiderlily_in_stages[idx]
        spiderlily_out_reveal = spiderlily_out_stages[idx]
        

        
        if "red" in name:
            spiderlily_in_COLOR = [[1,0,0], cgc.hex_to_rgb("#d10013")]
            spiderlily_out_COLOR =  [cgc.hex_to_rgb("#a2153b"), [1,0,0]]
            soil_COLOR = [[1,0,0]]
        elif "white" in name:
            spiderlily_in_COLOR = [[1,1,1], cgc.hex_to_rgb("#d8e6e6")]
            spiderlily_out_COLOR =  [cgc.hex_to_rgb("#defdf9"), [1,1,1]]
            soil_COLOR = [[1,1,1]]
            
        root_COLOR = [cgc.hex_to_rgb("#1e4941")]
        pot_COLOR = [cgc.hex_to_rgb("#15a27c")]
        
        keys = ["pot_reveal", "soil_reveal", "root_reveal", "spiderlily_in_reveal", "spiderlily_out_reveal"]
        
        colors = [pot_COLOR,soil_COLOR,  root_COLOR, spiderlily_in_COLOR, spiderlily_out_COLOR]
    
    elif  "spider lily pot" in name:
        root, soil, pot= ITEM_F.draw_plant_pot(center_row, center_col, "spider lily pot")
        
        root_reveal = cga.reveal_rows(root, snapshot, reverse=False)
        soil_reveal = cga.reveal_rows(soil, snapshot, reverse=False)
        pot_reveal = cga.reveal_rows(pot, snapshot, reverse=False)
        
        N_root = len(set(r for r,c in root))
        N_soil = len(set(r for r,c in soil))
        N_pot  = len(set(r for r,c in pot))
        N_grow = max(N_root, N_soil, N_pot)   # whichever is tallest sets the pace

        # Phase 1: grow together, row by row. Shorter ones hit their own
        # full count early and just hold there (via min-clamp) while the
        # tallest keeps revealing rows until everyone's full.
        root_grow = [cga.reveal_rows(root, min(s, N_root), reverse=False) for s in range(N_grow+1)]
        soil_grow = [cga.reveal_rows(soil, min(s, N_soil), reverse=False) for s in range(N_grow+1)]
        pot_grow  = [cga.reveal_rows(pot,  min(s, N_pot),  reverse=False) for s in range(N_grow+1)]

        root_shrink = [cga.reveal_rows(root, min(s, N_root), reverse=False) for s in range(N_grow, -1, -1)]
        soil_shrink = [cga.reveal_rows(soil, min(s, N_soil), reverse=False) for s in range(N_grow, -1, -1)]
        pot_shrink  = [cga.reveal_rows(pot,  min(s, N_pot),  reverse=False) for s in range(N_grow, -1, -1)]

        root_stages = root_grow + root_shrink
        soil_stages = soil_grow + soil_shrink
        pot_stages  = pot_grow  + pot_shrink
        
        cycle_len = len(pot_stages)   # == len(root_stages) == len(soil_stages) == len(spiderlily_out_stages) == len(spiderlily_in_stages)
        idx = snapshot % cycle_len

        root_reveal = root_stages[idx]
        soil_reveal = soil_stages[idx]
        pot_reveal  = pot_stages[idx]
        if "red" in name:
            soil_COLOR = [[1,0,0]]
            root_COLOR = [[1,1,1]]
        elif "white" in name:
            soil_COLOR = [[1,1,1]]
            root_COLOR = [[1,0,0]]
        
        pot_COLOR = [cgc.hex_to_rgb("#15a27c")]
        
        keys = ["pot_reveal", "soil_reveal", "root_reveal"]
        colors = [pot_COLOR,soil_COLOR,  root_COLOR]
    local_vars = locals()
    
    return {k: [local_vars[k], c] for k, c in zip(keys, colors)}



def draw_flower_anime(center_row, center_col, name, snapshot=0):
    if name == "spider lily top":
        
        spiderlily_in, spiderlily_out = ITEM_F.draw_spiderlily(center_row, center_col, 'top')
        spiderlily_reveal = cga.reveal_hex(spiderlily_out, snapshot, (center_row, center_col), 6, reverse=False, start_n=1)
        
        

        keys = ["spiderlily_in", "spiderlily_reveal"]
        
        colors = [[cgc.hex_to_rgb("#5b6000")],  
                  [cgc.hex_to_rgb("#ff0017"),cgc.hex_to_rgb("#ad0010"), [(center_row, center_col), 3,0,3, 'hex']]
             ]
    elif name == "spider lily side":
        stem, spiderlily_in, spiderlily_out = ITEM_F.draw_spiderlily(center_row, center_col, 'side')
        
        Stage_grow_out = [(r,c) for r,c in spiderlily_out if r != max(row for row,col in spiderlily_out)]
        Stage_die_out = [(r,c) for r,c in spiderlily_out if r <min(row for row,col in spiderlily_out)+2]
        Stage_die_in = [(r,c) for r,c in spiderlily_out if r >=min(row for row,col in spiderlily_out)+2
                     ]+spiderlily_in
        
        N_in  = len(set(r for r,c in spiderlily_in))
        N_out = len(set(r for r,c in Stage_grow_out))
        
        N_die_out = len(set(r for r,c in Stage_die_out))
        N_die_in = len(set(r for r,c in Stage_die_in))

        in_stages  = ([[]]*(N_out+1) + [cga.reveal_rows(spiderlily_in, s, reverse=True) for s in range(N_in+1)]
                    + [Stage_die_in]*(N_die_out+1)+ [cga.reveal_rows(Stage_die_in, s, reverse=True) for s in range(N_die_in, -1, -1)])
        out_stages = ([cga.reveal_rows(Stage_grow_out, s, reverse=True) for s in range(N_out+1)] + [spiderlily_out]*(N_in+1)
                    + [cga.reveal_rows(Stage_die_out, s, reverse=True) for s in range(N_die_out, -1, -1)]+ [[]]*(N_die_in+1))

        
        spiderlily_out_reveal = out_stages[snapshot % len(out_stages)]
        spiderlily_in_reveal  = in_stages[snapshot % len(in_stages)]
        
        keys = ["stem", "spiderlily_in_reveal", "spiderlily_out_reveal"]#
        
        colors = [[cgc.hex_to_rgb("#067228")], 
                  [[1,0,0], cgc.hex_to_rgb("#d10013")], [cgc.hex_to_rgb("#bb0616"), [1,0,0]]
             ]   #
    elif name == "jimsonweed top":
        
        jimsonweed_in, jimsonweed_out = ITEM_F.draw_jimsonweed(center_row, center_col, 'top')
        stages = [(1,0), (2,2), (1,2), (1,3), (1,4), (1,4), (1,4), (1,3), (1,2), (1,1), (1,0)]
        in_snap, out_snap = stages[snapshot % len(stages)]

        jimsonweed_in_reveal  = cga.reveal_hex(jimsonweed_in,  in_snap,  (center_row, center_col), 2, start_n=0)
        jimsonweed_out_reveal = cga.reveal_hex(jimsonweed_out, out_snap, (center_row, center_col), 3, start_n=0)
        
        keys = ["jimsonweed_out_reveal", "jimsonweed_in_reveal", ]
        
        colors = [[cgc.hex_to_rgb("#fffcb9"), cgc.hex_to_rgb("#ffe885"), [(center_row, center_col), 3,0,3, 'hex']],
                  [cgc.hex_to_rgb("#c2df85")], 
                 ]
    elif name == "jimsonweed side":    
        stem, jimsonweed_bot, jimsonweed_mid, jimsonweed_top = ITEM_F.draw_jimsonweed(center_row, center_col, 'side')
        jimsonweed_full = stem+jimsonweed_bot+jimsonweed_mid+jimsonweed_top
        
        stage_die_1 = [(r,c) for r,c in jimsonweed_full if c!=max(col for row, col in jimsonweed_full) and 
                        c!=min(col for row, col in jimsonweed_full)]
        stage_die_2_keep_region =  cgd.draw_block((center_row, (center_col-1,center_col+1 )), max(r for r,c in jimsonweed_full))
        stage_die_2 = [(r,c) for r,c in jimsonweed_full if (r,c) in stage_die_2_keep_region]
        
        stage_die_3_keep_region =  cgd.verticle_line(center_row, center_col, max(r for r,c in jimsonweed_full), bend = 'left'
                                    )+cgd.verticle_line(center_row, center_col, max(r for r,c in jimsonweed_full), bend = 'right'
                                    )

        stage_die_3 = [(r,c) for r,c in jimsonweed_full if (r,c) in stage_die_3_keep_region]
        
        N_die3 = len(set(r for r,c in stage_die_3))
       
        N_stem = len(set(r for r,c in stem))
        N_bot  = len(set(r for r,c in jimsonweed_bot))
        N_mid  = len(set(r for r,c in jimsonweed_mid))
        N_top  = len(set(r for r,c in jimsonweed_top))

        die_regions = ([stage_die_1, stage_die_2, stage_die_3]
             + [cga.reveal_rows(stage_die_3, s, reverse=False) for s in range(N_die3-1, 0, -1)]
             + [[(center_row, center_col)]])

        stem_stages = ([cga.reveal_rows(stem, s, reverse=False) for s in range(1, N_stem+1)]
             + [stem]*(N_bot+N_mid+N_top+2)
             + [[(r,c) for r,c in stem if (r,c) in R] for R in die_regions])
        bot_stages  = ([[]]*N_stem
                     + [cga.reveal_rows(jimsonweed_bot, s, reverse=False) for s in range(1, N_bot+1)]
                     + [jimsonweed_bot]*(N_mid+N_top+2)
                     + [[(r,c) for r,c in jimsonweed_bot if (r,c) in R] for R in die_regions])
        mid_stages  = ([[]]*(N_stem+N_bot)
                     + [cga.reveal_rows(jimsonweed_mid, s, reverse=False) for s in range(1, N_mid+1)]
                     + [jimsonweed_mid]*(N_top+2)
                     + [[(r,c) for r,c in jimsonweed_mid if (r,c) in R] for R in die_regions])
        top_stages  = ([[]]*(N_stem+N_bot+N_mid)
                     + [cga.reveal_rows(jimsonweed_top, s, reverse=False) for s in range(1, N_top+1)]
                     + [jimsonweed_top]*2
                     + [[(r,c) for r,c in jimsonweed_top if (r,c) in R] for R in die_regions])

        stem_reveal = stem_stages[snapshot % len(stem_stages)]
        bot_reveal  = bot_stages[snapshot % len(stem_stages)]
        mid_reveal  = mid_stages[snapshot % len(stem_stages)]
        top_reveal  = top_stages[snapshot % len(stem_stages)]

                                                
        #print(len(stem_stages), len(bot_stages), len(mid_stages), len(top_stages), )
        keys = ["stem_reveal", "bot_reveal","mid_reveal","top_reveal" ]
        
        colors = [[cgc.hex_to_rgb("#326b1a"), cgc.hex_to_rgb("#a7c861")],  [cgc.hex_to_rgb("#c8c761"), cgc.hex_to_rgb("#faf989")], 
              [cgc.hex_to_rgb("#faf989"), cgc.hex_to_rgb("#ffd056")], [cgc.hex_to_rgb("#fffcb9")], 
                 ]
        
        
    elif name == "ghost plant top":
        ghostplant_in, ghostplant_mid_left, ghostplant_out_left = ITEM_F.draw_ghostplant(center_row, center_col, 'top left')
        _, ghostplant_mid_right, ghostplant_out_right = ITEM_F.draw_ghostplant(center_row, center_col, 'top right')
        
        ghostplant_out_left_stage1 = [(r,c) for r,c in ghostplant_out_left if (r,c) 
                                 not in cg.hex_neighbours_n(center_row, center_col, n=2, keep_origin =False , return_frontier=True)[-1]]
        ghostplant_out_right_stage1 = [(r,c) for r,c in ghostplant_out_right if (r,c) 
                                 not in cg.hex_neighbours_n(center_row, center_col, n=2, keep_origin =False , return_frontier=True)[-1]]
        
        ghostplant_out_left_stage2 = [(r,c) for r,c in ghostplant_out_left if (r,c) 
                                 not in cg.get_hex_corners(center_row, center_col, 2)]
        ghostplant_out_right_stage2 = [(r,c) for r,c in ghostplant_out_right if (r,c) 
                                 not in cg.get_hex_corners(center_row, center_col, 2)]
        
        
        ghostplant_out_left_stage3 = ghostplant_out_left
        ghostplant_out_right_stage3 = ghostplant_out_right
        
        stages = [(ghostplant_mid_right, ghostplant_out_right_stage1),
                  (ghostplant_mid_left,  ghostplant_out_left_stage1),
                  
                  (ghostplant_mid_right, ghostplant_out_right_stage2),
                  (ghostplant_mid_left, ghostplant_out_left_stage2),
                  
                  (ghostplant_mid_right,  ghostplant_out_right_stage3),
                  (ghostplant_mid_left,  ghostplant_out_left_stage3),
                  
                  (ghostplant_mid_right, ghostplant_out_right_stage2),
                  (ghostplant_mid_left, ghostplant_out_left_stage2),
                  ]

        ghostplant_mid, ghostplant_out_reveal = stages[snapshot % len(stages)]
        #ghostplant_out_reveal = ghostplant_out_reveal_raw#[(r,c) for r,c in ghostplant_out_reveal_raw if (r,c) not in ghostplant_mid]
        keys = ["ghostplant_in","ghostplant_out_reveal", "ghostplant_mid", ]
        
        colors = [[cgc.hex_to_rgb("#91dbef")],[cgc.hex_to_rgb("#f3fcff")], [cgc.hex_to_rgb("#d4ad6b")], 
                 ]
    
    elif "ghost plant side down" in name:
        stem, flower_bot, flower_mid, flower_top = ITEM_F.draw_ghostplant(center_row, center_col, name)
        if 'left' in name:
            center = (min(r for r,c in stem), min(c for r,c in stem if r==min(r for r,c in stem)))
        elif 'right' in name:
            center = (min(r for r,c in stem), max(c for r,c in stem if r==min(r for r,c in stem)))
      
        regions = [cg.hex_neighbours_n(center[0], center[1], n=n) for n in range(6)]
        
        reveal_line = cgd.draw_slope_0p5_diagonal(center[0], center[1], center[0]+6, 
                                                  left_down=True, right_down=True, left_up=True, right_up=True)
        stages = regions + [[pt for pt in reveal_line if pt in region] for region in reversed(regions)]
        reveal_region = stages[snapshot % len(stages)]

        flower_bot_reveal = [pt for pt in flower_bot if pt in reveal_region]
        flower_mid_reveal = [pt for pt in flower_mid if pt in reveal_region]
        flower_top_reveal = [pt for pt in flower_top if pt in reveal_region]
        
        keys = ["stem","flower_bot_reveal", "flower_mid_reveal", "flower_top_reveal"]
        
        colors = [[cgc.hex_to_rgb("#eafaff"), cgc.hex_to_rgb("#d1d1c3")], [cgc.hex_to_rgb("#eafaff")], [cgc.hex_to_rgb("#f3fcff")], [cgc.hex_to_rgb("#ffc93e")],
                 ]
        
    elif "ghost plant side up" in name:
        stem, flower_bot, flower_mid= ITEM_F.draw_ghostplant(center_row, center_col, name)
        if 'left' in name:
            center_stem = (min(r for r,c in stem), min(c for r,c in stem if r==min(r for r,c in stem)))
            center_flower = (min(r for r,c in flower_bot), min(c for r,c in flower_bot if r==min(r for r,c in flower_bot)))
        elif 'right' in name:
            center_stem = (min(r for r,c in stem), max(c for r,c in stem if r==min(r for r,c in stem)))
            center_flower = (min(r for r,c in flower_bot), max(c for r,c in flower_bot if r==min(r for r,c in flower_bot)))
      
        regions1 = [cg.hex_neighbours_n(center_stem[0], center_stem[1], n=n) for n in range(4)]
        regions2 = [cg.hex_neighbours_n(center_flower[0], center_flower[1], n=n) for n in range(4)]
        
        stages = regions1+regions2+list(reversed(regions2))+list(reversed(regions1))
        idx = snapshot % len(stages)
        reveal_region = stages[idx]

        if idx < len(regions1) or idx >= len(regions1)+2*len(regions2):
            flower_bot_reveal = [pt for pt in flower_bot if pt in reveal_region]
            flower_mid_reveal = []
        else:
            flower_bot_reveal = flower_bot
            flower_mid_reveal = [pt for pt in flower_mid if pt in reveal_region]

        keys = ["stem","flower_bot_reveal", "flower_mid_reveal"]
        
        colors = [[cgc.hex_to_rgb("#eafaff"), cgc.hex_to_rgb("#d1d1c3")], [cgc.hex_to_rgb("#eafaff")], [cgc.hex_to_rgb("#f3fcff")], 
                 ]
    local_vars = locals()
    
    return {k: [local_vars[k], c] for k, c in zip(keys, colors)}


