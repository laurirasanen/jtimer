import math

def calc_points(wr_time, pb_time, completions):
    """Tom "Tim" Sinister's point weight scaling algorithm"""
    wr_points = 200 *(5 + math.log(completions))
    scale_factor = wr_time / (wr_time + (pb_time - wr_time) * math.log(completions))
    points_awarded = float.__round__(wr_points * scale_factor)
    return points_awarded