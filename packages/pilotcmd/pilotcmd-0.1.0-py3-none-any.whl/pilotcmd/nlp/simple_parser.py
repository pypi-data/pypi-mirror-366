"""
Simple fallback parser for when AI models are not available.
"""

from typing import List, Dict, Any
import re

from pilotcmd.os_utils.detector import OSInfo


class SafetyLevel:
    """Simple safety level constants."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"


class Command:
    """Simple command class for fallback parser."""
    def __init__(self, command: str, explanation: str, safety_level: str = "safe", requires_sudo: bool = False):
        self.command = command
        self.explanation = explanation
        self.safety_level = safety_level
        self.requires_sudo = requires_sudo


class SimpleParser:
    """Simple pattern-based parser as fallback when AI models fail."""
    
    def __init__(self, os_info: OSInfo):
        self.os_info = os_info
        self.patterns = self._get_patterns()
    
    async def parse(self, prompt: str) -> List[Command]:
        """Parse prompt using simple pattern matching."""
        prompt_lower = prompt.lower().strip()
        commands = []
        
        # Try each pattern
        for pattern_info in self.patterns:
            if self._matches_pattern(prompt_lower, pattern_info):
                cmd = self._generate_command(prompt, pattern_info)
                if cmd:
                    commands.append(cmd)
                    break
        
        # If no pattern matches, return empty list
        return commands
    
    def _matches_pattern(self, prompt: str, pattern_info: Dict[str, Any]) -> bool:
        """Check if prompt matches a pattern."""
        keywords = pattern_info.get('keywords', [])
        return any(keyword in prompt for keyword in keywords)
    
    def _generate_command(self, prompt: str, pattern_info: Dict[str, Any]) -> Command:
        """Generate command from pattern."""
        if self.os_info.is_windows():
            cmd = pattern_info.get('windows', '')
        elif self.os_info.is_macos():
            cmd = pattern_info.get('macos', pattern_info.get('unix', ''))
        else:  # Linux
            cmd = pattern_info.get('linux', pattern_info.get('unix', ''))
        
        if not cmd:
            return None
        
        # Simple parameter extraction
        cmd = self._extract_parameters(prompt, cmd)
        
        return Command(
            command=cmd,
            explanation=pattern_info.get('explanation', f"Execute: {cmd}"),
            safety_level=pattern_info.get('safety', 'safe'),
            requires_sudo=pattern_info.get('requires_sudo', False)
        )
    
    def _extract_parameters(self, prompt: str, cmd_template: str) -> str:
        """Extract parameters from prompt and substitute in command template."""
        # Simple parameter extraction
        if '{file}' in cmd_template:
            # Try to find file names in prompt
            words = prompt.split()
            for word in words:
                if '.' in word and not word.startswith('.'):
                    cmd_template = cmd_template.replace('{file}', word)
                    break
            else:
                cmd_template = cmd_template.replace('{file}', '*')
        
        if '{target}' in cmd_template:
            # Try to find IP addresses or hostnames
            words = prompt.split()
            for word in words:
                if '.' in word and not word.startswith('.'):
                    cmd_template = cmd_template.replace('{target}', word)
                    break
            else:
                cmd_template = cmd_template.replace('{target}', 'google.com')
        
        return cmd_template
    
    def _get_patterns(self) -> List[Dict[str, Any]]:
        """Get list of command patterns."""
        return [
            {
                'keywords': ['time', 'current time', 'show time', 'what time'],
                'explanation': 'Show current time',
                'windows': 'time /t',
                'unix': 'date',
                'safety': 'safe'
            },
            {
                'keywords': ['list', 'show', 'files', 'directory', 'folder'],
                'explanation': 'List directory contents',
                'windows': 'dir',
                'unix': 'ls -la',
                'safety': 'safe'
            },
            {
                'keywords': ['current', 'directory', 'where am i', 'pwd'],
                'explanation': 'Show current directory',
                'windows': 'cd',
                'unix': 'pwd',
                'safety': 'safe'
            },
            {
                'keywords': ['ping'],
                'explanation': 'Ping a host',
                'windows': 'ping {target}',
                'unix': 'ping -c 4 {target}',
                'safety': 'safe'
            },
            {
                'keywords': ['python', 'files', 'find'],
                'explanation': 'Find Python files',
                'windows': 'dir *.py /s',
                'unix': 'find . -name "*.py"',
                'safety': 'safe'
            },
            {
                'keywords': ['disk', 'space', 'usage', 'free'],
                'explanation': 'Show disk usage',
                'windows': 'dir /-c',
                'unix': 'df -h',
                'safety': 'safe'
            },
            {
                'keywords': ['process', 'running', 'task'],
                'explanation': 'List running processes',
                'windows': 'tasklist',
                'unix': 'ps aux',
                'safety': 'safe'
            },
            {
                'keywords': ['ip', 'address', 'network'],
                'explanation': 'Show IP configuration',
                'windows': 'ipconfig',
                'unix': 'ip addr show',
                'safety': 'safe'
            },
            {
                'keywords': ['system', 'info', 'information'],
                'explanation': 'Show system information',
                'windows': 'systeminfo',
                'unix': 'uname -a',
                'safety': 'safe'
            },
            {
                'keywords': ['create', 'mkdir', 'folder', 'directory'],
                'explanation': 'Create directory',
                'windows': 'mkdir test_folder',
                'unix': 'mkdir test_folder',
                'safety': 'safe'
            },
            {
                'keywords': ['copy', 'cp'],
                'explanation': 'Copy files',
                'windows': 'copy {file} backup_{file}',
                'unix': 'cp {file} backup_{file}',
                'safety': 'caution'
            }
        ]
