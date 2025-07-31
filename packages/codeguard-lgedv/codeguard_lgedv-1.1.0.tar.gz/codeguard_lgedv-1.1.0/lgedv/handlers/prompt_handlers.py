"""
Prompt handlers for MCP server operations
Xử lý các MCP prompts cho phân tích code
"""
import os
from typing import Dict
from mcp import types
from lgedv.prompts.prompt_templates import PromptTemplates
from lgedv.analyzers.memory_analyzer import MemoryAnalyzer
from lgedv.modules.config import get_cpp_dir, setup_logging

logger = setup_logging()

class PromptHandler:
    """Handler cho các MCP prompts"""
    
    def __init__(self):
        self.templates = PromptTemplates()
    
    async def handle_prompt(self, name: str, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Route và xử lý prompt calls
        
        Args:
            name: Tên prompt
            arguments: Arguments cho prompt
            
        Returns:
            GetPromptResult
        """
        logger.info(f"Prompt called: {name} with arguments: {arguments}")
        
        try:
            if name == "check_lgedv":
                return await self._handle_lgedv_check()
            elif name == "check_misra":
                return await self._handle_misra_check()
            elif name == "check_certcpp":
                return await self._handle_certcpp_check()
            elif name == "check_custom":
                return await self._handle_custom_check()
            elif name == "check_races":
                return await self._handle_race_condition_analysis(arguments)
            elif name == "check_leaks":
                return await self._handle_memory_leak_analysis(arguments)
            elif name == "check_resources":
                return await self._handle_resource_leak_analysis(arguments)
            else:
                raise ValueError(f"Unknown prompt: {name}")
                
        except Exception as e:
            logger.exception(f"Error in prompt handler for {name}: {e}")
            raise
    
    async def _handle_lgedv_check(self) -> types.GetPromptResult:
        """Handle LGEDV code checking prompt"""
        prompt = self.templates.get_lgedv_analysis_prompt()
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for LGEDV rule on current file.",
        )
        
        logger.info("LGEDV check prompt completed")
        return result
    
    async def _handle_misra_check(self) -> types.GetPromptResult:
        """Handle MISRA code checking prompt"""
        prompt = self.templates.get_misra_analysis_prompt()
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for MISRA rule on current file.",
        )
        
        logger.info("MISRA check prompt completed")
        return result
    
    async def _handle_certcpp_check(self) -> types.GetPromptResult:
        """Handle CERT C++ code checking prompt"""
        prompt = self.templates.get_certcpp_analysis_prompt()
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for CERT C++ rule on current file.",
        )
        
        logger.info("CERT C++ check prompt completed")
        return result
    
    async def _handle_custom_check(self) -> types.GetPromptResult:
        """Handle Custom rule checking prompt"""
        prompt = self.templates.get_custom_analysis_prompt()
        
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for Custom rule on current file.",
        )
        
        logger.info("Custom check prompt completed")
        return result
    
    async def _handle_race_condition_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle race condition analysis prompt - always use fallback-style prompt with findings if available"""
        dir_path = get_cpp_dir()
        logger.info(f"[check_races] Using CPP_DIR: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            tool_result = await tool_handler._handle_detect_races({})
           
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Race condition analysis (full result)",
                )
                logger.info("Race condition analysis prompt (fallback style) completed")
                return result
            else:
                 return self._create_fallback_race_prompt(dir_path, "No result from tool")
            
        except Exception as e:
            logger.error(f"Error in race condition analysis: {e}")
            return self._create_fallback_race_prompt(dir_path, str(e))
    
    async def _handle_memory_leak_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle memory leak analysis prompt - always use fallback-style prompt with findings if available"""
        dir_path = get_cpp_dir()
        logger.info(f"[check_leaks] Using CPP_DIR: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            tool_result = await tool_handler._handle_memory_analysis({"dir_path": dir_path})
            
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Memory leak analysis (full result)",
                )
                logger.info("Memory leak analysis prompt")
                return result
            else:
                 return self._create_fallback_memory_leak_prompt(dir_path, "No result from tool")
        except Exception as e:
            logger.error(f"Error in memory leak analysis: {e}")
            return self._create_fallback_memory_leak_prompt(dir_path, str(e))

       
    async def _handle_resource_leak_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle resource leak analysis prompt - always use fallback-style prompt with findings if available, now with line numbers"""
        dir_path = get_cpp_dir()
        logger.info(f"[check_resources] Using CPP_DIR: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            # Also append the original findings text for reference
            tool_result = await tool_handler._handle_resource_analysis({})
            # logger.info(f"tool_result: {tool_result}")
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Resource leak analysis (full prompt)",
                )
                logger.info("Resource leak analysis prompt completed")
                return result
            else:
                 logger.warning("No result from tool for resource leak analysis, using fallback prompt")
                 return self._create_fallback_resource_leak_prompt(dir_path, "No result from tool")
        except Exception as e:
            logger.error(f"Error in resource leak analysis: {e}")
            return self._create_fallback_resource_leak_prompt(dir_path, str(e))
        
    def _format_resource_leak_summary(self, leaks: list) -> str:
        """Format a summary of resource leaks by type and severity"""
        summary = {}
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for leak in leaks:
            leak_type = leak.get('type', 'unknown')
            severity = leak.get('severity', 'medium')
            
            if leak_type not in summary:
                summary[leak_type] = 0
            
            summary[leak_type] += 1
            severity_counts[severity] += 1
        
        summary_text = f"**By Severity:** {severity_counts['critical']} Critical, {severity_counts['high']} High, {severity_counts['medium']} Medium, {severity_counts['low']} Low\n\n"
        summary_text += "**By Resource Type:**\n"
        
        for leak_type, count in summary.items():
            summary_text += f"- {leak_type.title()}: {count} leak(s)\n"
        
        return summary_text
    
    def _create_fallback_race_prompt(self, dir_path: str, error_msg: str) -> types.GetPromptResult:
        """Tạo fallback prompt khi có lỗi"""
        # Lấy danh sách file C++ trong dir_path
        try:
            cpp_files = [f for f in os.listdir(dir_path) if f.endswith('.cpp')]
            code_snippets = []
            for f in cpp_files[:2]:  # Chỉ lấy 2 file đầu cho ngắn gọn
                file_path = os.path.join(dir_path, f)
                with open(file_path, 'r', encoding='utf-8') as file:
                    code = file.read()
                code_snippets.append(f"### {f}\n```cpp\n{code[:1000]}\n```\n")
            code_context = "\n".join(code_snippets)
        except Exception:
            code_context = "Cannot get file C++."

        fallback_prompt = (
            f"You are an expert C++ concurrency analyst.\n"
            f"Please use the `detect_races` tool first to manually analyze the C++ files in the directory: {dir_path}\n\n"
            f"Then provide your expert analysis of potential race conditions, focusing on:\n"
            f"1. Unprotected shared state modifications\n"
            f"2. Missing synchronization mechanisms\n"
            f"3. Thread-unsafe patterns\n"
            f"4. Potential deadlock scenarios\n\n"
            f"IMPORTANT: Only list race conditions or deadlocks if there is clear evidence in the code that a variable or resource is accessed from multiple threads\n"
            f"(e.g., thread creation, callback, or handler running on a different thread). Do not warn about cases that are only potential or speculative.\n"
            f"If no evidence is found, clearly state: 'No multi-threaded access detected for this variable in the current code.'\n\n"
            f"This will help ensure the analysis focuses on real issues and avoids unnecessary or speculative warnings.\n"
            f"\n"
            f"Use this format for each issue found:\n"
            f"\n"
            f"## 🚨 **RACE CONDITION #[number]**: [Brief Description]\n"
            f"**Type:** [data_race|deadlock|missing_sync]\n"
            f"**Severity:** [Critical|High|Medium|Low]\n"
            f"**Files Involved:** [list of files]\n"
            f"**Function Name:** [function name or global scope/unknown]\n"
            f"**Problem Description:** [explanation]\n"
            f"**Fix Recommendation:** [suggested solution]\n\n"
            f"Target Directory: {dir_path}\n"
            f"Files Found: {', '.join(cpp_files)}\n"
            f"# Source Code Context\n"
            f"{code_context}"
        )
        messages = [
            types.PromptMessage(
                role="user", 
                content=types.TextContent(type="text", text=fallback_prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="Race condition analysis (fallback mode).",
        )
        
        logger.info("Race condition analysis fallback prompt completed")
        return result
    
    def _create_fallback_memory_leak_prompt(self, dir_path: str, error_msg: str) -> types.GetPromptResult:
        """Tạo fallback prompt cho phân tích rò rỉ bộ nhớ"""
        fallback_prompt = f"""You are an expert C++ memory management analyst. 
            There was an error analyzing the codebase for memory leaks automatically: {error_msg}

            Please use the `analyze_leaks` tool first to manually analyze the C++ files in the directory: {dir_path}

            Then provide your expert analysis of potential memory leaks, focusing on:
            1. Unreleased memory allocations
            2. Dangling pointers
            3. Memory corruption issues
            4. Inefficient memory usage patterns

            Only provide your expert analysis. Do not repeat the Automated Findings section.

            Additionally, propose refactored code for all relevant C++ files.

            Use this format for each issue found:

            ## 🚨 **MEMORY LEAK #[number]**: [Brief Description]
            **Severity:** [Critical|High|Medium|Low]
            **Files Involved:** [list of files]
            **Problem Description:** [explanation]
            **Fix Recommendation:** [suggested solution]
            """
        messages = [
            types.PromptMessage(
                role="user", 
                content=types.TextContent(type="text", text=fallback_prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="Memory leak analysis (fallback mode).",
        )
        
        logger.info("Memory leak analysis fallback prompt completed")
        return result

    def _create_fallback_resource_leak_prompt(self, dir_path: str, error_msg: str) -> types.GetPromptResult:
        """Create fallback prompt for resource leak analysis"""
        fallback_prompt = f"""You are an expert Linux C++ resource management analyst.

There was an error analyzing the codebase for resource leaks automatically: {error_msg}

Please use the `analyze_resources` tool first to manually analyze the C++ files in the directory: {dir_path}

Then provide your expert analysis of potential resource leaks, focusing on:

## 🎯 **Analysis Focus Areas**

1. **File Resources:**
   - Unmatched open()/close() calls
   - FILE* streams not properly closed
   - Missing fclose() for fopen()

2. **Socket Resources:**
   - Socket descriptors not closed
   - Network connections left open
   - Unmatched socket()/close() pairs

3. **Memory Mapping:**
   - mmap() without corresponding munmap()
   - Shared memory segments not cleaned up

4. **IPC Resources:**
   - Message queues not destroyed
   - Semaphores not cleaned up
   - Shared memory not detached

5. **Directory Handles:**
   - opendir() without closedir()
   - Directory streams left open

Only provide your expert analysis. Do not repeat the Automated Findings section.

Additionally, propose refactored code for all relevant C++ files.

## 📋 **Report Format**
For each resource leak found, use this format:

### 🚨 **RESOURCE LEAK #[number]**: [Resource Type]
- **Severity:** [Critical|High|Medium|Low]
- **File:** [filename]
- **Line:** [line number]
- **Resource:** [specific resource name/variable]
- **Description:** [what resource is leaking and why]
- **Fix:** [specific remediation steps]

Focus on Linux-specific resources and provide actionable recommendations for each finding.
"""
        
        messages = [
            types.PromptMessage(
                role="user", 
                content=types.TextContent(type="text", text=fallback_prompt),
            )
        ]
        
        result = types.GetPromptResult(
            messages=messages,
            description="Resource leak analysis (fallback mode).",
        )
        
        logger.info("Resource leak analysis fallback prompt completed")
        return result
    
    def _create_race_analysis_prompt_section(self, race_result: dict) -> str:
        """Create analysis prompt section with detailed race condition information (no grouping, no limit)"""
        # Comment out the main prompt generation logic
        # detected_races = race_result.get('potential_race_conditions', [])
        # prompt_section = "## 🔍 Detailed Race Condition Findings:\n\n"
        # prompt_section += f"**Total Detected Race Conditions**: {len(detected_races)} issues requiring attention\n\n"
        # if not detected_races:
        #     prompt_section += "✅ **No potential race conditions detected in static analysis.**\n\n"
        #     prompt_section += "However, please perform a manual review focusing on:\n"
        #     prompt_section += "1. Shared state access patterns\n"
        #     prompt_section += "2. Thread synchronization mechanisms\n"
        #     prompt_section += "3. Atomic operations usage\n"
        #     prompt_section += "4. Lock-free programming patterns\n\n"
        #     return prompt_section
        # for i, race in enumerate(detected_races, 1):
        #     severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(race.get('severity', 'medium').lower(), "🟡")
        #     prompt_section += f"### {severity_emoji} Race Condition #{i}: {race.get('type', 'Unknown')} - {race.get('severity', 'Medium')} Priority\n"
        #     prompt_section += f"- **Description**: {race.get('description', 'No description')}\n"
        #     prompt_section += f"- **Files Involved**: {', '.join(race.get('files_involved', []))}\n"
        #     prompt_section += f"- **Line Numbers**: {', '.join(map(str, race.get('line_numbers', [])))}\n"
        #     prompt_section += f"- **Severity**: {race.get('severity', 'Medium')}\n"
        #     if 'potential_causes' in race:
        #         prompt_section += f"- **Potential Causes**: {race.get('potential_causes', 'Unknown')}\n"
        #     if 'recommended_actions' in race:
        #         prompt_section += f"- **Recommended Actions**: {race.get('recommended_actions', 'Unknown')}\n"
        #     prompt_section += "\n" + "─" * 60 + "\n\n"
        # Chỉ giữ lại phần hướng dẫn ưu tiên
        prompt_section = "## 🎯 Priority Analysis Guidelines:\n\n"
        prompt_section += "1. Focus on shared state accessed by multiple threads.\n"
        prompt_section += "2. Ensure proper synchronization (mutexes, locks, atomics).\n"
        prompt_section += "3. Review thread creation and join/detach logic.\n"
        prompt_section += "4. Check for lock-free and concurrent data structure usage.\n"
        prompt_section += "5. Provide before/after code examples for fixes.\n\n"
        return prompt_section
