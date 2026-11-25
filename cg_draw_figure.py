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
def draw_basic_lines(head_center_row, head_center_col, n, version="7"):
    if version not in ("7", "5", "3"):
        raise ValueError("version must be '7', '5' or '3'")
 
    head_size = n*2
    skull_size = int(head_size*(2/3))
 
    # "eff_*" are the step sizes the rest of the figure is laid out with.
    # version 7 uses the raw head/skull size; versions 5 and 3 use half of it.
    eff_head_size = head_size if version == "7" else head_size//2
    eff_skull_size = skull_size if version == "7" else int(max(1, eff_head_size*(2/3)))
    eff_n = n if version == "7" else max(1, n//2)
 
    head_top_r = head_center_row-n
    skull_end_r = head_top_r+skull_size
 
    #measure by skull size
    if version == "7":
        shoulder_joint_r = skull_end_r+eff_skull_size
    else:
        shoulder_joint_r = max(head_center_row+n+1, skull_end_r+eff_skull_size)
    deltoid_end_r = shoulder_joint_r+eff_skull_size
    elbow_r = ribcage_end_r = deltoid_end_r+eff_skull_size
    wrist_r = elbow_r+eff_skull_size+eff_skull_size
 
    #measure by head size
    jaw_end_r = head_center_row+n
 
    breastbone_end_r = jaw_end_r+eff_head_size
    bellybutton_r = breastbone_end_r+eff_head_size
    femoral_head_r = bellybutton_r+eff_head_size
    sartorius_turning_r = femoral_head_r+eff_head_size
    knee_r = femoral_head_r+eff_head_size+eff_head_size
    gastrocnemius_end_r = knee_r+eff_head_size
    foot_r = knee_r+eff_head_size+eff_head_size
 
    ribcage_start_r = jaw_end_r+(shoulder_joint_r-jaw_end_r)//2
 
    exclude = {"head_center_row", "head_center_col",  "version"}
    line_dict = {k: v for k, v in locals().items() if k not in exclude}
 
    return line_dict
'''
def draw_basic_lines(head_center_row, head_center_col, n):
    
    #head_raw = cg.hex_neighbours_n(head_center_row,head_center_col, n=n, keep_origin = True)
    
    head_size = 2*n
    skull_size = int( head_size*(2/3) )
    
    head_top_r = head_center_row-n
    skull_end_r = head_top_r+skull_size
    
    #measure by skull size
    shoulder_joint_r = skull_end_r+skull_size
    deltoid_end_r = shoulder_joint_r+skull_size
    elbow_r = ribcage_end_r = deltoid_end_r+skull_size
    wrist_r = elbow_r+skull_size+skull_size
    
    
    #measure by head size
    jaw_end_r = head_center_row+n
    
    breastbone_end_r = jaw_end_r+head_size
    bellybutton_r = breastbone_end_r+head_size
    femoral_head_r = bellybutton_r+head_size
    sartorius_turning_r = femoral_head_r+head_size
    knee_r = femoral_head_r+head_size+head_size
    gastrocnemius_end_r = knee_r+head_size
    foot_r = knee_r+head_size+head_size
    
    ribcage_start_r = jaw_end_r+(shoulder_joint_r-jaw_end_r)//2
    
    exclude = {"head_center_row", "head_center_col", "n"}
    line_dict = {k: v for k, v in locals().items() if k not in exclude}

    return line_dict
'''
def draw_torso(head_size, neck, shoulder_joint_r, breastbone_end_r, ribcage_end_r, bellybutton_r, femoral_head_r):
    neck2_shoulder = cgd.draw_trapezoid(max(r for r,c in neck), 
                                        min(c for r,c in neck if r == max(r for r,c in neck)) ,
                                        max(c for r,c in neck if r == max(r for r,c in neck)) , shoulder_joint_r, 
                               slope_left = '0.5', slope_right = '0.5', direction = 'lr',bend_left = 'left', bend_right = 'right'
                              )[-2]
    chest = cgd.draw_trapezoid(max(r for r,c in neck2_shoulder), 
                               min(c for r,c in neck2_shoulder if r == max(r for r,c in neck2_shoulder)) , 
                               max(c for r,c in neck2_shoulder if r == max(r for r,c in neck2_shoulder)) , breastbone_end_r, 
                               slope_left = 'inf', slope_right = 'inf', direction = 'rl',
                  bend_left = 'left', bend_right = 'right')[-2]
    
    ribcage = cgd.draw_trapezoid(max(r for r,c in chest), min(c for r,c in chest if r == max(r for r,c in chest)), 
                                max(c for r,c in chest if r == max(r for r,c in chest)), ribcage_end_r, 
                               slope_left = 'inf', slope_right = 'inf', direction = 'rl',
                  bend_left = 'left', bend_right = 'right')[-2]
    waist = cgd.draw_trapezoid(max(r for r,c in ribcage), min(c for r,c in ribcage if r == max(r for r,c in ribcage)), 
                                max(c for r,c in ribcage if r == max(r for r,c in ribcage)), bellybutton_r, 
                               slope_left = 'inf', slope_right = 'inf', direction = 'lr',
                  bend_left = 'right', bend_right = 'left')[-2]
    
    
    pelvis_part1 = cgd.draw_trapezoid(max(r for r,c in waist), min(c for r,c in waist if r == max(r for r,c in waist)), 
                                max(c for r,c in waist if r == max(r for r,c in waist)), max(r for r,c in waist)+head_size//2, 
                               slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                  bend_left = 'left', bend_right = 'right')[-2]
    
    pelvis_part3 = cgd.draw_trapezoid(max(r for r,c in pelvis_part1), min(c for r,c in pelvis_part1 if r == max(r for r,c in pelvis_part1)), 
                       max(c for r,c in pelvis_part1 if r == max(r for r,c in pelvis_part1)), max(r for r,c in pelvis_part1)+head_size//3, 
                               slope_left = '0.5', slope_right = '0.5', direction = 'rl',
                  bend_left = 'left', bend_right = 'right')[-2]
    pelvis_part4 = cgd.draw_trapezoid(max(r for r,c in pelvis_part3), min(c for r,c in pelvis_part3 if r == max(r for r,c in pelvis_part3)), 
                       max(c for r,c in pelvis_part3 if r == max(r for r,c in pelvis_part3)), femoral_head_r, 
                               slope_left = '1.5', slope_right = '1.5', direction = 'rl',
                  bend_left = 'left', bend_right = 'right')[-2]
    
    pelvis= pelvis_part1+pelvis_part3+pelvis_part4
    torso = neck2_shoulder+chest+ribcage+waist+pelvis
    keys = [ "neck2_shoulder",  "chest", "ribcage", "waist", "pelvis", "torso", "pelvis_part1", "pelvis_part3", "pelvis_part4"]
    local_vars = locals()
    torso_dict = {k: local_vars[k] for k in keys}
    return torso_dict
    
    
def draw_head(head_center_row,head_center_col, head_raw, skull_end_r, jaw_end_r, n_skull):
    remove_head =[]
    for row in range(skull_end_r+1, jaw_end_r+1, 1):
        remove_head += [(row,min(c for r,c in head_raw if r == row)), (row,max(c for r,c in head_raw if r == row))]
    
    skull = cg.hex_neighbours_n(head_center_row,head_center_col, n=n_skull, keep_origin = True)
    head = [(r,c) for r,c in head_raw if (r,c) not in remove_head]
    jaw = [(r,c) for r,c in head if r >skull_end_r]
    full_head = skull+jaw
    keys = [ "skull",  "jaw", "full_head",]

    local_vars = locals()
    head_dict = {k: local_vars[k] for k in keys}
    return head_dict

def draw_upperlimb_joint(left_shoulder_joint_row, left_shoulder_joint_c, right_shoulder_joint_row, right_shoulder_joint_c, n_shoulder_joint,
                   left_elbow_joint_row, left_elbow_joint_c, right_elbow_joint_row,  right_elbow_joint_c, n_elbow_joint,
                  left_wrist_joint_row, left_wrist_joint_c, right_wrist_joint_row, right_wrist_joint_c, n_wrist_joint):
    
    left_shoulder_joint = cg.hex_neighbours_n(left_shoulder_joint_row,left_shoulder_joint_c, n=n_shoulder_joint, keep_origin = True)
    right_shoulder_joint = cg.hex_neighbours_n(right_shoulder_joint_row,right_shoulder_joint_c, n=n_shoulder_joint, keep_origin = True)
    
    left_elbow_joint = cg.hex_neighbours_n(left_elbow_joint_row,left_elbow_joint_c, n=n_elbow_joint, keep_origin = True)
    right_elbow_joint = cg.hex_neighbours_n(right_elbow_joint_row,right_elbow_joint_c , n=n_elbow_joint, keep_origin = True)
    
    left_wrist_joint = cg.hex_neighbours_n(left_wrist_joint_row,left_wrist_joint_c, n=n_wrist_joint, keep_origin = True)
    right_wrist_joint = cg.hex_neighbours_n(right_wrist_joint_row,right_wrist_joint_c, n=n_wrist_joint, keep_origin = True)
    
    full_joints = left_shoulder_joint+right_shoulder_joint+left_elbow_joint+right_elbow_joint+left_wrist_joint+right_wrist_joint
    
    
    upperlimbjoint_dict = {k: v for k, v in locals().items()}
    return upperlimbjoint_dict

def draw_botlimb_joint(left_thigh_joint_row, left_thigh_joint_c, right_thigh_joint_row, right_thigh_joint_c, n_thigh_joint,
                   left_knee_joint_row, left_knee_joint_c, right_knee_joint_row,  right_knee_joint_c, n_knee_joint,
                  left_ankle_joint_row, left_ankle_joint_c, right_ankle_joint_row, right_ankle_joint_c, n_ankle_joint):
    
    left_thigh_joint =  cg.hex_neighbours_n(left_thigh_joint_row,left_thigh_joint_c, n=n_thigh_joint, keep_origin = True)
    right_thigh_joint = cg.hex_neighbours_n(right_thigh_joint_row,right_thigh_joint_c,n=n_thigh_joint, keep_origin = True)
    
    
    left_knee_joint = cg.hex_neighbours_n(left_knee_joint_row,left_knee_joint_c, n=n_knee_joint, keep_origin = True)
    right_knee_joint = cg.hex_neighbours_n(right_knee_joint_row,right_knee_joint_c, n=n_knee_joint, keep_origin = True)
    
    
    left_ankle_joint = cg.hex_neighbours_n(left_ankle_joint_row,left_ankle_joint_c, n=n_ankle_joint, keep_origin = True)
    right_ankle_joint = cg.hex_neighbours_n(right_ankle_joint_row,right_ankle_joint_c, n=n_ankle_joint, keep_origin = True)
    
    full_joints = left_thigh_joint+right_thigh_joint+left_knee_joint+right_knee_joint+left_ankle_joint+right_ankle_joint
    botlimbjoint_dict = {k: v for k, v in locals().items()}
    
    return botlimbjoint_dict
    
    
def draw_thigh(left_thigh_start_row, left_thigh_start_c, left_thigh_end_c, left_part_1_end_row, 
                left_part_2_end_row,
                left_part_3_start_row,left_part_3_start_c, left_part_3_end_row,
                
                right_thigh_start_row, right_thigh_start_c, right_thigh_end_c, right_part_1_end_row, 
                right_part_2_end_row,
                right_part_3_start_row,right_part_3_start_c, right_part_3_end_row
                ):
    
    left_thigh_part_1 = cgd.draw_trapezoid(left_thigh_start_row, 
                                           left_thigh_start_c, left_thigh_end_c, 
                                           left_part_1_end_row, 
                                           slope_left = 'inf', slope_right = 'inf', direction = 'll',
                                           bend_left = 'left', bend_right = 'right')[-2]
    
    left_thigh_part_2 = cgd.draw_trapezoid(max(r for r,c in left_thigh_part_1),
                                           min(c for r,c in left_thigh_part_1 if r == max(r for r,c in left_thigh_part_1)), 
                                           max(c for r,c in left_thigh_part_1 if r == max(r for r,c in left_thigh_part_1)), 
                                           left_part_2_end_row, 
                                           slope_left = '0.5', slope_right = 'inf', direction = 'rl',
                  bend_left = 'right', bend_right = 'left')[-2]
    
    left_thigh_part_3 = cgd.draw_triangle(left_part_3_start_row,left_part_3_start_c, left_part_3_end_row, 
                                          slope_left = '0.5', slope_right = 'inf', direction = 'lr',
                                          bend_left = 'left', bend_right = 'left')[-2]
    
    left_thigh = left_thigh_part_1+left_thigh_part_2+left_thigh_part_3
    
    right_thigh_part_1 = cgd.draw_trapezoid(right_thigh_start_row, 
                                            right_thigh_start_c, right_thigh_end_c, 
                                            right_part_1_end_row, 
                                            slope_left = 'inf', slope_right = 'inf', direction = 'rr',
                                            bend_left = 'right', bend_right = 'left')[-2]
    
    right_thigh_part_2 = cgd.draw_trapezoid(max(r for r,c in right_thigh_part_1),
                                            min(c for r,c in right_thigh_part_1 if r == max(r for r,c in right_thigh_part_1)), 
                                            max(c for r,c in right_thigh_part_1 if r == max(r for r,c in right_thigh_part_1)), 
                                            right_part_2_end_row, 
                                            slope_left = 'inf', slope_right = '0.5', direction = 'rl',
                                            bend_left = 'right', bend_right = 'left')[-2]
    
    right_thigh_part_3 = cgd.draw_triangle(right_part_3_start_row,right_part_3_start_c, right_part_3_end_row, 
                                           slope_left = 'inf', slope_right = '0.5', direction = 'lr',
                                           bend_left = 'right', bend_right = 'left')[-2]
    
    right_thigh = right_thigh_part_1+right_thigh_part_2+right_thigh_part_3
    
    thigh = left_thigh+right_thigh
    thigh_dict = {k: v for k, v in locals().items()}
    return thigh_dict
    

def draw_calf(left_calf_start_row, left_calf_start_c, left_calf_end_c, left_part_raw_end_row, 
                left_part_2_start_row,left_part_2_start_c,left_part_2_end_row,
                left_part_3_end_row,
                
                right_calf_start_row, right_calf_start_c, right_calf_end_c, right_part_raw_end_row, 
                right_part_2_start_row,right_part_2_start_c,right_part_2_end_row,
                right_part_3_end_row
                ):
    left_calf_raw = cgd.draw_block((left_calf_start_row, 
                                    (left_calf_start_c,left_calf_end_c)
                                   ), left_part_raw_end_row)

    left_calf_part2 = cgd.draw_triangle(left_part_2_start_row,left_part_2_start_c, left_part_2_end_row, 
                                        slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                                        bend_left = 'right', bend_right = 'left')[-2]
    
    left_calf_part3 = cgd.draw_trapezoid(max(r for r,c in left_calf_part2), 
                                         min(c for r,c in left_calf_part2 if r == max(r for r,c in left_calf_part2)), 
                                         max(c for r,c in left_calf_part2 if r == max(r for r,c in left_calf_part2)),
                                         left_part_3_end_row, 
                                         slope_left = '0.5', slope_right = 'inf', direction = 'rr',
                                         bend_left = 'left', bend_right = 'left')[-2]
    
    remove_left_calf = [(max(r for r,c in left_calf_part2), min(c for r,c in left_calf_part2 if r == max(r for r,c in left_calf_part2)))]
    left_calf = [(r,c) for r,c in left_calf_raw+left_calf_part2+left_calf_part3 if (r,c) not in remove_left_calf]
    
    right_calf_raw = cgd.draw_block((right_calf_start_row, 
                                     (right_calf_start_c,right_calf_end_c)
                                    ), right_part_raw_end_row)
 
    right_calf_part2 = cgd.draw_triangle(right_part_2_start_row,right_part_2_start_c, right_part_2_end_row,
                                         slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                                         bend_left = 'right', bend_right = 'left')[-2]
    
    right_calf_part3 = cgd.draw_trapezoid(max(r for r,c in right_calf_part2), 
                                          min(c for r,c in right_calf_part2 if r == max(r for r,c in right_calf_part2)), 
                                          max(c for r,c in right_calf_part2 if r == max(r for r,c in right_calf_part2)),
                                          right_part_3_end_row,
                                          slope_left = 'inf', slope_right = '0.5', direction = 'll',
                                          bend_left = 'right', bend_right = 'right')[-2]
    
    remove_right_calf = [(max(r for r,c in right_calf_part2),max(c for r,c in right_calf_part2 if r == max(r for r,c in right_calf_part2)))]
    right_calf = [(r,c) for r,c in right_calf_raw+right_calf_part2+right_calf_part3 if (r,c) not in remove_right_calf]
    
    calf = left_calf+right_calf
    calf_dict = {k: v for k, v in locals().items()}
    return calf_dict


def draw_feet(left_foot_start_row, left_foot_start_c, left_foot_end_c, left_part_1_end_row, 
              left_foot_part2_seg,left_foot_part3_seg,
                
              right_foot_start_row, right_foot_start_c, right_foot_end_c, right_part_1_end_row, 
              right_foot_part2_seg,right_foot_part3_seg,
                ):
    
    left_foot_part1 = cgd.draw_trapezoid(left_foot_start_row, left_foot_start_c, left_foot_end_c, left_part_1_end_row, 
                               slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                  bend_left = 'left', bend_right = 'right')[-2]
    
    left_foot_part2 = cgd.draw_trapezoid(max(r for r,c in left_foot_part1), 
                                         min(c for r,c in left_foot_part1 if r == max(r for r,c in left_foot_part1)), 
                                         max(c for r,c in left_foot_part1 if r == max(r for r,c in left_foot_part1)),
                                         max(r for r,c in left_foot_part1)+left_foot_part2_seg, 
                                         slope_left = '0.5', slope_right = '0.5', direction = 'll',
                                         bend_left = 'left', bend_right = 'right')[-2]
    
    left_foot_part3 = cgd.draw_trapezoid(max(r for r,c in left_foot_part2), 
                                         min(c for r,c in left_foot_part2 if r == max(r for r,c in left_foot_part2)), 
                                         max(c for r,c in left_foot_part2 if r == max(r for r,c in left_foot_part2)), 
                                         max(r for r,c in left_foot_part2)+left_foot_part3_seg, 
                                         slope_left = '0.5', slope_right = '1.5', direction = 'll',
                                         bend_left = 'left', bend_right = 'right')[-2]
    
    
    left_foot = left_foot_part1+left_foot_part2+left_foot_part3
    
    
    right_foot_part1 = cgd.draw_trapezoid(right_foot_start_row, right_foot_start_c, right_foot_end_c, right_part_1_end_row, 
                                          slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                                          bend_left = 'left', bend_right = 'right')[-2]
    
    right_foot_part2 = cgd.draw_trapezoid(max(r for r,c in right_foot_part1), 
                                          min(c for r,c in right_foot_part1 if r == max(r for r,c in right_foot_part1)), 
                                          max(c for r,c in right_foot_part1 if r == max(r for r,c in right_foot_part1)), 
                                          max(r for r,c in right_foot_part1)+right_foot_part2_seg, 
                                          slope_left = '0.5', slope_right = '0.5', direction = 'rr',
                                          bend_left = 'left', bend_right = 'right')[-2]
    
    right_foot_part3 = cgd.draw_trapezoid(max(r for r,c in right_foot_part2), 
                                          min(c for r,c in right_foot_part2 if r == max(r for r,c in right_foot_part2)), 
                                          max(c for r,c in right_foot_part2 if r == max(r for r,c in right_foot_part2)), 
                                          max(r for r,c in right_foot_part2)+right_foot_part3_seg, 
                                          slope_left = '1.5', slope_right = '0.5', direction = 'rr',
                                          bend_left = 'left', bend_right = 'right')[-2]
    
    
    right_foot = right_foot_part1+right_foot_part2+right_foot_part3
    
    feet = left_foot+right_foot
    
    feet_dict = {k: v for k, v in locals().items()}
    return feet_dict

def draw_upper_arm(left_upperarm_start_row, left_upperarm_start_c, left_upperarm_end_c, left_upperarm_end_row, 
                   right_upperarm_start_row, right_upperarm_start_c, right_upperarm_end_c, right_upperarm_end_row, 
                  ):
    left_upperarm = cgd.draw_trapezoid(left_upperarm_start_row, left_upperarm_start_c,left_upperarm_end_c,
                                          left_upperarm_end_row, 
                                          slope_left = '0.5', slope_right = 'inf', direction = 'rl',
                                          bend_left = 'left', bend_right = 'right')[-2]
    
    right_upperarm = cgd.draw_trapezoid(right_upperarm_start_row, right_upperarm_start_c,right_upperarm_end_c,
                                           right_upperarm_end_row, 
                                           slope_left ='0.5',slope_right =  'inf',  direction = 'lr',
                                           bend_left = 'right', bend_right = 'left')[-2]
    
    upperarm = left_upperarm+right_upperarm
    upperarm_dict = {k: v for k, v in locals().items()}
    return upperarm_dict
    
def draw_fore_arm(left_forearm_upward_start_row, left_forearm_upward_start_c, left_forearm_upward_end_c, left_forearm_upward_end_row, 
                  left_forearm_downward_start_row, left_forearm_downward_start_c, left_forearm_downward_end_c, 
                  
                  right_forearm_upward_start_row, right_forearm_upward_start_c, right_forearm_upward_end_c, right_forearm_upward_end_row, 
                  right_forearm_downward_start_row, right_forearm_downward_start_c, right_forearm_downward_end_c, 
                  
                  ):
    left_forearm_upward = cgd.draw_trapezoid(left_forearm_upward_start_row, 
                                             left_forearm_upward_start_c,left_forearm_upward_end_c,
                                             left_forearm_upward_end_row, 
                                             slope_left ='0.5',slope_right =  '0.5',  direction = 'rr',
                                             bend_left = 'right', bend_right = 'left')[-2]
    
    left_forearm_downward = cgd.draw_block((left_forearm_downward_start_row, 
                                            (left_forearm_downward_start_c,left_forearm_downward_end_c)
                                           ), min(r for r,c in left_forearm_upward))
    
   
    
    
    right_forearm_upward = cgd.draw_trapezoid(right_forearm_upward_start_row, 
                                              right_forearm_upward_start_c, right_forearm_upward_end_c, 
                                              right_forearm_upward_end_row,
                                              slope_left ='0.5',slope_right =  '0.5',  direction = 'll',
                                              bend_left = 'right', bend_right = 'left')[-2]
    
    right_forearm_downward = cgd.draw_block((right_forearm_downward_start_row, 
                                             (right_forearm_downward_start_c,right_forearm_downward_end_c)
                                            ), min(r for r,c in right_forearm_upward))
    left_forearm = left_forearm_upward+left_forearm_downward
    right_forearm = right_forearm_upward+right_forearm_downward
    
    forearm = left_forearm+right_forearm
    forearm_dict = {k: v for k, v in locals().items()}
    return forearm_dict

def draw_hand(left_hand_start_r, left_hand_start_c, left_hand_end_c, left_hand_end_row, left_hand_part2_seg,
             right_hand_start_r, right_hand_start_c, right_hand_end_c, right_hand_end_row, right_hand_part2_seg
             ):
    
    left_hand_part1 = cgd.draw_trapezoid(left_hand_start_r, 
                                         left_hand_start_c,left_hand_end_c,
                                         left_hand_end_row,
                                         slope_left ='1.5',slope_right =  '0.5',  direction = 'lr',
                                         bend_left = 'right', bend_right = 'left')[-2]
    
    left_hand_part2 = cgd.draw_trapezoid(max(r for r,c in left_hand_part1), 
                                         min(c for r,c in left_hand_part1 if r == max(r for r,c in left_hand_part1)),
                                         max(c for r,c in left_hand_part1 if r == max(r for r,c in left_hand_part1)),
                                         max(r for r,c in left_hand_part1)+left_hand_part2_seg,
                                         slope_left ='0.5',slope_right =  '1.5',  direction = 'll',
                                         bend_left = 'right', bend_right = 'left')[-2]
    
    
    right_hand_part1 = cgd.draw_trapezoid(right_hand_start_r, 
                                          right_hand_start_c,right_hand_end_c,
                                          right_hand_end_row,
                                          slope_left ='0.5',slope_right =  '1.5',  direction = 'lr',
                                          bend_left = 'right', bend_right = 'left')[-2]
    
    right_hand_part2 = cgd.draw_trapezoid(max(r for r,c in right_hand_part1), 
                                          min(c for r,c in right_hand_part1 if r == max(r for r,c in right_hand_part1)),
                                          max(c for r,c in right_hand_part1 if r == max(r for r,c in right_hand_part1)),
                                          max(r for r,c in right_hand_part1)+right_hand_part2_seg,
                                          slope_left ='1.5',slope_right =  '0.5',  direction = 'rr',
                                          bend_left = 'right', bend_right = 'left')[-2]
    left_hand = left_hand_part1+left_hand_part2
    right_hand = right_hand_part1+right_hand_part2
    hand = left_hand+right_hand
    hand_dict = {k: v for k, v in locals().items()}
    return hand_dict
def draw_human_body(head_center_row, head_center_col, version="7"):
    n=3
    if version not in ("7", "5", "3"):
        raise ValueError("version must be '7', '5' or '3'")
 
    head_raw = cg.hex_neighbours_n(head_center_row,head_center_col, n=n, keep_origin = True)
 
    line_dict = draw_basic_lines(head_center_row, head_center_col, n, version=version)
    ln = SimpleNamespace(**line_dict)
 
    head_size = ln.head_size
    shoulder_joint_r = ln.shoulder_joint_r
    elbow_r = ln.elbow_r
 
    # n_skull / n_joint / n_small_joint: version 7 has no lower clamp, 5/3 do.
    n_skull = ln.eff_n-1 if version == "7" else max(1, ln.eff_n-1)
    n_joint = n_skull-1 if version == "7" else max(1, n_skull-1)
    n_small_joint = n_joint-1 if version == "7" else max(0, n_joint-1)
 
    # --- head / neck / torso (shared) ---
    head_n_skull = n_skull if version == "7" else n-1
    head_dict = draw_head(head_center_row,head_center_col, head_raw, ln.skull_end_r, ln.jaw_end_r, head_n_skull)
    hd = SimpleNamespace(**head_dict)
    head = hd.full_head
 
    jaw = hd.jaw
    neck = cgd.draw_block((min(r for r,c in jaw),
                           (min(c for r,c in jaw if r == min(r for r,c in jaw)),
                            max(c for r,c in jaw if r == min(r for r,c in jaw)))), ln.ribcage_start_r)
 
    torso_head_size = ln.head_size if version == "7" else ln.eff_skull_size
    torso_dict = draw_torso(torso_head_size, neck,
                            ln.shoulder_joint_r, ln.breastbone_end_r, ln.ribcage_end_r, ln.bellybutton_r, ln.femoral_head_r)
    tr = SimpleNamespace(**torso_dict)
    torso = tr.torso
 
    # --- upper limbs (shared call, version-dependent widths/offsets) ---
    wrist_r = ln.wrist_r if version != "3" else ln.wrist_r-n_joint-n_joint
 
    elbow_joint_c_offset = head_size//2        # same numeric value for every version
    n_elbow_joint = n_joint if version == "7" else n_small_joint
    wrist_joint_c_offset = ln.eff_head_size     # already version-baked (== head_size for "7")
    n_wrist_joint = n_small_joint
 
    upperlimb_joint_dict = draw_upperlimb_joint(
 
        shoulder_joint_r+n_joint, min(c for r,c in torso if r == shoulder_joint_r+n_joint)-n_joint,
        shoulder_joint_r+n_joint, max(c for r,c in torso if r == shoulder_joint_r+n_joint)+n_joint, n_joint,
 
        elbow_r, min(c for r,c in torso if r ==elbow_r)-elbow_joint_c_offset,
        elbow_r, max(c for r,c in torso if r ==elbow_r)+elbow_joint_c_offset, n_elbow_joint,
 
        wrist_r, min(c for r,c in torso if r ==wrist_r)-wrist_joint_c_offset,
        wrist_r, max(c for r,c in torso if r ==wrist_r)+wrist_joint_c_offset, n_wrist_joint)
    uplj = SimpleNamespace(**upperlimb_joint_dict)
 
    upperarm_dict = draw_upper_arm(min(r for r,c in uplj.left_elbow_joint),
                                   min(c for r,c in uplj.left_elbow_joint if r == min(r for r,c in uplj.left_elbow_joint)),
                                   max(c for r,c in uplj.left_elbow_joint if r == min(r for r,c in uplj.left_elbow_joint)),
                                   max(r for r,c in uplj.left_shoulder_joint),
 
                                   min(r for r,c in uplj.right_elbow_joint),
                                   max(c for r,c in uplj.right_elbow_joint if r == min(r for r,c in uplj.right_elbow_joint)),
                                   min(c for r,c in uplj.right_elbow_joint if r == min(r for r,c in uplj.right_elbow_joint)),
                                   max(r for r,c in uplj.right_shoulder_joint),
                  )
    upperarm = upperarm_dict["upperarm"]
 
    forearm_end_row_offset = head_size//2 if version == "7" else 0
    forearm_dict = draw_fore_arm(min(r for r,c in uplj.left_wrist_joint),
                                 min(c for r,c in uplj.left_wrist_joint if r == min(r for r,c in uplj.left_wrist_joint)),
                                 max(c for r,c in uplj.left_wrist_joint if r == min(r for r,c in uplj.left_wrist_joint)),
                                 max(r for r,c in uplj.left_elbow_joint)+forearm_end_row_offset,
 
                                 max(r for r,c in uplj.left_elbow_joint),
                                 min(c for r,c in uplj.left_elbow_joint if r == max(r for r,c in uplj.left_elbow_joint)),
                                 max(c for r,c in uplj.left_elbow_joint if r == max(r for r,c in uplj.left_elbow_joint)),
 
                                 min(r for r,c in uplj.right_wrist_joint),
                                 min(c for r,c in uplj.right_wrist_joint if r == min(r for r,c in uplj.right_wrist_joint)),
                                 max(c for r,c in uplj.right_wrist_joint if r == min(r for r,c in uplj.right_wrist_joint)),
                                 max(r for r,c in uplj.right_elbow_joint)+forearm_end_row_offset,
 
                                 max(r for r,c in uplj.right_elbow_joint),
                                 min(c for r,c in uplj.right_elbow_joint if r == max(r for r,c in uplj.right_elbow_joint)),
                                 max(c for r,c in uplj.right_elbow_joint if r == max(r for r,c in uplj.right_elbow_joint)),
                  )
    forearm = forearm_dict["forearm"] if version == "7" else forearm_dict["left_forearm_upward"]+forearm_dict["right_forearm_upward"]
 
    hand_end_row_offset = n_small_joint if version == "3" else n_joint
    hand_part2_seg = n_joint if version == "3" else n_joint+n_joint
    hand_dict = draw_hand(max(r for r,c in uplj.left_wrist_joint),
                          min(c for r,c in uplj.left_wrist_joint if r == max(r for r,c in uplj.left_wrist_joint)),
                          max(c for r,c in uplj.left_wrist_joint if r == max(r for r,c in uplj.left_wrist_joint)),
                          max(r for r,c in uplj.left_wrist_joint)+hand_end_row_offset,
                          hand_part2_seg,
                          max(r for r,c in uplj.right_wrist_joint),
                          min(c for r,c in uplj.right_wrist_joint if r == max(r for r,c in uplj.right_wrist_joint)),
                          max(c for r,c in uplj.right_wrist_joint if r == max(r for r,c in uplj.right_wrist_joint)),
                          max(r for r,c in uplj.right_wrist_joint)+hand_end_row_offset,
                          hand_part2_seg
             )
    hand = hand_dict['hand']
 
    # --- lower limbs: the row/col anchors genuinely differ by version ---
    femoral_head_r = ln.femoral_head_r
 
    if version == "7":
        thigh_joint_r = femoral_head_r-n_joint
        knee_joint_r = ln.knee_r-n_joint
        ankle_joint_r = ln.foot_r-n_joint
        left_thigh_joint_c = min(c for r,c in torso if r == thigh_joint_r)-n_joint
        right_thigh_joint_c = max(c for r,c in torso if r == thigh_joint_r)+n_joint
        left_knee_joint_c = left_thigh_joint_c+n_joint
        right_knee_joint_c = right_thigh_joint_c-n_joint
        left_ankle_joint_c = left_thigh_joint_c+n_joint
        right_ankle_joint_c = right_thigh_joint_c-n_joint
    elif version == "5":
        thigh_joint_r = femoral_head_r
        knee_joint_r = ln.knee_r
        ankle_joint_r = ln.foot_r-n_joint-n_joint
        left_thigh_joint_c = min(c for r,c in torso if r == thigh_joint_r)
        right_thigh_joint_c = max(c for r,c in torso if r == thigh_joint_r)
        left_knee_joint_c = left_thigh_joint_c+n_joint
        right_knee_joint_c = right_thigh_joint_c-n_joint
        left_ankle_joint_c = left_thigh_joint_c
        right_ankle_joint_c = right_thigh_joint_c
    else:  # "3"
        thigh_joint_r = femoral_head_r-n_joint
        knee_joint_r = max(ln.knee_r-n_joint-n_joint-n_joint, thigh_joint_r+n_joint+2)
        ankle_joint_r = min(ln.foot_r-n_joint-n_joint-n_joint, knee_joint_r+n_small_joint+2)
        left_thigh_joint_c = min(c for r,c in torso if r == thigh_joint_r)-n_joint
        right_thigh_joint_c = max(c for r,c in torso if r == thigh_joint_r)+n_joint
        left_knee_joint_c = left_thigh_joint_c
        right_knee_joint_c = right_thigh_joint_c
        left_ankle_joint_c = left_thigh_joint_c
        right_ankle_joint_c = right_thigh_joint_c
 
    n_knee_joint = n_joint if version == "7" else n_small_joint
    botlimb_joint_dict = draw_botlimb_joint(
 
        thigh_joint_r, left_thigh_joint_c,
        thigh_joint_r, right_thigh_joint_c, n_joint,
 
        knee_joint_r, left_knee_joint_c,
        knee_joint_r, right_knee_joint_c, n_knee_joint,
 
        ankle_joint_r, left_ankle_joint_c,
        ankle_joint_r, right_ankle_joint_c, n_small_joint)
    btlj = SimpleNamespace(**botlimb_joint_dict)
 
    left_thigh_joint = btlj.left_thigh_joint
    right_thigh_joint = btlj.right_thigh_joint
    pelvis = tr.pelvis
 
    if version == "7":
        left_thigh_start_c = min(c for r,c in left_thigh_joint if r == femoral_head_r)
        left_thigh_end_c = min(c for r,c in pelvis if r == femoral_head_r)-1
        right_thigh_start_c = max(c for r,c in right_thigh_joint if r == femoral_head_r)
        right_thigh_end_c = max(c for r,c in pelvis if r == femoral_head_r)+1
    else:
        left_thigh_start_c = max(c for r,c in left_thigh_joint if r == femoral_head_r)
        left_thigh_end_c = min(c for r,c in left_thigh_joint if r == femoral_head_r)
        right_thigh_start_c = min(c for r,c in right_thigh_joint if r == femoral_head_r)
        right_thigh_end_c = max(c for r,c in right_thigh_joint if r == femoral_head_r)
 
    thigh_dict = draw_thigh(femoral_head_r, left_thigh_start_c, left_thigh_end_c, ln.sartorius_turning_r,
                            knee_joint_r, knee_joint_r, left_knee_joint_c, knee_joint_r-head_size//3,
 
                            femoral_head_r, right_thigh_start_c, right_thigh_end_c, ln.sartorius_turning_r,
                            knee_joint_r, knee_joint_r, right_knee_joint_c, knee_joint_r-head_size//3
                           )
    thigh = thigh_dict['thigh'] if version in ("7", "5") else thigh_dict['left_thigh_part_1']+thigh_dict['right_thigh_part_1']
 
    left_knee_joint = btlj.left_knee_joint
    right_knee_joint = btlj.right_knee_joint
    calf_edge_c_adj = 1 if version != "7" else 0
    calf_dict = draw_calf(max(r for r,c in left_knee_joint),
                          min(c for r,c in left_knee_joint if r == max(r for r,c in left_knee_joint))-calf_edge_c_adj,
                          max(c for r,c in left_knee_joint if r == max(r for r,c in left_knee_joint)),
                          ankle_joint_r,
                          max(r for r,c in left_knee_joint),
                          min(c for r,c in left_knee_joint if r == max(r for r,c in left_knee_joint)),
                          max(r for r,c in left_knee_joint)+head_size//2,
                          ln.gastrocnemius_end_r,
 
                          max(r for r,c in right_knee_joint),
                          min(c for r,c in right_knee_joint if r == max(r for r,c in right_knee_joint)),
                          max(c for r,c in right_knee_joint if r == max(r for r,c in right_knee_joint))+calf_edge_c_adj,
                          ankle_joint_r,
                          max(r for r,c in right_knee_joint),
                          max(c for r,c in right_knee_joint if r == max(r for r,c in right_knee_joint)),
                          max(r for r,c in right_knee_joint)+head_size//2,
                          ln.gastrocnemius_end_r
                )
    calf = calf_dict['calf'] if version == "7" else calf_dict['left_calf_raw']+calf_dict['right_calf_raw']
 
    left_ankle_joint = btlj.left_ankle_joint
    right_ankle_joint = btlj.right_ankle_joint
    foot_part1_end_row_offset = n_joint if version == "3" else head_size//3
    feet_dict = draw_feet(max(r for r,c in left_ankle_joint),
                          min(c for r,c in left_ankle_joint if r == max(r for r,c in left_ankle_joint)),
                          max(c for r,c in left_ankle_joint if r == max(r for r,c in left_ankle_joint)),
                          max(r for r,c in left_ankle_joint)+foot_part1_end_row_offset,
                          1,1,
                          max(r for r,c in right_ankle_joint),
                          min(c for r,c in right_ankle_joint if r == max(r for r,c in right_ankle_joint)),
                          max(c for r,c in right_ankle_joint if r == max(r for r,c in right_ankle_joint)),
                          max(r for r,c in right_ankle_joint)+foot_part1_end_row_offset,
                          1,1,
                )
    feet = feet_dict['feet']
 
    up_joints = uplj.full_joints
    bot_joints = btlj.full_joints
    raw_body = head+neck+torso+thigh+calf+feet+up_joints+bot_joints+upperarm+forearm+hand
    plot_temp = { 'raw_body': [raw_body, [[0,0,0]]],
        'joint': [ list(set(up_joints+bot_joints)), [[0.4,0.4,0.4]]],
            }
 
    return head_raw, raw_body, line_dict, head_dict, neck, torso_dict, upperlimb_joint_dict, botlimb_joint_dict, thigh_dict, calf_dict, feet_dict, upperarm_dict, forearm_dict, hand_dict, plot_temp

def draw_tiny_body_(head_center_row, head_center_col, n):
    center_col = head_center_col
    if n >2:
        print(n, 'too big for tiny body, need n<=2')
        raw_body = []
        body_dict = dict()
    else:
        
        head_raw = cg.hex_neighbours_n(head_center_row,head_center_col, n=n, keep_origin = True)
        body_center_row = head_center_row+n+1+n+1
        thigh_center_row = body_center_row+n+1+n+1


        head_bottom_r = head_center_row+n
        neck_raw = cgd.draw_block((head_bottom_r, (min(c for r,c in head_raw if r ==head_bottom_r), 
                                              max(c for r,c in head_raw if r ==head_bottom_r)
                                              )), head_bottom_r+1
                             )
        neck = [x for x in neck_raw if x not in head_raw]
        

        body_raw = cg.hex_neighbours_n(body_center_row,center_col, n=n, keep_origin = True)   
        body_bottom_r = body_center_row+n
        body_top_r = body_center_row-n
        pelvis_raw = cgd.draw_trapezoid(body_bottom_r, 
                                            min(c for r,c in body_raw if r ==body_bottom_r), 
                                            max(c for r,c in body_raw if r ==body_bottom_r), 
                                            body_bottom_r+1, 
                                            slope_left = '0.5', slope_right = '0.5', direction = 'lr',
                                            bend_left = 'left', bend_right = 'right')[-2]

        pelvis = [x for x in pelvis_raw if x not in body_raw]
    
    
        body_part1 = cgd.draw_block((body_top_r, (min(c for r,c in body_raw if r ==body_top_r), 
                                              max(c for r,c in body_raw if r ==body_top_r)
                                              )), body_bottom_r
                             )
        body_part2 = cgd.draw_trapezoid(body_top_r, 
                                            min(c for r,c in body_raw if r ==body_top_r)-1, 
                                            max(c for r,c in body_raw if r ==body_top_r)+1, 
                                            body_bottom_r-n, 
                                            slope_left = '0.5', slope_right = '0.5', direction = 'rl',
                                            bend_left = 'left', bend_right = 'right')[-2]
        body = body_part1+body_part2
        left_upper_arm = cgd.verticle_line(body_top_r, min(c for r,c in body if r ==body_top_r)-1, body_bottom_r, bend = 'right')
        

        right_upper_arm = cgd.verticle_line(body_top_r, max(c for r,c in body if r ==body_top_r)+1, body_bottom_r, bend = 'left')
        upper_arm = left_upper_arm+right_upper_arm
        
        left_elbow = (max(r for r,c in left_upper_arm), 
                        min(c for r,c in left_upper_arm if r == max(r for r,c in left_upper_arm)))
        right_elbow = (max(r for r,c in right_upper_arm), 
                        max(c for r,c in right_upper_arm if r == max(r for r,c in right_upper_arm)))
        
        
        bottom_raw = cg.hex_neighbours_n(thigh_center_row,center_col, n=n, keep_origin = True) 
        bottom_top_r = max(r for r,c in pelvis)
        pelvis_size = (max(c for r,c in pelvis if r ==bottom_top_r)-min(c for r,c in pelvis if r ==bottom_top_r))/1+1
        leg_size = pelvis_size/2
        leg_radius = leg_size/2
        
        left_leg_part1 = cgd.draw_trapezoid(bottom_top_r, 
                                            min(c for r,c in pelvis if r ==bottom_top_r), 
                                            min(c for r,c in pelvis if r ==bottom_top_r)+math.floor(leg_radius), 
                                            thigh_center_row-1, 
                                            slope_left = 'inf', slope_right = '0.5', direction = 'll',
                                            bend_left = 'left', bend_right = 'right')[-2]
        left_leg_part2 = cgd.draw_trapezoid(max(r for r,c in left_leg_part1), 
                                      min(c for r,c in left_leg_part1 if r ==max(r for r,c in left_leg_part1)), 
                                      min(c for r,c in left_leg_part1 if r ==max(r for r,c in left_leg_part1)), 
                                      max(r for r,c in bottom_raw), 
                                      slope_left = 'inf', slope_right = 'inf', direction = 'll',
                                            bend_left = 'right', bend_right = 'right')[-2]
        left_leg = left_leg_part1+left_leg_part2
        
        
        right_leg_part1 = cgd.draw_trapezoid(bottom_top_r, 
                                            max(c for r,c in pelvis if r ==bottom_top_r)-math.floor(leg_radius), 
                                            max(c for r,c in pelvis if r ==bottom_top_r), 
                                            thigh_center_row-1, 
                                            slope_left = '0.5', slope_right = 'inf', direction = 'rr',
                                            bend_left = 'left', bend_right = 'right')[-2]
        right_leg_part2 = cgd.draw_trapezoid(max(r for r,c in right_leg_part1), 
                                      max(c for r,c in right_leg_part1 if r ==max(r for r,c in right_leg_part1)), 
                                      max(c for r,c in right_leg_part1 if r ==max(r for r,c in right_leg_part1)), 
                                      max(r for r,c in bottom_raw), 
                                      slope_left = 'inf', slope_right = 'inf', direction = 'rr',
                                      bend_left = 'left', bend_right = 'left')[-2]
        right_leg = right_leg_part1+right_leg_part2
        
        leg =left_leg+right_leg
        
   
        raw_body =head_raw+neck+body+pelvis+upper_arm+leg
        exclude = {"pelvis_raw", "body_raw",  "neck_raw"}
        body_dict = {k: v for k, v in locals().items() if k not in exclude}

    plot_temp = { 'tiny_raw_body': [raw_body, [[0,0,0]]],
                # 'pelvis': [pelvis, [[0,1,0]]],
                # 'left_leg_part1': [left_leg_part1, [[1,1,0]]],
            }

    return body_dict, plot_temp

'''
def draw_human_body(head_center_row, head_center_col, n = 2):
    head_raw = cg.hex_neighbours_n(head_center_row,head_center_col, n=n, keep_origin = True)
    
    line_dict = draw_basic_lines(head_center_row, head_center_col, n)
    ln = SimpleNamespace(**line_dict)
    
    n_skull = n-1
    head_dict = draw_head(head_center_row,head_center_col, head_raw, ln.skull_end_r, ln.jaw_end_r, n_skull)
    hd = SimpleNamespace(**head_dict)
    head = hd.full_head
    
    jaw = hd.jaw
    neck = cgd.draw_block((min(r for r,c in jaw), 
                           (min(c for r,c in jaw if r == min(r for r,c in jaw)), 
                            max(c for r,c in jaw if r == min(r for r,c in jaw)))), ln.ribcage_start_r)
    
    torso_dict = draw_torso(ln.head_size, neck, 
                            ln.shoulder_joint_r, ln.breastbone_end_r, ln.ribcage_end_r, ln.bellybutton_r, ln.femoral_head_r)
    tr = SimpleNamespace(**torso_dict)
    torso = tr.torso
    
    n_joint = n_skull-1
    n_small_joint = n_joint-1
    
    head_size = ln.head_size
    shoulder_joint_r = ln.shoulder_joint_r
    elbow_r = ln.elbow_r
    wrist_r = ln.wrist_r
    
    upperlimb_joint_dict = draw_upperlimb_joint(
        
        shoulder_joint_r+n_joint, min(c for r,c in torso if r == shoulder_joint_r+n_joint)-n_joint, 
        shoulder_joint_r+n_joint, max(c for r,c in torso if r == shoulder_joint_r+n_joint)+n_joint, n_joint,
        
        elbow_r, min(c for r,c in torso if r ==elbow_r)-head_size//2, 
        elbow_r, max(c for r,c in torso if r ==elbow_r)+head_size//2, n_joint,
        
        wrist_r, min(c for r,c in torso if r ==wrist_r)-head_size, 
        wrist_r, max(c for r,c in torso if r ==wrist_r)+head_size, n_small_joint)
    uplj = SimpleNamespace(**upperlimb_joint_dict)
    
    upperarm_dict = draw_upper_arm(min(r for r,c in uplj.left_elbow_joint), 
                                   min(c for r,c in uplj.left_elbow_joint if r == min(r for r,c in uplj.left_elbow_joint)),
                                   max(c for r,c in uplj.left_elbow_joint if r == min(r for r,c in uplj.left_elbow_joint)),
                                   max(r for r,c in uplj.left_shoulder_joint), 
                                   
                   
                                   min(r for r,c in uplj.right_elbow_joint), 
                                   max(c for r,c in uplj.right_elbow_joint if r == min(r for r,c in uplj.right_elbow_joint)),
                                   min(c for r,c in uplj.right_elbow_joint if r == min(r for r,c in uplj.right_elbow_joint)),
                                   max(r for r,c in uplj.right_shoulder_joint), 
                  )
    upperarm = upperarm_dict["upperarm"]
    
    forearm_dict = draw_fore_arm(min(r for r,c in uplj.left_wrist_joint), 
                                 min(c for r,c in uplj.left_wrist_joint if r == min(r for r,c in uplj.left_wrist_joint)),
                                 max(c for r,c in uplj.left_wrist_joint if r == min(r for r,c in uplj.left_wrist_joint)),
                                 max(r for r,c in uplj.left_elbow_joint)+head_size//2, 
                  
                                 max(r for r,c in uplj.left_elbow_joint), 
                                 min(c for r,c in uplj.left_elbow_joint if r == max(r for r,c in uplj.left_elbow_joint)),
                                 max(c for r,c in uplj.left_elbow_joint if r == max(r for r,c in uplj.left_elbow_joint)), 
                                 
                                 
                                 min(r for r,c in uplj.right_wrist_joint), 
                                 min(c for r,c in uplj.right_wrist_joint if r == min(r for r,c in uplj.right_wrist_joint)),
                                 max(c for r,c in uplj.right_wrist_joint if r == min(r for r,c in uplj.right_wrist_joint)),
                                 max(r for r,c in uplj.right_elbow_joint)+head_size//2, 
                                 
                  
                                 max(r for r,c in uplj.right_elbow_joint), 
                                 min(c for r,c in uplj.right_elbow_joint if r == max(r for r,c in uplj.right_elbow_joint)), 
                                 max(c for r,c in uplj.right_elbow_joint if r == max(r for r,c in uplj.right_elbow_joint)), 
                  
                  )
    forearm = forearm_dict["forearm"]
    
    hand_dict = draw_hand(max(r for r,c in uplj.left_wrist_joint), 
                          min(c for r,c in uplj.left_wrist_joint if r == max(r for r,c in uplj.left_wrist_joint)),
                          max(c for r,c in uplj.left_wrist_joint if r == max(r for r,c in uplj.left_wrist_joint)),
                          max(r for r,c in uplj.left_wrist_joint)+n_joint,
                          n_joint+n_joint,
                          max(r for r,c in uplj.right_wrist_joint), 
                          min(c for r,c in uplj.right_wrist_joint if r == max(r for r,c in uplj.right_wrist_joint)),
                          max(c for r,c in uplj.right_wrist_joint if r == max(r for r,c in uplj.right_wrist_joint)),
                          max(r for r,c in uplj.right_wrist_joint)+n_joint, 
                          n_joint+n_joint
             )
    hand = hand_dict['hand']
    
    femoral_head_r = ln.femoral_head_r
    thigh_joint_r = femoral_head_r-n_joint
    knee_joint_r = ln.knee_r-n_joint
    #print('ln.knee_r', ln.knee_r, 'knee_joint_r', knee_joint_r)
    ankle_joint_r = ln.foot_r-n_joint
    
    left_thigh_joint_c = min(c for r,c in torso if r == thigh_joint_r)-n_joint
    right_thigh_joint_c =max(c for r,c in torso if r == thigh_joint_r)+n_joint
    
    
    left_knee_joint_c = left_thigh_joint_c+n_joint
    right_knee_joint_c = right_thigh_joint_c-n_joint
    
    left_ankle_joint_c = left_thigh_joint_c+n_joint
    right_ankle_joint_c = right_thigh_joint_c-n_joint
    
    botlimb_joint_dict = draw_botlimb_joint(
        
        thigh_joint_r, left_thigh_joint_c, 
        thigh_joint_r, right_thigh_joint_c, n_joint,
        
        knee_joint_r, left_knee_joint_c, 
        knee_joint_r, right_knee_joint_c, n_joint,
        
        ankle_joint_r, left_ankle_joint_c, 
        ankle_joint_r, right_ankle_joint_c, n_small_joint)
    btlj = SimpleNamespace(**botlimb_joint_dict)
    
    
    left_thigh_joint = btlj.left_thigh_joint
    right_thigh_joint = btlj.right_thigh_joint
    pelvis = tr.pelvis
    thigh_dict = draw_thigh(femoral_head_r, 
                            min(c for r,c in left_thigh_joint if r == femoral_head_r), 
                            min(c for r,c in pelvis if r == femoral_head_r)-1, ln.sartorius_turning_r, 
                            knee_joint_r,
                            knee_joint_r,left_knee_joint_c, knee_joint_r-head_size//3,
                            
                            femoral_head_r, 
                            max(c for r,c in right_thigh_joint if r == femoral_head_r), 
                            max(c for r,c in pelvis if r == femoral_head_r)+1, ln.sartorius_turning_r, 
                            knee_joint_r,
                            knee_joint_r,right_knee_joint_c, knee_joint_r-head_size//3
                           
                           )
    thigh = thigh_dict['thigh']
    
    left_knee_joint = btlj.left_knee_joint
    right_knee_joint = btlj.right_knee_joint
    calf_dict = draw_calf(max(r for r,c in left_knee_joint), 
                          min(c for r,c in left_knee_joint if r == max(r for r,c in left_knee_joint)), 
                          max(c for r,c in left_knee_joint if r == max(r for r,c in left_knee_joint)), 
                          ankle_joint_r, 
                          max(r for r,c in left_knee_joint),
                          min(c for r,c in left_knee_joint if r == max(r for r,c in left_knee_joint)),
                          max(r for r,c in left_knee_joint)+head_size//2,
                          ln.gastrocnemius_end_r,
                
                          max(r for r,c in right_knee_joint), 
                          min(c for r,c in right_knee_joint if r == max(r for r,c in right_knee_joint)), 
                          max(c for r,c in right_knee_joint if r == max(r for r,c in right_knee_joint)), 
                          ankle_joint_r, 
                          max(r for r,c in right_knee_joint),
                          max(c for r,c in right_knee_joint if r == max(r for r,c in right_knee_joint)),
                          max(r for r,c in right_knee_joint)+head_size//2,
                          ln.gastrocnemius_end_r
                )
    calf = calf_dict['calf']
    
    left_ankle_joint = btlj.left_ankle_joint
    right_ankle_joint = btlj.right_ankle_joint
    feet_dict = draw_feet(max(r for r,c in left_ankle_joint), 
                          min(c for r,c in left_ankle_joint if r == max(r for r,c in left_ankle_joint)), 
                          max(c for r,c in left_ankle_joint if r == max(r for r,c in left_ankle_joint)), 
                          max(r for r,c in left_ankle_joint)+head_size//3, 
                          1,1,
                          max(r for r,c in right_ankle_joint), 
                          min(c for r,c in right_ankle_joint if r == max(r for r,c in right_ankle_joint)), 
                          max(c for r,c in right_ankle_joint if r == max(r for r,c in right_ankle_joint)), 
                          max(r for r,c in right_ankle_joint)+head_size//3, 
                          1,1,
                )
    feet = feet_dict['feet']
    
    up_joints = uplj.full_joints
    bot_joints = btlj.full_joints
    raw_body = head+neck+torso+thigh+calf+feet+up_joints+bot_joints+upperarm+forearm+hand
    plot_temp = { 'raw_body': [raw_body, [[0,0,0]]],
        'joint': [ list(set(up_joints+bot_joints)), [[0.4,0.4,0.4]]],
       
            }

    return head_raw, raw_body, line_dict, head_dict, neck, torso_dict, upperlimb_joint_dict, botlimb_joint_dict, thigh_dict, calf_dict, feet_dict, upperarm_dict, forearm_dict, hand_dict, plot_temp
'''
    
