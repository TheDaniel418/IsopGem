#!/usr/bin/env python3
"""
Cursor Mode Information Generator

This script generates information about your Cursor installation and custom modes
that you can share with Cursor support when asking about mode activation.
"""

import json
import os
import sys
import platform
import subprocess
from datetime import datetime
from pathlib import Path


def get_cursor_version():
    """Try to get Cursor version."""
    try:
        # This may not work depending on how Cursor is installed
        result = subprocess.run(["cursor", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    return "Unknown (Please fill in manually)"


def load_modes():
    """Load modes from the modes.json file."""
    cursor_dir = Path(".cursor")
    modes_file = cursor_dir / "modes.json"

    if not modes_file.exists():
        return None

    try:
        with open(modes_file, "r") as f:
            data = json.load(f)
            return data.get("modes", [])
    except Exception as e:
        return None


def generate_mode_info():
    """Generate information about Cursor and modes."""
    cursor_version = get_cursor_version()
    modes = load_modes()

    info = [
        "# Cursor Mode Activation Support Information",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## System Information",
        f"- OS: {platform.system()} {platform.release()}",
        f"- Cursor Version: {cursor_version}",
        "",
        "## Problem Description",
        "I'm unable to find a way to activate custom agent modes defined in my .cursor/modes.json file.",
        "I've tried the following commands:",
        "- /mode ModeName",
        "- /switch ModeName",
        "- /agent ModeName",
        "",
        "I don't see any dropdown or UI element to select a mode.",
        "",
        "## Available Modes",
    ]

    if modes:
        for i, mode in enumerate(modes, 1):
            name = mode.get("name", "Unnamed")
            desc = mode.get("description", "No description")
            model = mode.get("model", "Unknown model")

            info.append(f"{i}. **{name}** - {desc}")
            info.append(f"   - Model: {model}")
            info.append("")
    else:
        info.append("No modes found in .cursor/modes.json")

    info.append("## Question")
    info.append(
        "How can I activate a specific mode from my modes.json file in the current Cursor version?"
    )

    # Generate output file
    output_path = Path("cursor_mode_activation_support.md")
    with open(output_path, "w") as f:
        f.write("\n".join(info))

    print(f"Support information generated in {output_path}")
    print(
        "You can share this file with Cursor support when asking about mode activation."
    )


if __name__ == "__main__":
    generate_mode_info()
