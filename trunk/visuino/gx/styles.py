#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Nelso
#
# Created:     12/04/2013
# Copyright:   (c) Nelso 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class StyleNotch(object):
    def __init__(self):
        self.io_insertion_marker_color = '#111111'

        self.io_notch_shape = 'arc'
        self.io_notch_width = 10
        self.io_notch_height = 20
        self.io_notch_basis = 0.0

        self.vf_notch_shape = 'trig'
        self.vf_notch_basis = 0.85
        self.vf_notch_width = 40
        self.vf_notch_height = 5
        self.vf_notch_x0 =  20

    def getIoNotchSize(self):
        return (self.io_notch_width, self.io_notch_height)

    def getVfNotchSize(self):
        return (self.vf_notch_width, self.vf_notch_height)


class StyleArgLabel(object):
    def __init__(self):
        self.background_color = 'yellow'
        self.border_color ='black'
        self.border_width = 2
        self.corner_shape = 'arc'
        self.corner_width = 12
        self.corner_height = 12

        self.font_color = 'black'
        self.font_family = 'Verdana'
        self.font_size = 12
        self.font_vcorrection = -1

        self.hpadd = 10
        self.vpadd = 5

    def getCornerSize(self):
        return (self.corner_width, self.corner_height)

    def getPadding(self):
        return (self.hpadd, self.vpadd)


class StyleFunctionCall(object):
    '''
    Collection of attributes to customize all the metrics of the function
    call block.
    '''
    def __init__(self):
        self.background_color = 'blue'
        self.border_color ='black'
        self.border_width = 2
        self.corner_shape = 'arc'
        self.corner_width = 6
        self.corner_height = 6

        self.name_font_color = 'white'
        self.name_font_family = 'Verdana'
        self.name_font_size = 10
        self.name_hpadd = 10
        self.name_vpadd = 10

        self.arg_min_left_padd = 40
        self.arg_spacing = -2

    def getNamePadding(self):
        return (self.name_hpadd, self.name_vpadd)
