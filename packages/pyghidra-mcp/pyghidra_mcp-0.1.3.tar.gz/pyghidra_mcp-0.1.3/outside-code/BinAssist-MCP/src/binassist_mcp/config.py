"""
Configuration management for BinAssist-MCP

This module provides configuration management using Pydantic settings with
Binary Ninja integration for persistent storage.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class TransportType(str, Enum):
    """Available transport types for the MCP server"""
    SSE = "sse"
    STDIO = "stdio"  
    BOTH = "both"


class LogLevel(str, Enum):
    """Available logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ServerConfig(BaseModel):
    """Server-specific configuration"""
    host: str = Field(default="localhost", description="Server host address")
    port: int = Field(default=9090, ge=1024, le=65535, description="Server port")
    transport: TransportType = Field(default=TransportType.BOTH, description="Transport type")
    max_connections: int = Field(default=100, ge=1, description="Maximum concurrent connections")
    
    @validator("host")
    def validate_host(cls, v):
        """Validate host address"""
        if not v or not isinstance(v, str):
            raise ValueError("Host must be a non-empty string")
        return v.strip()


class BinaryConfig(BaseModel):
    """Binary analysis configuration"""
    max_binaries: int = Field(default=10, ge=1, le=50, description="Maximum concurrent binaries")
    auto_analysis: bool = Field(default=True, description="Enable automatic analysis")
    analysis_timeout: int = Field(default=300, ge=30, description="Analysis timeout in seconds")
    cache_results: bool = Field(default=True, description="Cache analysis results")


class PluginConfig(BaseModel):
    """Binary Ninja plugin configuration"""
    auto_startup: bool = Field(default=True, description="Auto-start server on file load")
    show_notifications: bool = Field(default=True, description="Show status notifications")
    menu_integration: bool = Field(default=True, description="Enable menu integration")


