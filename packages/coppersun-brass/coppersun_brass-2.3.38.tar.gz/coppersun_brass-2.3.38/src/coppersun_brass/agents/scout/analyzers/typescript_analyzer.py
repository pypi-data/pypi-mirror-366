"""TypeScript analyzer extending JavaScript analysis with type information.

General Staff Role: G2 Intelligence - TypeScript Specialist
Provides enhanced analysis of TypeScript code leveraging type information
to identify additional patterns and provide type-aware recommendations.

Persistent Value: Creates TypeScript-specific observations that help AI
understand type safety, interface contracts, and architectural patterns.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import tempfile
import os
import atexit
import shlex
import subprocess
import json

from .javascript_analyzer import JavaScriptAnalyzer
from .base_analyzer import AnalysisResult, CodeEntity, CodeIssue, CodeMetrics

logger = logging.getLogger(__name__)


class MissingTypeScriptDependencies(Exception):
    """Raised when required TypeScript parser dependencies are missing."""
    
    def __init__(self, missing_packages: List[str], suggested_action: str = None):
        self.missing_packages = missing_packages
        self.suggested_action = suggested_action or "Install missing TypeScript dependencies"
        
        package_list = ", ".join(missing_packages)
        message = f"Missing required TypeScript parser dependencies: {package_list}"
        if suggested_action:
            message += f"\nSuggested action: {suggested_action}"
        
        super().__init__(message)


class TypeScriptParseError(Exception):
    """Raised when TypeScript parsing fails."""
    
    def __init__(self, file_path: str, error_details: str, suggestion: str = None):
        self.file_path = file_path
        self.error_details = error_details
        self.suggestion = suggestion
        
        message = f"Failed to parse TypeScript file '{file_path}': {error_details}"
        if suggestion:
            message += f"\nSuggestion: {suggestion}"
            
        super().__init__(message)


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """TypeScript analyzer extending JavaScript analysis with type awareness.
    
    This analyzer provides additional intelligence about TypeScript-specific
    patterns, type safety issues, and architectural decisions.
    """
    
    def __init__(self, dcp_path: Optional[str] = None):
        """Initialize TypeScript analyzer."""
        super().__init__(dcp_path)
        self._supported_languages = {'typescript', 'tsx'}
        self._check_node_availability()
        self._ensure_typescript_dependencies()
        self.parser_script = self._create_typescript_parser_script()
        
    def _check_node_availability(self):
        """Check if Node.js is available for parsing."""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise MissingTypeScriptDependencies(
                    ['nodejs'], 
                    "Node.js is required for TypeScript parsing"
                )
            else:
                self.node_available = True
                logger.info(f"Using Node.js {result.stdout.strip()} for TypeScript parsing")
        except FileNotFoundError:
            raise MissingTypeScriptDependencies(
                ['nodejs'], 
                "Node.js not found. Please install Node.js to enable TypeScript analysis"
            )
            
    def _ensure_typescript_dependencies(self):
        """Ensure required npm packages are available with auto-install.
        
        Attempts to auto-install @typescript-eslint/parser and @typescript-eslint/types if missing.
        Falls back to setup script creation if auto-install fails.
        """
        missing_packages = []
        required_packages = ['@typescript-eslint/parser', '@typescript-eslint/types']
        
        # Check which packages are missing
        for package in required_packages:
            if not self._check_package_available(package):
                missing_packages.append(package)
        
        if not missing_packages:
            logger.debug("All required TypeScript parser dependencies are available")
            return
        
        logger.info(f"Missing TypeScript parser dependencies: {', '.join(missing_packages)}")
        
        # Attempt auto-install
        try:
            self._auto_install_dependencies(missing_packages)
            
            # Verify installation succeeded
            still_missing = []
            for package in missing_packages:
                if not self._check_package_available(package):
                    still_missing.append(package)
            
            if still_missing:
                raise MissingTypeScriptDependencies(
                    still_missing,
                    "Auto-install completed but some packages still not found. Try manual installation."
                )
            
            logger.info("Successfully auto-installed TypeScript parser dependencies")
            # Mark that dependencies were auto-installed for metadata tracking
            self._dependency_install_method = "auto-installed-global"
            
        except Exception as e:
            logger.warning(f"Auto-install failed: {e}")
            # Fall back to creating setup script
            self._create_setup_script(missing_packages)
            raise MissingTypeScriptDependencies(
                missing_packages,
                f"Auto-install failed. Please run the setup script or install manually: npm install --no-save {' '.join(missing_packages)}"
            )
            
    def _check_package_available(self, package_name):
        """Check if a package is available via require.resolve, with NODE_PATH support."""
        # Try without NODE_PATH first (for local packages)
        check_result = subprocess.run(
            ['node', '-e', f"require.resolve('{package_name}')"],
            capture_output=True,
            text=True
        )
        
        if check_result.returncode == 0:
            logger.debug(f"Package {package_name} found locally")
            return True
            
        # Try with NODE_PATH (for global packages)
        global_path = self._get_global_node_modules_path()
        if global_path:
            logger.info(f"Trying NODE_PATH fallback at {global_path} for {package_name}")
            env = os.environ.copy()
            env['NODE_PATH'] = global_path
            check_result = subprocess.run(
                ['node', '-e', f"require.resolve('{package_name}')"],
                capture_output=True,
                text=True,
                env=env
            )
            if check_result.returncode == 0:
                logger.info(f"Package {package_name} found via NODE_PATH")
                return True
        
        logger.debug(f"Package {package_name} not found locally or globally")
        return False
        
    def _get_global_node_modules_path(self):
        """Get the global node_modules path for NODE_PATH."""
        try:
            result = subprocess.run(['npm', 'config', 'get', 'prefix'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                prefix = result.stdout.strip()
                return f"{prefix}/lib/node_modules"
        except Exception:
            pass
        return None
        
    def _auto_install_dependencies(self, packages: List[str]):
        """Auto-install npm packages with timeout and error handling."""
        install_command = ['npm', 'install', '-g'] + packages
        
        logger.info(f"Auto-installing dependencies globally: {' '.join(packages)}")
        
        try:
            result = subprocess.run(
                install_command,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                error_msg = f"npm install failed with exit code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                raise RuntimeError(error_msg)
            
            if result.stdout:
                logger.debug(f"npm install output: {result.stdout}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("npm install timed out after 30 seconds")
        except FileNotFoundError:
            raise RuntimeError("npm command not found. Please ensure Node.js and npm are installed.")
    
    def _create_setup_script(self, packages: List[str]):
        """Create a setup script as fallback when auto-install fails."""
        try:
            setup_script = Path(self.parser_script).parent / "setup_ts_parser.sh"
            setup_content = f"""#!/bin/bash
