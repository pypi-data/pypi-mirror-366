"""
AI Instructions Manager for Copper Sun Brass Pro - Manages AI instruction files.

This module handles detection, updating, and creation of AI instruction files
that ensure Claude Code (and other AI agents) remember to use Copper Sun Brass features.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import json
import re
from datetime import datetime
import tempfile
import shutil

# PrependTemplateManager removed - no longer needed after elimination of forced prepending system


class AIInstructionsManager:
    """Manages AI instruction files for persistent Copper Sun Brass configuration."""
    
    # Constants for file processing
    CONTENT_PREVIEW_LENGTH = 1000  # Characters to read for content analysis
    MIN_KEYWORDS_THRESHOLD = 3     # Minimum keywords to classify as AI instruction file
    MAX_FILES_TO_SCAN = 1000      # Maximum markdown files to scan (prevent memory exhaustion)
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB limit for file size checking
    MAX_SYMLINK_DEPTH = 5         # Maximum symlink depth to prevent traversal attacks
    
    # Common AI instruction file names to search for
    AI_FILE_PATTERNS = [
        "AI_START_HERE.md",
        "AI_INSTRUCTIONS.md",
        "README_AI.md",
        "CLAUDE.md",
        ".ai/instructions.md",
        ".github/AI_GUIDE.md",
        "docs/AI_CONTEXT.md",
        "AI_AGENT_START_HERE.md",
        ".claude/instructions.md",
        "ASSISTANT_GUIDE.md"
    ]
    
    # Keywords for identifying AI instruction files
    AI_INSTRUCTION_KEYWORDS = [
        'ai assistant', 'claude', 'gpt', 'instruction', 'guideline',
        'when you', 'you should', 'you must', 'always', 'never',
        'context', 'remember', 'important:', 'note:'
    ]
    
    # Copper Sun Brass section markers
    BRASS_SECTION_START = "<!-- BRASS_SECTION_START -->"
    BRASS_SECTION_END = "<!-- BRASS_SECTION_END -->"
    
    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.brass_dir = project_root / ".brass"
        self.config_file = self.brass_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Copper Sun Brass configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (OSError, PermissionError) as e:
                print(f"Warning: Unable to read config file {self.config_file}: {e}")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Warning: Invalid config file format {self.config_file}: {e}")
            except Exception as e:
                print(f"Warning: Unexpected error reading config {self.config_file}: {e}")
        return {"user_preferences": {}}
    
    def find_ai_instruction_files(self) -> List[Path]:
        """Find all AI instruction files in the project."""
        found_files = []
        
        # Search for exact matches
        for pattern in self.AI_FILE_PATTERNS:
            file_path = self.project_root / pattern
            if file_path.exists() and file_path.is_file() and self._is_safe_path(file_path):
                found_files.append(file_path)
        
        # Also search for files with AI/Claude in the name (limit scope for performance)
        try:
            scanned_count = 0
            for file_path in self.project_root.rglob("*.md"):
                # Prevent memory exhaustion on large repositories
                if scanned_count >= self.MAX_FILES_TO_SCAN:
                    print(f"Warning: Scanned {self.MAX_FILES_TO_SCAN} markdown files, stopping to prevent memory issues")
                    break
                
                scanned_count += 1
                if file_path.is_file() and self._is_safe_path(file_path):
                    filename_lower = file_path.name.lower()
                    if any(keyword in filename_lower for keyword in ['ai_', 'claude', 'assistant', 'llm']):
                        if file_path not in found_files:
                            # Check if it looks like an instruction file
                            if self._is_likely_ai_instruction_file(file_path):
                                found_files.append(file_path)
        except (OSError, PermissionError) as e:
            # Log error but continue with found files
            print(f"Warning: Unable to scan some directories: {e}")
        
        return found_files
    
    def _atomic_write(self, file_path: Path, content: str) -> None:
        """Atomically write content to a file using temp file + rename pattern."""
        # Create temp file in same directory to ensure atomic move
        temp_fd, temp_path = tempfile.mkstemp(
            suffix='.tmp',
            dir=file_path.parent,
            prefix=f"{file_path.name}."
        )
        
        try:
            # Write content to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Atomically move temp file to target location
            shutil.move(temp_path, file_path)
            
        except Exception:
            # Cleanup temp file on any error
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # Temp file may not exist or already cleaned up
            raise
    
    def _is_safe_path(self, file_path: Path) -> bool:
        """Validate that a file path is safe to access (within project boundaries)."""
        try:
            # Check symlink depth first to prevent deep traversal attacks
            current_path = file_path
            depth = 0
            # Cache parent path to avoid repeated resolution in symlink loop
            parent_path = file_path.parent
            while current_path.is_symlink() and depth < self.MAX_SYMLINK_DEPTH:
                try:
                    current_path = current_path.readlink()
                    # Handle relative symlinks by resolving against cached parent
                    if not current_path.is_absolute():
                        current_path = parent_path / current_path
                    depth += 1
                except (OSError, ValueError):
                    return False
            
            # If we hit the symlink depth limit, consider unsafe
            if depth >= self.MAX_SYMLINK_DEPTH:
                return False
            
            # Resolve path to handle symlinks and relative paths
            resolved_path = file_path.resolve()
            resolved_root = self.project_root.resolve()
            
            # Check if the file is within the project root
            return resolved_path.is_relative_to(resolved_root)
        except (OSError, ValueError):
            # If path resolution fails, consider it unsafe
            return False
    
    def _is_likely_ai_instruction_file(self, file_path: Path) -> bool:
        """Check if a file is likely an AI instruction file based on content."""
        try:
            # Check file size before reading to prevent performance issues
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE_BYTES:
                print(f"Warning: Skipping large file {file_path.name} ({file_size // (1024*1024)}MB)")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read only what we need, respecting both preview length and actual file size
                read_length = min(self.CONTENT_PREVIEW_LENGTH, file_size)
                content = f.read(read_length).lower()
            
            # Count matching keywords
            keyword_count = sum(1 for keyword in self.AI_INSTRUCTION_KEYWORDS if keyword in content)
            return keyword_count >= self.MIN_KEYWORDS_THRESHOLD
            
        except (OSError, PermissionError, UnicodeDecodeError):
            return False
    
    def create_brass_section(self) -> str:
        """Create a minimal Brass reference for AI instruction files."""
        section = f"""
{self.BRASS_SECTION_START}
<!-- Note: The following prompt instructs Claude Code to check and use Brass intelligence. 
     It will be automatically removed when you run 'brass uninstall --all' or 'brass remove-integration'. -->

