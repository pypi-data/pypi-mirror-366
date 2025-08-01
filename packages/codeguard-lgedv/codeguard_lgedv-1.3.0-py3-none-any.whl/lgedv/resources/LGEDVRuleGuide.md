## Rule LGEDV_CRCL_0001:
Definition: Use definition/enumerations instead of magic number.

## Rule LGEDV_CRCL_0002:
Definition: Remove duplicated source code. Make a common class to handle similar actions.

## Rule LGEDV_CRCL_0003:
Definition: Allows up to 1 return point in a function. Multiple returns are a violation.

## Rule LGEDV_CRCL_0004:
Definition: Default (Initialization) value of return need to be a negative/false/failure or any other error meaning. Initialize the returning value to FAILED or the negative meaning value.

## Rule LGEDV_CRCL_0009:
Definition: Recommended Cyclomatic Complexity is lower than 10 (some of function should be break down for readability, maintainability).

## Rule LGEDV_CRCL_0010:
Definition: Return value should be valid. Only return True has no meaning. Make change on return type if return value is not necessary.

## Rule LGEDV_CRCL_0011:
Definition: Add at least one log in the beginning of each function for log traceability, especially the interface function which called by other component. Add log to track the important information for branching.

## Rule LGEDV_CRCL_0012:
Definition: Should sync the data to make sure the actual file content reflect our modification. Interact with raw file need to call sync after flush or close with consideration of performance trade-off.

## Rule LGEDV_CRCL_0013 
Definition: Every switch case must have a break, if there is no break it is a violation.

## Rule LGEDV_CRCL_0014:
Definition: Pointer parameters need to be null checked before using it, and out-of-bound index memory accessing (access array/vector by index) should be checked before using it.

## Rule LGEDV_CRCL_0015:
Definition: A case (having >= 2 logical lines) in switch case should be a block of code. Wrap statements of a case in a curly bracce pair {}.

## Rule LGEDV_CRCL_0016:
Definition: Use bounded C functions instead of unbounded ones to prevent buffer overrun, for example, replace sprintf by snprintf.

## Rule LGEDV_CRCL_0019:
Definition: Every function need to return valuable/meaningful value. For void return functions need to be rechecked if void is really enough or not. 

## Rule LGEDV_CRCL_0020:
Definition: Every allocated resources (memory, file, mutex lock, etc) need to be released properly. Delete, free memories, close files, unlock mutex etc before leave the function.