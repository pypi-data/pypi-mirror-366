# 🔍 Memory Leak Analysis Request

## 🎯 Key Areas to Focus:
1. **Unmatched Allocations**: `new`/`malloc` without corresponding `delete`/`free`
2. **Mismatched Operations**: `new[]` with `delete`, `malloc` with `delete`, etc.
3. **Exception Safety**: Memory leaks in exception paths
4. **Class Destructors**: Missing deallocations in destructors
5. **Smart Pointer Usage**: Areas that could benefit from RAII

## 📊 Comprehensive Analysis Results:

### 🗂️ Project Overview:
- **Directory Analyzed**: `/home/worker/src/code_test/memory_leak/test_1`
- **Total Files Processed**: 4
- **Total Variables Tracked**: 32
- **Analysis Scope**: Full codebase with dynamic grouping

### 📈 Memory Operations Summary:
- **Total Allocations Found**: 19
- **Total Deallocations Found**: 2
- **Allocation/Deallocation Ratio**: 0.11 🔴
- **Memory Operations Balance**: Poor

### 🚨 Leak Severity Distribution:
- **Critical**: 0 leaks (Immediate action required)
- **High**: 0 leaks (Review soon)  
- **Medium**: 15 leaks (Monitor and fix)
- **Total Issues**: 15 potential memory leaks

### 🔍 Leak Pattern Analysis:
- **Definite Leaks** (No cleanup): 13 cases 🔴
- **Partial Leaks** (Incomplete cleanup): 2 cases 🟡
- **Cross-File Memory Flows**: 0 complex cases
- **Single-File Leaks**: 15 localized cases

### 🎯 Risk Assessment:
- **Immediate Risk**: HIGH
- **Code Quality**: Poor
- **Maintenance Burden**: High

## 📄 Complete Code Context:

### 📁 mixed_allocation.cpp
**Path**: `/home/worker/src/code_test/memory_leak/test_1/mixed_allocation.cpp`
**Lines with Memory Operations**: [19, 20, 32, 33, 39, 40, 100, 101, 111]

```cpp
/*
 * Mixed Allocation/Deallocation Types - Memory Leaks
 * Lỗi sử dụng sai kiểu allocation/deallocation
 */

#include <iostream>
#include <cstdlib>

class DataManager {
private:
    int* singleValue;
    double* arrayData;
    char* stringBuffer;
    
public:
    DataManager(int size) {
        // Mixed allocation types
        singleValue = (int*)malloc(sizeof(int));  // malloc
        arrayData = new double[size];              // new[]  // 🔴 ALLOCATION: arrayData - new[] array
        stringBuffer = new char[256];              // new[]  // 🔴 ALLOCATION: stringBuffer - new[] array
        
        *singleValue = 42;
        for (int i = 0; i < size; i++) {
            arrayData[i] = i * 1.5;
        }
        strcpy(stringBuffer, "Initial data");
    }
    
    ~DataManager() {
        // MEMORY LEAK: Wrong deallocation types!
        delete singleValue;    // Should be free()! 
        delete arrayData;      // Should be delete[]!  // 🟢 DEALLOCATION: arrayData - delete
        free(stringBuffer);    // Should be delete[]!  // 🟢 DEALLOCATION: stringBuffer - free
    }
    
    void resetData() {
        // MEMORY LEAK: Reassignment without cleanup
        singleValue = (int*)malloc(sizeof(int));
        arrayData = new double[100];  // 🔴 ALLOCATION: arrayData - new[] array
        stringBuffer = new char[512];  // 🔴 ALLOCATION: stringBuffer - new[] array
        
        // Old pointers are lost forever!
    }
};

void mixedAllocationExample() {
    // C-style allocation
    int* cArray = (int*)calloc(50, sizeof(int));
    
    // C++ style allocation  
    std::string* cppString = new std::string("Hello");
    
    // Array allocation
    float* floatArray = new float[25];
    
    // Process data...
    for (int i = 0; i < 50; i++) {
        cArray[i] = i;
    }
    
    *cppString = "Modified string";
    
    for (int i = 0; i < 25; i++) {
        floatArray[i] = i * 2.5f;
    }
    
    // MEMORY LEAKS: Wrong cleanup!
    delete cArray;           // Should be free()!
    delete[] cppString;      // Should be delete!
    free(floatArray);        // Should be delete[]!
}

class ResourceHolder {
    int* data;
    
public:
    ResourceHolder(int* ptr) : data(ptr) {}
    
    // MEMORY LEAK: No destructor to clean up data!
    // Also no copy constructor/assignment operator
    
    ResourceHolder(const ResourceHolder& other) {
        // MEMORY LEAK: Shallow copy creates double-delete potential
        data = other.data;
    }
    
    ResourceHolder& operator=(const ResourceHolder& other) {
        // MEMORY LEAK: No cleanup of existing data
        data = other.data;
        return *this;
    }
    
    void replaceData(int* newData) {
        // MEMORY LEAK: Old data pointer lost
        data = newData;
    }
};

void objectLifecycleLeaks() {
    DataManager* dm1 = new DataManager(20);  // 🔴 ALLOCATION: dm1 - new DataManager(20)
    DataManager* dm2 = new DataManager(30);  // 🔴 ALLOCATION: dm2 - new DataManager(30)
    
    // Use objects
    dm1->resetData();  // Creates internal leaks
    dm2->resetData();  // Creates internal leaks
    
    // MEMORY LEAK: Objects never deleted
    // Even if deleted, destructors have wrong deallocation!
    
    // Test ResourceHolder
    int* testData = new int[10];  // 🔴 ALLOCATION: testData - new[] array
    ResourceHolder holder1(testData);
    ResourceHolder holder2 = holder1;  // Shallow copy
    
    // MEMORY LEAK: testData will be referenced by both holders
    // When they go out of scope, potential double-delete or no delete
}

int main() {
    std::cout << "Testing mixed allocation leaks..." << std::endl;
    
    for (int i = 0; i < 3; i++) {
        mixedAllocationExample();
        objectLifecycleLeaks();
    }
    
    std::cout << "Mixed allocation test completed (with leaks!)" << std::endl;
    return 0;
}

```

