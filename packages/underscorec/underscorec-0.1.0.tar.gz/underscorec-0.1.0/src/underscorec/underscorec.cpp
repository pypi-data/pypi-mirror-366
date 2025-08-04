/*
 * Underscore: Consolidated Python Functional Programming Library
 *
 * This is the unified implementation combining:
 * - Basic underscore operations (module, funcptr versions)
 * - Function composition and method calls (compose version)
 * - Scientific computing integration (NumPy/PyTorch/Pandas)
 * - Performance optimizations and smart type detection
 */

#include <Python.h>
#include <numpy/arrayobject.h> // NumPy C API for import_array()

// Modular headers for specific integrations
#include "underscorec_numpy.h"
#include "underscorec_torch.h"
#include "underscorec_types.h"

// Forward declaration for UnderscoreType (needed by create functions)
extern PyTypeObject UnderscoreType;

// Deep copy a composition chain to prevent shallow copy bugs
static UnderscoreObject *deep_copy(UnderscoreObject *chain) {
  // Create new node for this chain element
  UnderscoreObject *copy = (UnderscoreObject *)PyObject_CallObject(
      (PyObject *)&UnderscoreType, NULL);
  if (!copy)
    return nullptr;

  // Copy all fields from the original node
  copy->operation = chain->operation;
  copy->operand = chain->operand;
  copy->left_expr = chain->left_expr;
  copy->right_expr = chain->right_expr;
  copy->method_args = chain->method_args;
  copy->method_kwargs = chain->method_kwargs;

  // Increment reference counts for copied objects
  Py_XINCREF(copy->operand);
  Py_XINCREF(copy->left_expr);
  Py_XINCREF(copy->right_expr);
  Py_XINCREF(copy->method_args);
  Py_XINCREF(copy->method_kwargs);

  // Recursively deep copy the next expression in chain
  if (chain->next_expr)
    copy->next_expr = deep_copy(chain->next_expr);

  return copy;
}

static PyObject *create_multiref_operation(UnderscoreObject *left_expr,
                                           UnderscoreOperation op_type,
                                           UnderscoreObject *right_expr) {
  UnderscoreObject *result = (UnderscoreObject *)PyObject_CallObject(
      (PyObject *)&UnderscoreType, NULL);
  if (!result)
    return nullptr;

  // Set up as multi-reference expression
  result->left_expr = left_expr;
  result->right_expr = right_expr;
  result->operation = op_type;
  result->operand = nullptr;

  // Keep references to the expressions
  Py_INCREF(left_expr);
  Py_INCREF(right_expr);

  return (PyObject *)result;
}

static PyObject *create_operation(UnderscoreObject *self,
                                  UnderscoreOperation op_type,
                                  PyObject *operand) {
  // For multi-reference operation like __ OP __
  if (operand && PyObject_TypeCheck(operand, &UnderscoreType) &&
      op_type != UnderscoreOperation::FUNCTION_CALL) {
    return create_multiref_operation(self, op_type,
                                     (UnderscoreObject *)operand);
  }

  UnderscoreObject *new_op = (UnderscoreObject *)PyObject_CallObject(
      (PyObject *)&UnderscoreType, NULL);
  if (!new_op)
    return nullptr;

  new_op->operation = op_type;
  new_op->operand = operand;
  Py_XINCREF(operand);

  // create simple operation for identity case
  if (self->operation == UnderscoreOperation::IDENTITY) {
    return (PyObject *)new_op;
  }

  UnderscoreObject *result = deep_copy(self);
  // Append the new operation to the end of the chain
  UnderscoreObject *current = result;
  while (current->next_expr) {
    current = current->next_expr;
  }
  current->next_expr = new_op;

  return (PyObject *)result;
}

/*
 * Converts the last GETATTR operation into a method call.
 * It is similar to create_operation, but specifically for method calls.
 * Entry point is underscore_call.
 */
