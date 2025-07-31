# 🔍 Memory Leak Detection Workflow

## 📋 **Overview**

This document describes the comprehensive workflow for detecting, analyzing, and fixing memory leaks in C++ codebases using the MCP (Model Context Protocol) server's memory leak analyzer.

---

## 🎯 **Workflow Phases**

### **Phase 1: Preparation & Setup** 🛠️

#### **1.1 Environment Setup**
```bash
# Navigate to MCP server directory
cd /home/worker/src/codefun/deepl/mcp_server

# Activate virtual environment
source venv/bin/activate

# Verify codeguard is available
which codeguard
```

#### **1.2 Configure Analysis Target**
```json
// Update .vscode/mcp.json
{
  "servers": {
    "lgedv": {
      "command": "/path/to/codeguard",
      "args": ["--transport", "stdio"],
      "env": {
        "CPP_DIR": "/path/to/your/cpp/code",  // ← Target directory
        "CUSTOM_RULE_PATH": "/path/to/rules.md"
      }
    }
  }
}
```

#### **1.3 Pre-Analysis Checklist**
- ✅ Ensure all C++ files are compilable
- ✅ Remove temporary/build artifacts
- ✅ Backup original code before making fixes
- ✅ Document known issues for comparison

---

### **Phase 2: Memory Leak Detection** 🔍

#### **2.1 Trigger Analysis**
```markdown
# Use MCP tool directly
analyze_memory_leaks_with_ai

# Or via prompt (recommended for rich analysis)
memory_leak_analysis
```

#### **2.2 Analysis Process Flow**
```mermaid
graph TD
    A[🎯 Start Memory Leak Analysis] --> B[📂 Multi-File Discovery]
    B --> B1[Scan *.cpp files]
    B --> B2[Scan *.h files]
    B --> B3[Filter build artifacts]
    B1 --> C[🔍 Per-File Memory Operation Parsing]
    B2 --> C
    B3 --> C
    
    C --> C1[Parse new/malloc allocations]
    C --> C2[Parse delete/free deallocations]
    C --> C3[Track variable scopes]
    C --> C4[Detect function signatures]
    
    C1 --> D[🧠 Cross-File Memory Flow Analysis]
    C2 --> D
    C3 --> D
    C4 --> D
    
    D --> D1[Build variable flow map]
    D --> D2[Track cross-file references]
    D --> D3[Identify memory ownership]
    D --> D4[Map allocation-deallocation pairs]
    
    D1 --> E[⚠️ Multi-Pattern Leak Detection]
    D2 --> E
    D3 --> E
    D4 --> E
    
    E --> E1[🔴 Definite Leaks<br/>Alloc: N, Dealloc: 0]
    E --> E2[🟡 Partial Leaks<br/>Alloc: N, Dealloc: M, N>M]
    E --> E3[🟠 Mismatched Types<br/>new[] → delete, malloc → delete]
    E --> E4[🔵 Cross-File Leaks<br/>Alloc in File A, No cleanup in File B]
    
    E1 --> F[📊 Dynamic Priority & Grouping]
    E2 --> F
    E3 --> F
    E4 --> F
    
    F --> F1[Group by file criticality]
    F --> F2[Sort by severity: Critical→High→Medium]
    F --> F3[Prioritize definite leaks first]
    F --> F4[Limit output: Top 5 files, Top 5 leaks]
    
    F1 --> G[📋 Smart Report Generation]
    F2 --> G
    F3 --> G
    F4 --> G
    
    G --> G1[📈 Rich metadata<br/>Ratios, statistics, risk assessment]
    G --> G2[📄 Code context<br/>Truncated files with leak markers]
    G --> G3[🎯 Actionable findings<br/>Line numbers, fix recommendations]
    
    G1 --> H[✅ Optimized Output Delivery]
    G2 --> H
    G3 --> H
    
    H --> H1[Token-optimized format<br/>~2,300 tokens vs 6,000+ before]
    H --> H2[Developer-ready insights<br/>File paths, priorities, solutions]
    
    style A fill:#e1f5fe
    style E1 fill:#ffebee
    style E2 fill:#fff8e1
    style E3 fill:#fff3e0
    style E4 fill:#e3f2fd
    style H1 fill:#e8f5e8
    style H2 fill:#e8f5e8
```

