/*
 * UnderscoreC PyTorch Integration Module
 *
 * This module provides PyTorch tensor operations using the direct C++ API
 * for better performance compared to standard Python protocols.
 */

#include "underscorec_torch.h"
#include <torch/csrc/autograd/python_variable.h>
#include <torch/extension.h>
#include <torch/torch.h>

PyObject *apply_torch_operation(UnderscoreObject *self,
                                const torch::Tensor &tensor) {
  // First check if operation is supported
  switch (self->operation) {
  case UnderscoreOperation::ADD:
  case UnderscoreOperation::SUB:
  case UnderscoreOperation::MUL:
  case UnderscoreOperation::DIV:
  case UnderscoreOperation::POW:
  case UnderscoreOperation::MOD:
  case UnderscoreOperation::GT:
  case UnderscoreOperation::LT:
  case UnderscoreOperation::GE:
  case UnderscoreOperation::LE:
  case UnderscoreOperation::EQ:
  case UnderscoreOperation::NE:
    // Operation is supported, continue with operand conversion
    break;
  default:
    // Operation not supported by PyTorch optimization path
    // Return nullptr to fall back to standard Python protocols
    return nullptr;
  }

  // Only convert operand if we have a supported operation
  torch::Tensor operand;
  try {
    // Convert operand to tensor if it's not already
    if (THPVariable_Check(self->operand)) {
      operand = THPVariable_Unpack(self->operand);
    } else if (PyFloat_Check(self->operand)) {
      operand = torch::scalar_tensor(PyFloat_AsDouble(self->operand));
    } else if (PyLong_Check(self->operand)) {
      operand = torch::scalar_tensor(PyLong_AsLong(self->operand));
    } else {
      // Try to convert via torch.tensor()
      PyObject *torch_module = PyImport_ImportModule("torch");
      if (!torch_module)
        return nullptr;

      PyObject *torch_tensor_func =
          PyObject_GetAttrString(torch_module, "tensor");
      Py_DECREF(torch_module);
      if (!torch_tensor_func)
        return nullptr;

      PyObject *operand_tensor = PyObject_CallFunctionObjArgs(
          torch_tensor_func, self->operand, nullptr);
      Py_DECREF(torch_tensor_func);

      if (!operand_tensor) {
        // torch.tensor() failed - clear error for clean fallback
        if (PyErr_Occurred())
          PyErr_Clear();
        return nullptr;
      }

      try {
        operand = THPVariable_Unpack(operand_tensor);
        Py_DECREF(operand_tensor);
      } catch (...) {
        // this is not a fatal error, thus we need to handle it gracefully
        Py_DECREF(operand_tensor);
        return nullptr;
      }
    }
  } catch (...) {
    // Fallback to standard Python protocols if conversion fails
    if (PyErr_Occurred())
      PyErr_Clear();
    return nullptr;
  }

  // Perform the operation using PyTorch C++ API
  torch::Tensor result;
  switch (self->operation) { // NOLINT
  case UnderscoreOperation::ADD:
    result = torch::add(tensor, operand);
    break;
  case UnderscoreOperation::SUB:
    result = torch::sub(tensor, operand);
    break;
  case UnderscoreOperation::MUL:
    result = torch::mul(tensor, operand);
    break;
  case UnderscoreOperation::DIV:
    result = torch::div(tensor, operand);
    break;
  case UnderscoreOperation::POW:
    result = torch::pow(tensor, operand);
    break;
  case UnderscoreOperation::MOD:
    result = torch::remainder(tensor, operand);
    break;
  case UnderscoreOperation::GT:
    result = torch::gt(tensor, operand);
    break;
  case UnderscoreOperation::LT:
    result = torch::lt(tensor, operand);
    break;
  case UnderscoreOperation::GE:
    result = torch::ge(tensor, operand);
    break;
  case UnderscoreOperation::LE:
    result = torch::le(tensor, operand);
    break;
  case UnderscoreOperation::EQ:
    result = torch::eq(tensor, operand);
    break;
  case UnderscoreOperation::NE:
    result = torch::ne(tensor, operand);
    break;
  }

  return THPVariable_Wrap(result);
}

PyObject *apply_torch_operation_safe(UnderscoreObject *self,
                                     PyObject *tensor_obj) {
  if (!THPVariable_Check(tensor_obj))
    return nullptr;

  try {
    return apply_torch_operation(self, THPVariable_Unpack(tensor_obj));
  } catch (const std::exception &e) {
    return nullptr;
  }
}