# Install TypeScript parser dependencies
npm install --no-save {' '.join(packages)}
"""
            setup_script.write_text(setup_content)
            logger.info(f"Created setup script: {setup_script}")
        except Exception as e:
            logger.error(f"Failed to create setup script: {e}")
            
    def _create_typescript_parser_script(self) -> str:
        """Create enhanced parser script for TypeScript.
        
        Returns path to TypeScript-aware parser script.
        """
        # Create temporary parser script with proper cleanup
        parser_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.js', 
            delete=False,
            prefix='brass_ts_parser_'
        )
        
        # Register cleanup on exit
        atexit.register(lambda: self._cleanup_file(parser_file.name))
        
        parser_ts = '''
const fs = require('fs');
const parser = require('@typescript-eslint/parser');
const { TSESTree } = require('@typescript-eslint/types');

// Read file from command line argument
const filePath = process.argv[2];
const code = fs.readFileSync(filePath, 'utf8');

// Parse options for TypeScript
const parseOptions = {
    loc: true,
    range: true,
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
        jsx: filePath.endsWith('.tsx')
    }
};

try {
    const ast = parser.parse(code, parseOptions);
    
    const analysis = {
        entities: [],
        imports: [],
        exports: [],
        types: [],
        interfaces: [],
        complexity: {},
        issues: [],
        metrics: {
            lines: code.split('\\n').length,
            functions: 0,
            classes: 0,
            interfaces: 0,
            types: 0,
            generics: 0,
            anyUsage: 0,
            strictMode: false
        }
    };
    
    // Simple AST traversal for TypeScript-specific features
    function traverse(node, parent = null) {
        if (!node || typeof node !== 'object') return;
        
        switch (node.type) {
            case 'FunctionDeclaration':
            case 'FunctionExpression':
            case 'ArrowFunctionExpression':
                analysis.entities.push({
                    type: 'function',
                    name: node.id ? node.id.name : '<anonymous>',
                    line_start: node.loc.start.line,
                    line_end: node.loc.end.line,
                    async: node.async || false,
                    generator: node.generator || false,
                    params: node.params ? node.params.length : 0,
                    returnType: node.returnType ? true : false,
                    typeParams: node.typeParameters ? true : false
                });
                analysis.metrics.functions++;
                break;
                
            case 'ClassDeclaration':
                analysis.entities.push({
                    type: 'class',
                    name: node.id ? node.id.name : '<anonymous>',
                    line_start: node.loc.start.line,
                    line_end: node.loc.end.line,
                    abstract: node.abstract || false,
                    implements: node.implements ? node.implements.length : 0,
                    typeParams: node.typeParameters ? true : false
                });
                analysis.metrics.classes++;
                break;
                
            case 'TSInterfaceDeclaration':
                analysis.interfaces.push({
                    name: node.id.name,
                    line: node.loc.start.line,
                    extends: node.extends ? node.extends.length : 0,
                    members: node.body.body.length
                });
                analysis.metrics.interfaces++;
                break;
                
            case 'TSTypeAliasDeclaration':
                analysis.types.push({
                    name: node.id.name,
                    line: node.loc.start.line,
                    generic: node.typeParameters ? true : false
                });
                analysis.metrics.types++;
                if (node.typeParameters) analysis.metrics.generics++;
                break;
                
            case 'TSAnyKeyword':
                analysis.metrics.anyUsage++;
                analysis.issues.push({
                    type: 'any_type_usage',
                    line: node.loc.start.line,
                    severity: 'medium'
                });
                break;
                
            case 'ImportDeclaration':
                analysis.imports.push({
                    source: node.source.value,
                    line: node.loc.start.line,
                    typeOnly: node.importKind === 'type'
                });
                break;
        }
        
        // Traverse children
        for (const key in node) {
            if (key === 'parent' || key === 'loc' || key === 'range') continue;
            const child = node[key];
            if (Array.isArray(child)) {
                child.forEach(item => traverse(item, node));
            } else if (child && typeof child === 'object') {
                traverse(child, node);
            }
        }
    }
    
    traverse(ast);
    
    // Calculate type safety score
    const typeSafetyScore = Math.max(0, 100 - (analysis.metrics.anyUsage * 5));
    analysis.metrics.typeSafetyScore = typeSafetyScore;
    
    // Detect strict mode
    analysis.metrics.strictMode = code.includes('"use strict"') || 
                                 code.includes("'use strict'");
    
    console.log(JSON.stringify(analysis, null, 2));
    
} catch (error) {
    console.error(JSON.stringify({
        error: error.message,
        type: 'parse_error',
        file: filePath
    }));
    process.exit(1);
}
        '''
        
        parser_file.write(parser_ts)
        parser_file.close()
        return parser_file.name
        
    def analyze(self, file_path: Path) -> AnalysisResult:
        """Analyze TypeScript file with mandatory TypeScript parsing.
        
        Args:
            file_path: Path to TypeScript file
            
        Returns:
            AnalysisResult with TypeScript-specific intelligence
            
        Raises:
            MissingTypeScriptDependencies: If TypeScript parser dependencies are missing
            TypeScriptParseError: If TypeScript parsing fails
        """
        try:
            # Run TypeScript parser script with proper argument handling
            file_path_str = str(file_path)
            parser_script_str = self.parser_script
            
            # Get global npm modules path for NODE_PATH
            env = os.environ.copy()
            try:
                npm_global_result = subprocess.run(
                    ['npm', 'root', '-g'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if npm_global_result.returncode == 0:
                    global_modules_path = npm_global_result.stdout.strip()
                    env['NODE_PATH'] = global_modules_path
                    logger.debug(f"Set NODE_PATH to: {global_modules_path}")
            except Exception as e:
                logger.warning(f"Could not set NODE_PATH: {e}")
            
            result = subprocess.run(
                ['node', parser_script_str, file_path_str],
                capture_output=True,
                text=True,
                timeout=10,
                shell=False,  # Explicitly disable shell
                env=env
            )
            
            if result.returncode != 0:
                # Enhanced error handling for parse failures
                try:
                    error_data = json.loads(result.stderr)
                    error_details = error_data.get('error', 'Unknown parse error')
                    
                    raise TypeScriptParseError(
                        file_path=str(file_path),
                        error_details=error_details,
                        suggestion="Check TypeScript syntax and file encoding"
                    )
                except json.JSONDecodeError:
                    # Fallback for non-JSON error output - provide intelligent error recovery
                    error_details = result.stderr
                    suggestion = self._generate_intelligent_suggestion(error_details, file_path)
                    
                    logger.error(f"TypeScript parser error: {error_details}")
                    raise TypeScriptParseError(
                        file_path=str(file_path),
                        error_details=error_details,
                        suggestion=suggestion
                    )
                
            # Parse the analysis results
            analysis_data = json.loads(result.stdout)
            
            # Convert to our standard format
            return self._convert_to_analysis_result(file_path, analysis_data)
            
        except subprocess.TimeoutExpired:
            logger.error(f"TypeScript parser timeout for {file_path}")
            raise TypeScriptParseError(
                file_path=str(file_path),
                error_details="Parser execution timed out",
                suggestion="File may be too large or contain complex syntax"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid TypeScript parser output: {e}")
            raise TypeScriptParseError(
                file_path=str(file_path),
                error_details=f"Invalid parser output: {e}",
                suggestion="Parser may have encountered an unexpected error"
            )
        except Exception as e:
            logger.error(f"TypeScript analysis error: {e}")
            raise TypeScriptParseError(
                file_path=str(file_path),
                error_details=str(e),
                suggestion="Check file accessibility and TypeScript parser installation"
            )
            
    def _generate_intelligent_suggestion(self, error_details: str, file_path: Path) -> str:
        """Generate intelligent suggestions based on TypeScript parse errors.
        
        Args:
            error_details: Raw error message from parser
            file_path: Path to the file being analyzed
            
        Returns:
            Actionable suggestion for fixing the error
        """
        error_lower = error_details.lower()
        file_ext = file_path.suffix.lower()
        
        # Specific error pattern matching with actionable suggestions
        if 'unexpected identifier' in error_lower:
            return ("TypeScript syntax error detected. Check for missing semicolons, "
                   "incorrect type annotations, or invalid identifier names around the error location.")
        
        elif 'unexpected token' in error_lower:
            if 'authconfig' in error_lower:
                return ("AuthConfig identifier issue detected. Verify the import statement, "
                       "check if the module exports AuthConfig correctly, and ensure proper TypeScript syntax.")
            return ("Unexpected token found. Check for missing brackets, parentheses, "
                   "or incorrect operator usage.")
        
        elif 'cannot find module' in error_lower:
            return ("Module import error. Verify the import path is correct, "
                   "the module is installed, and TypeScript can resolve the import.")
        
        elif 'type' in error_lower and 'error' in error_lower:
            return ("TypeScript type error. Check type annotations, interface definitions, "
                   "and ensure all types are properly imported and defined.")
        
        elif file_ext not in ['.ts', '.tsx']:
            return (f"File extension '{file_ext}' may not be recognized as TypeScript. "
                   "Ensure the file has .ts or .tsx extension for proper TypeScript parsing.")
        
        elif 'jsx' in error_lower:
            if file_ext != '.tsx':
                return ("JSX syntax detected but file extension is not .tsx. "
                       "Rename the file to .tsx for proper JSX/TypeScript parsing.")
            return ("JSX syntax error. Check JSX element syntax, component imports, "
                   "and ensure proper TypeScript JSX configuration.")
        
        elif 'import' in error_lower or 'export' in error_lower:
            return ("ES6 module import/export error. Check import/export syntax, "
                   "verify module paths, and ensure proper TypeScript module configuration.")
        
        elif 'encoding' in error_lower or 'utf' in error_lower:
            return ("File encoding issue detected. Ensure the file is saved in UTF-8 encoding "
                   "and does not contain invalid characters.")
        
        else:
            # Generic but actionable fallback
            return ("TypeScript parsing failed. Common fixes: check syntax around the error location, "
                   "verify all imports are correct, ensure proper TypeScript configuration, "
                   "and confirm the file uses valid TypeScript syntax.")
            
    def _convert_to_analysis_result(self, file_path: Path, 
                                   parser_data: Dict[str, Any]) -> AnalysisResult:
        """Convert TypeScript parser output to standard AnalysisResult.
        
        Args:
            file_path: Path to analyzed file
            parser_data: Raw parser output
            
        Returns:
            Standardized AnalysisResult
        """
        entities = []
        issues = []
        
        # Convert entities
        for entity_data in parser_data.get('entities', []):
            entity = CodeEntity(
                entity_type=entity_data['type'],
                entity_name=entity_data['name'],
                file_path=str(file_path),
                line_start=entity_data['line_start'],
                line_end=entity_data['line_end'],
                parameters=list(range(entity_data.get('params', 0))),
                metadata={
                    'is_async': entity_data.get('async', False),
                    'is_generator': entity_data.get('generator', False),
                    'return_type': entity_data.get('returnType', False),
                    'type_params': entity_data.get('typeParams', False),
                    'is_abstract': entity_data.get('abstract', False),
                    'implements_count': entity_data.get('implements', 0)
                }
            )
            
            # Estimate complexity based on function length
            entity.complexity_score = max(1, (entity.line_end - entity.line_start) // 10)
            
            entities.append(entity)
            
            # Check for TypeScript-specific issues
            self._check_typescript_issues(entity, issues)
            
        # Add parser-detected issues
        for issue_data in parser_data.get('issues', []):
            issues.append(CodeIssue(
                issue_type=issue_data['type'],
                severity=issue_data['severity'],
                file_path=str(file_path),
                line_number=issue_data['line'],
                entity_name='',
                description=f"{issue_data['type'].replace('_', ' ').title()} detected",
                ai_recommendation=self._get_typescript_recommendation(issue_data['type']),
                fix_complexity='moderate'
            ))
            
        # Create metrics
        metrics_data = parser_data.get('metrics', {})
        metrics = CodeMetrics(
            total_lines=metrics_data.get('lines', 0),
            code_lines=int(metrics_data.get('lines', 0) * 0.8),  # Estimate
            total_entities=len(entities),
            total_functions=metrics_data.get('functions', 0),
            total_classes=metrics_data.get('classes', 0),
            average_complexity=parser_data.get('complexity', {}).get('average', 1),
            language_specific_metrics={
                'interfaces': metrics_data.get('interfaces', 0),
                'types': metrics_data.get('types', 0),
                'generics': metrics_data.get('generics', 0),
                'any_usage': metrics_data.get('anyUsage', 0),
                'strict_mode': metrics_data.get('strictMode', False),
                'type_safety_score': max(0, 100 - (metrics_data.get('anyUsage', 0) * 5)),
                'dependency_install_method': getattr(self, '_dependency_install_method', 'unknown'),
                'typescript_version': 'latest'  # Could be detected from parser
            }
        )
        
        return AnalysisResult(
            file_path=str(file_path),
            language='typescript',
            analysis_timestamp=datetime.now(),
            entities=entities,
            issues=issues,
            metrics=metrics,
            imports=[imp['source'] for imp in parser_data.get('imports', [])],
            analysis_metadata={
                'analyzer': 'TypeScriptAnalyzer',
                'version': '2.0',
                'parser': '@typescript-eslint/parser',
                'parse_success': True
            }
        )
        
    def _check_typescript_issues(self, entity: CodeEntity, issues: List[CodeIssue]):
        """Check for TypeScript-specific issues.
        
        Args:
            entity: Code entity to check
            issues: List to append issues to
        """
        # Check for missing return types
        if (entity.entity_type in ['function', 'method'] and 
            not entity.metadata.get('return_type')):
            issues.append(CodeIssue(
                issue_type='missing_return_type',
                severity='low',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description="Function lacks explicit return type annotation",
                ai_recommendation="Add explicit return type for better type safety and documentation",
                fix_complexity='simple'
            ))
            
        # Check for complex functions without type parameters
        function_length = entity.line_end - entity.line_start + 1
        if (function_length > 50 and entity.entity_type == 'function' and
            not entity.metadata.get('type_params')):
            issues.append(CodeIssue(
                issue_type='complex_function_no_generics',
                severity='medium',
                file_path=entity.file_path,
                line_number=entity.line_start,
                entity_name=entity.entity_name,
                description=f"Complex function ({function_length} lines) without generic types",
                ai_recommendation="Consider using generic types for better reusability",
                fix_complexity='moderate'
            ))
        
    def _enhance_typescript_analysis(self, result: AnalysisResult):
        """Add TypeScript-specific analysis to results.
        
        Args:
            result: Base analysis result to enhance
        """
        # Check for TypeScript-specific issues
        ts_metrics = result.metrics.language_specific_metrics
        
        # Check for excessive 'any' usage
        any_usage = ts_metrics.get('any_usage', 0)
        if any_usage > 5:
            result.issues.append(CodeIssue(
                issue_type='excessive_any_usage',
                severity='medium' if any_usage < 10 else 'high',
                file_path=result.file_path,
                line_number=1,
                entity_name='file',
                description=f"File uses 'any' type {any_usage} times",
                ai_recommendation="Replace 'any' with specific types or 'unknown' for better type safety",
                fix_complexity='moderate',
                metadata={'any_count': any_usage}
            ))
            
        # Check for missing return types
        functions_without_types = sum(
            1 for e in result.entities 
            if e.entity_type in ['function', 'method'] 
            and not e.metadata.get('returnType')
        )
        
        if functions_without_types > 3:
            result.issues.append(CodeIssue(
                issue_type='missing_return_types',
                severity='low',
                file_path=result.file_path,
                line_number=1,
                entity_name='file',
                description=f"{functions_without_types} functions lack explicit return types",
                ai_recommendation="Add explicit return type annotations for better type safety and documentation",
                fix_complexity='simple'
            ))
            
        # Check for interface vs type alias usage
        interfaces = ts_metrics.get('interfaces', 0)
        types = ts_metrics.get('types', 0)
        
        if interfaces == 0 and types > 5:
            result.issues.append(CodeIssue(
                issue_type='prefer_interfaces',
                severity='low',
                file_path=result.file_path,
                line_number=1,
                entity_name='file',
                description="Consider using interfaces instead of type aliases for object types",
                ai_recommendation="Interfaces provide better error messages and extend capabilities",
                fix_complexity='simple'
            ))
            
        # Update metrics with TypeScript-specific data
        result.metrics.language_specific_metrics.update({
            'type_safety_score': ts_metrics.get('typeSafetyScore', 100),
            'strict_mode': ts_metrics.get('strictMode', False),
            'uses_generics': ts_metrics.get('generics', 0) > 0,
            'interface_count': interfaces,
            'type_alias_count': types
        })
        
    def _get_typescript_recommendation(self, issue_type: str) -> str:
        """Get TypeScript-specific recommendations.
        
        Args:
            issue_type: Type of issue
            
        Returns:
            Strategic recommendation for AI
        """
        recommendations = {
            'any_type_usage': "Replace 'any' with specific types, 'unknown', or generic constraints",
            'missing_return_types': "Add explicit return type annotations for public APIs",
            'no_explicit_any': "Enable 'noImplicitAny' in tsconfig.json for stricter typing",
            'excessive_type_assertions': "Reduce type assertions; use type guards instead",
            'missing_null_checks': "Enable 'strictNullChecks' for null safety"
        }
        
        return recommendations.get(
            issue_type,
            super()._get_js_recommendation(issue_type)
        )
        
    def _cleanup_file(self, file_path: str):
        """Safely clean up temporary file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    def __del__(self):
        """Clean up temporary parser script."""
        if hasattr(self, 'parser_script'):
            self._cleanup_file(self.parser_script)