### 📁 circular_leaks.cpp
**Path**: `/home/worker/src/code_test/memory_leak/test_1/circular_leaks.cpp`
**Lines with Memory Operations**: [101, 102, 106, 111, 170, 200]

```cpp
/*
 * Circular Reference and Complex Memory Leaks
 * Memory leaks phức tạp: circular references, containers
 */

#include <iostream>
#include <vector>
#include <map>
#include <memory>

// Forward declaration
class Parent;
class Child;

class Child {
public:
    int id;
    Parent* parent;  // Raw pointer to parent
    std::vector<int*> data;  // Vector of raw pointers
    
    Child(int childId) : id(childId), parent(nullptr) {
        // Allocate some data
        for (int i = 0; i < 10; i++) {
            data.push_back(new int(i * childId));
        }
    }
    
    ~Child() {
        std::cout << "Child " << id << " destructor called" << std::endl;
        // MEMORY LEAK: data vector elements not cleaned!
        // Should delete all int* in data vector
    }
    
    void setParent(Parent* p) {
        parent = p;
    }
};

class Parent {
public:
    int id;
    std::vector<Child*> children;  // Raw pointers to children
    std::map<int, double*> calculations;  // Map with raw pointer values
    
    Parent(int parentId) : id(parentId) {}
    
    ~Parent() {
        std::cout << "Parent " << id << " destructor called" << std::endl;
        // MEMORY LEAK: children not deleted!
        // MEMORY LEAK: calculations map values not deleted!
    }
    
    void addChild(Child* child) {
        children.push_back(child);
        child->setParent(this);  // Creates circular reference
        
        // Add some calculation data
        calculations[child->id] = new double(child->id * 3.14);
    }
    
    void removeChild(int childId) {
        // MEMORY LEAK: Child object not deleted when removed!
        for (auto it = children.begin(); it != children.end(); ++it) {
            if ((*it)->id == childId) {
                children.erase(it);
                break;
            }
        }
        
        // MEMORY LEAK: calculation data for this child not deleted!
        if (calculations.find(childId) != calculations.end()) {
            calculations.erase(childId);  // Deletes map entry but not the double*
        }
    }
};

class GraphNode {
public:
    int value;
    std::vector<GraphNode*> neighbors;  // Raw pointers
    std::map<GraphNode*, int*> edgeWeights;  // Map with raw pointer values
    
    GraphNode(int val) : value(val) {}
    
    ~GraphNode() {
        std::cout << "GraphNode " << value << " destructor" << std::endl;
        // MEMORY LEAK: edgeWeights values not cleaned!
        // MEMORY LEAK: No cleanup of neighbor relationships
    }
    
    void addNeighbor(GraphNode* neighbor, int weight) {
        neighbors.push_back(neighbor);
        neighbor->neighbors.push_back(this);  // Bidirectional reference
        
        edgeWeights[neighbor] = new int(weight);
        neighbor->edgeWeights[this] = new int(weight);
    }
};

void createCircularReferences() {
    Parent* parent1 = new Parent(1);  // 🔴 ALLOCATION: parent1 - new Parent(1)
    Parent* parent2 = new Parent(2);  // 🔴 ALLOCATION: parent2 - new Parent(2)
    
    // Create children with circular references
    for (int i = 0; i < 5; i++) {
        Child* child = new Child(i);  // 🔴 ALLOCATION: child - new Child(i)
        parent1->addChild(child);
    }
    
    for (int i = 5; i < 10; i++) {
        Child* child = new Child(i);  // 🔴 ALLOCATION: child - new Child(i)
        parent2->addChild(child);
    }
    
    // Cross-reference children (more complex circular refs)
    if (!parent1->children.empty() && !parent2->children.empty()) {
        parent1->children[0]->setParent(parent2);  // Child has 2 parents now
        parent2->children[0]->setParent(parent1);  // Cross reference
    }
    
    // MEMORY LEAK: parent1 and parent2 never deleted!
    // Even if deleted, their destructors don't clean up properly
    
    // Try to remove some children (creates more leaks)
    parent1->removeChild(0);
    parent2->removeChild(5);
}

void createGraphLeaks() {
    std::vector<GraphNode*> graph;
    
    // Create nodes
    for (int i = 0; i < 10; i++) {
        graph.push_back(new GraphNode(i));
    }
    
    // Create complex interconnections
    for (int i = 0; i < 10; i++) {
        for (int j = i + 1; j < 10; j++) {
            if ((i + j) % 3 == 0) {  // Some arbitrary condition
                graph[i]->addNeighbor(graph[j], i * j);
            }
        }
    }
    
    // MEMORY LEAK: graph vector nodes never deleted!
    // MEMORY LEAK: All edgeWeights allocations leak!
    
    // Clear vector but don't delete nodes
    graph.clear();  // Pointers lost forever!
}

class ContainerWithRawPointers {
    std::vector<int*> intPtrs;
    std::map<std::string, double*> doublePtrs;
    std::vector<std::vector<char*>> nestedPtrs;
    
public:
    ContainerWithRawPointers() {
        // Fill containers with raw pointers
        for (int i = 0; i < 20; i++) {
            intPtrs.push_back(new int(i));
            doublePtrs[std::to_string(i)] = new double(i * 1.5);
        }
        
        // Create nested structure
        for (int i = 0; i < 5; i++) {
            std::vector<char*> innerVec;
            for (int j = 0; j < 4; j++) {
                char* str = new char[50];  // 🔴 ALLOCATION: str - new[] array
                sprintf(str, "String_%d_%d", i, j);
                innerVec.push_back(str);
            }
            nestedPtrs.push_back(innerVec);
        }
    }
    
    ~ContainerWithRawPointers() {
        // MEMORY LEAK: None of the allocated memory is freed!
        // Should iterate through all containers and delete elements
        std::cout << "ContainerWithRawPointers destructor (leaky!)" << std::endl;
    }
    
    void addMoreData() {
        // Add more raw pointers without cleaning old ones
        for (int i = 100; i < 120; i++) {
            intPtrs.push_back(new int(i));
        }
        
        // MEMORY LEAK: Growing containers with no cleanup
    }
};

int main() {
    std::cout << "Testing circular references and complex leaks..." << std::endl;
    
    createCircularReferences();
    createGraphLeaks();
    
    ContainerWithRawPointers* container = new ContainerWithRawPointers();  // 🔴 ALLOCATION: container - new ContainerWithRawPointers()
    container->addMoreData();
    // MEMORY LEAK: container never deleted!
    
    std::cout << "Complex leaks test completed (with many leaks!)" << std::endl;
    return 0;
}

```

### 📁 basic_leak.cpp
**Path**: `/home/worker/src/code_test/memory_leak/test_1/basic_leak.cpp`
**Lines with Memory Operations**: [17, 18, 30, 49, 57, 58]

```cpp
/*
 * Basic Memory Leak Examples
 * Các ví dụ cơ bản về memory leak
 */

#include <iostream>
#include <string>

class User {
private:
    std::string* name;
    int* age;
    
public:
    User(const std::string& userName, int userAge) {
        // Memory allocation without proper cleanup
        name = new std::string(userName);  // 🔴 ALLOCATION: name - new std::string(userName)
        age = new int(userAge);  // 🔴 ALLOCATION: age - new int(userAge)
    }
    
    // MEMORY LEAK: Missing destructor!
    // Destructor should delete name and age
    
    void displayInfo() {
        std::cout << "User: " << *name << ", Age: " << *age << std::endl;
    }
    
    void updateName(const std::string& newName) {
        // MEMORY LEAK: Old name pointer is lost!
        name = new std::string(newName);  // 🔴 ALLOCATION: name - new std::string(newName)
    }
};

void createTemporaryBuffer() {
    // MEMORY LEAK: malloc without free
    char* buffer = (char*)malloc(1024);
    strcpy(buffer, "Some data");
    
    // Function returns without freeing buffer!
    if (strlen(buffer) > 100) {
        return; // Early return causes memory leak
    }
    
    // Even if we reach here, still no free()!
}

int* createArray(int size) {
    // MEMORY LEAK: Caller might not know to delete[]
    int* arr = new int[size];  // 🔴 ALLOCATION: arr - new[] array
    for (int i = 0; i < size; i++) {
        arr[i] = i * 2;
    }
    return arr; // Caller responsible for cleanup, but not documented!
}

void processData() {
    User* user1 = new User("Alice", 25);  // 🔴 ALLOCATION: user1 - new User("Alice", 25)
    User* user2 = new User("Bob", 30);  // 🔴 ALLOCATION: user2 - new User("Bob", 30)
    
    user1->displayInfo();
    user2->displayInfo();
    
    // MEMORY LEAK: users never deleted!
    
    // Create array but forget to delete
    int* numbers = createArray(100);
    
    // Process numbers...
    std::cout << "First number: " << numbers[0] << std::endl;
    
    // MEMORY LEAK: numbers array never deleted!
}

int main() {
    std::cout << "Running memory leak examples..." << std::endl;
    
    // Multiple function calls creating leaks
    for (int i = 0; i < 5; i++) {
        createTemporaryBuffer();
        processData();
    }
    
    std::cout << "Program finished (with memory leaks!)" << std::endl;
    return 0;
}

```



## 🔍 Detailed Memory Leak Findings:

**Total Detected Leaks**: 15 issues requiring attention

### 🟡 Leak #1: single_file_leak - medium Priority
- **Variable**: `arrayData`
- **Files Involved**: 1 file(s)
- **Allocations**: 2
- **Deallocations**: 1
- **Leak Risk**: MEDIUM - Partial cleanup
- **🔴 Allocation Points** (2 locations):
  1. `mixed_allocation.cpp:19` - **new[] array**
     Scope: `global`
  2. `mixed_allocation.cpp:39` - **new[] array**
     Scope: `global`
- **🟢 Deallocation Points** (1 locations):
  1. `mixed_allocation.cpp:32` - **delete**
     Scope: `global`
- **Files to Review**: mixed_allocation.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #2: single_file_leak - medium Priority
- **Variable**: `stringBuffer`
- **Files Involved**: 1 file(s)
- **Allocations**: 2
- **Deallocations**: 1
- **Leak Risk**: MEDIUM - Partial cleanup
- **🔴 Allocation Points** (2 locations):
  1. `mixed_allocation.cpp:20` - **new[] array**
     Scope: `global`
  2. `mixed_allocation.cpp:40` - **new[] array**
     Scope: `global`
- **🟢 Deallocation Points** (1 locations):
  1. `mixed_allocation.cpp:33` - **free**
     Scope: `global`
