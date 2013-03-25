/*
 * reflection.cc
 *
 *  Copyright (C) 2013 Diamond Light Source
 *
 *  Author: James Parkhurst
 *
 *  This code is distributed under the BSD license, a copy of which is
 *  included in the root directory of this package.
 */
#include <boost/python.hpp>
#include <boost/python/def.hpp>
#include <sstream>
#include <string>
#include <scitbx/array_family/flex_types.h>
#include <scitbx/array_family/boost_python/flex_wrapper.h>
#include <scitbx/array_family/boost_python/flex_pickle_double_buffered.h>
#include <dials/model/data/reflection.h>

namespace dials { namespace model { namespace boost_python {

  using namespace boost::python;

  using scitbx::af::boost_python::flex_pickle_double_buffered;

  std::string reflection_to_string(const Reflection &reflection) {
    std::stringstream ss;
    ss << reflection;
    return ss.str();
  }

  struct ReflectionPickleSuite : boost::python::pickle_suite {
//    static
//    boost::python::tuple getinitargs(const Reflection &r) {
//      // ...
//    }

    static
    boost::python::tuple getstate(boost::python::object obj) {
      const Reflection &r = extract<const Reflection&>(obj)();
      return boost::python::make_tuple(
        obj.attr("__dict__"),
        r.get_miller_index(),
        r.get_rotation_angle(),
        r.get_beam_vector(),
        r.get_image_coord_mm(),
        r.get_image_coord_px(),
        r.get_frame_number(),
        r.get_panel_number(),
        r.get_bounding_box(),
        r.get_centroid_position(),
        r.get_centroid_variance(),
        r.get_shoebox(),
        r.get_shoebox_weights(),
        r.get_transformed_shoebox());
    }

    static
    void setstate(boost::python::object obj, boost::python::tuple state) {
      Reflection &r = extract<Reflection&>(obj)();
      
      // Check that the number of items is correct
      if (len(state) != 14) {
        PyErr_SetObject(PyExc_ValueError, (
          "expected 14-item tuple in call to __setstate__; got %s" 
          % state).ptr());
        throw_error_already_set();
      }

      // restore the object's __dict__
      dict d = extract<dict>(obj.attr("__dict__"))();
      d.update(state[0]);
      
      // restore the internal state of the C++ reflection object
      r.set_miller_index(extract<cctbx::miller::index<> >(state[1]));
      r.set_rotation_angle(extract<double>(state[2]));
      r.set_beam_vector(extract<vec3<double> >(state[3]));
      r.set_image_coord_mm(extract<vec2<double> >(state[4]));
      r.set_image_coord_px(extract<vec2<double> >(state[5]));
      r.set_frame_number(extract<double>(state[6]));
      r.set_panel_number(extract<int>(state[7]));
      r.set_bounding_box(extract<int6>(state[8]));
      r.set_centroid_position(extract<vec3<double> >(state[9]));
      r.set_centroid_variance(extract<vec3<double> >(state[10]));
      r.set_shoebox(extract<flex_int>(state[11]));
      r.set_shoebox_weights(extract<flex_double>(state[12]));
      r.set_transformed_shoebox(extract<flex_double>(state[13]));
    }
  };

  void export_reflection()
  {
    class_<ReflectionBase>("ReflectionBase")
      .def(init <miller_index_type> ((
          arg("miller_index"))))
      .add_property("miller_index", 
        &Reflection::get_miller_index,
        &Reflection::set_miller_index)
      .def("is_zero", &Reflection::is_zero);

    class_<Reflection, bases<ReflectionBase> > ("Reflection")
      .def(init <const Reflection &>())
      .def(init <miller_index_type> ((
          arg("miller_index"))))
      .add_property("rotation_angle", 
        &Reflection::get_rotation_angle,
        &Reflection::set_rotation_angle)
      .add_property("beam_vector", 
        &Reflection::get_beam_vector,
        &Reflection::set_beam_vector)
      .add_property("image_coord_mm",
        &Reflection::get_image_coord_mm,
        &Reflection::set_image_coord_mm)
      .add_property("image_coord_px",
        &Reflection::get_image_coord_px,
        &Reflection::set_image_coord_px)
      .add_property("frame_number",
        &Reflection::get_frame_number,
        &Reflection::set_frame_number)
      .add_property("panel_number",
        &Reflection::get_panel_number,
        &Reflection::set_panel_number)      
      .add_property("bounding_box",
        &Reflection::get_bounding_box,
        &Reflection::set_bounding_box)  
      .add_property("shoebox",
        &Reflection::get_shoebox,
        &Reflection::set_shoebox)
      .add_property("shoebox_weights",
        &Reflection::get_shoebox_weights,
        &Reflection::set_shoebox_weights)
      .add_property("transformed_shoebox",
        &Reflection::get_transformed_shoebox,
        &Reflection::set_transformed_shoebox)
      .add_property("centroid_position",
        &Reflection::get_centroid_position,
        &Reflection::set_centroid_position)
      .add_property("centroid_variance",
        &Reflection::get_centroid_variance,
        &Reflection::set_centroid_variance)
      .def("__str__", &reflection_to_string)
      .def_pickle(ReflectionPickleSuite());          

    scitbx::af::boost_python::flex_wrapper 
      <Reflection>::plain("ReflectionList")
        .enable_pickling();        
  }

}}} // namespace dials::model::boost_python
