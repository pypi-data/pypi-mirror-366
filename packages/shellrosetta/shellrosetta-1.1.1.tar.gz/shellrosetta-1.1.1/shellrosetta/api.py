# shellrosetta/api.py

try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    request = None
    jsonify = None
    render_template_string = None
    CORS = None

import os
import sys
from typing import Dict, Any, Optional
from .core import lnx2ps, ps2lnx
from .ml_engine import ml_engine
from .plugins import plugin_manager
from .config import config

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShellRosetta - Command Translator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .input-section {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }
        .input-group {
            flex: 1;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .result {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .suggestions {
            margin-top: 20px;
        }
        .suggestion {
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 4px;
            padding: 8px 12px;
            margin: 4px 0;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .suggestion:hover {
            background: #bbdefb;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 ShellRosetta Command Translator</h1>
        
        <div class="input-section">
            <div class="input-group">
                <label for="direction">Translation Direction:</label>
                <select id="direction">
                    <option value="lnx2ps">Linux → PowerShell</option>
                    <option value="ps2lnx">PowerShell → Linux</option>
                </select>
            </div>
            <div class="input-group">
                <label for="command">Command:</label>
                <input type="text" id="command" placeholder="Enter your command here...">
            </div>
            <div class="input-group">
                <label>&nbsp;</label>
                <button onclick="translate()">Translate</button>
            </div>
        </div>
        
        <div id="result" class="result" style="display: none;"></div>
        <div id="suggestions" class="suggestions"></div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalTranslations">0</div>
                <div class="stat-label">Total Translations</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="successRate">0%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="learnedPatterns">0</div>
                <div class="stat-label">Learned Patterns</div>
            </div>
        </div>
    </div>

    <script>
        async function translate() {
            const command = document.getElementById('command').value;
            const direction = document.getElementById('direction').value;
            
            if (!command.trim()) {
                alert('Please enter a command');
                return;
            }
            
            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        command: command,
                        direction: direction
                    })
                });
                
                const data = await response.json();
                
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.textContent = data.translation;
                
                // Show suggestions if available
                if (data.suggestions && data.suggestions.length > 0) {
                    const suggestionsDiv = document.getElementById('suggestions');
                    suggestionsDiv.innerHTML = '<h3>Suggestions:</h3>';
                    data.suggestions.forEach(suggestion => {
                        const div = document.createElement('div');
                        div.className = 'suggestion';
                        div.textContent = suggestion;
                        div.onclick = () => {
                            document.getElementById('command').value = suggestion;
                        };
                        suggestionsDiv.appendChild(div);
                    });
                }
                
                // Update stats
                updateStats();
                
            } catch (error) {
                console.error('Error:', error);
                alert('Translation failed. Please try again.');
            }
        }
        
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('totalTranslations').textContent = data.total_translations || 0;
                document.getElementById('successRate').textContent = 
                    Math.round((data.success_rate || 0) * 100) + '%';
                document.getElementById('learnedPatterns').textContent = data.learned_patterns || 0;
            } catch (error) {
                console.error('Error fetching stats:', error);
            }
        }
        
        // Load stats on page load
        updateStats();
        
        // Allow Enter key to trigger translation
        document.getElementById('command').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                translate();
            }
        });
    </script>
</body>
</html>
"""

def run_api_server(host='0.0.0.0', port=5000, debug=False):
    """Run the API server"""
    if not FLASK_AVAILABLE:
        print("Error: Flask is not installed. Install it with: pip install flask flask-cors")
        return
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    @app.route('/')
    def index():
        """Serve the web interface"""
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/translate', methods=['POST'])
    def translate_command():
        """Translate a command via API"""
        try:
            data = request.get_json()
            command = data.get('command', '').strip()
            direction = data.get('direction', 'lnx2ps')
            
            if not command:
                return jsonify({'error': 'No command provided'}), 400
            
            # Try plugin translation first
            plugin_translation = plugin_manager.translate_with_plugins(command, direction)
            
            # Try ML translation
            ml_translation = ml_engine.get_best_translation(command, direction)
            
            # Use core translation
            if direction == 'lnx2ps':
                translation = lnx2ps(command)
            else:
                translation = ps2lnx(command)
            
            # Prefer plugin translation, then ML, then core
            if plugin_translation:
                final_translation = plugin_translation
                source = 'plugin'
            elif ml_translation:
                final_translation = ml_translation
                source = 'ml'
            else:
                final_translation = translation
                source = 'core'
            
            # Learn the pattern
            ml_engine.learn_pattern(command, final_translation, direction, success=True)
            
            # Get suggestions
            suggestions = ml_engine.get_suggestions(command, direction, limit=3)
            suggestion_texts = [s[0] for s in suggestions]
            
            return jsonify({
                'translation': final_translation,
                'source': source,
                'suggestions': suggestion_texts,
                'command': command,
                'direction': direction
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/stats')
    def get_stats():
        """Get translation statistics"""
        try:
            analysis = ml_engine.analyze_patterns()
            
            return jsonify({
                'total_translations': analysis.get('total_patterns', 0),
                'success_rate': analysis.get('success_rate', 0),
                'learned_patterns': analysis.get('total_patterns', 0),
                'command_types': analysis.get('command_types', {}),
                'top_patterns': analysis.get('top_successful_patterns', [])
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/plugins')
    def list_plugins():
        """List available plugins"""
        try:
            plugins = plugin_manager.list_plugins()
            return jsonify({'plugins': plugins})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/plugins/<plugin_name>')
    def get_plugin_info(plugin_name):
        """Get information about a specific plugin"""
        try:
            if plugin_name in plugin_manager.plugins:
                plugin = plugin_manager.plugins[plugin_name]
                return jsonify(plugin.get_metadata())
            else:
                return jsonify({'error': 'Plugin not found'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/learn', methods=['POST'])
    def learn_pattern():
        """Manually learn a pattern"""
        try:
            data = request.get_json()
            command = data.get('command')
            translation = data.get('translation')
            direction = data.get('direction')
            success = data.get('success', True)
            
            if not all([command, translation, direction]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            ml_engine.learn_pattern(command, translation, direction, success)
            return jsonify({'message': 'Pattern learned successfully'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/cleanup', methods=['POST'])
    def cleanup_patterns():
        """Clean up old patterns"""
        try:
            data = request.get_json()
            days = data.get('days', 30)
            
            ml_engine.cleanup_old_patterns(days)
            return jsonify({'message': f'Cleaned up patterns older than {days} days'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    print(f"Starting ShellRosetta API server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api_server() 