static PyObject *create_method_call(UnderscoreObject *self, PyObject *args,
                                    PyObject *kwargs) {
  UnderscoreObject *result = deep_copy(self);

  // Traverse to the last expression in the chain, which is a GETATTR op
  UnderscoreObject *current = result;
  while (current->next_expr) {
    current = current->next_expr;
  }

  // NOTE: current->operand is already set to the method name in last GETATTR
  current->operation = UnderscoreOperation::METHOD_CALL;
  if (args) {
    current->method_args = args;
    Py_INCREF(args);
  } else {
    current->method_args = PyTuple_New(0);
  }

  current->method_kwargs = kwargs; // Keyword arguments dict
  Py_XINCREF(kwargs);

  return (PyObject *)result;
}

/*
 * Apply single operation to data
 */
static PyObject *underscore_eval_single(UnderscoreObject *self, PyObject *arg) {
  // Direct call low-level operations for supported packages.
  // Fall through to standard Python protocols if not applicable.
  if (PyArray_Check(arg)) {
    PyObject *numpy_result = apply_numpy_operation_cached(self, arg);
    if (numpy_result)
      return numpy_result;
  } else if (THPVariable_Check(arg)) {
    PyObject *torch_result = apply_torch_operation_safe(self, arg);
    if (torch_result) {
      return torch_result;
    }
  }

  switch (self->operation) {
  case UnderscoreOperation::ADD:
    return PyNumber_Add(arg, self->operand);
  case UnderscoreOperation::SUB:
    return PyNumber_Subtract(arg, self->operand);
  case UnderscoreOperation::MUL:
    return PyNumber_Multiply(arg, self->operand);
  case UnderscoreOperation::DIV:
    return PyNumber_TrueDivide(arg, self->operand);
  case UnderscoreOperation::MOD:
    return PyNumber_Remainder(arg, self->operand);
  case UnderscoreOperation::POW:
    return PyNumber_Power(arg, self->operand, Py_None);
  case UnderscoreOperation::GT:
    return PyObject_RichCompare(arg, self->operand, Py_GT);
  case UnderscoreOperation::LT:
    return PyObject_RichCompare(arg, self->operand, Py_LT);
  case UnderscoreOperation::GE:
    return PyObject_RichCompare(arg, self->operand, Py_GE);
  case UnderscoreOperation::LE:
    return PyObject_RichCompare(arg, self->operand, Py_LE);
  case UnderscoreOperation::EQ:
    return PyObject_RichCompare(arg, self->operand, Py_EQ);
  case UnderscoreOperation::NE:
    return PyObject_RichCompare(arg, self->operand, Py_NE);
  // Bitwise operations
  case UnderscoreOperation::AND:
    return PyNumber_And(arg, self->operand);
  case UnderscoreOperation::OR:
    return PyNumber_Or(arg, self->operand);
  case UnderscoreOperation::XOR:
    return PyNumber_Xor(arg, self->operand);
  case UnderscoreOperation::LSHIFT:
    return PyNumber_Lshift(arg, self->operand);
  case UnderscoreOperation::RSHIFT:
    return PyNumber_Rshift(arg, self->operand);
  // Unary operations
  case UnderscoreOperation::NEG:
    return PyNumber_Negative(arg);
  case UnderscoreOperation::ABS:
    return PyNumber_Absolute(arg);
  case UnderscoreOperation::INVERT:
    return PyNumber_Invert(arg);
  // Item/attribute access and method calls
  case UnderscoreOperation::GETITEM:
    return PyObject_GetItem(arg, self->operand);
  case UnderscoreOperation::GETATTR:
    return PyObject_GetAttr(arg, self->operand);
  case UnderscoreOperation::METHOD_CALL: {
    // Method call: arg.self->operand(*args, **kwargs)
    PyObject *method = PyObject_GetAttr(arg, self->operand);
    if (!method)
      return nullptr; // Let the AttributeError propagate

    PyObject *result =
        PyObject_Call(method, self->method_args, self->method_kwargs);

    Py_DECREF(method);
    return result;
  }
  case UnderscoreOperation::FUNCTION_CALL:
    // Function call: self->operand(arg)
    return PyObject_CallFunctionObjArgs(self->operand, arg, NULL);
  case UnderscoreOperation::IDENTITY:
    Py_INCREF(arg);
    return arg;
  default:
    PyErr_SetString(PyExc_NotImplementedError, "Operation not implemented");
    return nullptr;
  }
}

