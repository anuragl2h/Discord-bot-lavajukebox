"""
Flask Web Server for Discord Music Bot
Provides web interface and API endpoints for bot control.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import asyncio
import threading
import logging
import os
from bot import MusicBot
from config import Config
import wavelink
import discord

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Global bot instance
bot_instance = None
bot_thread = None
bot_running = False

def run_bot():
    """Run the Discord bot in a separate thread."""
    global bot_instance, bot_running
    
    async def start_bot():
        global bot_instance, bot_running
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logging.error("DISCORD_TOKEN not set!")
            return
            
        bot_instance = MusicBot()
        bot_running = True
        
        try:
            await bot_instance.start(token)
        except Exception as e:
            logging.error(f"Bot error: {e}")
            bot_running = False
    
    # Run the bot
    asyncio.run(start_bot())

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/bot/status')
def bot_status():
    """Get bot status information."""
    global bot_instance, bot_running
    
    if not bot_instance or not bot_running:
        return jsonify({
            'status': 'offline',
            'connected': False,
            'guilds': 0,
            'nodes': 0,
            'players': 0
        })
    
    try:
        # Get Wavelink node information
        nodes = wavelink.Pool.nodes
        connected_nodes = [node for node in nodes.values() if node.status is wavelink.NodeStatus.CONNECTED]
        
        # Get active players
        active_players = 0
        for guild in bot_instance.guilds:
            player = guild.voice_client
            if player and hasattr(player, 'playing') and player.playing:
                active_players += 1
        
        return jsonify({
            'status': 'online',
            'connected': True,
            'bot_name': str(bot_instance.user) if bot_instance.user else 'Unknown',
            'guilds': len(bot_instance.guilds),
            'nodes': len(connected_nodes),
            'total_nodes': len(nodes),
            'active_players': active_players,
            'lavalink_host': Config.LAVALINK_HOST,
            'command_prefix': Config.COMMAND_PREFIX
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'connected': False
        })

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the Discord bot."""
    global bot_thread, bot_running
    
    if bot_running:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        return jsonify({'success': True, 'message': 'Bot starting...'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to start bot: {e}'})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the Discord bot."""
    global bot_instance, bot_running
    
    if not bot_running:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        if bot_instance:
            asyncio.create_task(bot_instance.close())
        bot_running = False
        return jsonify({'success': True, 'message': 'Bot stopping...'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to stop bot: {e}'})

@app.route('/api/guilds')
def get_guilds():
    """Get list of guilds bot is in."""
    global bot_instance
    
    if not bot_instance:
        return jsonify([])
    
    try:
        guilds = []
        for guild in bot_instance.guilds:
            player = guild.voice_client
            guilds.append({
                'id': guild.id,
                'name': guild.name,
                'member_count': guild.member_count,
                'voice_connected': player is not None,
                'playing': player.playing if player and hasattr(player, 'playing') else False,
                'current_track': str(player.current) if player and hasattr(player, 'current') and player.current else None
            })
        return jsonify(guilds)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/config')
def get_config():
    """Get bot configuration."""
    return jsonify({
        'command_prefix': Config.COMMAND_PREFIX,
        'lavalink_host': Config.LAVALINK_HOST,
        'lavalink_port': Config.LAVALINK_PORT,
        'max_queue_size': Config.MAX_QUEUE_SIZE,
        'default_volume': Config.DEFAULT_VOLUME
    })

@app.route('/docs')
def documentation():
    """Bot documentation page."""
    return render_template('docs.html')

@app.route('/logs')
def logs():
    """View bot logs."""
    try:
        with open('bot.log', 'r') as f:
            log_content = f.read().split('\n')[-100:]  # Last 100 lines
        return render_template('logs.html', logs=log_content)
    except FileNotFoundError:
        return render_template('logs.html', logs=['No log file found'])

@app.route('/ping')
def ping():
    """Simple ping endpoint for uptime monitoring."""
    import time
    return jsonify({
        'status': 'alive',
        'timestamp': int(time.time()),
        'bot_connected': bot_instance and bot_running,
        'message': 'Discord Music Bot is running'
    })

@app.route('/health')
def health():
    """Health check endpoint with detailed status."""
    global bot_instance, bot_running
    
    import time
    health_status = {
        'status': 'healthy' if bot_running else 'unhealthy',
        'timestamp': int(time.time()),
        'services': {
            'flask': 'running',
            'discord_bot': 'connected' if (bot_instance and bot_running) else 'disconnected',
            'wavelink': 'unknown'
        }
    }
    
    # Check Wavelink status if bot is running
    if bot_instance and bot_running:
        try:
            nodes = wavelink.Pool.nodes
            connected_nodes = [node for node in nodes.values() if node.status is wavelink.NodeStatus.CONNECTED]
            health_status['services']['wavelink'] = 'connected' if connected_nodes else 'disconnected'
            health_status['nodes'] = len(connected_nodes)
        except:
            health_status['services']['wavelink'] = 'error'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/uptime-guide')
def uptime_guide():
    """Show uptime monitoring setup guide."""
    return render_template('uptime.html')

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # Auto-start bot if token is available
    if os.getenv("DISCORD_TOKEN"):
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)