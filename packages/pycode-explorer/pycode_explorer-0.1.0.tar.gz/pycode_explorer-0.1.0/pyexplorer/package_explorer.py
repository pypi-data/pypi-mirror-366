"""
Package Explorer - For exploring installed packages and their functions
"""

import importlib
import inspect
import pkgutil
from typing import Dict, List, Optional, Any
import sys

class PackageExplorer:
    def __init__(self):
        self.cache = {}  # Cache for package information
    
    def explore_package(self, package_name: str) -> Dict:
        """
        Explore an installed package and show its available functions.
        
        Args:
            package_name (str): Name of the package to explore
            
        Returns:
            Dict: Information about the package and its functions
        """
        if package_name in self.cache:
            return self.cache[package_name]
        
        try:
            # Import the package
            package = importlib.import_module(package_name)
            
            # Get basic package information
            package_info = {
                "package_name": package_name,
                "description": self._get_package_description(package),
                "version": self._get_package_version(package),
                "location": getattr(package, '__file__', 'Built-in'),
                "functions": [],
                "classes": [],
                "submodules": [],
                "constants": [],
                "total_items": 0
            }
            
            # Explore package contents
            self._explore_package_contents(package, package_info)
            
            # Cache the result
            self.cache[package_name] = package_info
            
            return package_info
            
        except ImportError as e:
            return {
                "error": f"Package '{package_name}' not found or not installed.",
                "suggestion": f"Try: pip install {package_name}"
            }
        except Exception as e:
            return {
                "error": f"Error exploring package '{package_name}': {str(e)}"
            }
    
    def _get_package_description(self, package) -> str:
        """Get package description from docstring or fallback."""
        doc = inspect.getdoc(package)
        if doc:
            # Get first meaningful line
            lines = [line.strip() for line in doc.split('\n') if line.strip()]
            if lines:
                return lines[0]
        
        # Fallback descriptions
        fallback_descriptions = {
            'numpy': 'Fundamental package for scientific computing with Python',
            'pandas': 'Data manipulation and analysis library',
            'matplotlib': 'Comprehensive library for creating visualizations',
            'scipy': 'Scientific computing library built on NumPy',
            'sklearn': 'Machine learning library for Python',
            'requests': 'HTTP library for making requests',
            'flask': 'Lightweight WSGI web application framework',
            'django': 'High-level Python web framework',
            'tensorflow': 'Open-source machine learning framework',
            'torch': 'PyTorch deep learning framework',
        }
        
        return fallback_descriptions.get(package.__name__, f"Python package: {package.__name__}")
    
    def _get_package_version(self, package) -> str:
        """Get package version."""
        # Try different ways to get version
        version_attrs = ['__version__', 'VERSION', 'version']
        
        for attr in version_attrs:
            if hasattr(package, attr):
                version = getattr(package, attr)
                if isinstance(version, str):
                    return version
                elif hasattr(version, '__str__'):
                    return str(version)
        
        # Try importlib.metadata for newer Python versions
        try:
            import importlib.metadata
            return importlib.metadata.version(package.__name__)
        except:
            pass
        
        return "Unknown"
    
    def _explore_package_contents(self, package, package_info: Dict):
        """Explore the contents of a package."""
        try:
            # Get all attributes from the package
            for name in dir(package):
                if name.startswith('_'):  # Skip private attributes
                    continue
                
                try:
                    obj = getattr(package, name)
                    obj_info = self._analyze_object(name, obj)
                    
                    if obj_info:
                        category = obj_info['type']
                        package_info[category].append(obj_info)
                        
                except Exception:
                    # Skip attributes that can't be accessed
                    continue
            
            # Sort all categories alphabetically
            for category in ['functions', 'classes', 'submodules', 'constants']:
                package_info[category].sort(key=lambda x: x['name'])
            
            # Calculate total items
            package_info['total_items'] = (
                len(package_info['functions']) + 
                len(package_info['classes']) + 
                len(package_info['submodules']) + 
                len(package_info['constants'])
            )
            
        except Exception as e:
            package_info['exploration_error'] = f"Error during exploration: {str(e)}"
    
    def _analyze_object(self, name: str, obj: Any) -> Optional[Dict]:
        """Analyze an object and return its information."""
        try:
            if inspect.isfunction(obj) or inspect.isbuiltin(obj):
                return {
                    'type': 'functions',
                    'name': name,
                    'description': self._get_object_description(obj),
                    'signature': self._get_function_signature(obj),
                    'is_builtin': inspect.isbuiltin(obj)
                }
            
            elif inspect.isclass(obj):
                return {
                    'type': 'classes',
                    'name': name,
                    'description': self._get_object_description(obj),
                    'methods': self._get_class_methods(obj),
                    'is_exception': issubclass(obj, Exception) if inspect.isclass(obj) else False
                }
            
            elif inspect.ismodule(obj):
                return {
                    'type': 'submodules',
                    'name': name,
                    'description': self._get_object_description(obj),
                    'location': getattr(obj, '__file__', 'Built-in')
                }
            
            else:
                # Constants, variables, etc.
                obj_type = type(obj).__name__
                if obj_type in ['int', 'float', 'str', 'bool', 'list', 'dict', 'tuple']:
                    return {
                        'type': 'constants',
                        'name': name,
                        'value_type': obj_type,
                        'value': str(obj)[:100] + ('...' if len(str(obj)) > 100 else ''),
                        'description': f"Constant of type {obj_type}"
                    }
        
        except Exception:
            return None
        
        return None
    
    def _get_object_description(self, obj) -> str:
        """Get description from object's docstring."""
        doc = inspect.getdoc(obj)
        if doc:
            # Get the first line as description
            first_line = doc.split('\n')[0].strip()
            return first_line if first_line else "No description available"
        return "No description available"
    
    def _get_function_signature(self, func) -> str:
        """Get function signature."""
        try:
            sig = inspect.signature(func)
            return str(sig)
        except (ValueError, TypeError):
            # For built-in functions, signature might not be available
            return "(...)"
    
    def _get_class_methods(self, cls) -> List[str]:
        """Get public methods of a class."""
        try:
            methods = []
            for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    methods.append(name)
            return sorted(methods)[:10]  # Limit to first 10 methods
        except Exception:
            return []
    
    def print_exploration(self, exploration_result: Dict):
        """Print the exploration result in a nicely formatted way."""
        if "error" in exploration_result:
            print(f"❌ Error: {exploration_result['error']}")
            if "suggestion" in exploration_result:
                print(f"💡 {exploration_result['suggestion']}")
            return
        
        pkg_name = exploration_result['package_name']
        print(f"\n{'='*70}")
        print(f"PACKAGE EXPLORATION: {pkg_name}")
        print(f"{'='*70}")
        print(f"📦 Package: {pkg_name}")
        print(f"📝 Description: {exploration_result['description']}")
        print(f"🏷️  Version: {exploration_result['version']}")
        print(f"📍 Location: {exploration_result['location']}")
        print(f"📊 Total Items: {exploration_result['total_items']}")
        
        # Functions
        if exploration_result['functions']:
            print(f"\n🔧 FUNCTIONS ({len(exploration_result['functions'])}):")
            print("-" * 50)
            for i, func in enumerate(exploration_result['functions'][:15], 1):  # Show first 15
                print(f"{i}. {func['name']}{func['signature']}")
                print(f"   {func['description']}")
                if i < len(exploration_result['functions']) and i % 5 == 0:
                    print()  # Add spacing every 5 functions
            
            if len(exploration_result['functions']) > 15:
                remaining = len(exploration_result['functions']) - 15
                print(f"   ... and {remaining} more functions")
        
        # Classes
        if exploration_result['classes']:
            print(f"\n🏗️  CLASSES ({len(exploration_result['classes'])}):")
            print("-" * 50)
            for i, cls in enumerate(exploration_result['classes'][:10], 1):  # Show first 10
                print(f"{i}. {cls['name']}")
                print(f"   {cls['description']}")
                if cls['methods']:
                    methods_str = ', '.join(cls['methods'][:5])
                    if len(cls['methods']) > 5:
                        methods_str += f" ... (+{len(cls['methods'])-5} more)"
                    print(f"   Methods: {methods_str}")
                print()
            
            if len(exploration_result['classes']) > 10:
                remaining = len(exploration_result['classes']) - 10
                print(f"   ... and {remaining} more classes")
        
        # Submodules
        if exploration_result['submodules']:
            print(f"\n📂 SUBMODULES ({len(exploration_result['submodules'])}):")
            print("-" * 50)
            for i, submod in enumerate(exploration_result['submodules'][:8], 1):  # Show first 8
                print(f"{i}. {submod['name']} - {submod['description']}")
            
            if len(exploration_result['submodules']) > 8:
                remaining = len(exploration_result['submodules']) - 8
                print(f"   ... and {remaining} more submodules")
        
        # Constants
        if exploration_result['constants']:
            print(f"\n🔢 CONSTANTS & VARIABLES ({len(exploration_result['constants'])}):")
            print("-" * 50)
            for i, const in enumerate(exploration_result['constants'][:8], 1):  # Show first 8
                print(f"{i}. {const['name']} ({const['value_type']}) = {const['value']}")
            
            if len(exploration_result['constants']) > 8:
                remaining = len(exploration_result['constants']) - 8
                print(f"   ... and {remaining} more constants")
        
        print(f"\n{'='*70}")
        print(f"✅ Package exploration complete! Found {exploration_result['total_items']} items.")
        print(f"{'='*70}\n")
    
    def search_in_package(self, package_name: str, search_term: str) -> Dict:
        """
        Search for specific functions/classes in a package.
        
        Args:
            package_name (str): Name of the package to search in
            search_term (str): Term to search for
            
        Returns:
            Dict: Search results
        """
        exploration = self.explore_package(package_name)
        
        if "error" in exploration:
            return exploration
        
        search_results = {
            "package_name": package_name,
            "search_term": search_term,
            "functions": [],
            "classes": [],
            "submodules": [],
            "constants": []
        }
        
        search_lower = search_term.lower()
        
        # Search in each category
        for category in ['functions', 'classes', 'submodules', 'constants']:
            for item in exploration[category]:
                if (search_lower in item['name'].lower() or 
                    search_lower in item.get('description', '').lower()):
                    search_results[category].append(item)
        
        return search_results
    
    def print_search_results(self, search_results: Dict):
        """Print search results in a formatted way."""
        if "error" in search_results:
            print(f"❌ Error: {search_results['error']}")
            return
        
        pkg_name = search_results['package_name']
        term = search_results['search_term']
        
        total_found = (len(search_results['functions']) + 
                      len(search_results['classes']) + 
                      len(search_results['submodules']) + 
                      len(search_results['constants']))
        
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS: '{term}' in {pkg_name}")
        print(f"{'='*60}")
        print(f"🔍 Found {total_found} matching items:")
        
        for category, icon in [('functions', '🔧'), ('classes', '🏗️'), 
                              ('submodules', '📂'), ('constants', '🔢')]:
            items = search_results[category]
            if items:
                print(f"\n{icon} {category.upper()} ({len(items)}):")
                for item in items:
                    print(f"  • {item['name']} - {item.get('description', 'No description')}")
        
        if total_found == 0:
            print(f"❌ No items found matching '{term}' in {pkg_name}")
        
        print(f"\n{'='*60}\n")