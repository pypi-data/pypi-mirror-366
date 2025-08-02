"""
API Key Management System
Handles secure storage and retrieval of API keys for AI Helper Agent
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

class APIKeyManager:
    """Manages API keys with encryption and secure storage"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".ai_helper_agent"
        self.config_dir.mkdir(exist_ok=True)
        
        self.env_file = self.config_dir / ".env"
        self.encrypted_file = self.config_dir / "keys.enc"
        self.key_file = self.config_dir / ".key"
        
        # Load existing keys
        self.keys = self._load_keys()
    
    def _generate_key(self, password: bytes) -> bytes:
        """Generate encryption key from password"""
        salt = b'ai_helper_agent_salt_2025'  # Static salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Get or create encryption key"""
        if self.key_file.exists():
            try:
                with open(self.key_file, 'rb') as f:
                    return f.read()
            except:
                pass
        
        # Create new key with password
        print("🔐 Setting up secure API key storage...")
        password = getpass.getpass("Enter a password to secure your API keys: ").encode()
        
        if not password:
            return None
        
        key = self._generate_key(password)
        
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions (Unix-style)
            try:
                os.chmod(self.key_file, 0o600)
            except:
                pass  # Windows doesn't support chmod
            
            return key
        except Exception as e:
            print(f"❌ Failed to create encryption key: {e}")
            return None
    
    def _load_keys(self) -> Dict[str, str]:
        """Load API keys from storage"""
        keys = {}
        
        # Try to load from .env file first (plain text)
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            keys[key.strip()] = value.strip().strip('"\'')
            except Exception as e:
                print(f"⚠️ Warning: Could not load .env file: {e}")
        
        # Try to load from encrypted file
        if self.encrypted_file.exists():
            try:
                encryption_key = self._get_encryption_key()
                if encryption_key:
                    fernet = Fernet(encryption_key)
                    
                    with open(self.encrypted_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    decrypted_data = fernet.decrypt(encrypted_data)
                    encrypted_keys = json.loads(decrypted_data.decode())
                    
                    # Merge with .env keys (encrypted takes precedence)
                    keys.update(encrypted_keys)
            except Exception as e:
                print(f"⚠️ Warning: Could not load encrypted keys: {e}")
        
        # Also check environment variables
        env_keys = {
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        }
        
        for key, value in env_keys.items():
            if value and key not in keys:
                keys[key] = value
        
        return keys
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        provider_map = {
            'groq': 'GROQ_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'claude': 'ANTHROPIC_API_KEY',
            'gpt': 'OPENAI_API_KEY',
        }
        
        key_name = provider_map.get(provider.lower(), f"{provider.upper()}_API_KEY")
        return self.keys.get(key_name)
    
    def set_api_key(self, provider: str, api_key: str, encrypt: bool = True) -> bool:
        """Set API key for a provider"""
        provider_map = {
            'groq': 'GROQ_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'claude': 'ANTHROPIC_API_KEY',
            'gpt': 'OPENAI_API_KEY',
        }
        
        key_name = provider_map.get(provider.lower(), f"{provider.upper()}_API_KEY")
        self.keys[key_name] = api_key
        
        return self._save_keys(encrypt)
    
    def _save_keys(self, encrypt: bool = True) -> bool:
        """Save API keys to storage"""
        try:
            if encrypt:
                # Save to encrypted file
                encryption_key = self._get_encryption_key()
                if encryption_key:
                    fernet = Fernet(encryption_key)
                    
                    data = json.dumps(self.keys).encode()
                    encrypted_data = fernet.encrypt(data)
                    
                    with open(self.encrypted_file, 'wb') as f:
                        f.write(encrypted_data)
                    
                    # Set restrictive permissions
                    try:
                        os.chmod(self.encrypted_file, 0o600)
                    except:
                        pass
                    
                    return True
            else:
                # Save to .env file
                with open(self.env_file, 'w') as f:
                    f.write("# AI Helper Agent API Keys\n")
                    f.write("# Generated automatically - do not edit manually\n\n")
                    
                    for key, value in self.keys.items():
                        f.write(f'{key}="{value}"\n')
                
                # Set restrictive permissions
                try:
                    os.chmod(self.env_file, 0o600)
                except:
                    pass
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to save API keys: {e}")
            return False
    
    def list_stored_keys(self) -> Dict[str, bool]:
        """List which API keys are stored (without revealing values)"""
        stored_keys = {}
        
        for key in ['GROQ_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'GEMINI_API_KEY']:
            stored_keys[key] = bool(self.keys.get(key))
        
        return stored_keys
    
    def remove_api_key(self, provider: str) -> bool:
        """Remove API key for a provider"""
        provider_map = {
            'groq': 'GROQ_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'claude': 'ANTHROPIC_API_KEY',
            'gpt': 'OPENAI_API_KEY',
        }
        
        key_name = provider_map.get(provider.lower(), f"{provider.upper()}_API_KEY")
        
        if key_name in self.keys:
            del self.keys[key_name]
            return self._save_keys()
        
        return False
    
    def setup_interactive(self):
        """Interactive setup for API keys"""
        print("🔧 API Key Setup for AI Helper Agent")
        print("This will help you store API keys securely for all CLI tools.")
        print()
        
        providers = {
            'groq': 'Groq (Required for fast inference)',
            'openai': 'OpenAI (For GPT models)',
            'anthropic': 'Anthropic (For Claude models)', 
            'google': 'Google (For Gemini models)',
        }
        
        stored_keys = self.list_stored_keys()
        
        for provider_key, description in providers.items():
            key_name = f"{provider_key.upper()}_API_KEY"
            
            if stored_keys.get(key_name):
                print(f"✅ {description}: Already stored")
                continue
            
            print(f"\n🔑 {description}")
            print(f"   Get your key from: {self._get_provider_url(provider_key)}")
            
            api_key = getpass.getpass(f"   Enter {provider_key.upper()} API key (or press Enter to skip): ").strip()
            
            if api_key:
                if self.set_api_key(provider_key, api_key):
                    print(f"   ✅ {provider_key.upper()} API key saved securely")
                else:
                    print(f"   ❌ Failed to save {provider_key.upper()} API key")
        
        print("\n🎉 API key setup complete!")
        print(f"📁 Keys are stored in: {self.config_dir}")
        
        # Show stored keys summary
        print("\n📊 Stored API Keys:")
        stored = self.list_stored_keys()
        for key, is_stored in stored.items():
            status = "✅ Stored" if is_stored else "❌ Not stored"
            print(f"   {key}: {status}")
    
    def _get_provider_url(self, provider: str) -> str:
        """Get URL where user can get API key for provider"""
        urls = {
            'groq': 'https://console.groq.com/keys',
            'openai': 'https://platform.openai.com/api-keys',
            'anthropic': 'https://console.anthropic.com/',
            'google': 'https://makersuite.google.com/app/apikey',
        }
        return urls.get(provider, 'Provider website')

# Global instance
api_key_manager = APIKeyManager()

def get_api_key(provider: str) -> Optional[str]:
    """Convenience function to get API key"""
    return api_key_manager.get_api_key(provider)

def setup_api_keys():
    """Convenience function for interactive setup"""
    api_key_manager.setup_interactive()

if __name__ == "__main__":
    setup_api_keys()
