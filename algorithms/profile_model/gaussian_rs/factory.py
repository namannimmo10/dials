#
# factory.py
#
#  Copyright (C) 2013 Diamond Light Source
#
#  Author: James Parkhurst
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

from __future__ import division

class Factory(object):
  '''
  A factory class to compute the profile models.

  '''

  @classmethod
  def compute_single(cls,
                     experiment,
                     reflections,
                     min_zeta=0.05,
                     scan_varying=False):
    '''
    Compute the profile model.

    :param experiment: The experiment
    :param reflections: The list of reflections
    :param min_zeta: The minimum zeta value of reflection to use
    :param scan_varying: True/False do a scan varying model
    :return: The profile model

    '''
    from dials.algorithms.profile_model.gaussian_rs.calculator \
      import ProfileModelCalculator
    from dials.algorithms.profile_model.gaussian_rs.calculator \
      import ScanVaryingProfileModelCalculator
    from dials.algorithms.profile_model.gaussian_rs.model import ProfileModel
    from dials.algorithms.profile_model.gaussian_rs.model import ScanVaryingProfileModel
    if not scan_varying:
      calculator = ProfileModelCalculator(experiment, reflections, min_zeta)
      n_sigma = 3
      sigma_b = calculator.sigma_b()
      sigma_m = calculator.sigma_m()
      return ProfileModel(n_sigma, sigma_b, sigma_m)
    else:
      calculator = ScanVaryingProfileModelCalculator(experiment, reflections, min_zeta)
      n_sigma = 3
      sigma_b = calculator.sigma_b()
      sigma_m = calculator.sigma_m()
      return ScanVaryingProfileModel(n_sigma, sigma_b, sigma_m)

  @classmethod
  def compute(cls, params, experiments, reflections):
    '''
    Compute the profile models.

    :param experiments: The experiment list
    :param reflections: The list of reflections
    :return: The profile models

    '''
    from dials.algorithms.profile_model.model_list import ProfileModelList
    from dials.util.command_line import heading
    from logging import info
    assert(len(experiments) > 0)

    info("=" * 80)
    info("")
    info(heading("Computing Profile Model"))
    info("")

    # Split the reflections by experiment id
    if len(experiments) > 1:
      from dials.array_family import flex
      reflections_split = reflections.split_by_experiment_id()
      assert(len(reflections_split) == len(experiments))
    else:
      reflections_split = [reflections]

    # Compute the profile models
    min_zeta = params.gaussian_rs.filter.min_zeta
    scan_varying = params.gaussian_rs.scan_varying
    profile_model_list = ProfileModelList()
    for exp, ref in zip(experiments, reflections_split):
      model = Factory.compute_single(exp, ref, min_zeta, scan_varying)
      info(" Sigma_b: %.3f degrees" % model.sigma_b(deg=True))
      info(" Sigma_m: %.3f degrees" % model.sigma_m(deg=True))
      profile_model_list.append(model)

    # Return the profile models
    return profile_model_list

  @classmethod
  def load(cls, params):
    '''
    Load from phil parameters.

    :param params: The input phil parameters
    :return: The profile model list

    '''
    from dials.algorithms.profile_model.model_list import ProfileModelList
    from dials.algorithms.profile_model.gaussian_rs.model import ProfileModel
    from dials.algorithms.profile_model.gaussian_rs.model import ScanVaryingProfileModel
    from dials.array_family import flex
    from math import pi
    dtor = pi / 180.0
    assert(len(params.gaussian_rs.model) > 0)
    profile_model_list = ProfileModelList()
    if params.gaussian_rs.scan_varying:
      for i in range(len(params.gaussian_rs.model)):
        profile_model_list.append(ProfileModel(
          params.gaussian_rs.scan_varying_model[i].n_sigma,
          flex.double(params.gaussian_rs.scan_varying_model[i].sigma_b) * dtor,
          flex.double(params.gaussian_rs.scan_varying_model[i].sigma_m) * dtor))
    else:
      for i in range(len(params.gaussian_rs.model)):
        profile_model_list.append(ProfileModel(
          params.gaussian_rs.model[i].n_sigma,
          params.gaussian_rs.model[i].sigma_b * dtor,
          params.gaussian_rs.model[i].sigma_m * dtor))
    return profile_model_list

  @classmethod
  def create(cls, params, experiments, reflections):
    '''
    Create the profile models.

    :param params: The input phil parameters
    :param experiments: The experiment list
    :param reflections: The reflection table
    :return: The profile model

    '''
    if len(params.profile.gaussian_rs.model) > 0:
      assert(len(params.profile.gaussian_rs.model) == len(experiments))
      model = Factory.load(params.profile)
    else:
      assert(reflections is not None)
      model = Factory.compute(params.profile, experiments, reflections)
    return model
