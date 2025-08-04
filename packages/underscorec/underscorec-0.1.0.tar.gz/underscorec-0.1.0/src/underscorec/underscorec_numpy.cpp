/*
 * UnderscoreC NumPy Integration Module
 * 
 * This module provides optimized NumPy array operations using cached ufuncs
 * for better performance compared to standard Python protocols.
 */

#include "underscorec_numpy.h"
#include <numpy/arrayobject.h>
#include <numpy/ndarraytypes.h>
#include <numpy/npy_math.h>
#include <numpy/ufuncobject.h>

// Cache NumPy ufuncs to avoid repeated imports and lookups
static PyObject *numpy_add_ufunc = NULL;
static PyObject *numpy_subtract_ufunc = NULL;
static PyObject *numpy_multiply_ufunc = NULL;
static PyObject *numpy_divide_ufunc = NULL;
static PyObject *numpy_power_ufunc = NULL;
static PyObject *numpy_remainder_ufunc = NULL;
static PyObject *numpy_greater_ufunc = NULL;
static PyObject *numpy_less_ufunc = NULL;
static PyObject *numpy_greater_equal_ufunc = NULL;
static PyObject *numpy_less_equal_ufunc = NULL;
static PyObject *numpy_equal_ufunc = NULL;
static PyObject *numpy_not_equal_ufunc = NULL;

int initialize_numpy_ufuncs(void) {
  PyObject *numpy = PyImport_ImportModule("numpy");
  if (!numpy)
    return -1;

  // Cache all ufuncs once
  numpy_add_ufunc = PyObject_GetAttrString(numpy, "add");
  numpy_subtract_ufunc = PyObject_GetAttrString(numpy, "subtract");
  numpy_multiply_ufunc = PyObject_GetAttrString(numpy, "multiply");
  numpy_divide_ufunc = PyObject_GetAttrString(numpy, "divide");
  numpy_power_ufunc = PyObject_GetAttrString(numpy, "power");
  numpy_remainder_ufunc = PyObject_GetAttrString(numpy, "remainder");
  numpy_greater_ufunc = PyObject_GetAttrString(numpy, "greater");
  numpy_less_ufunc = PyObject_GetAttrString(numpy, "less");
  numpy_greater_equal_ufunc = PyObject_GetAttrString(numpy, "greater_equal");
  numpy_less_equal_ufunc = PyObject_GetAttrString(numpy, "less_equal");
  numpy_equal_ufunc = PyObject_GetAttrString(numpy, "equal");
  numpy_not_equal_ufunc = PyObject_GetAttrString(numpy, "not_equal");

  Py_DECREF(numpy);

  return (numpy_add_ufunc && numpy_subtract_ufunc && numpy_multiply_ufunc &&
          numpy_divide_ufunc && numpy_power_ufunc && numpy_remainder_ufunc &&
          numpy_greater_ufunc && numpy_less_ufunc &&
          numpy_greater_equal_ufunc && numpy_less_equal_ufunc &&
          numpy_equal_ufunc && numpy_not_equal_ufunc)
             ? 0
             : -1;
}

PyObject *apply_numpy_operation_cached(UnderscoreObject *self, PyObject *array) {
  // Use cached ufuncs for better performance - no repeated imports/lookups
  PyObject *ufunc;
  switch (self->operation) {
  case UnderscoreOperation::ADD:
    ufunc = numpy_add_ufunc;
    break;
  case UnderscoreOperation::SUB:
    ufunc = numpy_subtract_ufunc;
    break;
  case UnderscoreOperation::MUL:
    ufunc = numpy_multiply_ufunc;
    break;
  case UnderscoreOperation::DIV:
    ufunc = numpy_divide_ufunc;
    break;
  case UnderscoreOperation::POW:
    ufunc = numpy_power_ufunc;
    break;
  case UnderscoreOperation::MOD:
    ufunc = numpy_remainder_ufunc;
    break;
  case UnderscoreOperation::GT:
    ufunc = numpy_greater_ufunc;
    break;
  case UnderscoreOperation::LT:
    ufunc = numpy_less_ufunc;
    break;
  case UnderscoreOperation::GE:
    ufunc = numpy_greater_equal_ufunc;
    break;
  case UnderscoreOperation::LE:
    ufunc = numpy_less_equal_ufunc;
    break;
  case UnderscoreOperation::EQ:
    ufunc = numpy_equal_ufunc;
    break;
  case UnderscoreOperation::NE:
    ufunc = numpy_not_equal_ufunc;
    break;
  default:
    return nullptr; // Operation not supported for NumPy arrays
  }

  if (!ufunc) {
    // Lazy initialization if ufuncs haven't been cached yet
    if (initialize_numpy_ufuncs() < 0)
      return nullptr;
    // Retry with the operation
    return apply_numpy_operation_cached(self, array);
  }

  return PyObject_CallFunctionObjArgs(ufunc, array, self->operand, NULL);
}

void cleanup_numpy_ufuncs(void) {
  Py_XDECREF(numpy_add_ufunc);
  Py_XDECREF(numpy_subtract_ufunc);
  Py_XDECREF(numpy_multiply_ufunc);
  Py_XDECREF(numpy_divide_ufunc);
  Py_XDECREF(numpy_power_ufunc);
  Py_XDECREF(numpy_remainder_ufunc);
  Py_XDECREF(numpy_greater_ufunc);
  Py_XDECREF(numpy_less_ufunc);
  Py_XDECREF(numpy_greater_equal_ufunc);
  Py_XDECREF(numpy_less_equal_ufunc);
  Py_XDECREF(numpy_equal_ufunc);
  Py_XDECREF(numpy_not_equal_ufunc);
  
  // Reset pointers
  numpy_add_ufunc = NULL;
  numpy_subtract_ufunc = NULL;
  numpy_multiply_ufunc = NULL;
  numpy_divide_ufunc = NULL;
  numpy_power_ufunc = NULL;
  numpy_remainder_ufunc = NULL;
  numpy_greater_ufunc = NULL;
  numpy_less_ufunc = NULL;
  numpy_greater_equal_ufunc = NULL;
  numpy_less_equal_ufunc = NULL;
  numpy_equal_ufunc = NULL;
  numpy_not_equal_ufunc = NULL;
}