/*
 * Helper function to apply an underscore expression call to input
 */
static PyObject *underscore_eval(UnderscoreObject *expr, PyObject *arg) {

  PyObject *result = nullptr;
  if (expr->left_expr && expr->right_expr) {
    // This is a multi-reference expression - recursively handle it
    PyObject *left_result = underscore_eval(expr->left_expr, arg);
    if (!left_result)
      return nullptr;

    PyObject *right_result = underscore_eval(expr->right_expr, arg);
    if (!right_result) {
      Py_DECREF(left_result);
      return nullptr;
    }

    // temporarily set the operand to left_result
    expr->operand = left_result;
    result = underscore_eval_single(expr, right_result);

    expr->operand = nullptr;
    Py_DECREF(left_result);
    Py_DECREF(right_result);
  } else {
    result = underscore_eval_single(expr, arg);
  }

  if (!result)
    return nullptr;

  // If there's a composition chain, continue applying operations
  UnderscoreObject *current = expr->next_expr;
  while (current) {
    PyObject *next_result = underscore_eval_single(current, result);
    Py_DECREF(result);
    if (!next_result)
      return nullptr;
    result = next_result;
    current = current->next_expr;
  }

  return result;
}

/*
 * Main Call Method with Multi-Reference Support
 */
static PyObject *underscore_call(UnderscoreObject *self, PyObject *args,
                                 PyObject *kwargs) {
  // Special case: GETATTR being called
  UnderscoreObject *current = self;
  while (current->next_expr) {
    current = current->next_expr;
  }
  if (current->operation == UnderscoreOperation::GETATTR) {
    // Smart handling: check if attribute is callable
    // If called with single argument and attribute is not callable, execute GETATTR directly
    if (PyTuple_Size(args) == 1 && kwargs == nullptr) {
      PyObject *arg = PyTuple_GET_ITEM(args, 0);
      PyObject *attr = PyObject_GetAttr(arg, current->operand);
      
      if (attr) {
        int is_callable = PyCallable_Check(attr);
        Py_DECREF(attr);
        
        if (!is_callable) {
          // Attribute exists but is not callable (like tensor.shape property)
          // Execute GETATTR operation directly instead of creating METHOD_CALL
          return underscore_eval(self, arg);
        }
      } else {
        // Clear the error from PyObject_GetAttr for attribute that doesn't exist
        PyErr_Clear();
      }
    }
    
    // Attribute is callable or error occurred - create method call as before
    return create_method_call(self, args, kwargs);
  }

  // Normal case: Apply the underscore expression to a single argument
  if (PyTuple_Size(args) != 1 || kwargs != nullptr) {
    PyErr_SetString(PyExc_TypeError,
                    "underscore object expects exactly one argument");
    return nullptr;
  }

  PyObject *arg = PyTuple_GET_ITEM(args, 0);
  return underscore_eval(self, arg);
}

/*
 * Object Creation and Operator Overloading
 */

static PyObject *underscore_add(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::ADD, other);
}

static PyObject *underscore_sub(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::SUB, other);
}

static PyObject *underscore_div(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::DIV, other);
}

static PyObject *underscore_mod(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::MOD, other);
}

static PyObject *underscore_mul(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::MUL, other);
}

