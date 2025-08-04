"""
Setup utilities for NIA MCP Server configuration
"""
import os
import json
import platform
import shutil
from pathlib import Path
from typing import Dict, Optional, Any


def find_mcp_config_path(ide: str = "cursor") -> Path:
    """
    Find the MCP configuration file path based on OS and IDE.
    
    Args:
        ide: IDE to configure (cursor, vscode, continue)
    
    Returns:
        Path to the MCP configuration file
    """
    system = platform.system()
    home = Path.home()
    
    if ide == "cursor":
        if system == "Darwin":  # macOS
            return home / ".cursor" / "mcp.json"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA", home / "AppData" / "Roaming")
            return Path(appdata) / "Cursor" / "mcp.json"
        else:  # Linux and others
            return home / ".config" / "cursor" / "mcp.json"
    
    elif ide == "vscode":
        # VS Code uses different config locations
        if system == "Darwin":
            return home / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA", home / "AppData" / "Roaming")
            return Path(appdata) / "Code" / "User" / "mcp.json"
        else:
            return home / ".config" / "Code" / "User" / "mcp.json"
    
    elif ide == "continue":
        # Continue.dev uses .continue directory
        return home / ".continue" / "config.json"
    
    else:
        raise ValueError(f"Unsupported IDE: {ide}")


def backup_config(config_path: Path) -> Optional[Path]:
    """
    Create a backup of existing configuration file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Path to the backup file if created, None otherwise
    """
    if config_path.exists():
        backup_path = config_path.with_suffix(".json.backup")
        # If backup already exists, add timestamp
        if backup_path.exists():
            import time
            timestamp = int(time.time())
            backup_path = config_path.with_suffix(f".json.backup.{timestamp}")
        
        shutil.copy2(config_path, backup_path)
        return backup_path
    return None


def create_nia_config(api_key: str) -> Dict[str, Any]:
    """
    Create NIA MCP server configuration.
    
    Args:
        api_key: NIA API key
    
    Returns:
        Dictionary with NIA server configuration
    """
    return {
        "command": "pipx",
        "args": ["run", "nia-mcp-server"],
        "env": {
            "NIA_API_KEY": api_key,
            "NIA_API_URL": "https://apigcp.trynia.ai/"
        }
    }


def update_mcp_config(config_path: Path, api_key: str) -> bool:
    """
    Update or create MCP configuration file with NIA server.
    
    Args:
        config_path: Path to the MCP configuration file
        api_key: NIA API key
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config or create new one
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add or update NIA server configuration
        config["mcpServers"]["nia"] = create_nia_config(api_key)
        
        # Write updated configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False


def setup_mcp_config(api_key: str, ide: str = "cursor") -> bool:
    """
    Main setup function to configure NIA MCP Server.
    
    Args:
        api_key: NIA API key
        ide: IDE to configure
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n🚀 Setting up NIA MCP Server for {ide.title()}...\n")
    
    # Find config path
    config_path = find_mcp_config_path(ide)
    print(f"📍 Configuration path: {config_path}")
    
    # Backup existing config
    backup_path = backup_config(config_path)
    if backup_path:
        print(f"📦 Backed up existing config to: {backup_path}")
    
    # Update configuration
    if update_mcp_config(config_path, api_key):
        print(f"\n✅ NIA MCP Server setup complete!")
        print(f"\n📝 Configuration written to: {config_path}")
        print(f"🔑 API Key: {api_key[:10]}...")
        
        print("\n📌 Next steps:")
        print(f"   1. Restart {ide.title()} to load the NIA MCP server")
        print(f"   2. Test with: \"Claude, list my repositories\"")
        print(f"   3. Get started: \"Claude, index https://github.com/owner/repo\"")
        
        print("\n💡 Learn more:")
        print("   - Documentation: https://docs.trynia.ai")
        print("   - Get help: https://discord.gg/BBSwUMrrfn")
        
        return True
    else:
        print(f"\n❌ Setup failed. Please check the error messages above.")
        if backup_path:
            print(f"   Your original config is safe at: {backup_path}")
        return False