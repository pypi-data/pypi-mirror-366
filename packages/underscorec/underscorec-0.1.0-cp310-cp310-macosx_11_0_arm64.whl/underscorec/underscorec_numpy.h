/*
 * UnderscoreC NumPy Integration Header
 * 
 * Header file for NumPy array operations with cached ufuncs
 */

#ifndef UNDERSCOREC_NUMPY_H
#define UNDERSCOREC_NUMPY_H

#include <Python.h>
#include <numpy/arrayobject.h>
#include "underscorec_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Initialize NumPy ufuncs cache for optimized operations
 * @return 0 on success, -1 on failure
 */
int initialize_numpy_ufuncs(void);

/**
 * Apply optimized NumPy operation using cached ufuncs
 * @param self UnderscoreObject containing the operation and operand
 * @param array NumPy array to operate on
 * @return Result PyObject or NULL on error
 */
PyObject *apply_numpy_operation_cached(UnderscoreObject *self, PyObject *array);

/**
 * Cleanup NumPy ufuncs cache (called on module cleanup)
 */
void cleanup_numpy_ufuncs(void);

#ifdef __cplusplus
}
#endif

#endif // UNDERSCOREC_NUMPY_H