#### **2.3 What Gets Analyzed**
- **File Scanning**: All `.cpp` and `.h` files in target directory
- **Memory Operations Detection**:
  ```cpp
  // Allocations detected
  new Type()           // Single object
  new Type[size]       // Array allocation
  malloc(size)         // C-style allocation
  calloc(n, size)      // Zero-initialized allocation
  
  // Deallocations detected
  delete ptr           // Single object deletion
  delete[] ptr         // Array deletion
  free(ptr)           // C-style deallocation
  ```
- **Pattern Analysis**:
  - Variable tracking across scopes
  - Constructor/destructor pairs
  - Exception safety paths
  - Cross-file memory flows

#### **2.4 Memory Leak Pattern Detection Workflow**
```mermaid
graph TD
    A[🔍 Multi-File Memory Leak Detection Engine] --> B[📁 File Analysis Phase]
    
    B --> B1[File 1: basic_leak.cpp]
    B --> B2[File 2: circular_leaks.cpp]
    B --> B3[File 3: mixed_allocation.cpp]
    B --> B4[File N: other files...]
    
    B1 --> C1[🔎 Pattern Detection in File 1]
    B2 --> C2[🔎 Pattern Detection in File 2]
    B3 --> C3[🔎 Pattern Detection in File 3]
    B4 --> C4[🔎 Pattern Detection in File N]
    
    C1 --> D1[📊 Memory Operations Found:<br/>• User class: new std::string, new int<br/>• Missing destructor<br/>• Variable reassignment without cleanup]
    
    C2 --> D2[📊 Memory Operations Found:<br/>• Parent/Child objects: new Parent(), new Child()<br/>• Container raw pointers: vector&lt;int*&gt;<br/>• Complex object graphs<br/>• Missing container cleanup]
    
    C3 --> D3[📊 Memory Operations Found:<br/>• Mixed allocation: malloc + new[]<br/>• Wrong deallocation: delete vs delete[] vs free<br/>• Object lifetime management<br/>• Scope-based leaks]
    
    C4 --> D4[📊 Memory Operations Found:<br/>• Additional patterns...<br/>• Cross-reference analysis<br/>• Include dependency tracking]
    
    D1 --> E[🧠 Cross-File Analysis Engine]
    D2 --> E
    D3 --> E
    D4 --> E
    
    E --> F[🔗 Memory Flow Correlation]
    F --> F1[Variable tracking across files]
    F --> F2[Function parameter passing]
    F --> F3[Return value ownership]
    F --> F4[Include dependency impact]
    
    F1 --> G[⚠️ Leak Classification Algorithm]
    F2 --> G
    F3 --> G
    F4 --> G
    
    G --> G1[🔴 TYPE 1: Definite Leaks<br/>✗ Allocation found<br/>✗ No matching deallocation<br/>→ GUARANTEED MEMORY LEAK]
    
    G --> G2[🟡 TYPE 2: Partial Leaks<br/>✓ Some allocations<br/>✗ Missing some deallocations<br/>→ INCOMPLETE CLEANUP]
    
    G --> G3[🟠 TYPE 3: Mismatched Operations<br/>✓ Allocation found<br/>✗ Wrong deallocation type<br/>→ UNDEFINED BEHAVIOR]
    
    G --> G4[🔵 TYPE 4: Cross-File Complexity<br/>✓ Allocation in File A<br/>? Unclear ownership in File B<br/>→ OWNERSHIP AMBIGUITY]
    
    G1 --> H[📈 Risk & Impact Assessment]
    G2 --> H
    G3 --> H
    G4 --> H
    
    H --> H1[High Impact:<br/>• Frequently called functions<br/>• Large object allocations<br/>• Loop-based allocations]
    
    H --> H2[Medium Impact:<br/>• One-time allocations<br/>• Small object leaks<br/>• Conditional paths]
    
    H --> H3[Low Impact:<br/>• Startup-only allocations<br/>• Debug/test code<br/>• Rare execution paths]
    
    H1 --> I[🎯 Smart Prioritization & Output Optimization]
    H2 --> I
    H3 --> I
    
    I --> I1[Priority Sorting:<br/>1. Critical/High severity first<br/>2. Definite leaks before partial<br/>3. High-impact functions priority<br/>4. Cross-file issues highlighted]
    
    I --> I2[Content Optimization:<br/>• Limit to top 3 files<br/>• Show top 5 priority leaks<br/>• Truncate files > 1000 chars<br/>• Include leak markers 🔴🟢]
    
    I --> I3[Token Management:<br/>• Target: ~2,300 tokens<br/>• Reduction: 63% from original<br/>• Smart context preservation<br/>• Essential metadata only]
    
    I1 --> J[📋 Final Report Generation]
    I2 --> J
    I3 --> J
    
    J --> K[📊 Developer-Ready Output]
    K --> K1[Rich Metadata:<br/>• File statistics<br/>• Allocation/deallocation ratios<br/>• Risk assessment scores<br/>• Priority recommendations]
    
    K --> K2[Code Context:<br/>• Relevant file excerpts<br/>• Visual leak markers<br/>• Line number references<br/>• Smart truncation indicators]
    
    K --> K3[Actionable Insights:<br/>• Specific fix recommendations<br/>• Before/after code examples<br/>• RAII suggestions<br/>• Exception safety guidance]
    
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style G1 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style G2 fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    style G3 fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style G4 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style K1 fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    style K2 fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    style K3 fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
```

