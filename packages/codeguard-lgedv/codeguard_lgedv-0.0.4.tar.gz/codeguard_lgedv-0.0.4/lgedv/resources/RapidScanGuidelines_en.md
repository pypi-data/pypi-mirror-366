### RapidScan Rule Guidelines

### sprintf
**Definition**: Use snprintf instead.
**Exception**: None.

### sscanf
**Definition**: Use fgets instead.
**Exception**: None.

### strcat
**Definition**: Use strncat or safer library functions like strlcat (if available).
**Exception**: None.

### strcpy
**Definition**: Use strncpy or strlcpy (if available).
**Exception**: None.

### __builtin___sprintf_chk
**Definition**: Use snprintf directly or functions that include built-in bounds checking.
**Exception**: None.

### wrongPrintfScanfArgNum
**Definition**: Make sure to the number of arguments match the number of format specifiers.
**Exception**: None.

### invalidPrintfArgType_s
**Definition**: Make sure to the type of arguments match the type of format specifiers.
**Exception**: None.

### M-C-UNINIT_MEMORY
**Definition**: Make sure to initialize the variables when declaring local variables.
**Exception**: None.

### M-C-FLOAT_EQUAL
**Definition**: When comparing floating points, do not use ==, !=.
**Exception**: None.

### M-C-MISSING_RETURN
**Definition**: Functions whose return type is not void must return an explicit value to return according to the type.
**Exception**: None.

### M-C-STR_INIT_LENGTH
**Definition**: The string is always null-terminated, and the dimension of the string array must be "length of the string + 1".
**Exception**: None.

### M-C-RETURN_LOCAL
**Definition**: Functions shall not return pointers or references to non-static local objects.
**Exception**: None.

### M-CPP-DEALLOC_PAIR
**Definition**: Dynamically allocated resources should be properly released.
**Exception**: Cpp code only.

### R-CPP-NEW_DELETE_PAIR
**Definition**: If you override the new or delete operator, always define it by pairing the new-delete.
**Exception**: Cpp code only.

### R-C-SEQ_POINT
**Definition**: If you change the value of a variable, you should not refer to it or change it to another value before the sentence or declaration is finished.
**Exception**: None.

### R-C-ARRAY_OVERRUN
**Definition**: When using an array, make sure that you are using it within the valid index range.
**Exception**: None.

### R-CPP-VIRTUAL_DTOR
**Definition**: The destructor of the base class is declared as virtual or protected.
**Exception**: Cpp code only.

### VULDOC_BOF_STRCPY
**Definition**: Do not use strcpy function.
**Exception**: None.

### VULDOC_BOF_SPRINTF
**Definition**: Do not use sprintf function.
**Exception**: None.

### VULDOC_BOF_STRCAT
**Definition**: Do not use string concatenation functions : strcat.
**Exception**: None.

### VULDOC_INSUFFICIENT_SPACE_READ
**Definition**: Guarantee the storage space for the null terminator : read().
**Exception**: None.

### VULDOC_INSUFFICIENT_SPACE_FREAD
**Definition**: Guarantee the storage space for the null terminator : fread().
**Exception**: None.

### VULDOC_INSUFFICIENT_SPACE_STRNCPY
**Definition**: Guarantee the storage space for character data : strncpy().
**Exception**: None.

### VULDOC_INSUFFICIENT_SPACE_FSCANF
**Definition**: Guarantee the storage space for character data : fscanf().
**Exception**: None.

### VULDOC_VALID_SIZE_MEMCPY
**Definition**: Make sure that the copy size is not larger than buffer size : memcpy().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_FOPEN
**Definition**: Avoid TOCTOU race conditions during the period between access() and fopen().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_MKDIR
**Definition**: Avoid TOCTOU race conditions during the period between access() and mkdir().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_OPEN
**Definition**: Avoid TOCTOU race conditions during the period between access() and open().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_REMOVE
**Definition**: Avoid TOCTOU race conditions during the period between access() and remove().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_RENAME
**Definition**: Avoid TOCTOU race conditions during the period between access() and rename().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_UNLINK
**Definition**: Avoid TOCTOU race conditions during the period between access() and unlink().
**Exception**: None.

### VULDOC_TOCTOU_ACCESS_LSTAT
**Definition**: Avoid TOCTOU race conditions during the period between access() and lstat().
**Exception**: None.

### VULDOC_TOCTOU_STAT_CHMOD
**Definition**: Avoid TOCTOU race conditions during the period between stat() and chmod().
**Exception**: None.

### VULDOC_TOCTOU_STAT_FOPEN
**Definition**: Avoid TOCTOU race conditions during the period between stat() and fopen().
**Exception**: None.

### VULDOC_TOCTOU_STAT_MKDIR
**Definition**: Avoid TOCTOU race conditions during the period between stat() and mkdir().
**Exception**: None.

### VULDOC_TOCTOU_LSTAT_UNLINK
**Definition**: Avoid TOCTOU race conditions during the period between lstat() and unlink().
**Exception**: None.

### VULDOC_TOCTOU_CHMOD_MKDIR
**Definition**: Avoid TOCTOU race conditions during the period between chmod() and mkdir().
**Exception**: None.

### VULDOC_RANDOM_RAND
**Definition**: Do not use the rand() function for generating pseudorandom numbers.
**Exception**: None.

### VULDOC_RANDOM_BAD_SEED
**Definition**: Use properly seed pseudorandom number generators.
**Exception**: None.

### VULDOC_INVALID_ARRAY_INDEX
**Definition**: Make sure the array index is smaller than the array size.
**Exception**: None.

### VULDOC_UNINITIALIZED_MEMORY
**Definition**: Do not read uninitialized memory.
**Exception**: None.

### VULDOC_SYSCALL_POPEN
**Definition**: Do not call system function: popen.
**Exception**: None.

### VULDOC_SYSCALL_SYSTEM
**Definition**: Do not call system function: system.
**Exception**: None.

### VULDOC_INSECURE_PRIVATE_KEY_SAVE
**Definition**: Do not save private key in non-secure storage.
**Exception**: None.

### VULDOC_INSECURE_PRIVATE_KEY_LOAD
**Definition**: Do not load private key in non-secure storage.
**Exception**: None.

### VULDOC_INSECURE_CERTIFICATE_SAVE
**Definition**: Do not save certificate in non-secure storage.
**Exception**: None.

### VULDOC_INSECURE_CERTIFICATE_LOAD
**Definition**: Do not load certificates in non-secure storage.
**Exception**: None.

### VULDOC_INSECURE_CERTIFICATE_LOAD_OPENSSL
**Definition**: Do not load certificates in non-secure storage with openssl.
**Exception**: None.

### VULDOC_SOCKET_WILDCARD_BINDING
**Definition**: Do not use Network Wildcard binding.
**Exception**: None.