> **🎺 Copper Sun Brass**: Going forward, always check `.brass/AI_INSTRUCTIONS.md` for vital project intelligence, security alerts, todos, and more to improve your responses. Copper Sun Brass provides persistent memory and enhanced context across AI sessions.
{self.BRASS_SECTION_END}
"""
        return section
    
    def update_ai_instruction_file(self, file_path: Path) -> Tuple[bool, str]:
        """Update an AI instruction file with Copper Sun Brass section."""
        # Validate path safety first
        if not self._is_safe_path(file_path):
            return False, "Path validation failed: file is outside project boundaries"
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if Copper Sun Brass section already exists
            if self.BRASS_SECTION_START in content:
                # Update existing section - check if both markers exist before calculating indices
                start_idx = content.find(self.BRASS_SECTION_START)
                end_idx = content.find(self.BRASS_SECTION_END)
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    end_idx += len(self.BRASS_SECTION_END)
                    # Replace existing section
                    new_content = (
                        content[:start_idx] +
                        self.create_brass_section() +
                        content[end_idx:]
                    )
                    
                    # Use atomic write to prevent corruption
                    self._atomic_write(file_path, new_content)
                    
                    return True, "Updated existing Copper Sun Brass section"
                else:
                    return False, "Malformed Copper Sun Brass section markers"
            else:
                # Add new section
                # Try to add after the first heading or at the beginning
                lines = content.split('\n')
                insert_index = 0
                
                # Find a good place to insert (after first heading)
                for i, line in enumerate(lines):
                    if line.strip().startswith('#') and i > 0:
                        insert_index = i + 1
                        break
                
                # Insert the section
                lines.insert(insert_index, self.create_brass_section())
                new_content = '\n'.join(lines)
                
                # Use atomic write to prevent corruption
                self._atomic_write(file_path, new_content)
                
                return True, "Added Copper Sun Brass section"
                
        except (OSError, PermissionError) as e:
            return False, f"File access error: {str(e)}"
        except UnicodeDecodeError as e:
            return False, f"File encoding error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error updating file: {str(e)}"
    
    def create_default_ai_instructions(self) -> Path:
        """Create a default AI instructions file with Copper Sun Brass configuration."""
        # Ensure .brass directory exists
        self.brass_dir.mkdir(exist_ok=True)
        
        file_path = self.brass_dir / "AI_INSTRUCTIONS.md"
        
        content = f"""# AI Assistant Instructions

This file contains instructions for AI assistants (Claude, GPT, etc.) working on this project.

## 🎺 Copper Sun Brass Integration

> **Going forward, always check the following Brass files before responding to development questions** for vital project intelligence, security alerts, todos, and enhanced context:

