#!/usr/bin/env python3

"""
PyExplorer Command Line Interface
For busy managers who need quick script analysis
"""

import argparse
import os
import sys
import json
from pathlib import Path
from typing import List

from .script_analyzer import ScriptAnalyzer
from .package_explorer import PackageExplorer

class PyExplorerCLI:
    def __init__(self):
        self.analyzer = ScriptAnalyzer()
        self.explorer = PackageExplorer()
    
    def analyze_script(self, file_path: str, output_format: str = "console", 
                      brief: bool = False, warnings_only: bool = False) -> None:
        """Analyze a single Python script."""
        if not os.path.exists(file_path):
            print(f"❌ Error: File '{file_path}' not found.")
            return
        
        print(f"🔍 Analyzing: {file_path}")
        result = self.analyzer.analyze_file(file_path)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        if warnings_only:
            self._print_warnings_only(result, file_path)
        elif brief:
            self._print_brief_analysis(result)
        elif output_format == "json":
            self._output_json(result)
        else:
            self.analyzer.print_analysis(result)
    
    def analyze_directory(self, directory_path: str, output_format: str = "console",
                         brief: bool = False) -> None:
        """Analyze all Python files in a directory."""
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"❌ Error: Directory '{directory_path}' not found.")
            return
        
        python_files = list(directory.glob("**/*.py"))
        
        if not python_files:
            print(f"❌ No Python files found in '{directory_path}'")
            return
        
        print(f"🔍 Found {len(python_files)} Python files in '{directory_path}'")
        print("=" * 70)
        
        all_results = []
        total_warnings = 0
        package_usage = {}
        
        for file_path in python_files:
            print(f"\n📄 Analyzing: {file_path.name}")
            result = self.analyzer.analyze_file(str(file_path))
            
            if "error" not in result:
                all_results.append(result)
                total_warnings += len(result.get('warnings', []))
                
                # Track package usage across files
                for import_info in result.get('imports', []):
                    pkg = import_info['module']
                    if pkg not in package_usage:
                        package_usage[pkg] = 0
                    package_usage[pkg] += 1
                
                if brief:
                    self._print_brief_analysis(result)
                else:
                    self.analyzer.print_analysis(result)
            else:
                print(f"❌ Error: {result['error']}")
        
        # Summary for corporate overview
        self._print_directory_summary(all_results, total_warnings, package_usage, len(python_files))
    
    def explore_package(self, package_name: str, search_term: str = None) -> None:
        """Explore a package or search within it."""
        if search_term:
            result = self.explorer.search_in_package(package_name, search_term)
            self.explorer.print_search_results(result)
        else:
            result = self.explorer.explore_package(package_name)
            self.explorer.print_exploration(result)
    
    def _print_brief_analysis(self, result: dict) -> None:
        """Print a brief one-liner analysis - perfect for busy managers."""
        filename = os.path.basename(result['file_path'])
        imports = result.get('imports', [])
        warnings = result.get('warnings', [])
        
        if not imports:
            print(f"   📄 {filename}: Basic Python script (no external packages)")
        else:
            packages = [imp['module'] for imp in imports]
            package_str = ", ".join(packages[:3])
            if len(packages) > 3:
                package_str += f" (+{len(packages)-3} more)"
            
            warning_indicator = f" ⚠️{len(warnings)}" if warnings else " ✅"
            print(f"   📄 {filename}: Uses {package_str}{warning_indicator}")
    
    def _print_warnings_only(self, result: dict, file_path: str) -> None:
        """Print only warnings - for quick issue detection."""
        filename = os.path.basename(file_path)
        warnings = result.get('warnings', [])
        
        if warnings:
            print(f"\n⚠️  {filename} - {len(warnings)} issue(s):")
            for warning in warnings:
                print(f"   {warning}")
        else:
            print(f"✅ {filename} - No issues detected")
    
    def _print_directory_summary(self, results: List[dict], total_warnings: int, 
                                package_usage: dict, total_files: int) -> None:
        """Print executive summary for corporate oversight."""
        print(f"\n{'='*70}")
        print("📊 EXECUTIVE SUMMARY")
        print(f"{'='*70}")
        print(f"📁 Total Files Analyzed: {total_files}")
        print(f"⚠️  Total Issues Found: {total_warnings}")
        print(f"📦 Unique Packages Used: {len(package_usage)}")
        
        if package_usage:
            print(f"\n🔝 Most Used Packages:")
            sorted_packages = sorted(package_usage.items(), key=lambda x: x[1], reverse=True)
            for i, (pkg, count) in enumerate(sorted_packages[:10], 1):
                print(f"   {i}. {pkg} (used in {count} files)")
        
        # Risk assessment for corporate environments
        risk_packages = {
            'requests': 'Network access',
            'urllib': 'Network access', 
            'socket': 'Network access',
            'subprocess': 'System command execution',
            'os': 'File system access',
            'sys': 'System access',
            'pickle': 'Unsafe deserialization risk',
            'eval': 'Code execution risk'
        }
        
        found_risks = []
        for pkg in package_usage:
            if pkg in risk_packages:
                found_risks.append(f"{pkg} ({risk_packages[pkg]})")
        
        if found_risks:
            print(f"\n🚨 SECURITY CONSIDERATIONS:")
            for risk in found_risks:
                print(f"   • {risk}")
        
        # Recommendation for team lead
        if total_warnings > total_files * 0.3:  # More than 30% of files have issues
            print(f"\n💡 RECOMMENDATION: High issue rate detected. Consider code review.")
        elif len(package_usage) > 15:
            print(f"\n💡 RECOMMENDATION: Many dependencies detected. Consider dependency audit.")
        else:
            print(f"\n✅ OVERALL STATUS: Codebase looks healthy.")
        
        print(f"{'='*70}")
    
    def _output_json(self, result: dict) -> None:
        """Output results in JSON format for integration with other tools."""
        print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description="PyCode-Explorer - Understand Python scripts and packages quickly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pycode-explorer script.py                    # Analyze single script
  pycode-explorer script.py --brief            # Quick one-liner analysis  
  pycode-explorer script.py --warnings-only   # Show only issues
  pycode-explorer --directory ./project       # Analyze all files in directory
  pycode-explorer --explore pandas            # Explore pandas package
  pycode-explorer --explore pandas --search read  # Search for 'read' in pandas
        """
    )
    
    # Main action group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('file', nargs='?', help='Python file to analyze')
    group.add_argument('--directory', '-d', help='Directory to analyze (all .py files)')
    group.add_argument('--explore', '-e', help='Package name to explore')
    
    # Analysis options
    parser.add_argument('--brief', '-b', action='store_true', 
                       help='Brief one-line analysis (perfect for busy managers)')
    parser.add_argument('--warnings-only', '-w', action='store_true',
                       help='Show only warnings and issues')
    parser.add_argument('--output', '-o', choices=['console', 'json'], default='console',
                       help='Output format')
    
    # Package exploration options
    parser.add_argument('--search', '-s', help='Search term within package')
    
    args = parser.parse_args()
    
    cli = PyExplorerCLI()
    
    try:
        if args.file:
            cli.analyze_script(args.file, args.output, args.brief, args.warnings_only)
        elif args.directory:
            cli.analyze_directory(args.directory, args.output, args.brief)
        elif args.explore:
            cli.explore_package(args.explore, args.search)
    
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()