---

### **Phase 3: Analysis Results Interpretation** 📊

#### **3.1 Understanding the Report Structure**

```markdown
# 🔍 Memory Leak Analysis Request

## 📊 Comprehensive Analysis Results:
### 🗂️ Project Overview:
- Directory Analyzed: [Target path]
- Total Files Processed: [Number]
- Total Variables Tracked: [Number]
- Analysis Scope: Full codebase with dynamic grouping

### 📈 Memory Operations Summary:
- Total Allocations Found: [Number]
- Total Deallocations Found: [Number]
- Allocation/Deallocation Ratio: [Ratio] [Status indicator]
- Memory Operations Balance: [Good/Fair/Poor]

### 🚨 Leak Severity Distribution:
- Critical: [Number] leaks (Immediate action required)
- High: [Number] leaks (Review soon)
- Medium: [Number] leaks (Monitor and fix)
```

#### **3.2 Risk Assessment Indicators**

| **Ratio** | **Status** | **Action Required** | **Priority** |
|-----------|------------|---------------------|--------------|
| **≥ 0.9** | ✅ Good | Maintain current practices | Low |
| **0.5-0.9** | ⚠️ Fair | Review and improve | Medium |
| **< 0.5** | 🔴 Poor | Immediate fixes needed | **HIGH** |

#### **3.3 Leak Type Classification**

```cpp
// Type 1: Definite Leaks (Allocations: N, Deallocations: 0)
int* ptr = new int(42);
// No delete found → GUARANTEED LEAK

// Type 2: Partial Leaks (Allocations: N, Deallocations: M, N > M)
int* ptr1 = new int(1);
int* ptr2 = new int(2);
delete ptr1;  // ptr2 never deleted → PARTIAL LEAK

// Type 3: Mismatched Deallocation
int* array = new int[100];
delete array;  // Should be delete[] → UNDEFINED BEHAVIOR

// Type 4: Exception Safety Issues
void riskyFunction() {
    char* buffer = new char[1024];
    if (someCondition) {
        throw std::exception();  // buffer leaked!
    }
    delete[] buffer;
}
```

---

### **Phase 4: Priority-Based Fixing Strategy** 🛠️

#### **4.1 Fix Priority Matrix**

| **Priority** | **Leak Type** | **Impact** | **Fix Timeline** |
|--------------|---------------|------------|------------------|
| **P0 - Critical** | Definite leaks in frequently called functions | High memory consumption | **Immediate** |
| **P1 - High** | Mismatched allocation/deallocation | Undefined behavior | **Within 24h** |
| **P2 - Medium** | Constructor without destructor | Gradual memory growth | **Within week** |
| **P3 - Low** | Potential exception safety issues | Conditional leaks | **Next iteration** |

#### **4.2 Systematic Fix Approach**

##### **Step 1: Address Definite Leaks**
```cpp
// BEFORE (Leak #1 from report)
class User {
    std::string* name;
    int* age;
public:
    User(const std::string& userName, int userAge) {
        name = new std::string(userName);  // LEAK!
        age = new int(userAge);           // LEAK!
    }
    // Missing destructor
};

// AFTER - Fix Option 1: Add Destructor
class User {
    std::string* name;
    int* age;
public:
    User(const std::string& userName, int userAge) {
        name = new std::string(userName);
        age = new int(userAge);
    }
    
    ~User() {  // ✅ Added destructor
        delete name;
        delete age;
    }
    
    // Rule of Three: Also need copy constructor and assignment operator
    User(const User& other) = delete;
    User& operator=(const User& other) = delete;
};

// AFTER - Fix Option 2: RAII (Recommended)
class User {
    std::string name;  // ✅ No pointers needed
    int age;
public:
    User(const std::string& userName, int userAge) 
        : name(userName), age(userAge) {
        // Automatic cleanup when object goes out of scope
    }
    // No destructor needed - automatic cleanup
};
```

