/*
 * UnderscoreC Shared Types and Enums
 * 
 * Common types and enumerations used across all UnderscoreC modules
 */

#ifndef UNDERSCOREC_TYPES_H
#define UNDERSCOREC_TYPES_H

#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif

// Modern C++ scoped enum for type safety
enum class UnderscoreOperation : int {
  IDENTITY = 0,
  // Binary operations
  ADD = 1,
  SUB = 2,
  MUL = 3,
  DIV = 4,
  POW = 5,
  MOD = 6,
  // Comparison operations
  GT = 7,
  LT = 8,
  EQ = 9,
  NE = 10,
  GE = 11,
  LE = 12,
  // Bitwise operations
  AND = 13,
  OR = 14,
  XOR = 15,
  LSHIFT = 16,
  RSHIFT = 17, // NOTE: RSHIFT is overloaded for function composition
  // Unary operations
  NEG = 18,    // Unary negation (-)
  ABS = 19,    // Absolute value
  INVERT = 20, // Bitwise invert (~)
  // Other operations
  GETITEM = 21,      // Array/object indexing
  GETATTR = 22,      // Attribute access (__.attr)
  METHOD_CALL = 23,  // Method call with arguments
  FUNCTION_CALL = 24 // Function composition (was COMPOSE)
};

// Underscore object with clear, maintainable fields
typedef struct UnderscoreObject {
  PyObject_HEAD;

  UnderscoreOperation operation;
  PyObject *operand;

  // Multi-reference expression support: __ OP __
  struct UnderscoreObject *left_expr;
  struct UnderscoreObject *right_expr; // Right __ expression

  // Method call support: __.<operand>(method_args, **method_kwargs)
  PyObject *method_args;
  PyObject *method_kwargs;

  // Function composition support
  struct UnderscoreObject *next_expr; // Next operation in composition chain
} UnderscoreObject;

#ifdef __cplusplus
}
#endif

#endif // UNDERSCOREC_TYPES_H