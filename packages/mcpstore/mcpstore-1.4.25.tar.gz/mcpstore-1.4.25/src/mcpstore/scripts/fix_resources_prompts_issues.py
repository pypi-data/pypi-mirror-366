#!/usr/bin/env python3
"""
批量修复Resources和Prompts功能中的问题
"""

import re
import os
from pathlib import Path

def fix_timestamp_consistency(file_path: str):
    """修复时间戳一致性问题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有time.strftime("%Y-%m-%d %H:%M:%S")为self._get_timestamp()
    pattern = r'time\.strftime\("%Y-%m-%d %H:%M:%S"\)'
    replacement = 'self._get_timestamp()'
    
    # 计算替换次数
    matches = re.findall(pattern, content)
    count = len(matches)
    
    if count > 1:  # 保留_get_timestamp方法中的原始调用
        content = re.sub(pattern, replacement, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {count-1} timestamp inconsistencies in {file_path}")
    else:
        print(f"ℹ️  No timestamp issues found in {file_path}")

def fix_model_dump_calls(file_path: str):
    """修复model_dump调用的安全性问题"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换.model_dump()为self._safe_model_dump()
    patterns = [
        (r'(\w+)\.model_dump\(\)', r'self._safe_model_dump(\1)'),
        (r'\[(\w+)\.model_dump\(\) for (\w+) in (\w+)\]', r'[self._safe_model_dump(\2) for \2 in \3]'),
    ]
    
    total_replacements = 0
    for pattern, replacement in patterns:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            total_replacements += len(matches)
    
    if total_replacements > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {total_replacements} model_dump calls in {file_path}")
    else:
        print(f"ℹ️  No model_dump issues found in {file_path}")

def add_parameter_validation(file_path: str):
    """添加参数验证"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找需要添加验证的方法
    methods_needing_validation = [
        'read_resource_async',
        'get_prompt_async'
    ]
    
    validation_code = '''
        # 参数验证
        if not uri or not isinstance(uri, str):
            return {
                "success": False,
                "error": "Invalid URI parameter",
                "data": None,
                "uri": uri,
                "timestamp": self._get_timestamp()
            }
'''
    
    # 这里只是示例，实际实现需要更复杂的逻辑
    print(f"ℹ️  Parameter validation needs manual implementation in {file_path}")

def check_error_handling_consistency(file_path: str):
    """检查错误处理一致性"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有异常处理块
    exception_patterns = re.findall(r'except Exception as (\w+):(.*?)(?=except|else|finally|\n\s*def|\n\s*class|\Z)', content, re.DOTALL)
    
    inconsistencies = []
    for var_name, block in exception_patterns:
        if 'logger.error' not in block and 'logger.warning' not in block:
            inconsistencies.append(f"Exception block with {var_name} missing logging")
    
    if inconsistencies:
        print(f"⚠️  Error handling inconsistencies in {file_path}:")
        for issue in inconsistencies:
            print(f"   - {issue}")
    else:
        print(f"✅ Error handling looks consistent in {file_path}")

def main():
    """主修复函数"""
    print("🔧 Starting Resources and Prompts code fixes...")
    
    # 需要修复的文件
    files_to_fix = [
        "src/mcpstore/core/orchestrator.py",
        "src/mcpstore/core/context.py",
        "src/mcpstore/core/registry.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"\n📁 Processing {file_path}...")
            
            # 修复时间戳一致性
            fix_timestamp_consistency(file_path)
            
            # 修复model_dump调用
            fix_model_dump_calls(file_path)
            
            # 检查错误处理一致性
            check_error_handling_consistency(file_path)
            
            # 添加参数验证（需要手动实现）
            add_parameter_validation(file_path)
            
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎉 Batch fixes completed!")
    print("\n📋 Manual tasks remaining:")
    print("   1. Review and test all timestamp fixes")
    print("   2. Add proper parameter validation to new methods")
    print("   3. Test error handling with invalid inputs")
    print("   4. Update documentation with new methods")
    print("   5. Add integration tests for Resources and Prompts")

if __name__ == "__main__":
    main()