### Brass Intelligence Files
- `.brass/CODE_SECURITY_AND_QUALITY_ANALYSIS.md` - Security vulnerabilities and quality issues
- `.brass/todos.yaml` - Prioritized TODO analysis with structured data (shows what's actually urgent vs. what can wait)
- `.brass/brass_analysis.yaml` - Structured project health data optimized for AI consumption
- `.brass/privacy_analysis.yaml` - Structured privacy and PII analysis with compliance guidance (optimized for AI consumption)
- `.brass/best_practices.yaml` - Evidence-based AI development best practices with implementation guidance (optimized for AI consumption)
- `.brass/STATUS.md` - Current project state and focus areas
- `.brass/CONTEXT.md` - Ongoing work context
- `.brass/INSIGHTS.md` - Codebase-specific best practices (prevents suggesting failed approaches)
- `.brass/HISTORY.md` - Project evolution and previously tried approaches

### Attribution Rule
If you use information from a `.brass/` file in your response:
- ✅ Say "Brass found..." or "According to Brass..." (users understand the source of unique insights)
- ❌ Otherwise, respond normally (maintains authenticity)

### Example Attribution
"Brass found 3 security vulnerabilities in the authentication flow..."
"According to Brass, this pattern was avoided in previous iterations..."

**Key principle:** Only mention Brass when you're actually using its intelligence - this shows users exactly when they're benefiting from enhanced context.

**What Brass Provides:** Persistent memory and enhanced context across AI sessions to improve your responses.

**Status: Active** ✅ | Use `brass refresh` to update context

## Project Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

### Testing
- Write tests for new functionality
- Ensure existing tests pass
- Follow the project's testing conventions

### Documentation
- Update documentation when changing APIs
- Keep README files current
- Document complex algorithms

### Security
- Never commit secrets or API keys
- Review code for security implications
- Follow security best practices

## Remember
- Brass provides persistent memory and enhanced context across sessions
- Only mention Brass when you're actually using its intelligence
- Check .brass/ files for project context when relevant
- You're building WITH Brass, not FOR Brass

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        # Use atomic write to prevent corruption
        self._atomic_write(file_path, content)
        
        return file_path
    
    def ensure_ai_instructions_exist(self) -> Tuple[Path, str]:
        """Ensure AI instructions exist, creating or updating as needed."""
        # ALWAYS ensure the main AI_INSTRUCTIONS.md file exists
        ai_instructions_path = self.brass_dir / "AI_INSTRUCTIONS.md"
        
        # Create AI_INSTRUCTIONS.md if it doesn't exist
        if not ai_instructions_path.exists():
            self.create_default_ai_instructions()
        
        # Now look for existing AI instruction files to update (excluding our own .brass/AI_INSTRUCTIONS.md)
        existing_files = self.find_ai_instruction_files()
        # Filter out our own .brass/AI_INSTRUCTIONS.md file
        external_files = [f for f in existing_files if f != ai_instructions_path]
        
        if external_files:
            # Update the first found external file with Brass section
            target_file = external_files[0]
            success, message = self.update_ai_instruction_file(target_file)
            
            if success:
                return ai_instructions_path, f"Updated existing file: {target_file.name} and ensured AI_INSTRUCTIONS.md exists"
            else:
                return ai_instructions_path, f"Ensured AI_INSTRUCTIONS.md exists, but update failed for {target_file.name}: {message}"
        else:
            # No external AI files found, create CLAUDE.md reference
            claude_md_path = self.project_root / "CLAUDE.md"
            if not claude_md_path.exists():
                claude_md_content = self.create_brass_section()
                
                # Use atomic write to prevent corruption
                self._atomic_write(claude_md_path, claude_md_content)
                
                return ai_instructions_path, "Created AI instructions file and CLAUDE.md reference"
            else:
                return ai_instructions_path, "Ensured AI_INSTRUCTIONS.md exists"
    
    def validate_brass_integration(self, file_path: Path) -> Dict[str, Any]:
        """Validate that an AI instruction file has proper Copper Sun Brass integration."""
        result = {
            "has_brass_section": False,
            "has_correct_theme": False,
            "has_context_check": False,
            "has_indicator_examples": False,
            "issues": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Copper Sun Brass section
            result["has_brass_section"] = self.BRASS_SECTION_START in content
            
            if result["has_brass_section"]:
                # Extract Copper Sun Brass section with proper validation
                start_idx = content.find(self.BRASS_SECTION_START)
                end_idx = content.find(self.BRASS_SECTION_END)
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    section_content = content[start_idx:end_idx + len(self.BRASS_SECTION_END)]
                    
                    # Check for theme
                    prefs = self.config.get("user_preferences", {})
                    current_theme = prefs.get("visual_theme", "colorful")
                    result["has_correct_theme"] = current_theme in section_content
                    
                    # Check for context file references
                    result["has_context_check"] = all(
                        filename in section_content 
                        for filename in ["STATUS.md", "CONTEXT.md", "INSIGHTS.md", "HISTORY.md"]
                    )
                    
                    # Check for indicator examples
                    result["has_indicator_examples"] = "Copper Sun Brass:" in section_content
                    
                    # Identify issues
                    if not result["has_correct_theme"]:
                        result["issues"].append(f"Theme mismatch: expected '{current_theme}'")
                    
                    if not result["has_context_check"]:
                        result["issues"].append("Missing references to .brass/ context files")
                    
                    if not result["has_indicator_examples"]:
                        result["issues"].append("Missing Copper Sun Brass indicator examples")
                else:
                    result["issues"].append("Malformed Copper Sun Brass section markers")
            else:
                result["issues"].append("No Copper Sun Brass section found")
            
        except (OSError, PermissionError) as e:
            result["issues"].append(f"File access error: {str(e)}")
        except UnicodeDecodeError as e:
            result["issues"].append(f"File encoding error: {str(e)}")
        except Exception as e:
            result["issues"].append(f"Unexpected error reading file: {str(e)}")
        
        return result