- **Files to Review**: mixed_allocation.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #3: single_file_leak - medium Priority
- **Variable**: `dm1`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `mixed_allocation.cpp:100` - **new DataManager(20)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: mixed_allocation.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #4: single_file_leak - medium Priority
- **Variable**: `dm2`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `mixed_allocation.cpp:101` - **new DataManager(30)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: mixed_allocation.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #5: single_file_leak - medium Priority
- **Variable**: `testData`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `mixed_allocation.cpp:111` - **new[] array**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: mixed_allocation.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #6: single_file_leak - medium Priority
- **Variable**: `parent1`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `circular_leaks.cpp:101` - **new Parent(1)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: circular_leaks.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #7: single_file_leak - medium Priority
- **Variable**: `parent2`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `circular_leaks.cpp:102` - **new Parent(2)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: circular_leaks.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #8: single_file_leak - medium Priority
- **Variable**: `child`
- **Files Involved**: 1 file(s)
- **Allocations**: 2
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (2 locations):
  1. `circular_leaks.cpp:106` - **new Child(i)**
     Scope: `global`
  2. `circular_leaks.cpp:111` - **new Child(i)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: circular_leaks.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #9: single_file_leak - medium Priority
- **Variable**: `str`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `circular_leaks.cpp:170` - **new[] array**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: circular_leaks.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #10: single_file_leak - medium Priority
- **Variable**: `container`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `circular_leaks.cpp:200` - **new ContainerWithRawPointers()**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: circular_leaks.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #11: single_file_leak - medium Priority
- **Variable**: `name`
- **Files Involved**: 1 file(s)
- **Allocations**: 2
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (2 locations):
  1. `basic_leak.cpp:17` - **new std::string(userName)**
     Scope: `global`
  2. `basic_leak.cpp:30` - **new std::string(newName)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: basic_leak.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #12: single_file_leak - medium Priority
- **Variable**: `age`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `basic_leak.cpp:18` - **new int(userAge)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: basic_leak.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #13: single_file_leak - medium Priority
- **Variable**: `arr`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `basic_leak.cpp:49` - **new[] array**
     Scope: `createArray`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: basic_leak.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #14: single_file_leak - medium Priority
- **Variable**: `user1`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `basic_leak.cpp:57` - **new User("Alice", 25)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: basic_leak.cpp

────────────────────────────────────────────────────────────

### 🟡 Leak #15: single_file_leak - medium Priority
- **Variable**: `user2`
- **Files Involved**: 1 file(s)
- **Allocations**: 1
- **Deallocations**: 0
- **Leak Risk**: HIGH - No cleanup found!
- **🔴 Allocation Points** (1 locations):
  1. `basic_leak.cpp:58` - **new User("Bob", 30)**
     Scope: `global`
- **⚠️ NO DEALLOCATIONS FOUND** - This is a definite memory leak!
- **Files to Review**: basic_leak.cpp

────────────────────────────────────────────────────────────

## 🎯 Priority Analysis Guidelines:

1. **Focus on leaks with 0 deallocations first** - These are guaranteed leaks
2. **Check allocation/deallocation type mismatches** - `new`/`delete[]`, `malloc`/`delete`, etc.
3. **Look for exception safety issues** - Leaks when exceptions occur
4. **Verify RAII compliance** - Use smart pointers where possible
5. **Check constructor/destructor pairs** - Ensure proper cleanup in class destructors



## 🔧 Please Provide:

1. **Detailed Analysis**: Review each potential memory leak and assess its validity
2. **Risk Assessment**: Categorize findings by severity and likelihood  
3. **Fix Recommendations**: Specific code changes for each issue
4. **Best Practices**: Suggest modern C++ approaches (RAII, smart pointers)
5. **Prevention Strategies**: How to avoid similar issues in the future

## 📋 Expected Output Format:

For each memory leak found:
- **Issue Type**: (e.g., Missing delete, Mismatched allocation)
- **Severity**: Critical/High/Medium/Low
- **Location**: File and line number
- **Current Code**: Show the problematic code
- **Fixed Code**: Show the corrected version
- **Explanation**: Why this is a problem and how the fix works

Focus on actionable recommendations that can be immediately implemented.
