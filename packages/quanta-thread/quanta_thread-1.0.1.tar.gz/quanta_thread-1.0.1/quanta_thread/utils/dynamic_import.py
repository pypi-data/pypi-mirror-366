"""
Dynamic Import module for QuantaThread framework.

Provides dynamic module loading, dependency management, and plugin system
for the quantum-inspired computing framework.
"""

import importlib
import importlib.util
import sys
import os
import inspect
from typing import Any, Dict, List, Optional, Callable, Type, Union
from pathlib import Path
import logging
import json
from dataclasses import dataclass, field


@dataclass
class ModuleInfo:
    """Information about a dynamically loaded module."""
    name: str
    path: str
    module: Any
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    load_time: float = 0.0
    is_plugin: bool = False


@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    author: str
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class DynamicImporter:
    """
    Dynamic module loader and plugin system for QuantaThread.
    
    Provides capabilities for:
    - Dynamic module loading from various sources
    - Plugin discovery and management
    - Dependency resolution and checking
    - Hot-reloading of modules
    - Class and function discovery
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None, enable_logging: bool = True):
        """
        Initialize the dynamic importer.
        
        Args:
            plugin_dirs: Directories to search for plugins
            enable_logging: Whether to enable logging
        """
        self.plugin_dirs = plugin_dirs or []
        self.loaded_modules: Dict[str, ModuleInfo] = {}
        self.loaded_plugins: Dict[str, PluginInfo] = {}
        self.module_cache: Dict[str, Any] = {}
        
        # Setup logging
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger('QuantaThread.DynamicImporter')
        else:
            self.logger = None
        
        # Add plugin directories to Python path
        for plugin_dir in self.plugin_dirs:
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
    
    def load_module(self, module_name: str, module_path: Optional[str] = None) -> Optional[Any]:
        """
        Load a module dynamically.
        
        Args:
            module_name: Name of the module to load
            module_path: Optional path to the module file
            
        Returns:
            Loaded module or None if failed
        """
        try:
            if module_path:
                # Load from specific path
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is None or spec.loader is None:
                    if self.logger:
                        self.logger.error(f"Could not create spec for module: {module_name}")
                    return None
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Load from Python path
                module = importlib.import_module(module_name)
            
            # Extract module information
            module_info = self._extract_module_info(module_name, module_path or "", module)
            self.loaded_modules[module_name] = module_info
            
            if self.logger:
                self.logger.info(f"Successfully loaded module: {module_name}")
            
            return module
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load module {module_name}: {str(e)}")
            return None
    
    def load_class(self, module_name: str, class_name: str, 
                  module_path: Optional[str] = None) -> Optional[Type]:
        """
        Load a specific class from a module.
        
        Args:
            module_name: Name of the module
            class_name: Name of the class to load
            module_path: Optional path to the module file
            
        Returns:
            Loaded class or None if failed
        """
        module = self.load_module(module_name, module_path)
        if module is None:
            return None
        
        try:
            class_obj = getattr(module, class_name)
            if inspect.isclass(class_obj):
                return class_obj
            else:
                if self.logger:
                    self.logger.error(f"{class_name} is not a class in module {module_name}")
                return None
        except AttributeError:
            if self.logger:
                self.logger.error(f"Class {class_name} not found in module {module_name}")
            return None
    
    def load_function(self, module_name: str, function_name: str,
                     module_path: Optional[str] = None) -> Optional[Callable]:
        """
        Load a specific function from a module.
        
        Args:
            module_name: Name of the module
            function_name: Name of the function to load
            module_path: Optional path to the module file
            
        Returns:
            Loaded function or None if failed
        """
        module = self.load_module(module_name, module_path)
        if module is None:
            return None
        
        try:
            func_obj = getattr(module, function_name)
            if callable(func_obj) and not inspect.isclass(func_obj):
                return func_obj
            else:
                if self.logger:
                    self.logger.error(f"{function_name} is not a function in module {module_name}")
                return None
        except AttributeError:
            if self.logger:
                self.logger.error(f"Function {function_name} not found in module {module_name}")
            return None
    
    def discover_modules(self, search_paths: Optional[List[str]] = None) -> List[str]:
        """
        Discover available modules in specified paths.
        
        Args:
            search_paths: Paths to search for modules
            
        Returns:
            List of discovered module names
        """
        if search_paths is None:
            search_paths = self.plugin_dirs
        
        discovered_modules = []
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        # Convert file path to module name
                        rel_path = os.path.relpath(os.path.join(root, file), search_path)
                        module_name = os.path.splitext(rel_path)[0].replace(os.sep, '.')
                        discovered_modules.append(module_name)
        
        return discovered_modules
    
    def load_plugin(self, plugin_path: str) -> Optional[PluginInfo]:
        """
        Load a plugin from a directory or file.
        
        Args:
            plugin_path: Path to the plugin
            
        Returns:
            Plugin information or None if failed
        """
        try:
            plugin_path = Path(plugin_path)
            
            # Check for plugin manifest
            manifest_path = plugin_path / "plugin.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                plugin_info = PluginInfo(
                    name=manifest.get('name', plugin_path.name),
                    version=manifest.get('version', '1.0.0'),
                    description=manifest.get('description', ''),
                    author=manifest.get('author', ''),
                    entry_point=manifest.get('entry_point', '__init__.py'),
                    dependencies=manifest.get('dependencies', []),
                    config=manifest.get('config', {})
                )
            else:
                # Create default plugin info
                plugin_info = PluginInfo(
                    name=plugin_path.name,
                    version='1.0.0',
                    description='',
                    author='',
                    entry_point='__init__.py',
                    dependencies=[],
                    config={}
                )
            
            # Load the plugin module
            entry_point_path = plugin_path / plugin_info.entry_point
            if entry_point_path.exists():
                module_name = f"plugin.{plugin_info.name}"
                module = self.load_module(module_name, str(entry_point_path))
                
                if module is not None:
                    self.loaded_plugins[plugin_info.name] = plugin_info
                    
                    if self.logger:
                        self.logger.info(f"Successfully loaded plugin: {plugin_info.name}")
                    
                    return plugin_info
            
            if self.logger:
                self.logger.error(f"Failed to load plugin: {plugin_path}")
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading plugin {plugin_path}: {str(e)}")
            return None
    
    def discover_plugins(self) -> List[PluginInfo]:
        """
        Discover and load all available plugins.
        
        Returns:
            List of loaded plugin information
        """
        discovered_plugins = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                if os.path.isdir(item_path):
                    plugin_info = self.load_plugin(item_path)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
        
        return discovered_plugins
    
    def check_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """
        Check if dependencies are available.
        
        Args:
            dependencies: List of dependency names to check
            
        Returns:
            Dictionary mapping dependency names to availability status
        """
        results = {}
        
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False
        
        return results
    
    def hot_reload(self, module_name: str) -> bool:
        """
        Hot-reload a module (reload without restarting).
        
        Args:
            module_name: Name of the module to reload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if module_name in sys.modules:
                # Reload the module
                module = importlib.reload(sys.modules[module_name])
                
                # Update module info
                if module_name in self.loaded_modules:
                    module_info = self._extract_module_info(
                        module_name, 
                        self.loaded_modules[module_name].path, 
                        module
                    )
                    self.loaded_modules[module_name] = module_info
                
                if self.logger:
                    self.logger.info(f"Successfully hot-reloaded module: {module_name}")
                
                return True
            else:
                if self.logger:
                    self.logger.warning(f"Module {module_name} not found for hot-reload")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to hot-reload module {module_name}: {str(e)}")
            return False
    
    def get_loaded_modules(self) -> Dict[str, ModuleInfo]:
        """Get information about all loaded modules."""
        return dict(self.loaded_modules)
    
    def get_loaded_plugins(self) -> Dict[str, PluginInfo]:
        """Get information about all loaded plugins."""
        return dict(self.loaded_plugins)
    
    def unload_module(self, module_name: str) -> bool:
        """
        Unload a module.
        
        Args:
            module_name: Name of the module to unload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            if module_name in self.loaded_modules:
                del self.loaded_modules[module_name]
            
            if module_name in self.module_cache:
                del self.module_cache[module_name]
            
            if self.logger:
                self.logger.info(f"Successfully unloaded module: {module_name}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to unload module {module_name}: {str(e)}")
            return False
    
    def clear_cache(self) -> None:
        """Clear the module cache."""
        self.module_cache.clear()
        if self.logger:
            self.logger.info("Module cache cleared")
    
    def _extract_module_info(self, name: str, path: str, module: Any) -> ModuleInfo:
        """Extract information from a loaded module."""
        classes = []
        functions = []
        
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(module, attr_name)
            
            if inspect.isclass(attr):
                classes.append(attr_name)
            elif callable(attr) and not inspect.isclass(attr):
                functions.append(attr_name)
        
        return ModuleInfo(
            name=name,
            path=path,
            module=module,
            classes=classes,
            functions=functions,
            dependencies=[],  # Could be enhanced to detect dependencies
            load_time=0.0,   # Could be enhanced to track load time
            is_plugin=name.startswith('plugin.')
        ) 