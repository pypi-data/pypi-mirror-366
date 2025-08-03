# shellrosetta/ml_engine.py

import json
import pickle
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
import re
from datetime import datetime, timedelta

class CommandPattern:
    """Represents a learned command pattern"""
    
    def __init__(self, command: str, translation: str, direction: str, 
                 success_count: int = 0, failure_count: int = 0):
        self.command = command
        self.translation = translation
        self.direction = direction
        self.success_count = success_count
        self.failure_count = failure_count
        self.last_used = datetime.now()
        self.created = datetime.now()
    
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    def record_success(self):
        """Record a successful translation"""
        self.success_count += 1
        self.last_used = datetime.now()
    
    def record_failure(self):
        """Record a failed translation"""
        self.failure_count += 1
        self.last_used = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'command': self.command,
            'translation': self.translation,
            'direction': self.direction,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_used': self.last_used.isoformat(),
            'created': self.created.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandPattern':
        """Create from dictionary"""
        pattern = cls(
            data['command'],
            data['translation'],
            data['direction'],
            data['success_count'],
            data['failure_count']
        )
        pattern.last_used = datetime.fromisoformat(data['last_used'])
        pattern.created = datetime.fromisoformat(data['created'])
        return pattern

class MLEngine:
    """Machine learning engine for command translation"""
    
    def __init__(self):
        self.data_dir = Path.home() / ".shellrosetta" / "ml"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.data_dir / "patterns.json"
        self.context_file = self.data_dir / "context.json"
        self.suggestions_file = self.data_dir / "suggestions.json"
        
        self.patterns: Dict[str, CommandPattern] = {}
        self.context_history: List[Dict[str, Any]] = []
        self.suggestion_cache: Dict[str, List[str]] = {}
        
        self.load_data()
    
    def load_data(self):
        """Load learned patterns and context"""
        # Load patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    for key, pattern_data in data.items():
                        self.patterns[key] = CommandPattern.from_dict(pattern_data)
            except Exception as e:
                print(f"Failed to load patterns: {e}")
        
        # Load context history
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    self.context_history = json.load(f)
            except Exception as e:
                print(f"Failed to load context: {e}")
        
        # Load suggestions
        if self.suggestions_file.exists():
            try:
                with open(self.suggestions_file, 'r') as f:
                    self.suggestion_cache = json.load(f)
            except Exception as e:
                print(f"Failed to load suggestions: {e}")
    
    def save_data(self):
        """Save learned patterns and context"""
        # Save patterns
        patterns_data = {}
        for key, pattern in self.patterns.items():
            patterns_data[key] = pattern.to_dict()
        
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save patterns: {e}")
        
        # Save context (keep only last 1000 entries)
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.context_history[-1000:], f, indent=2)
        except Exception as e:
            print(f"Failed to save context: {e}")
        
        # Save suggestions
        try:
            with open(self.suggestions_file, 'w') as f:
                json.dump(self.suggestion_cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save suggestions: {e}")
    
    def learn_pattern(self, command: str, translation: str, direction: str, 
                     success: bool = True):
        """Learn a new command pattern"""
        key = f"{direction}:{command}"
        
        if key in self.patterns:
            pattern = self.patterns[key]
            if success:
                pattern.record_success()
            else:
                pattern.record_failure()
        else:
            pattern = CommandPattern(command, translation, direction)
            if success:
                pattern.record_success()
            else:
                pattern.record_failure()
            self.patterns[key] = pattern
        
        # Update context
        self._update_context(command, translation, direction, success)
        
        # Save data periodically
        if len(self.patterns) % 10 == 0:
            self.save_data()
    
    def _update_context(self, command: str, translation: str, direction: str, success: bool):
        """Update context history"""
        context_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'translation': translation,
            'direction': direction,
            'success': success,
            'command_type': self._classify_command(command)
        }
        self.context_history.append(context_entry)
    
    def _classify_command(self, command: str) -> str:
        """Classify command type"""
        if 'ls' in command or 'dir' in command:
            return 'file_listing'
        elif 'grep' in command or 'find' in command:
            return 'search'
        elif 'cp' in command or 'mv' in command:
            return 'file_operation'
        elif 'docker' in command:
            return 'container'
        elif 'git' in command:
            return 'version_control'
        else:
            return 'general'
    
    def get_suggestions(self, partial_command: str, direction: str, 
                       limit: int = 5) -> List[Tuple[str, float]]:
        """Get suggestions for a partial command"""
        suggestions = []
        
        # Look for exact matches in learned patterns
        for key, pattern in self.patterns.items():
            if key.startswith(f"{direction}:") and pattern.command.startswith(partial_command):
                success_rate = pattern.get_success_rate()
                suggestions.append((pattern.translation, success_rate))
        
        # Look for similar patterns
        for key, pattern in self.patterns.items():
            if key.startswith(f"{direction}:") and self._similar_commands(partial_command, pattern.command):
                success_rate = pattern.get_success_rate()
                suggestions.append((pattern.translation, success_rate * 0.8))  # Lower confidence
        
        # Sort by confidence and return top results
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:limit]
    
    def _similar_commands(self, cmd1: str, cmd2: str) -> bool:
        """Check if two commands are similar"""
        # Simple similarity check - can be improved with more sophisticated algorithms
        words1 = set(cmd1.split())
        words2 = set(cmd2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) > 0.5
    
    def get_best_translation(self, command: str, direction: str) -> Optional[str]:
        """Get the best learned translation for a command"""
        key = f"{direction}:{command}"
        
        if key in self.patterns:
            pattern = self.patterns[key]
            if pattern.get_success_rate() > 0.5:  # Only use if success rate > 50%
                return pattern.translation
        
        return None
    
    def get_context_suggestions(self, current_command: str, direction: str) -> List[str]:
        """Get suggestions based on recent context"""
        if not self.context_history:
            return []
        
        # Get recent commands of similar type
        current_type = self._classify_command(current_command)
        recent_commands = []
        
        for entry in self.context_history[-50:]:  # Last 50 entries
            if entry['direction'] == direction and entry['success']:
                recent_commands.append(entry['translation'])
        
        # Return most common recent translations
        counter = Counter(recent_commands)
        return [cmd for cmd, _ in counter.most_common(3)]
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze learned patterns for insights"""
        if not self.patterns:
            return {}
        
        total_patterns = len(self.patterns)
        successful_patterns = sum(1 for p in self.patterns.values() if p.get_success_rate() > 0.5)
        
        # Most common command types
        command_types = Counter()
        for pattern in self.patterns.values():
            command_types[self._classify_command(pattern.command)] += 1
        
        # Most successful patterns
        successful_patterns_list = [
            (p.command, p.get_success_rate()) 
            for p in self.patterns.values() 
            if p.get_success_rate() > 0.7
        ]
        successful_patterns_list.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'total_patterns': total_patterns,
            'successful_patterns': successful_patterns,
            'success_rate': successful_patterns / total_patterns if total_patterns > 0 else 0,
            'command_types': dict(command_types),
            'top_successful_patterns': successful_patterns_list[:10]
        }
    
    def cleanup_old_patterns(self, days: int = 30):
        """Remove patterns that haven't been used recently"""
        cutoff_date = datetime.now() - timedelta(days=days)
        keys_to_remove = []
        
        for key, pattern in self.patterns.items():
            if pattern.last_used < cutoff_date and pattern.get_success_rate() < 0.3:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.patterns[key]
        
        if keys_to_remove:
            self.save_data()

# Global ML engine instance
ml_engine = MLEngine() 