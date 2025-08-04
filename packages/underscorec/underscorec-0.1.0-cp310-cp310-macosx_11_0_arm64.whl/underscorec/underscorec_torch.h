/*
 * UnderscoreC PyTorch Integration Header
 *
 * Header file for PyTorch tensor operations using direct C++ API
 */

#ifndef UNDERSCOREC_TORCH_H
#define UNDERSCOREC_TORCH_H

#include "underscorec_types.h"
#include <Python.h>

// Include PyTorch headers for tensor operations
#include <torch/csrc/autograd/python_variable.h>
#include <torch/extension.h>
#include <torch/torch.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Apply PyTorch operation using direct C++ API
 * @param self UnderscoreObject containing the operation and operand
 * @param tensor PyTorch tensor to operate on
 * @return Result PyObject or NULL on error
 */
PyObject *apply_torch_operation(UnderscoreObject *self,
                                const torch::Tensor &tensor);

/**
 * Safe wrapper for PyTorch operations that checks tensor type first
 * @param self UnderscoreObject containing the operation and operand
 * @param tensor_obj Python object that should be a PyTorch tensor
 * @return Result PyObject or NULL if not a tensor or on error
 */
PyObject *apply_torch_operation_safe(UnderscoreObject *self,
                                     PyObject *tensor_obj);

#ifdef __cplusplus
}
#endif

#endif // UNDERSCOREC_TORCH_H