##### **Step 2: Fix Mismatched Allocation/Deallocation**
```cpp
// BEFORE (DataManager from report)
~DataManager() {
    delete singleValue;    // malloc → delete (WRONG!)
    delete arrayData;      // new[] → delete (WRONG!)
    free(stringBuffer);    // new[] → free (WRONG!)
}

// AFTER
~DataManager() {
    free(singleValue);        // malloc → free ✅
    delete[] arrayData;       // new[] → delete[] ✅
    delete[] stringBuffer;    // new[] → delete[] ✅
}
```

##### **Step 3: Implement Exception Safety**
```cpp
// BEFORE (Exception unsafe)
void riskyFunction() {
    char* buffer = new char[1024];
    processData(buffer);  // Might throw
    delete[] buffer;      // Never reached if exception
}

// AFTER - RAII Approach
void riskyFunction() {
    std::unique_ptr<char[]> buffer(new char[1024]);
    processData(buffer.get());  // Automatic cleanup even if exception
    // No manual delete needed
}

// AFTER - Alternative with scope guard
void riskyFunction() {
    char* buffer = new char[1024];
    auto cleanup = [&]() { delete[] buffer; };
    std::unique_ptr<char[], decltype(cleanup)> guard(buffer, cleanup);
    
    processData(buffer);  // Automatic cleanup via guard
}
```

---

### **Phase 5: Verification & Testing** ✅

#### **5.1 Re-run Analysis**
```bash
# After implementing fixes, re-analyze
# Should see improved allocation/deallocation ratio
```

#### **5.2 Validation Checklist**

**Before/After Metrics Comparison:**
```markdown
## BEFORE FIXES:
- Allocation/Deallocation Ratio: 0.11 🔴
- Definite Leaks: 13 cases
- Critical Issues: 5 items

## AFTER FIXES:
- Allocation/Deallocation Ratio: 0.95 ✅
- Definite Leaks: 0 cases
- Critical Issues: 0 items
```

#### **5.3 Runtime Verification Tools**

```bash
# Valgrind (Linux)
valgrind --leak-check=full --show-leak-kinds=all ./your_program

# AddressSanitizer (Compiler built-in)
g++ -fsanitize=address -g -o program source.cpp
./program

# Static Analysis Tools
cppcheck --enable=all source.cpp
clang-static-analyzer source.cpp
```

---

### **Phase 6: Prevention & Best Practices** 🛡️

#### **6.1 Modern C++ Guidelines**

##### **Rule 1: Prefer RAII over Raw Pointers**
```cpp
// ❌ BAD: Raw pointers
class DataContainer {
    int* data;
public:
    DataContainer(size_t size) : data(new int[size]) {}
    ~DataContainer() { delete[] data; }  // Manual cleanup required
};

// ✅ GOOD: RAII with containers
class DataContainer {
    std::vector<int> data;
public:
    DataContainer(size_t size) : data(size) {}
    // Automatic cleanup - no destructor needed
};
```

##### **Rule 2: Use Smart Pointers for Dynamic Allocation**
```cpp
// ✅ For single objects
std::unique_ptr<User> user = std::make_unique<User>("John", 25);

// ✅ For arrays
std::unique_ptr<int[]> array = std::make_unique<int[]>(100);

// ✅ For shared ownership
std::shared_ptr<Resource> resource = std::make_shared<Resource>();
```

##### **Rule 3: Follow Rule of Three/Five**
```cpp
class ResourceManager {
public:
    // Rule of Five
    ResourceManager();                                    // Constructor
    ~ResourceManager();                                   // Destructor
    ResourceManager(const ResourceManager& other);       // Copy constructor
    ResourceManager& operator=(const ResourceManager& other); // Copy assignment
    ResourceManager(ResourceManager&& other) noexcept;   // Move constructor
    ResourceManager& operator=(ResourceManager&& other) noexcept; // Move assignment
};
```

#### **6.2 Code Review Checklist**