static PyObject *underscore_pow(UnderscoreObject *self, PyObject *other,
                                PyObject *mod) {
  if (mod != Py_None) {
    // Check if all arguments are integers (to match Python's behavior)
    if (!PyLong_Check(other) || !PyLong_Check(mod)) {
      PyErr_SetString(
          PyExc_TypeError,
          "pow() 3rd argument not allowed unless all arguments are integers");
      return nullptr;
    }

    // All arguments are integers, but we don't implement 3-arg pow for
    // UnderscoreC Give a more specific error message for this case
    PyErr_SetString(PyExc_NotImplementedError,
                    "3-argument pow() (modular exponentiation) not implemented "
                    "for UnderscoreC array operations");
    return nullptr;
  }
  return create_operation(self, UnderscoreOperation::POW, other);
}

static PyObject *underscore_richcompare(UnderscoreObject *self, PyObject *other,
                                        int op) {
  UnderscoreOperation op_type;
  switch (op) {
  case Py_GT:
    op_type = UnderscoreOperation::GT;
    break;
  case Py_LT:
    op_type = UnderscoreOperation::LT;
    break;
  case Py_GE:
    op_type = UnderscoreOperation::GE;
    break;
  case Py_LE:
    op_type = UnderscoreOperation::LE;
    break;
  case Py_EQ:
    op_type = UnderscoreOperation::EQ;
    break;
  case Py_NE:
    op_type = UnderscoreOperation::NE;
    break;
  default:
    Py_RETURN_NOTIMPLEMENTED;
  }
  return create_operation(self, op_type, other);
}

// Bitwise operations
static PyObject *underscore_and(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::AND, other);
}

static PyObject *underscore_or(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::OR, other);
}

static PyObject *underscore_xor(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::XOR, other);
}

static PyObject *underscore_lshift(UnderscoreObject *self, PyObject *other) {
  return create_operation(self, UnderscoreOperation::LSHIFT, other);
}

static PyObject *underscore_rshift(UnderscoreObject *self, PyObject *other) {
  // Check if other is a function/callable for composition, otherwise do bitwise
  // right shift
  if (PyCallable_Check(other)) {
    return create_operation(self, UnderscoreOperation::FUNCTION_CALL, other);
  } else {
    return create_operation(self, UnderscoreOperation::RSHIFT, other);
  }
}

static PyObject *underscore_getitem(UnderscoreObject *self, PyObject *key) {
  return create_operation(self, UnderscoreOperation::GETITEM, key);
}

// Unary operations - now using helper function
static PyObject *underscore_neg(UnderscoreObject *self) {
  return create_operation(self, UnderscoreOperation::NEG, nullptr);
}

static PyObject *underscore_abs(UnderscoreObject *self) {
  return create_operation(self, UnderscoreOperation::ABS, nullptr);
}

static PyObject *underscore_invert(UnderscoreObject *self) {
  return create_operation(self, UnderscoreOperation::INVERT, nullptr);
}

// __getattr__ implementation for attribute access
static PyObject *underscore_getattr(UnderscoreObject *self, PyObject *name) {
  return create_operation(self, UnderscoreOperation::GETATTR, name);
}

/*
 * Object Lifecycle Management
 */
static int underscore_init(UnderscoreObject *self, PyObject *args,
                           PyObject *kwargs) {
  self->operation = UnderscoreOperation::IDENTITY;
  self->operand = NULL;
  self->left_expr = NULL;
  self->right_expr = NULL;
  self->method_args = NULL;
  self->method_kwargs = NULL;
  self->next_expr = NULL;

  return 0;
}

static void underscore_dealloc(UnderscoreObject *self) {
  Py_XDECREF(self->operand);
  Py_XDECREF(self->left_expr);
  Py_XDECREF(self->right_expr);
  Py_XDECREF(self->method_args);
  Py_XDECREF(self->method_kwargs);
  Py_XDECREF(self->next_expr);

  Py_TYPE(self)->tp_free((PyObject *)self);
}

