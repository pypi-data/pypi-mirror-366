import ast
import importlib
import inspect
from typing import Dict, List, Set, Tuple, Optional
import sys
import os

class ScriptAnalyzer:
    def __init__(self):
        self.imports = {}  # {module_name: alias}
        self.from_imports = {}  # {module_name: [imported_items]}
        self.function_calls = []  # List of function calls found
        self.module_descriptions = {}  # Cache for module descriptions
        
    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyze a Python file and return detailed information about imports and function usage.
        
        Args:
            file_path (str): Path to the Python file to analyze
            
        Returns:
            Dict: Analysis results containing imports, functions, and overall understanding
        """
        # Reset state for new analysis
        self._reset_state()
        
        # Read and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {e}"}
            
        # Walk through the AST to extract information
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self._handle_import(node)
            elif isinstance(node, ast.ImportFrom):
                self._handle_from_import(node)
            elif isinstance(node, ast.Call):
                self._handle_function_call(node)
                
        # Generate the final analysis report
        return self._generate_report(file_path)
    
    def _reset_state(self):
        """Reset the analyzer state for a new file."""
        self.imports = {}
        self.from_imports = {}
        self.function_calls = []
    
    def _handle_import(self, node: ast.Import):
        """Handle 'import module' or 'import module as alias' statements."""
        for alias in node.names:
            module_name = alias.name
            alias_name = alias.asname if alias.asname else module_name.split('.')[0]
            self.imports[module_name] = alias_name
    
    def _handle_from_import(self, node: ast.ImportFrom):
        """Handle 'from module import item' statements."""
        if node.module:
            module_name = node.module
            imported_items = []
            for alias in node.names:
                item_name = alias.name
                alias_name = alias.asname if alias.asname else item_name
                imported_items.append((item_name, alias_name))
            
            if module_name not in self.from_imports:
                self.from_imports[module_name] = []
            self.from_imports[module_name].extend(imported_items)
    
    def _handle_function_call(self, node: ast.Call):
        """Extract function calls from the AST."""
        if isinstance(node.func, ast.Attribute):
            # Handle calls like 'np.array()' or 'module.function()'
            if isinstance(node.func.value, ast.Name):
                module_alias = node.func.value.id
                function_name = node.func.attr
                self.function_calls.append((module_alias, function_name))
        elif isinstance(node.func, ast.Name):
            # Handle direct function calls like 'array()' (from imports)
            function_name = node.func.id
            self.function_calls.append((None, function_name))
    
    def _get_module_description(self, module_name: str) -> str:
        """Get a description of the module from its docstring."""
        if module_name in self.module_descriptions:
            return self.module_descriptions[module_name]
        
        try:
            module = importlib.import_module(module_name)
            doc = inspect.getdoc(module)
            if doc:
                # Get the first line of the docstring as a brief description
                description = doc.split('\n')[0].strip()
                # Remove common prefixes and clean up
                if description.lower().startswith(module_name.lower()):
                    description = description[len(module_name):].strip(' -:.')
                self.module_descriptions[module_name] = description
                return description
        except (ImportError, AttributeError):
            pass
        
        # Fallback descriptions for common packages
        fallback_descriptions = {
            # Data Science & Analysis
            'numpy': 'Fundamental package for scientific computing with Python',
            'pandas': 'Data manipulation and analysis library',
            'scipy': 'Scientific computing library built on NumPy',
            'statsmodels': 'Statistical modeling and econometrics',
            'sympy': 'Symbolic mathematics library',
            'dask': 'Parallel computing library for analytics',
            'polars': 'Fast DataFrame library for data manipulation',
            'pyarrow': 'Python library for Apache Arrow columnar memory format',
            
            # Machine Learning & AI
            'sklearn': 'Machine learning library for Python',
            'scikit-learn': 'Machine learning library for Python',
            'xgboost': 'Gradient boosting framework for machine learning',
            'lightgbm': 'Gradient boosting framework using tree-based learning',
            'catboost': 'Gradient boosting library for machine learning',
            'mlflow': 'Machine learning lifecycle management platform',
            'optuna': 'Hyperparameter optimization framework',
            'hyperopt': 'Python library for hyperparameter optimization',
            'joblib': 'Lightweight pipelining with Python functions',
            
            # Deep Learning & Neural Networks
            'tensorflow': 'Open-source machine learning framework by Google',
            'torch': 'PyTorch deep learning framework',
            'pytorch': 'PyTorch deep learning framework',
            'keras': 'High-level neural networks API',
            'transformers': 'State-of-the-art Natural Language Processing library',
            'huggingface_hub': 'Hub for sharing machine learning models',
            'accelerate': 'Training and inference acceleration library',
            'datasets': 'Library for accessing and sharing datasets',
            'tokenizers': 'Fast tokenizers for natural language processing',
            'sentence_transformers': 'Framework for sentence, text and image embeddings',
            'openai': 'OpenAI API client library',
            'langchain': 'Framework for developing applications with language models',
            'llama_index': 'Data framework for LLM applications',
            'gymnasium': 'API for reinforcement learning environments',
            'stable_baselines3': 'Reliable implementations of reinforcement learning algorithms',
            
            # Computer Vision
            'cv2': 'OpenCV computer vision library',
            'opencv': 'OpenCV computer vision library',
            'pillow': 'Python Imaging Library for image processing',
            'PIL': 'Python Imaging Library for image processing',
            'skimage': 'Image processing in Python',
            'imageio': 'Library for reading and writing image data',
            'albumentations': 'Image augmentation library for machine learning',
            
            # Visualization & Plotting
            'matplotlib': 'Comprehensive library for creating static, animated, and interactive visualizations',
            'seaborn': 'Statistical data visualization based on matplotlib',
            'plotly': 'Interactive graphing library for Python',
            'bokeh': 'Interactive visualization library for web browsers',
            'altair': 'Declarative statistical visualization library',
            'pygal': 'Python SVG Charts Library',
            'wordcloud': 'Little word cloud generator in Python',
            'folium': 'Library for visualizing geospatial data',
            
            # Web Development & APIs
            'requests': 'HTTP library for making requests',
            'httpx': 'Next generation HTTP client for Python',
            'urllib3': 'HTTP library with thread-safe connection pooling',
            'aiohttp': 'Asynchronous HTTP client/server framework',
            'flask': 'Lightweight WSGI web application framework',
            'django': 'High-level Python web framework',
            'fastapi': 'Modern, fast web framework for building APIs',
            'starlette': 'Lightweight ASGI framework for building async web services',
            'uvicorn': 'Lightning-fast ASGI server implementation',
            'gunicorn': 'Python WSGI HTTP Server for UNIX',
            'celery': 'Distributed task queue for Python',
            'redis': 'Python client for Redis key-value store',
            'pymongo': 'Python driver for MongoDB',
            'sqlalchemy': 'SQL toolkit and Object-Relational Mapping library',
            'psycopg2': 'PostgreSQL adapter for Python',
            'mysql': 'MySQL database connector for Python',
            'sqlite3': 'SQLite database interface',
            
            # Data Processing & File Handling
            'json': 'JSON encoder and decoder',
            'csv': 'CSV file reading and writing',
            'xml': 'XML processing library',
            'yaml': 'YAML parser and emitter',
            'toml': 'TOML parser and writer',
            'openpyxl': 'Library for reading/writing Excel files',
            'xlrd': 'Library for reading Excel files',
            'xlwt': 'Library for writing Excel files',
            'h5py': 'Interface to the HDF5 binary data format',
            'pickle': 'Python object serialization',
            'lxml': 'XML and HTML processing library',
            'beautifulsoup4': 'HTML/XML parsing library',
            'bs4': 'Beautiful Soup HTML/XML parsing library',
            
            # Async & Concurrency
            'asyncio': 'Asynchronous I/O framework',
            'threading': 'Thread-based parallelism',
            'multiprocessing': 'Process-based parallelism',
            'concurrent': 'High-level interface for asynchronously executing callables',
            'gevent': 'Coroutine-based networking library',
            'tornado': 'Python web framework and asynchronous networking library',
            
            # Testing & Development
            'pytest': 'Testing framework for Python',
            'unittest': 'Unit testing framework',
            'mock': 'Mock object library for testing',
            'coverage': 'Code coverage measurement for Python',
            'tox': 'Testing tool for multiple Python versions',
            'black': 'Code formatter for Python',
            'flake8': 'Tool for style guide enforcement',
            'mypy': 'Static type checker for Python',
            'pylint': 'Python code analysis tool',
            
            # System & Utilities
            'os': 'Operating system interface',
            'sys': 'System-specific parameters and functions',
            'pathlib': 'Object-oriented filesystem paths',
            'shutil': 'High-level file operations',
            'glob': 'Unix shell-style pathname pattern expansion',
            'subprocess': 'Subprocess management',
            'argparse': 'Command-line argument parsing',
            'logging': 'Logging facility for Python',
            'configparser': 'Configuration file parser',
            'datetime': 'Date and time handling',
            'time': 'Time-related functions',
            'calendar': 'Calendar-related functions',
            'random': 'Generate random numbers',
            'secrets': 'Generate secure random numbers for cryptography',
            'uuid': 'UUID objects according to RFC 4122',
            'hashlib': 'Secure hash and message digest algorithms',
            'base64': 'Base64 encoding and decoding',
            'zlib': 'Compression library',
            'gzip': 'Support for gzip files',
            'zipfile': 'Work with ZIP archives',
            'tarfile': 'Read and write tar archive files',
            
            # Math & Statistics
            'math': 'Mathematical functions',
            'statistics': 'Statistical functions',
            'decimal': 'Decimal fixed point and floating point arithmetic',
            'fractions': 'Rational numbers',
            'cmath': 'Mathematical functions for complex numbers',
            
            # Text Processing & NLP
            'nltk': 'Natural Language Toolkit',
            'spacy': 'Industrial-strength Natural Language Processing',
            'gensim': 'Topic modeling and document similarity',
            'textblob': 'Simple, pythonic text processing',
            're': 'Regular expression operations',
            'string': 'String operations and constants',
            'textwrap': 'Text wrapping and filling',
            
            # Networking & Internet
            'socket': 'Low-level networking interface',
            'ssl': 'TLS/SSL wrapper for socket objects',
            'ftplib': 'FTP protocol client',
            'smtplib': 'SMTP protocol client',
            'email': 'Email handling package',
            'urllib': 'URL handling modules',
            'http': 'HTTP modules',
            
            # GUI Development
            'tkinter': 'Python interface to Tcl/Tk GUI toolkit',
            'pyqt5': 'Python bindings for Qt application framework',
            'kivy': 'Open source Python framework for rapid development of applications',
            'streamlit': 'Framework for building data applications',
            'gradio': 'Create UIs for machine learning models',
            'dash': 'Build analytical web applications',
            
            # Game Development & Graphics
            'pygame': 'Set of Python modules designed for writing games',
            'arcade': '2D game development library',
            'panda3d': '3D game engine',
            
            # Scientific Computing Specialized
            'astropy': 'Astronomy and astrophysics library',
            'biopython': 'Tools for biological computation',
            'rdkit': 'Cheminformatics and machine learning software',
            'networkx': 'Network analysis and graph theory',
            'igraph': 'Network analysis and visualization',
            
            # Financial & Economics
            'yfinance': 'Yahoo Finance market data downloader',
            'pandas_datareader': 'Data readers for financial data',
            'quantlib': 'Quantitative finance library',
            'zipline': 'Algorithmic trading library',
            
            # Cloud & Infrastructure
            'boto3': 'Amazon Web Services SDK for Python',
            'google': 'Google Cloud Platform libraries',
            'azure': 'Microsoft Azure SDK for Python',
            'docker': 'Docker SDK for Python',
            'kubernetes': 'Kubernetes client library',
            
            # Cryptography & Security
            'cryptography': 'Cryptographic recipes and primitives',
            'pycryptodome': 'Cryptographic library for Python',
            'jwt': 'JSON Web Token implementation',
            'passlib': 'Password hashing library',
        }
        
        description = fallback_descriptions.get(module_name, f"Python module: {module_name}")
        self.module_descriptions[module_name] = description
        return description
    
    def _get_function_description(self, module_name: str, function_name: str) -> str:
        """Get a description of a specific function from its docstring."""
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                doc = inspect.getdoc(func)
                if doc:
                    # Get the first line as a brief description
                    description = doc.split('\n')[0].strip()
                    return description
        except (ImportError, AttributeError):
            pass
        
        return f"Function from {module_name}"
    
    def _resolve_module_from_alias(self, alias: str) -> Optional[str]:
        """Resolve the actual module name from an alias used in the script."""
        # Check direct imports
        for module_name, module_alias in self.imports.items():
            if module_alias == alias:
                return module_name
        
        # Check if it's a direct function import
        for module_name, imported_items in self.from_imports.items():
            for original_name, item_alias in imported_items:
                if item_alias == alias:
                    return module_name
        
        return None
    
    def _generate_report(self, file_path: str) -> Dict:
        """Generate the final analysis report."""
        report = {
            "file_path": file_path,
            "imports": [],
            "warnings": [],
            "overall_understanding": ""
        }
        
        # Process imports and their function usage
        import_counter = 1
        all_modules_used = set()
        
        # Handle regular imports
        for module_name, alias in self.imports.items():
            module_functions = []
            
            # Find functions used from this module (avoid duplicates)
            seen_functions = set()
            for module_alias, func_name in self.function_calls:
                if module_alias == alias and func_name not in seen_functions:
                    func_desc = self._get_function_description(module_name, func_name)
                    module_functions.append({
                        "name": func_name,
                        "description": func_desc
                    })
                    seen_functions.add(func_name)
            
            if module_functions:  # Only include modules that are actually used
                import_info = {
                    "number": import_counter,
                    "module": module_name,
                    "alias": alias if alias != module_name.split('.')[0] else None,
                    "description": self._get_module_description(module_name),
                    "functions": module_functions
                }
                report["imports"].append(import_info)
                all_modules_used.add(module_name)
                import_counter += 1
        
        # Handle from imports
        for module_name, imported_items in self.from_imports.items():
            module_functions = []
            
            # Find functions used from this module (avoid duplicates)
            seen_functions = set()
            for _, func_name in self.function_calls:
                for original_name, alias_name in imported_items:
                    if func_name == alias_name and original_name not in seen_functions:
                        func_desc = self._get_function_description(module_name, original_name)
                        module_functions.append({
                            "name": original_name,
                            "description": func_desc
                        })
                        seen_functions.add(original_name)
            
            if module_functions:  # Only include modules that are actually used
                import_info = {
                    "number": import_counter,
                    "module": module_name,
                    "alias": None,
                    "description": self._get_module_description(module_name),
                    "functions": module_functions,
                    "import_type": "from_import"
                }
                report["imports"].append(import_info)
                all_modules_used.add(module_name)
                import_counter += 1
        
        # Generate warnings for unresolved function calls
        self._generate_warnings(report, all_modules_used)
        
        # Generate overall understanding
        report["overall_understanding"] = self._generate_overall_understanding(all_modules_used, file_path)
        
        return report
    
    def _generate_warnings(self, report: Dict, all_modules_used: Set[str]):
        """Generate warnings for potential issues in the script."""
        warnings = []
        
        # Check for function calls that couldn't be resolved to any import
        unresolved_calls = []
        for module_alias, func_name in self.function_calls:
            if module_alias and not self._resolve_module_from_alias(module_alias):
                unresolved_calls.append(f"{module_alias}.{func_name}()")
        
        # Remove duplicates and add warning
        unique_unresolved = list(set(unresolved_calls))
        if unique_unresolved:
            if len(unique_unresolved) == 1:
                warnings.append(f"⚠️  Potential issue: Function call {unique_unresolved[0]} found, but the module was not imported.")
            else:
                func_list = ", ".join(unique_unresolved)
                warnings.append(f"⚠️  Potential issues: Function calls {func_list} found, but their modules were not imported.")
        
        # Check for imported modules that are never used
        unused_imports = []
        all_imported_modules = set(self.imports.keys()) | set(self.from_imports.keys())
        for imported_module in all_imported_modules:
            if imported_module not in all_modules_used:
                unused_imports.append(imported_module)
        
        if unused_imports:
            if len(unused_imports) == 1:
                warnings.append(f"💡 Optimization tip: Module '{unused_imports[0]}' is imported but never used.")
            else:
                module_list = ", ".join(f"'{m}'" for m in unused_imports)
                warnings.append(f"💡 Optimization tips: Modules {module_list} are imported but never used.")
        
        report["warnings"] = warnings
    
    def _generate_overall_understanding(self, modules_used: Set[str], file_path: str) -> str:
        """Generate an overall understanding of what the script does."""
        filename = os.path.basename(file_path)
        
        if not modules_used:
            return f"Technical Summary: The script '{filename}' doesn't use any external packages - it contains only built-in Python functionality.\n\nClear Explanation: This is a basic Python script that relies solely on Python's built-in features without importing external libraries."
        
        # Technical summary
        module_list = ", ".join(sorted(modules_used))
        tech_summary = f"Technical Summary: The script '{filename}' imports and utilizes {len(modules_used)} external package(s): {module_list}."
        
        # Determine script purpose based on modules used
        purpose_indicators = {
            'numpy': 'numerical computations',
            'pandas': 'data manipulation and analysis',
            'matplotlib': 'data visualization',
            'seaborn': 'statistical visualization',
            'scipy': 'scientific computing',
            'sklearn': 'machine learning',
            'tensorflow': 'deep learning',
            'pytorch': 'deep learning',
            'requests': 'web requests and API interactions',
            'flask': 'web application development',
            'django': 'web application development',
            'sqlite3': 'database operations',
            'json': 'JSON data processing',
            'csv': 'CSV file processing',
            'os': 'file system operations',
            'sys': 'system-level operations',
            'datetime': 'date and time processing',
            'random': 'random number generation',
            're': 'text pattern matching'
        }
        
        purposes = []
        for module in modules_used:
            if module in purpose_indicators:
                purposes.append(purpose_indicators[module])
        
        if purposes:
            if len(purposes) == 1:
                clear_explanation = f"Clear Explanation: This script is designed for {purposes[0]}."
            else:
                purpose_text = ", ".join(purposes[:-1]) + f" and {purposes[-1]}"
                clear_explanation = f"Clear Explanation: This script combines multiple functionalities including {purpose_text}."
        else:
            clear_explanation = "Clear Explanation: This script uses specialized Python packages for custom functionality."
        
        return f"{tech_summary}\n\n{clear_explanation}"
    
    def print_analysis(self, analysis_result: Dict):
        """Print the analysis result in a nicely formatted way."""
        if "error" in analysis_result:
            print(f"Error: {analysis_result['error']}")
            return
        
        print(f"\n{'='*60}")
        print(f"SCRIPT ANALYSIS: {os.path.basename(analysis_result['file_path'])}")
        print(f"{'='*60}")
        
        if not analysis_result['imports']:
            print("No external packages used in this script.")
        else:
            for import_info in analysis_result['imports']:
                print(f"\nImport: {import_info['number']}. {import_info['module']}", end="")
                if import_info.get('alias'):
                    print(f" (as {import_info['alias']})", end="")
                print(f" - {import_info['description']}")
                
                print("Functions used under this import:")
                for i, func in enumerate(import_info['functions'], 1):
                    print(f"  {import_info['number']}.{chr(96+i)}. {func['name']}() - {func['description']}")
        
        # Print warnings if any
        if analysis_result.get('warnings'):
            print(f"\n{'='*60}")
            print("WARNINGS & SUGGESTIONS:")
            print(f"{'='*60}")
            for warning in analysis_result['warnings']:
                print(warning)
        
        print(f"\n{'='*60}")
        print("OVERALL UNDERSTANDING:")
        print(f"{'='*60}")
        print(analysis_result['overall_understanding'])
        print(f"{'='*60}\n")