**For Every New Class:**
- ✅ Does it allocate dynamic memory?
- ✅ Does it have a proper destructor?
- ✅ Does it follow Rule of Three/Five?
- ✅ Can RAII be used instead of raw pointers?

**For Every Function:**
- ✅ Are all allocations matched with deallocations?
- ✅ Is exception safety considered?
- ✅ Are early returns properly handled?

#### **6.3 Automated Integration**

##### **CI/CD Pipeline Integration**
```yaml
# .github/workflows/memory-check.yml
name: Memory Leak Check
on: [push, pull_request]

jobs:
  memory-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup MCP Server
        run: |
          cd mcp_server
          source venv/bin/activate
      - name: Run Memory Leak Analysis
        run: |
          # Run analysis and check for leaks
          # Fail CI if critical leaks found
```

##### **IDE Integration**
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Memory Leak Check",
      "type": "shell",
      "command": "analyze_memory_leaks_with_ai",
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    }
  ]
}
```

---

### **Phase 7: Monitoring & Maintenance** 📈

#### **7.1 Regular Analysis Schedule**

| **Frequency** | **Trigger** | **Scope** | **Action** |
|---------------|-------------|-----------|------------|
| **Every Commit** | Pre-commit hook | Changed files | Quick scan |
| **Daily** | CI/CD pipeline | Full codebase | Automated report |
| **Weekly** | Manual review | Critical components | Deep analysis |
| **Release** | Pre-release gate | Complete project | Comprehensive audit |

#### **7.2 Metrics Tracking**

```markdown
## Memory Health Dashboard
- **Current Ratio**: 0.95 ✅ (Target: >0.9)
- **Leak Trend**: ↓ Decreasing (Good)
- **Critical Issues**: 0 (Target: 0)
- **Code Coverage**: 85% analyzed

## Historical Trends
- Week 1: Ratio 0.11 → Week 4: Ratio 0.95 (850% improvement)
- Definite Leaks: 13 → 0 (100% resolved)
- Time to Fix: Avg 2 days → 4 hours (80% faster)
```

#### **7.3 Knowledge Sharing**

```markdown
## Team Guidelines
1. **New Developer Onboarding**:
   - Memory management training
   - MCP analyzer usage guide
   - Code review standards

2. **Best Practice Sharing**:
   - Monthly tech talks on RAII
   - Memory leak case studies
   - Tool usage optimization

3. **Documentation Updates**:
   - Coding standards evolution
   - Tool configuration updates
   - Workflow improvements
```

---

## 🎯 **Workflow Summary**

### **Quick Reference Checklist**

#### **Pre-Development** ✅
- [ ] MCP server configured for target directory
- [ ] Development environment setup with static analysis tools
- [ ] Team aware of memory management guidelines

#### **During Development** ✅  
- [ ] Follow RAII principles
- [ ] Use smart pointers over raw pointers
- [ ] Implement proper destructors
- [ ] Consider exception safety

#### **Pre-Commit** ✅
- [ ] Run memory leak analysis on changed files
- [ ] Address any new leaks found
- [ ] Verify allocation/deallocation balance

#### **Code Review** ✅
- [ ] Review memory management in new classes
- [ ] Check for proper cleanup in functions
- [ ] Validate exception safety measures
- [ ] Ensure modern C++ best practices

#### **Pre-Release** ✅
- [ ] Comprehensive memory leak analysis
- [ ] Runtime verification with Valgrind/AddressSanitizer
- [ ] Performance impact assessment
- [ ] Documentation updates

---

## 📚 **Resources & References**

### **Tools & Documentation**
- **MCP Memory Analyzer**: This workflow's primary tool
- **Valgrind**: Runtime memory leak detection
- **AddressSanitizer**: Compiler-based memory debugging
- **Static Analysis**: Cppcheck, Clang Static Analyzer

### **Learning Resources**
- **Modern C++ Guidelines**: https://isocpp.github.io/CppCoreGuidelines/
- **RAII Principles**: Resource Acquisition Is Initialization patterns
- **Smart Pointers Guide**: std::unique_ptr, std::shared_ptr best practices
- **Exception Safety**: Strong/Basic/No-throw guarantee principles

### **Team Contacts**
- **Memory Management Expert**: [Team lead contact]
- **MCP Server Admin**: [DevOps contact]  
- **Static Analysis Owner**: [Tools team contact]

---

*Workflow Version: 1.0*  
*Last Updated: July 6, 2025*  
*Next Review: August 6, 2025*
