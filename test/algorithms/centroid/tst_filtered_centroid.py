from __future__ import division
from dials.algorithms.centroid.filtered_centroid import FilteredCentroid

def tst_filtered_centroid():
    import libtbx.load_env
    try:
        dials_regression = libtbx.env.dist_path('dials_regression')
    except KeyError, e:
        print 'FAIL: dials_regression not configured'
        return

    import os

    frames = [os.path.join(dials_regression, 'centroid_test_data',
                           'centroid_%04d.cbf' % j) for j in range(1, 10)]

    import dxtbx

    sweep = dxtbx.sweep(frames)

    bounding_boxes = {
        (0, 0, 0):[(0, 8, 1022, 1036, 1070, 1083)]
        }

    tc = FilteredCentroid(bounding_boxes, sweep, n_sigma=3)

    centroids = tc.get_centroids()

    for hkl in centroids:
        for centroid in centroids[hkl]:
            print '%.1f %.1f %.1f %.1f %.1f %.1f' % centroid

if __name__ == '__main__':
    tst_filtered_centroid()
