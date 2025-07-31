import os
import zipfile
import fnmatch
from pathlib import Path
from typing import List, Set


class CodePackager:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.ignore_patterns = self._load_ignore_patterns()
    
    def _load_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from .agentignore file"""
        ignore_file = self.project_path / ".agentignore"
        patterns = []
        
        if ignore_file.exists():
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns"""
        relative_path = file_path.relative_to(self.project_path)
        path_str = str(relative_path)
        
        for pattern in self.ignore_patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                if path_str.startswith(pattern[:-1] + '/') or path_str == pattern[:-1]:
                    return True
            # Handle file patterns
            elif fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
            # Handle patterns with path separators
            elif '/' in pattern and fnmatch.fnmatch(path_str, pattern):
                return True
        
        return False
    
    def _validate_required_files(self) -> None:
        """Validate that required files exist"""
        required_files = ['agent.yaml']
        missing_files = []
        
        for required_file in required_files:
            if not (self.project_path / required_file).exists():
                missing_files.append(required_file)
        
        if missing_files:
            raise ValueError(f"Required files missing: {', '.join(missing_files)}")
    
    def _collect_files(self) -> List[Path]:
        """Collect all files that should be included in the package"""
        files_to_include = []
        
        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            
            # Filter directories to avoid walking into ignored ones
            dirs[:] = [d for d in dirs if not self._should_ignore(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                if not self._should_ignore(file_path):
                    files_to_include.append(file_path)
        
        return files_to_include
    
    def create_package(self, output_path: str = None) -> str:
        """Create a zip package of the project code"""
        # Validate required files exist
        self._validate_required_files()
        
        # Default output path
        if output_path is None:
            output_path = str(self.project_path / "agent_package.zip")
        
        # Collect files to include
        files_to_include = self._collect_files()
        
        if not files_to_include:
            raise ValueError("No files to package")
        
        # Create zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_include:
                # Calculate relative path for archive
                arc_name = file_path.relative_to(self.project_path)
                zipf.write(file_path, arc_name)
        
        return output_path
    
    def get_package_info(self) -> dict:
        """Get information about what would be packaged"""
        try:
            self._validate_required_files()
            files_to_include = self._collect_files()
            
            total_size = sum(f.stat().st_size for f in files_to_include)
            
            return {
                'valid': True,
                'file_count': len(files_to_include),
                'total_size': total_size,
                'files': [str(f.relative_to(self.project_path)) for f in files_to_include]
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }