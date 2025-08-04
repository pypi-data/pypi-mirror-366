"""
Pure Base Analyzer - handles only JAR analysis operations.
Clean separation following the ideal architecture diagram.
"""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseAnalyzer:
    """
    Pure base analyzer focused solely on JAR analysis.
    
    Follows the ideal architecture - no cloning, no path decisions,
    just pure analysis of local directories.
    """
    
    def __init__(self, config: Dict[str, Any], memory_overrides: Optional[Dict[str, str]] = None):
        """Initialize base analyzer with JAR configuration"""
        self.config = config
        self.memory_overrides = memory_overrides or {}
        
        # Get base directory from user config
        self.base_dir = self._get_base_dir()
        
        # JAR configuration
        jar_config = config.get("graphshift", {}).get("jar", {})
        jar_path_config = jar_config.get("path", "resources/gs-analyzer.jar")
        
        # Handle package installation vs development
        if Path(jar_path_config).is_absolute() or Path(jar_path_config).exists():
            self.jar_path = Path(jar_path_config)
        else:
            # Try to find JAR in package installation
            try:
                import importlib.resources as pkg_resources
                with pkg_resources.path(__name__.split('.')[0] + '.resources', 'gs-analyzer.jar') as p:
                    self.jar_path = Path(p)
            except (ImportError, ModuleNotFoundError):
                try:
                    # Fallback to old pkg_resources
                    import pkg_resources
                    self.jar_path = Path(pkg_resources.resource_filename(__name__.split('.')[0], jar_path_config))
                except:
                    # Fallback to relative path
                    self.jar_path = Path(jar_path_config)
        
        # Defensive programming - ensure defaults are strings
        default_memory = jar_config.get("memory", "2g")
        default_initial_memory = jar_config.get("initial_memory", "512m")
        
        # Safety check - if config contains dicts, use hardcoded defaults
        self.default_memory = default_memory if isinstance(default_memory, str) else "2g"
        self.default_initial_memory = default_initial_memory if isinstance(default_initial_memory, str) else "512m"
        
        logger.debug(f"Initialized with memory: {self.default_memory}, initial: {self.default_initial_memory}")
    
    def _get_base_dir(self) -> Path:
        """Get base directory from user config, fallback to current directory"""
        from core.initialization import get_user_config_file
        import yaml
        
        try:
            user_config_file = get_user_config_file()
            if user_config_file.exists():
                with open(user_config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config and 'base_directory' in user_config:
                        return Path(user_config['base_directory'])
        except Exception:
            pass
        
        # Fallback to current directory
        return Path('.')
    
    async def analyze_directory(
        self,
        directory_path: str,
        target_jdk: str = "21",
        scope: str = "all-deprecations"
    ) -> Optional[Dict[str, Any]]:
        """
        Pure directory analysis using JAR.
        
        Args:
            directory_path: Local directory to analyze
            target_jdk: Target JDK version
            scope: Analysis scope
            
        Returns:
            Raw JSON from JAR or None if failed
        """
        try:
            # Validate directory exists
            dir_path = Path(directory_path)
            if not dir_path.exists() or not dir_path.is_dir():
                logger.error(f"Directory does not exist: {directory_path}")
                return None
            
            # Get memory settings - handle both parameter name formats
            memory = (self.memory_overrides.get("memory") or 
                     self.memory_overrides.get("heap_size") or 
                     self.default_memory)
            initial_memory = (self.memory_overrides.get("initial_memory") or 
                             self.memory_overrides.get("initial_heap") or 
                             self.default_initial_memory)
            
            logger.debug(f"Using memory: {memory}, initial: {initial_memory}")
            
            # Ensure temp directory exists
            temp_dir = self.base_dir / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Build JAR command - make filename unique per directory to avoid conflicts
            import hashlib
            dir_hash = hashlib.md5(str(dir_path).encode()).hexdigest()[:8]
            output_file = f"temp_analysis_{target_jdk}_{scope}_{dir_hash}.json"
            cmd = [
                'java',
                f'-Xmx{memory}',
                f'-Xms{initial_memory}',
                '-Xss4m',
                '-jar', str(self.jar_path),
                '-d', str(dir_path),
                '-t', target_jdk,
                '--scope', scope,
                '-o', str(temp_dir / output_file)
            ]
            
            logger.debug(f"Running analysis: {' '.join(cmd)}")
            
            # Execute JAR with proper cleanup
            process = None
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
            except asyncio.CancelledError:
                # Handle keyboard interrupt gracefully
                if process and process.returncode is None:
                    try:
                        process.terminate()
                        await asyncio.wait_for(process.wait(), timeout=5.0)
                    except (ProcessLookupError, asyncio.TimeoutError):
                        try:
                            process.kill()
                            await process.wait()
                        except ProcessLookupError:
                            pass
                raise
            except Exception:
                # Cleanup on any other exception
                if process and process.returncode is None:
                    try:
                        process.terminate()
                        await process.wait()
                    except ProcessLookupError:
                        pass
                raise
            
            # Log stderr only if it contains actual errors (not normal status messages)
            if stderr:
                stderr_text = stderr.decode()
                # Filter out normal JAR status messages
                if not any(normal_msg in stderr_text for normal_msg in [
                    "Loaded", "deprecation entries", "GraphShift Analyzer", 
                    "Directory:", "Target JDK:", "Output:", "Scanning Java files",
                    "Analysis complete", "Total findings:"
                ]):
                    logger.warning(f"JAR stderr output: {stderr_text}")
            
            if process.returncode == 0:
                # Read the output file
                output_path = temp_dir / output_file
                if output_path.exists():
                    try:
                        with open(output_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if not content.strip():
                                logger.error(f"JAR output file is empty: {output_path}")
                                return None
                            result = json.loads(content)
                        output_path.unlink()  # Clean up temp file
                        
                        logger.debug(f"JAR analysis completed for {directory_path}")
                        return result
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in output file: {e}")
                        logger.error(f"File content (first 500 chars): {content[:500]}")
                        return None
                else:
                    logger.error("JAR completed but output file not found")
                    logger.error(f"Expected output file: {output_path}")
                    logger.error(f"Temp directory contents: {list(temp_dir.glob('*'))}")
                    return None
            else:
                logger.error(f"JAR analysis failed: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"JAR execution failed: {e}")
            return None
    
    def get_memory_info(self) -> str:
        """Get memory configuration for display"""
        # Use same logic as JAR execution for consistency
        memory = (self.memory_overrides.get("memory") or 
                 self.memory_overrides.get("heap_size") or 
                 self.default_memory)
        initial_memory = (self.memory_overrides.get("initial_memory") or 
                         self.memory_overrides.get("initial_heap") or 
                         self.default_initial_memory)
        
        return f"{memory} memory, {initial_memory} initial"