// Helper function to get operation string for binary operations
static const char *get_operation_string(UnderscoreOperation op) {
  switch (op) {
  case UnderscoreOperation::ADD:
    return " + ";
  case UnderscoreOperation::SUB:
    return " - ";
  case UnderscoreOperation::MUL:
    return " * ";
  case UnderscoreOperation::DIV:
    return " / ";
  case UnderscoreOperation::MOD:
    return " % ";
  case UnderscoreOperation::POW:
    return " ** ";
  case UnderscoreOperation::GT:
    return " > ";
  case UnderscoreOperation::LT:
    return " < ";
  case UnderscoreOperation::GE:
    return " >= ";
  case UnderscoreOperation::LE:
    return " <= ";
  case UnderscoreOperation::EQ:
    return " == ";
  case UnderscoreOperation::NE:
    return " != ";
  case UnderscoreOperation::AND:
    return " & ";
  case UnderscoreOperation::OR:
    return " | ";
  case UnderscoreOperation::XOR:
    return " ^ ";
  case UnderscoreOperation::LSHIFT:
    return " << ";
  case UnderscoreOperation::RSHIFT:
    return " >> ";
  default:
    return " ? ";
  }
}

// Helper function to get representation of a single expression node (no chain
// traversal)
static PyObject *repr_single_expr(UnderscoreObject *self,
                                  PyObject *current_repr) {
  switch (self->operation) {
  case UnderscoreOperation::IDENTITY:
    return PyUnicode_FromFormat("%U", current_repr);
  case UnderscoreOperation::ADD:
  case UnderscoreOperation::SUB:
  case UnderscoreOperation::MUL:
  case UnderscoreOperation::DIV:
  case UnderscoreOperation::MOD:
  case UnderscoreOperation::POW:
  case UnderscoreOperation::GT:
  case UnderscoreOperation::LT:
  case UnderscoreOperation::GE:
  case UnderscoreOperation::LE:
  case UnderscoreOperation::EQ:
  case UnderscoreOperation::NE:
  case UnderscoreOperation::AND:
  case UnderscoreOperation::OR:
  case UnderscoreOperation::XOR:
  case UnderscoreOperation::LSHIFT:
  case UnderscoreOperation::RSHIFT:
    return PyUnicode_FromFormat("(%U%s%R)", current_repr,
                                get_operation_string(self->operation),
                                self->operand);
  case UnderscoreOperation::GETITEM:
    return PyUnicode_FromFormat("(%U[%R])", current_repr, self->operand);
  case UnderscoreOperation::NEG:
    return PyUnicode_FromFormat("(-%U)", current_repr);
  case UnderscoreOperation::ABS:
    return PyUnicode_FromFormat("abs(%U)", current_repr);
  case UnderscoreOperation::INVERT:
    return PyUnicode_FromFormat("(~%U)", current_repr);
  case UnderscoreOperation::GETATTR:
    return PyUnicode_FromFormat("%U.%U", current_repr, self->operand);
  case UnderscoreOperation::METHOD_CALL: {
    PyObject *args_repr = PyObject_Repr(self->method_args);
    PyObject *result =
        PyUnicode_FromFormat("%U.%U%U", current_repr, self->operand, args_repr);
    Py_XDECREF(args_repr);
    return result;
  }
  case UnderscoreOperation::FUNCTION_CALL:
    return PyUnicode_FromFormat("%U >> %R", current_repr, self->operand);
  default:
    return PyUnicode_FromFormat("%U ??", current_repr);
  }
}

static PyObject *underscore_repr(UnderscoreObject *self) {
  PyObject *result = nullptr;
  // Handle multi-reference expressions first (__ OP __)
  if (self->left_expr && self->right_expr) {
    PyObject *left_repr = underscore_repr(self->left_expr);
    PyObject *right_repr = underscore_repr(self->right_expr);
    if (!left_repr || !right_repr) {
      Py_XDECREF(left_repr);
      Py_XDECREF(right_repr);
      return nullptr;
    }

    const char *op_str = get_operation_string(self->operation);
    result = PyUnicode_FromFormat("%U%s%U", left_repr, op_str, right_repr);

    Py_DECREF(left_repr);
    Py_DECREF(right_repr);
  } else {
    PyObject *identity_repr = PyUnicode_FromString("__");
    result = repr_single_expr(self, identity_repr);
    Py_DECREF(identity_repr);
  }

  UnderscoreObject *current = self->next_expr;
  while (current) {
    PyObject *new_result =
        repr_single_expr(current, result); // Use single_expr to avoid recursion
    Py_DECREF(result);

    result = new_result;
    current = current->next_expr;
  }

  return result;
}

