#!/usr/bin/env python3
"""
Mode Activation Helper Script for Cursor

This script helps display available custom agent modes and provides instructions
on how to activate them.
"""

import json
import os
import sys
from pathlib import Path


def load_modes():
    """Load modes from the modes.json file."""
    cursor_dir = Path(".cursor")
    modes_file = cursor_dir / "modes.json"

    if not modes_file.exists():
        print("❌ No modes.json file found in .cursor directory!")
        return None

    try:
        with open(modes_file, "r") as f:
            data = json.load(f)
            return data.get("modes", [])
    except Exception as e:
        print(f"❌ Error loading modes.json: {e}")
        return None


def display_modes(modes):
    """Display available modes with details."""
    if not modes:
        return

    print("\n💁‍♀️ Available Custom Agent Modes:")
    print("=" * 60)

    for i, mode in enumerate(modes, 1):
        name = mode.get("name", "Unnamed")
        desc = mode.get("description", "No description")
        model = mode.get("model", "Unknown model")

        print(f"{i}. {name} - {desc}")
        print(f"   Model: {model}")
        print("-" * 60)


def display_activation_instructions():
    """Display instructions for activating modes in Cursor."""
    print("\n✨ How to Activate a Mode in Cursor:")
    print("=" * 60)
    print("1. Look for a model selector in the Cursor UI (top-right corner)")
    print("2. Try using the Command Palette (Ctrl+Shift+P or Cmd+Shift+P)")
    print("   - Search for 'mode', 'agent', or 'model'")
    print("3. Try chat commands like:")
    print("   - /mode ModeName")
    print("   - /switch ModeName")
    print("   - /agent ModeName")
    print("4. Check Cursor documentation for the latest instructions")
    print("   - The UI might have changed since the repository was created")
    print(
        "\n💡 Tip: If you can't find the mode selector, try updating Cursor to the latest version."
    )


def main():
    """Main function."""
    print("🔮 Cursor Mode Activation Helper")

    # Load and display modes
    modes = load_modes()
    if modes:
        display_modes(modes)
    else:
        print(
            "No modes found. Please make sure .cursor/modes.json exists and is properly formatted."
        )
        return

    # Display activation instructions
    display_activation_instructions()

    print("\n😊 Good luck activating your preferred mode!")


if __name__ == "__main__":
    main()
