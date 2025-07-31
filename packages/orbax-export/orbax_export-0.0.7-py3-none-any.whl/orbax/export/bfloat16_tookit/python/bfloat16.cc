#include "orbax/export/bfloat16_tookit/bfloat16.h"

#include <pybind11/pybind11.h>

#include "third_party/pybind11/include/pybind11/cast.h"
#include "third_party/pybind11_abseil/absl_casters.h"
#include "third_party/pybind11_abseil/no_throw_status.h"
#include "third_party/pybind11_abseil/status_casters.h"
#include "third_party/pybind11_protobuf/native_proto_caster.h"

namespace tensorflow::orbax {
namespace {

PYBIND11_MODULE(bfloat16, m) {
  pybind11_protobuf::ImportNativeProtoCasters();
  pybind11::google::ImportStatusModule();

  m.doc() = "Python bindings for bfloat16";

  pybind11::enum_<DeviceAgnosticBFloat16Scope>(m, "DeviceAgnosticBFloat16Scope")
      .value("DEVICE", DeviceAgnosticBFloat16Scope::kDevice)
      .value("BATCH", DeviceAgnosticBFloat16Scope::kBatch)
      .value("ALL", DeviceAgnosticBFloat16Scope::kAll)
      .value("OTHER", DeviceAgnosticBFloat16Scope::kOther)
      .export_values();

  m.def("apply_bfloat16_optimization", &ApplyBFloat16Optimization,
        "Convert a Function or its ancester to bfloat16, depending on "
        "bfloat16_scope",
        pybind11::arg("bfloat16_scope"), pybind11::arg("options"),
        pybind11::arg("bfloat16_func"));
}

}  // namespace
}  // namespace tensorflow::orbax
