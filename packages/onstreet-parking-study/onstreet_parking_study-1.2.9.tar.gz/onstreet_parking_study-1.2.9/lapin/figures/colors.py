# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 10:12:56 2021

This file contains colors and colormap information used to create the different figures

@author: lgauthier
"""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.colors as mcolors

class color_wrapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattribute__(self, key):
        try:
            return mcolors.to_rgba(dict.__getitem__(self, key))
        except:
            return dict.__getattribute__(self, key)

    def with_shifted_alpha(self, key, alpha=1):
        return mcolors.to_rgba(dict.__getitem__(self, key), alpha=alpha)

#Color transform
def string_value(num):
    """
    To return char for a value. For example
    '2' is returned for 2. 'A' is returned
    for 10. 'B' for 11, etc.
    """
    if (num >= 0 and num <= 9):
        return chr(num + ord('0'))
    else:
        return chr(num - 10 + ord('A'))

def to_base_from_deci(inputNum, base):
    """
    Converts input number in given base
    by repeatedly dividing it by base
    and taking remainder
    """
    res=''
    while (inputNum > 0):
        res = string_value(inputNum % base) + res
        inputNum = int(inputNum / base)
    return res

def xform_RGB_to_Hexa(R, G, B):
    r = '{:0>2}'.format(to_base_from_deci(R, 16))
    g = '{:0>2}'.format(to_base_from_deci(G, 16))
    b = '{:0>2}'.format(to_base_from_deci(B, 16))

    return '#'+r+g+b

def rel_luminance(R,G,B):
    R_sRGB = R/255
    G_sRGB = G/255
    B_sRGB = B/255

    r = R_sRGB /12.92 if R_sRGB <= 0.03928 else ((R_sRGB +0.055)/1.055) ** 2.4
    g = G_sRGB /12.92 if G_sRGB <= 0.03928 else ((G_sRGB +0.055)/1.055) ** 2.4
    b = B_sRGB /12.92 if B_sRGB <= 0.03928 else ((B_sRGB +0.055)/1.055) ** 2.4

    return 0.2126 * r + 0.7152 * g + 0.0722 * b

#Accessibility tests
def two_colors_contrast_ratio(color1, color2):

    if not isinstance(color1, (tuple, list, np.ndarray)):
        raise TypeError(f"Expecting a tuple for color1, received {color1.__class__}")
    if not isinstance(color2, (tuple, list, np.ndarray)):
        raise TypeError(f"Expecting a tuple for color2, received {color2.__class__}")
    if not len(color1) == 3:
        raise ValueError(f"Expecting 3 inputs for R,G,B tuple of color1, received {len(color1)}")
    if not len(color2) == 3:
        raise ValueError(f"Expecting 3 inputs for R,G,B tuple of color2, received {len(color2)}")

    l1 = rel_luminance(*color1)
    l2 = rel_luminance(*color2)

    L1 = max(l1, l2)
    L2 = min(l1, l2)

    return (L1 + 0.05) / (L2 + 0.05)

def constrast_ratio_matrix(*colors):
    """


    Parameters
    ----------
    *colors : 3 tuple
        DESCRIPTION.

    Returns
    -------
    mat : TYPE
        DESCRIPTION.

    """
    if not isinstance(colors, (list, tuple)):
        colors=[colors]

    mat = np.ones((len(colors),len(colors)))

    for i in range(len(colors)):
        for j in range(len(colors)):
            mat[i][j] = round(two_colors_contrast_ratio(colors[i], colors[j]), 2)
    return mat

def constrast_ratio_df(color_dict):
    return pd.DataFrame(
        index=color_dict.keys(),
        columns=color_dict.keys(),
        data=constrast_ratio_matrix(*color_dict.values())
        )

#Variables
LAPIN_COLORS = color_wrapper(
    HYDRO        = 'lightgray',
    ROADS        = '#36454f',
    MISSING_GREY = '#b3b3b3',#'#D3D3D3',
    TRAVAUX      = '#ff801f90',#'yellow',#'#ff801f',
    HORS_ZONE    = 'white',#'#333333',#'white',#'#b3b3b3',#'#a1c5ff',
    VR           = '#ee82ee90',#'#99ff66',#'#e0e4ff',
    NO_PLACES    = '#dbb7c0',#'#80002050', #'#333333',#'#6aa5fc',
    LEGEND_BG    = 'whitesmoke',#'#404145',
    LEG_TXT      = 'dimgray',#'white',
)

LAPIN_PALETTES = dict(
     PROV_BLUES = lambda n_colors=None, reverse=None, as_cmap=False: sns.dark_palette("#69d", n_colors, reverse, as_cmap),
     PROV_REDS = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette("flare", n_colors, desat, as_cmap),
     CAPA = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette("crest", n_colors, desat, as_cmap),
     OCC_BLUES = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette('Blues', n_colors, desat, as_cmap),
     OCC_REDS = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette('Reds', n_colors, desat, as_cmap),
     OCC_GREENS = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette('Greens', n_colors, desat, as_cmap),
     OCC_GNYLRD = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette('RdYlGn_r', n_colors, desat, as_cmap),
     OCC_VLAG = lambda n_colors=None, desat=None, as_cmap=False: sns.color_palette('coolwarm', n_colors, desat, as_cmap)
)