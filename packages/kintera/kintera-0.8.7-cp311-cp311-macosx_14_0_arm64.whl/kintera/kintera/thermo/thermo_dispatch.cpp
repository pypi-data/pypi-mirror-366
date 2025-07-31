// torch
#include <ATen/Dispatch.h>
#include <ATen/Parallel.h>
#include <ATen/native/ReduceOpsUtils.h>
#include <ATen/native/cpu/Loops.h>

// kintera
#include "equilibrate_tp.h"
#include "equilibrate_uv.h"
#include "thermo_dispatch.hpp"

namespace kintera {

void call_equilibrate_tp_cpu(at::TensorIterator &iter, int ngas,
                             at::Tensor const &stoich,
                             user_func1 const *logsvp_func, float logsvp_eps,
                             int max_iter) {
  int grain_size = iter.numel() / at::get_num_threads();

  AT_DISPATCH_FLOATING_TYPES(iter.dtype(), "call_equilibrate_tp_cpu", [&] {
    int nspecies = at::native::ensure_nonempty_size(stoich, 0);
    int nreaction = at::native::ensure_nonempty_size(stoich, 1);

    auto stoich_ptr = stoich.data_ptr<scalar_t>();

    iter.for_each(
        [&](char **data, const int64_t *strides, int64_t n) {
          for (int i = 0; i < n; i++) {
            auto gain = reinterpret_cast<scalar_t *>(data[0] + i * strides[0]);
            auto diag = reinterpret_cast<scalar_t *>(data[1] + i * strides[1]);
            auto xfrac = reinterpret_cast<scalar_t *>(data[2] + i * strides[2]);
            auto temp = reinterpret_cast<scalar_t *>(data[3] + i * strides[3]);
            auto pres = reinterpret_cast<scalar_t *>(data[4] + i * strides[4]);
            auto mask = reinterpret_cast<scalar_t *>(data[5] + i * strides[5]);
            int max_iter_i = max_iter;
            equilibrate_tp(gain, diag, xfrac, *temp, *pres, *mask, stoich_ptr,
                           nspecies, nreaction, ngas, logsvp_func, logsvp_eps,
                           &max_iter_i);
          }
        },
        grain_size);
  });
}

void call_equilibrate_uv_cpu(at::TensorIterator &iter, at::Tensor const &stoich,
                             at::Tensor const &intEng_offset,
                             at::Tensor const &cv_const,
                             user_func1 const *logsvp_func,
                             user_func1 const *logsvp_func_ddT,
                             user_func2 const *intEng_extra,
                             user_func2 const *intEng_extra_ddT,
                             float logsvp_eps, int max_iter) {
  int grain_size = iter.numel() / at::get_num_threads();

  AT_DISPATCH_FLOATING_TYPES(iter.dtype(), "call_equilibrate_uv_cpu", [&] {
    int nspecies = at::native::ensure_nonempty_size(stoich, 0);
    int nreaction = at::native::ensure_nonempty_size(stoich, 1);

    auto stoich_ptr = stoich.data_ptr<scalar_t>();
    auto intEng_offset_ptr = intEng_offset.data_ptr<scalar_t>();
    auto cv_const_ptr = cv_const.data_ptr<scalar_t>();

    iter.for_each(
        [&](char **data, const int64_t *strides, int64_t n) {
          for (int i = 0; i < n; i++) {
            auto gain = reinterpret_cast<scalar_t *>(data[0] + i * strides[0]);
            auto diag = reinterpret_cast<scalar_t *>(data[1] + i * strides[1]);
            auto conc = reinterpret_cast<scalar_t *>(data[2] + i * strides[2]);
            auto temp = reinterpret_cast<scalar_t *>(data[3] + i * strides[3]);
            auto intEng =
                reinterpret_cast<scalar_t *>(data[4] + i * strides[4]);
            auto mask = reinterpret_cast<scalar_t *>(data[5] + i * strides[5]);

            int max_iter_i = max_iter;
            equilibrate_uv(gain, diag, temp, conc, *intEng, *mask, stoich_ptr,
                           nspecies, nreaction, intEng_offset_ptr, cv_const_ptr,
                           logsvp_func, logsvp_func_ddT, intEng_extra,
                           intEng_extra_ddT, logsvp_eps, &max_iter_i);
          }
        },
        grain_size);
  });
}

}  // namespace kintera

namespace at::native {

DEFINE_DISPATCH(call_equilibrate_tp);
DEFINE_DISPATCH(call_equilibrate_uv);

REGISTER_ALL_CPU_DISPATCH(call_equilibrate_tp,
                          &kintera::call_equilibrate_tp_cpu);
REGISTER_ALL_CPU_DISPATCH(call_equilibrate_uv,
                          &kintera::call_equilibrate_uv_cpu);

}  // namespace at::native