class BinAssistMCPConfig(BaseSettings):
    """Main configuration class for BinAssist-MCP"""
    
    # Core settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Server configuration
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    # Binary analysis configuration  
    binary: BinaryConfig = Field(default_factory=BinaryConfig)
    
    # Plugin configuration
    plugin: PluginConfig = Field(default_factory=PluginConfig)
    
    class Config:
        env_prefix = "BINASSISTMCP_"
        env_nested_delimiter = "__"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.log_level.value),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            force=True
        )
        
        if self.debug:
            logging.getLogger("binassist_mcp").setLevel(logging.DEBUG)
            
    def update_from_binja_settings(self, settings_manager=None):
        """Update configuration from Binary Ninja settings"""
        if not settings_manager:
            try:
                import binaryninja as bn
                settings_manager = bn.Settings()
            except ImportError:
                logger.warning("Binary Ninja not available, using default settings")
                return
                
        try:
            # Server settings
            if settings_manager.contains("binassist.server.host"):
                self.server.host = settings_manager.get_string("binassist.server.host")
            if settings_manager.contains("binassist.server.port"):
                self.server.port = settings_manager.get_integer("binassist.server.port")
            if settings_manager.contains("binassist.server.transport"):
                transport_str = settings_manager.get_string("binassist.server.transport")
                try:
                    self.server.transport = TransportType(transport_str)
                except ValueError:
                    logger.warning(f"Invalid transport type: {transport_str}")
                    
            # Plugin settings
            if settings_manager.contains("binassist.plugin.auto_startup"):
                self.plugin.auto_startup = settings_manager.get_bool("binassist.plugin.auto_startup")
            if settings_manager.contains("binassist.plugin.show_notifications"):
                self.plugin.show_notifications = settings_manager.get_bool("binassist.plugin.show_notifications")
                
            # Binary settings
            if settings_manager.contains("binassist.binary.max_binaries"):
                self.binary.max_binaries = settings_manager.get_integer("binassist.binary.max_binaries")
            if settings_manager.contains("binassist.binary.auto_analysis"):
                self.binary.auto_analysis = settings_manager.get_bool("binassist.binary.auto_analysis")
                
            logger.info("Configuration updated from Binary Ninja settings")
            
        except Exception as e:
            logger.error(f"Failed to load Binary Ninja settings: {e}")
            
    def save_to_binja_settings(self, settings_manager=None):
        """Save configuration to Binary Ninja settings"""
        if not settings_manager:
            try:
                import binaryninja as bn
                settings_manager = bn.Settings()
            except ImportError:
                logger.warning("Binary Ninja not available, cannot save settings")
                return
                
        try:
            # Register settings if they don't exist
            self._register_binja_settings(settings_manager)
            
            # Save current values
            settings_manager.set_string("binassist.server.host", self.server.host)
            settings_manager.set_integer("binassist.server.port", self.server.port)
            settings_manager.set_string("binassist.server.transport", self.server.transport.value)
            settings_manager.set_bool("binassist.plugin.auto_startup", self.plugin.auto_startup)
            settings_manager.set_bool("binassist.plugin.show_notifications", self.plugin.show_notifications)
            settings_manager.set_integer("binassist.binary.max_binaries", self.binary.max_binaries)
            settings_manager.set_bool("binassist.binary.auto_analysis", self.binary.auto_analysis)
            
            logger.info("Configuration saved to Binary Ninja settings")
            
        except Exception as e:
            logger.error(f"Failed to save Binary Ninja settings: {e}")
            
    def _register_binja_settings(self, settings_manager):
        """Register settings with Binary Ninja if not already registered"""
        try:
            import binaryninja as bn
            
            # Server settings
            if not settings_manager.contains("binassist.server.host"):
                settings_manager.register_setting(
                    "binassist.server.host",
                    '{"description": "BinAssist-MCP server host address", "title": "Server Host", "default": "localhost", "type": "string"}'
                )
            if not settings_manager.contains("binassist.server.port"):
                settings_manager.register_setting(
                    "binassist.server.port", 
                    '{"description": "BinAssist-MCP server port", "title": "Server Port", "default": 8000, "type": "number", "minValue": 1024, "maxValue": 65535}'
                )
            if not settings_manager.contains("binassist.server.transport"):
                settings_manager.register_setting(
                    "binassist.server.transport",
                    '{"description": "MCP transport type", "title": "Transport Type", "default": "both", "type": "string", "enum": ["sse", "stdio", "both"]}'
                )
                
            # Plugin settings
            if not settings_manager.contains("binassist.plugin.auto_startup"):
                settings_manager.register_setting(
                    "binassist.plugin.auto_startup",
                    '{"description": "Automatically start server when Binary Ninja loads a file", "title": "Auto Startup", "default": true, "type": "boolean"}'
                )
            if not settings_manager.contains("binassist.plugin.show_notifications"):
                settings_manager.register_setting(
                    "binassist.plugin.show_notifications",
                    '{"description": "Show status notifications", "title": "Show Notifications", "default": true, "type": "boolean"}'
                )
                
            # Binary settings
            if not settings_manager.contains("binassist.binary.max_binaries"):
                settings_manager.register_setting(
                    "binassist.binary.max_binaries",
                    '{"description": "Maximum number of concurrent binaries", "title": "Max Binaries", "default": 10, "type": "number", "minValue": 1, "maxValue": 50}'
                )
            if not settings_manager.contains("binassist.binary.auto_analysis"):
                settings_manager.register_setting(
                    "binassist.binary.auto_analysis",
                    '{"description": "Enable automatic binary analysis", "title": "Auto Analysis", "default": true, "type": "boolean"}'
                )
                
        except Exception as e:
            logger.error(f"Failed to register Binary Ninja settings: {e}")
            
    def get_server_url(self) -> str:
        """Get the server URL for SSE connections"""
        return f"http://{self.server.host}:{self.server.port}"
        
    def get_sse_url(self) -> str:
        """Get the SSE endpoint URL"""
        return f"{self.get_server_url()}/sse"
        
    def is_transport_enabled(self, transport: TransportType) -> bool:
        """Check if a specific transport is enabled"""
        if self.server.transport == TransportType.BOTH:
            return True
        return self.server.transport == transport
        
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate server configuration
        if self.server.port < 1024 or self.server.port > 65535:
            errors.append("Server port must be between 1024 and 65535")
            
        if not self.server.host.strip():
            errors.append("Server host cannot be empty")
            
        # Validate binary configuration
        if self.binary.max_binaries < 1 or self.binary.max_binaries > 50:
            errors.append("Max binaries must be between 1 and 50")
            
        if self.binary.analysis_timeout < 30:
            errors.append("Analysis timeout must be at least 30 seconds")
            
        return errors


def create_default_config() -> BinAssistMCPConfig:
    """Create a default configuration instance"""
    return BinAssistMCPConfig()


def load_config_from_file(config_path: Optional[Path] = None) -> BinAssistMCPConfig:
    """Load configuration from file"""
    if config_path and config_path.exists():
        try:
            import json
            with open(config_path) as f:
                config_data = json.load(f)
            return BinAssistMCPConfig(**config_data)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            
    return create_default_config()