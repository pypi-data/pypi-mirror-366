// torch
#include <ATen/Dispatch.h>
#include <ATen/TensorIterator.h>
#include <ATen/native/ReduceOpsUtils.h>
#include <c10/cuda/CUDAGuard.h>

// kintera
#include <kintera/loops.cuh>
#include "equilibrate_tp.h"
#include "equilibrate_uv.h"
#include "thermo_dispatch.hpp"

namespace kintera {

void call_equilibrate_tp_cuda(at::TensorIterator &iter, int ngas,
                             at::Tensor const& stoich,
                             user_func1 const *logsvp_func, float logsvp_eps,
                             int max_iter) {
  AT_DISPATCH_FLOATING_TYPES(iter.dtype(), "call_equilibrate_tp_cuda", [&] {
    int nspecies = at::native::ensure_nonempty_size(stoich, 0);
    int nreaction = at::native::ensure_nonempty_size(stoich, 1);

    auto stoich_ptr = stoich.data_ptr<scalar_t>();

    native::gpu_kernel<6>(
        iter, [=] GPU_LAMBDA(char* const data[6], unsigned int strides[6]) {
        auto gain = reinterpret_cast<scalar_t *>(data[0] + strides[0]);
        auto diag = reinterpret_cast<scalar_t *>(data[1] + strides[1]);
        auto xfrac = reinterpret_cast<scalar_t *>(data[2] + strides[2]);
        auto temp = reinterpret_cast<scalar_t *>(data[3] + strides[3]);
        auto pres = reinterpret_cast<scalar_t *>(data[4] + strides[4]);
        auto mask = reinterpret_cast<scalar_t *>(data[5] + strides[5]);
        int max_iter_i = max_iter;
        equilibrate_tp(gain, diag, xfrac, *temp, *pres, *mask,
                       stoich_ptr, nspecies,
                       nreaction, ngas, logsvp_func, logsvp_eps, &max_iter_i);
      });
  });
}

void call_equilibrate_uv_cuda(at::TensorIterator &iter,
                             at::Tensor const& stoich,
                             at::Tensor const& intEng_offset,
                             at::Tensor const& cv_const,
                             user_func1 const *logsvp_func,
                             user_func1 const *logsvp_func_ddT,
                             user_func2 const *intEng_extra,
                             user_func2 const *intEng_extra_ddT,
                             float logsvp_eps, int max_iter) {
  AT_DISPATCH_FLOATING_TYPES(iter.dtype(), "call_equilibrate_uv_cuda", [&] {
    int nspecies = at::native::ensure_nonempty_size(stoich, 0);
    int nreaction = at::native::ensure_nonempty_size(stoich, 1);

    auto stoich_ptr = stoich.data_ptr<scalar_t>();
    auto intEng_offset_ptr = intEng_offset.data_ptr<scalar_t>();
    auto cv_const_ptr = cv_const.data_ptr<scalar_t>();

    native::gpu_kernel<6>(
        iter, [=] GPU_LAMBDA(char* const data[6], unsigned int strides[6]) {
        auto gain = reinterpret_cast<scalar_t *>(data[0] + strides[0]);
        auto diag = reinterpret_cast<scalar_t *>(data[1] + strides[1]);
        auto conc = reinterpret_cast<scalar_t *>(data[2] + strides[2]);
        auto temp = reinterpret_cast<scalar_t *>(data[3] + strides[3]);
        auto intEng = reinterpret_cast<scalar_t *>(data[4] + strides[4]);
        auto mask = reinterpret_cast<scalar_t *>(data[5] + strides[5]);
        int max_iter_i = max_iter;
        equilibrate_uv(gain, diag, temp, conc, *intEng, *mask,
                       stoich_ptr, nspecies,
                       nreaction, intEng_offset_ptr, cv_const_ptr, logsvp_func,
                       logsvp_func_ddT, intEng_extra, intEng_extra_ddT,
                       logsvp_eps, &max_iter_i);
      });
  });
}

}  // namespace kintera

namespace at::native {

REGISTER_CUDA_DISPATCH(call_equilibrate_tp,
                       &kintera::call_equilibrate_tp_cuda);

REGISTER_CUDA_DISPATCH(call_equilibrate_uv,
                       &kintera::call_equilibrate_uv_cuda);

}  // namespace at::native
