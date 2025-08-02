#include <PngIO.h>
#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/vector.h>
#include <nanobind/trampoline.h>
#include <optional>
#include <string>
#include <tuple>
#include <vector>

// TODO: delete this
#include <iostream>

using std::make_tuple, std::string, std::to_string;
namespace nb = nanobind;
using namespace RecFusion;
using namespace nb::literals;

struct PySensorListener : public SensorListener {
  NB_TRAMPOLINE(SensorListener, 1);

  void onSensorData(const ColorImage &colorImg,
                    const DepthImage &depthImg) override {
    NB_OVERRIDE_PURE(onSensorData, colorImg, depthImg);
  }
};

NB_MODULE(_pyRecFusionSDK_impl, m) {
  // TODO: keep these functions in the sdk submodule!
  m.def("init", &RecFusionSDK::init, "log_filename"_a = "");
  m.def("deinit", &RecFusionSDK::deinit);
  m.def("activate", &RecFusionSDK::activate, "key"_a, "code"_a = "");
  m.def("valid_license", &RecFusionSDK::validLicense);
  m.def("token", &RecFusionSDK::token);
  m.def("major_version", &RecFusionSDK::majorVersion);
  m.def("minor_version", &RecFusionSDK::minorVersion);
  m.def("build_version", &RecFusionSDK::buildVersion);
  // New API
  m.def("version", []() {
    return to_string(RecFusionSDK::majorVersion()) + "." +
           to_string(RecFusionSDK::minorVersion()) + "." +
           to_string(RecFusionSDK::buildVersion());
  });

  // RecFusion/Sensor.h
  // Sensor
  nb::class_<Sensor>(m, "Sensor")
      .def_prop_ro("device_name",
                   [](Sensor &sensor) {
                     char buffer[256];
                     auto result = sensor.deviceName(buffer, 256);
                     if (result == -2)
                       return string("buffer_too_small");
                     if (result == -1)
                       return string("sensor_manager_non_existing");
                     return string(buffer, result);
                   })
      .def_prop_ro("uuid",
                   [](Sensor &sensor) {
                     char buffer[256];
                     auto result = sensor.uuid(buffer, 256);
                     if (result == -2)
                       return string("buffer_too_small");
                     if (result == -1)
                       return string("sensor_manager_non_existing");
                     return string(buffer, result);
                   })
      .def("depth_format_count", &Sensor::depthFormatCount)
      .def("color_format_count", &Sensor::colorFormatCount)
      .def("depth_format", &Sensor::depthFormat, "id"_a)
      .def("color_format", &Sensor::colorFormat, "id"_a)
      .def("open", &Sensor::open, "color_width"_a = 640, "color_height"_a = 480,
           "depth_width"_a = 640, "depth_height"_a = 480, "max_fps"_a = 30)
      .def("close", &Sensor::close)
      .def("start", &Sensor::start)
      .def("stop", &Sensor::stop)
      .def_prop_ro("is_open", &Sensor::isOpen)
      .def_prop_ro("depth_width", &Sensor::depthWidth)
      .def_prop_ro("depth_height", &Sensor::depthHeight)
      .def_prop_ro("color_width", &Sensor::colorWidth)
      .def_prop_ro("color_height", &Sensor::colorHeight)
      .def_prop_ro("depth_intrinsics", &Sensor::depthIntrinsics)
      .def_prop_ro("color_intrinsics", &Sensor::colorIntrinsics)
      .def_prop_ro("depth_to_color_transformation",
                   &Sensor::depthToColorTransformation)
      .def_prop_ro("supports_color", &Sensor::supportsColor)
      .def("set_laser_state", &Sensor::setLaserState)
      .def_prop_ro("supports_auto_white_balance",
                   &Sensor::supportsAutoWhiteBalance)
      .def_prop_ro("supports_auto_exposure", &Sensor::supportsAutoExposure)
      .def(
          "add_listener",
          [](Sensor &sensor, SensorListener &listener) {
            sensor.addListener(&listener);
          },
          "listener"_a)
      .def("remove_listener", &Sensor::removeListener, "listener"_a)
      .def("read_image", &Sensor::readImage, "img_depth"_a, "img_color"_a,
           "timeout"_a = 2000)
      // New API
      .def_prop_ro("image_size",
                   [](Sensor &sensor) {
                     return make_tuple(
                         sensor.colorWidth(), sensor.colorHeight(),
                         sensor.depthWidth(), sensor.depthHeight());
                   })
      .def_prop_ro("depth_formats",
                   [](Sensor &sensor) {
                     std::vector<Sensor::Format> formats;
                     for (int i = 0; i < sensor.depthFormatCount(); ++i) {
                       formats.emplace_back(sensor.depthFormat(i));
                     }
                     return formats;
                   })
      .def_prop_ro("color_formats", [](Sensor &sensor) {
        std::vector<Sensor::Format> formats;
        for (int i = 0; i < sensor.colorFormatCount(); ++i) {
          formats.emplace_back(sensor.colorFormat(i));
        }
        return formats;
      });

  nb::class_<Sensor::Format>(m, "SensorFormat")
      // .def(nb::init<>())
      .def_ro("width", &Sensor::Format::width)
      .def_ro("height", &Sensor::Format::height)
      .def_ro("fps", &Sensor::Format::fps)
      // New API
      .def("__repr__", [](Sensor::Format &format) {
        return to_string(format.width) + "x" + to_string(format.height) + "@" +
               to_string(format.fps) + "fps";
      });

  nb::class_<SensorListener, PySensorListener>(m, "SensorListener")
      .def(nb::init<>())
      .def("on_sensor_data", &SensorListener::onSensorData);

  nb::class_<SensorManager>(m, "SensorManager")
      .def(nb::init<>())
      .def_prop_ro("device_count", &SensorManager::deviceCount)
      .def("sensor", &SensorManager::sensor, "id"_a, nb::rv_policy::reference)
      // New API
      .def(
          "open_all",
          [](SensorManager &manager, int colorWidth, int colorHeight,
             int depthWidth, int depthHeight, double maxFps) {
            std::vector<Sensor *> sensors;
            for (int i = 0; i < manager.deviceCount(); ++i) {
              auto sensor = manager.sensor(i);
              if (sensor->open(colorWidth, colorHeight, depthWidth, depthHeight,
                               maxFps)) {
                sensors.emplace_back(sensor);
              }
            }
            return sensors;
          },
          "color_width"_a = 640, "color_height"_a = 480, "depth_width"_a = 640,
          "depth_height"_a = 480, "max_fps"_a = 30, nb::rv_policy::reference)
      .def(
          "open_any",
          [](SensorManager &manager, int colorWidth, int colorHeight,
             int depthWidth, int depthHeight, double maxFps) -> Sensor * {
            if (manager.deviceCount() > 0) {
              auto sensor = manager.sensor(0);
              if (sensor->open(colorWidth, colorHeight, depthWidth, depthHeight,
                               maxFps)) {
                return sensor;
              }
            }
            return nullptr;
          },
          "color_width"_a = 640, "color_height"_a = 480, "depth_width"_a = 640,
          "depth_height"_a = 480, "max_fps"_a = 30, nb::rv_policy::reference);

  // ReconstructionParams
  nb::class_<ReconstructionParams>(m, "ReconstructionParams")
      .def(nb::init<int>(), "sensors"_a = 1)
      .def_prop_ro("sensors", &ReconstructionParams::sensors)
      .def("set_image_size", &ReconstructionParams::setImageSize,
           "color_width"_a, "color_height"_a, "depth_width"_a, "depth_height"_a,
           "sensor"_a = 0)
      // TODO: imageSize
      .def("set_intrinsics", &ReconstructionParams::setIntrinsics, "K"_a,
           "sensor"_a = 0)
      .def("set_color_intrinsics", &ReconstructionParams::setColorIntrinsics,
           "K"_a, "sensor"_a = 0)
      .def("set_depth_to_color_transformation",
           &ReconstructionParams::setDepthToColorTransformation, "T"_a,
           "sensor"_a = 0);
  // .def("intrinsics
  // Reconstruction
  nb::class_<Reconstruction>(m, "Reconstruction")
      .def(nb::init<ReconstructionParams>())
      .def_prop_ro("good", &Reconstruction::good)
      .def(
          "add_frame2",
          [](Reconstruction &reconstruction, int sensor, DepthImage &imgDepth,
             ColorImage &imgColor) {
            return reconstruction.addFrame(sensor, imgDepth, imgColor);
          },
          "sensor"_a, "img_depth"_a, "img_color"_a)
      .def("add_frame", &Reconstruction::addFrame, "sensor"_a, "img_depth"_a,
           "img_color"_a, "tracking_status"_a = 0, "img_scene"_a = 0, "T"_a = 0,
           "sensor_T"_a = 0, "tracked_t"_a = 0,
           "dont_force_first_frame"_a = false)
      .def("get_mesh", [](Reconstruction &reconstruction) {
        auto mesh = new Mesh();
        reconstruction.getMesh(mesh);
        return mesh;
      });

  // RecFusion/Common.h
  // ColorImage
  nb::class_<ColorImage>(m, "ColorImage")
      .def(nb::init<int, int, int, unsigned char *>(), "width"_a, "height"_a,
           "channels"_a = 3, "data"_a = nb::none())
      .def_prop_ro("width", &ColorImage::width)
      .def_prop_ro("height", &ColorImage::height)
      .def_prop_ro("channels", &ColorImage::channels)
      // New API
      .def_static(
          "empty",
          [](int width, int height, int channels) {
            return new ColorImage(width, height, channels);
          },
          "width"_a, "height"_a, "channels"_a = 3)
      .def_static(
          "for_sensor",
          [](const Sensor &sensor) {
            return new ColorImage(sensor.colorWidth(), sensor.colorHeight());
          },
          "sensor"_a)
      .def(
          "to_image",
          [](ColorImage &img_color, const char *filename, int compression = 3) {
            // BUG: for some reason, ColorImage::channels() returns 0
            auto num_channels =
                img_color.channels() > 0 ? img_color.channels() : 3;
            PngIO::writeImage(filename, img_color.data(), img_color.width(),
                              img_color.height(), num_channels, 0, compression);
          },
          "filename"_a, "compression"_a = 3);

  nb::class_<DepthImage>(m, "DepthImage")
      .def(nb::init<int, int, float *>(), "width"_a, "height"_a, "data"_a = 0)
      .def_prop_ro("width", &DepthImage::width)
      .def_prop_ro("height", &DepthImage::height)
      // New API
      .def_static(
          "empty",
          [](int width, int height) { return new DepthImage(width, height); },
          "width"_a, "height"_a)
      .def_static(
          "for_sensor",
          [](const Sensor &sensor) {
            return new DepthImage(sensor.depthWidth(), sensor.depthHeight());
          },
          "sensor"_a)
      .def(
          "to_image",
          [](DepthImage &img_depth, const char *filename, int compression = 3) {
            PngIO::writeImage(filename, img_depth.data(), img_depth.width(),
                              img_depth.height(), 1, compression);
          },
          "filename"_a, "compression"_a = 3);

  // Vec3
  nb::class_<Vec3>(m, "Vec3")
      .def(nb::init<double, double, double>(), "x"_a, "y"_a, "z"_a)
      .def_prop_ro("x", [](Vec3 &vec) { return vec[0]; })
      .def_prop_ro("y", [](Vec3 &vec) { return vec[1]; })
      .def_prop_ro("z", [](Vec3 &vec) { return vec[2]; });
  // Vec3i
  nb::class_<Vec3i>(m, "Vec3i")
      .def(nb::init<int, int, int>(), "x"_a, "y"_a, "z"_a)
      .def_prop_ro("x", [](Vec3i &vec) { return vec[0]; })
      .def_prop_ro("y", [](Vec3i &vec) { return vec[1]; })
      .def_prop_ro("z", [](Vec3i &vec) { return vec[2]; });
  // Mat3
  nb::class_<Mat3>(m, "Mat3").def(nb::init<double *>());
  // Mat4
  nb::class_<Mat4>(m, "Mat4")
      .def(nb::init<double *>())
      .def("inverse", &Mat4::inverse)
      .def_static("from_euler", &Mat4::fromEuler, "rx"_a, "ry"_a, "rz"_a);
  // RecFusion/Mesh.h
  nb::class_<Mesh>(m, "Mesh")
      .def(nb::init<>())
      // static Mesh* create()
      // TODO: this doesn't work :(
      // .def_static("create", "vertex_count"_a, "vertices"_a,
      // "triangle_count"_a,
      //             "triangle_indices"_a, "colors"_a = nb::none(), "normals"_a
      //             = nb::none(), "volume_resolution"_a = 512, &Mesh::create)
      .def_prop_ro("vertex_count", &Mesh::vertexCount)
      .def_prop_ro("triangle_count", &Mesh::triangleCount)
      .def(
          "vertex",
          [](Mesh &mesh, int idx) {
            auto coord = mesh.vertex(idx);
            return make_tuple(coord.x, coord.y, coord.z);
          },
          "idx"_a)
      .def(
          "set_vertex",
          [](Mesh &mesh, int idx, double x, double y, double z) {
            mesh.setVertex(idx, {x, y, z});
          },
          "idx"_a, "x"_a, "y"_a, "z"_a)
      .def(
          "normal",
          [](Mesh &mesh, int idx) {
            auto normal = mesh.normal(idx);
            return make_tuple(normal.x, normal.y, normal.z);
          },
          "idx"_a)
      .def(
          "set_normal",
          [](Mesh &mesh, int idx, double nx, double ny, double nz) {
            mesh.setNormal(idx, {nx, ny, nz});
          },
          "idx"_a, "nx"_a, "ny"_a, "nz"_a)
      .def(
          "color",
          [](Mesh &mesh, int idx) {
            auto color = mesh.color(idx);
            return make_tuple(color.r, color.g, color.b);
          },
          "idx"_a)
      .def(
          "set_color",
          [](Mesh &mesh, int idx, double r, double g, double b) {
            mesh.setNormal(idx, {r, g, b});
          },
          "idx"_a, "r"_a, "g"_a, "b"_a)
      .def_prop_ro("center", [](Mesh &mesh) {
        auto center = mesh.center();
        return make_tuple(center[0], center[1], center[2]);
      });
  //   .def_prop_ro("vertices", [](Mesh &mesh) {
  //     double *data = new double[mesh.vertexCount() * 3];
  //     for (int i = 0, j = 0; i < mesh.vertexCount(); ++i, j += 3) {
  //       auto v = mesh.vertex(i);
  //       data[j] = v.x;
  //       data[j+1] = v.y;
  //       data[j+2] = v.z;
  //     }
  //    // nb::capsule owner(data, [](void *p) noexcept {
  //    //       delete[] (double *) p;
  //    //    });
  //   return nb::ndarray<nb::numpy, double, nb::ndim<2>>(
  //           /* data = */ data,
  //           /* shape = */ { (size_t)mesh.vertexCount(), 3 }
  //       );
  // });
  // .def(
  //     "triangle",
  //     [](Mesh &mesh, int idx) {
  //       auto triangle = mesh.triangle(idx);
  //       return make_tuple(triangle.i1, triangle.i2, triangle.i3);
  //     },
  //     "idx"_a);
  // .def("add_triangle");
  //
  nb::class_<RFSRecorder>(m, "RFSRecorder")
      .def(nb::init<const char *>())
      .def("init", &RFSRecorder::init, "color_width"_a, "color_height"_a,
           "depth_width"_a, "depth_height"_a, "depth_k"_a,
           "color_k"_a = nb::none(), "depth_to_color_t"_a = nb::none())
      .def("cleanup", &RFSRecorder::cleanup)
      .def("start", &RFSRecorder::start)
      .def("stop", &RFSRecorder::stop)
      .def("add_frame", &RFSRecorder::addFrame, "img_depth"_a, "img_color"_a)
      // New API
      .def("init_from_sensor", [](RFSRecorder &recorder, Sensor &sensor) {
        recorder.init(sensor.colorWidth(), sensor.colorHeight(),
                      sensor.depthWidth(), sensor.depthHeight(),
                      sensor.depthIntrinsics());
      });

  nb::class_<RFSPlayback>(m, "RFSPlayback")
      .def(nb::init<>())
      .def("open", &RFSPlayback::open, "filename"_a)
      .def("close", &RFSPlayback::close)
      .def_prop_ro("frame_count", &RFSPlayback::frameCount)
      .def("read_image", &RFSPlayback::readImage, "frame"_a, "img_depth"_a,
           "img_color"_a)
      .def_prop_ro("color_width", &RFSPlayback::colorWidth)
      .def_prop_ro("color_height", &RFSPlayback::colorHeight)
      .def_prop_ro("depth_width", &RFSPlayback::depthWidth)
      .def_prop_ro("depth_height", &RFSPlayback::depthHeight)
      .def_prop_ro("intrinsics", &RFSPlayback::intrinsics)
      .def_prop_ro("color_intrinsics", &RFSPlayback::colorIntrinsics)
      .def_prop_ro("depth_to_color_t", &RFSPlayback::depthToColorT)
      // New API
      .def_prop_ro("depth_intrinsics", &RFSPlayback::intrinsics)
      .def_prop_ro("depth_to_color_transformation",
                   &RFSPlayback::depthToColorT);

  // Calibration.h
  nb::class_<Calibration>(m, "Calibration")
      .def(nb::init<>())
      .def("init", &Calibration::init, "num_sensors"_a)
      .def("set_marker", &Calibration::setMarker, "marked_id"_a,
           "marker_size"_a, "marker_t"_a = nb::none())
      .def("set_image", &Calibration::setImage, "sensor"_a, "img_depth"_a,
           "img_color"_a, "depth_k"_a, "color_k"_a,
           "depth_to_color_t"_a = nb::none())
      .def("calibrate", &Calibration::calibrate)
      .def(
          "get_transformation",
          [](Calibration &calibration, int sensor) -> std::optional<Mat4 *> {
            auto T = new Mat4();
            if (calibration.getTransformation(sensor, *T)) {
              return T;
            } else {
              // TODO: make sure we are returing here None!
              return {};
            }
          },
          "sensor"_a)
      .def_static("get_marker_pose", &Calibration::getMarkerPose, "marker_id"_a,
                  "marker_size"_a, "img_color"_a, "color_k"_a, "t"_a);

  nb::class_<MeshViewer>(m, "MeshViewer")
      .def(nb::init<>())
      .def("show_mesh", &MeshViewer::showMesh, "mesh"_a);
}