/*
 * Number Protocol Methods
 */
static PyNumberMethods underscore_as_number = {
    .nb_add = (binaryfunc)underscore_add,
    .nb_subtract = (binaryfunc)underscore_sub,
    .nb_multiply = (binaryfunc)underscore_mul,
    .nb_remainder = (binaryfunc)underscore_mod,
    .nb_power = (ternaryfunc)underscore_pow,
    .nb_negative = (unaryfunc)underscore_neg,
    .nb_absolute = (unaryfunc)underscore_abs,
    .nb_invert = (unaryfunc)underscore_invert,
    .nb_lshift = (binaryfunc)underscore_lshift,
    .nb_rshift = (binaryfunc)underscore_rshift,
    .nb_and = (binaryfunc)underscore_and,
    .nb_xor = (binaryfunc)underscore_xor,
    .nb_or = (binaryfunc)underscore_or,
    .nb_true_divide = (binaryfunc)underscore_div,
};

/*
 * Mapping Protocol Methods
 */
static PyMappingMethods underscore_as_mapping = {
    .mp_subscript = (binaryfunc)underscore_getitem,
};

/*
 * Type Definition
 */
PyTypeObject UnderscoreType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "underscorec.Underscore",
    .tp_basicsize = sizeof(UnderscoreObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)underscore_dealloc,
    .tp_repr = (reprfunc)underscore_repr,
    .tp_as_number = &underscore_as_number,
    .tp_as_mapping = &underscore_as_mapping,
    .tp_call = (ternaryfunc)underscore_call,
    .tp_getattro = (getattrofunc)underscore_getattr,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "Consolidated underscore functional programming object",
    .tp_richcompare = (richcmpfunc)underscore_richcompare,
    .tp_init = (initproc)underscore_init,
    .tp_new = PyType_GenericNew,
};

/*
 * Module Definition
 */
static PyObject *create_underscore(PyObject *self, PyObject *args) {
  return PyObject_CallObject((PyObject *)&UnderscoreType, NULL);
}

static PyMethodDef module_methods[] = {{"create", create_underscore,
                                        METH_NOARGS,
                                        "Create a new underscore object"},
                                       {NULL, NULL, 0, NULL}};

// Module cleanup function to free cached NumPy ufuncs
static void module_cleanup(void *module) { cleanup_numpy_ufuncs(); }

static struct PyModuleDef underscorec_module = {
    PyModuleDef_HEAD_INIT,
    "underscorec",
    "Consolidated C-based underscore functional programming library",
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    module_cleanup};

PyMODINIT_FUNC PyInit_underscorec(void) {
  PyObject *module;

  // Initialize NumPy
  import_array();
  if (PyErr_Occurred()) {
    return nullptr;
  }

  if (PyType_Ready(&UnderscoreType) < 0) {
    return nullptr;
  }

  module = PyModule_Create(&underscorec_module);
  if (module == NULL) {
    return nullptr;
  }

  Py_INCREF(&UnderscoreType);
  if (PyModule_AddObject(module, "Underscore", (PyObject *)&UnderscoreType) <
      0) {
    Py_DECREF(&UnderscoreType);
    Py_DECREF(module);
    return nullptr;
  }

  // Create the global underscore instance
  PyObject *underscore_instance = create_underscore(NULL, NULL);
  if (PyModule_AddObject(module, "__", underscore_instance) < 0) {
    Py_DECREF(underscore_instance);
    Py_DECREF(module);
    return nullptr;
  }

  return module;
}
