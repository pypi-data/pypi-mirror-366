## Rule LGEDV_CRCL_0003:
Definition: Allows up to 1 return point in a function. Multiple returns are a violation.

## Rule MISRA 6-4-2
Definition: All if â€¦ else if constructs shall be terminated with an else clause.

## Rule LGEDV_CRCL_0014:
Definition: Pointer parameters need to be null checked before using it, and out-of-bound index memory accessing (access array/vector by index) should be checked before using it.

## Rule MISRA 6-5-1
**Definition**: A for loop shall contain a single loop-counter which shall not have floating type.
**Exception**: None

## Rule MISRA 6-5-5
**Definition**: A loop-control-variable other than the loop-counter shall not be modified within condition or expression
**Exception**: None

## Rule MISRA 6-6-2
**Definition**: The goto statement shall jump to a label declared later in the same function body.
**Exception**: None

## Rule MISRA 6-6-4
**Definition**: For any iteration statement there shall be no more than one break or goto statement used for loop termination.
**Exception**: None

## Rule MISRA 7-5-1
**Definition**: A function shall not return a reference or a pointer to an automatic variable (including parameters), defined within the function
**Exception**: None

## Rule MISRA 7-5-2
**Definition**: The address of an object with automatic storage shall not be assigned to another object that may persist after the first object has ceased to exist
**Exception**: None

## Rule MISRA 8-4-3
**Definition**: All exit paths from a function with non-void return type shall have an explicit return statement with an expression
**Exception**: None

## Rule MISRA 8-5-1
**Definition**: All variables shall have a defined value before they are used
**Exception**: None

## Rule MISRA 10-3-3
**Definition**: A virtual function shall only be overridden by a pure virtual function if it is itself declared as pure virtual
**Exception**: None

## Rule MISRA 11-0-1
**Definition**: Member data in non-POD class types shall be private
**Exception**: None

## Rule MISRA 15-0-2
**Definition**: An exception object should not have pointer type
**Exception**: None

## Rule MISRA 16-0-6
**Definition**: In the definition of a function-like macro, each instance of a parameter shall be enclosed in parentheses, unless it is used as the operand of # or ##
**Exception**: None

## Rule MISRA 18-0-5
**Definition**: The unbounded functions of library <cstring> shall not be used
**Exception**: None