#
# dials.algorithms.background.curved_subtractor.py
#
#  Copyright (C) 2013 Diamond Light Source
#
#  Author: Luis Fuentes-Montero "luiso" & James Parkhurst
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

from __future__ import division
from dials.interfaces.background import BackgroundSubtractionInterface

from dials.algorithms.background.background_subtraction_2d \
          import curved_background_calc_2d

class InclinedSubtractor(BackgroundSubtractionInterface):
    ''' The Flat background subtractor '''

    def __init__(self, **kwargs):
        pass

    def __call__(self, sweep, crystal, reflections):
        #plane_constants = []
        layering_and_background_plane(reflections)
        #layering_and_background_plane(reflections, plane_constants)
        return reflections

#def layering_and_background_plane(reflections, plane_constants):
def layering_and_background_plane(reflections):
    from dials.algorithms.background \
     import get_plane_background_syml_sys_2d, variance_n_background_from_plane
    from scitbx.array_family import flex

    print "performing background plane calculation ...."
    plane_constants = []
    for ref in reflections:
        if ref.is_valid():
            shoebox = ref.shoebox
            mask = ref.shoebox_mask
            background = ref.shoebox_background
            tot_sigma = 0.0
            for i in range(shoebox.all()[0]):
                data2d = shoebox[i:i + 1, :, :]
                mask2d = mask[i:i + 1, :, :]
                background2d = background[i:i + 1, :, :]

                data2d.reshape(flex.grid(shoebox.all()[1:]))
                mask2d.reshape(flex.grid(shoebox.all()[1:]))
                background2d.reshape(flex.grid(background2d.all()[1:]))

                a_mat_flx = flex.double(flex.grid(3, 3))
                b_vec_flx = flex.double(flex.grid(3, 1))
                ok_logic = get_plane_background_syml_sys_2d(data2d, mask2d, a_mat_flx, b_vec_flx)
                if ok_logic == 0:
                    a_mat = a_mat_flx.as_scitbx_matrix()
                    b_mat = b_vec_flx.as_scitbx_matrix()


                    try:
                        x_mat = a_mat.inverse() * b_mat
                        abc_plane = x_mat.as_flex_double_matrix()
                    except:
                        abc_plane = flex.double(flex.grid(3, 1))
                        abc_plane[0, 0] = 0
                        abc_plane[1, 0] = 0
                        abc_plane[2, 0] = 0
                else:
                    abc_plane = flex.double(flex.grid(3, 1))
                    abc_plane[0, 0] = 0
                    abc_plane[1, 0] = 0
                    abc_plane[2, 0] = 0

                variance = variance_n_background_from_plane(data2d, mask2d, abc_plane, background2d)
                plane_constants.append(abc_plane)
                tot_sigma += variance
                background2d.reshape(flex.grid(1, background2d.all()[0], background2d.all()[1]))
                background[i:i + 1, :, :] = background2d.as_double()
            ref.intensity_variance = tot_sigma
    print "background plane calculation ..... done"

    return reflections#, plane_constants
