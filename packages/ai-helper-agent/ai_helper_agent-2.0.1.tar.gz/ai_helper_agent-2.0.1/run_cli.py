#!/usr/bin/env python3
"""
AI Helper Agent - CLI Launcher
Simple launcher script to start the AI Helper Agent CLI
"""

import sys
from pathlib import Path

# Add the package directory to Python path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

try:
    from ai_helper_agent.cli import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)