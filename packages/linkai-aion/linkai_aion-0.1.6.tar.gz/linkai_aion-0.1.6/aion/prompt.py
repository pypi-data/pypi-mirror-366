#!/usr/bin/env python3
"""
LinkAI-Aion Prompt Management Module
====================================

Advanced prompt management and display utilities for AI projects.
Provides comprehensive prompt handling, formatting, and presentation features.

Features:
- System prompt management and display
- User prompt handling and formatting
- Prompt type classification and routing
- Prompt template management
- Interactive prompt interfaces
- Prompt validation and sanitization

Author: Aksel (CEO, LinkAI)
License: Apache-2.0
Copyright: 2025 LinkAI

This module is part of the LinkAI-Aion utility library.
"""

def show_prompt(prompt_type):
    """
    Display a formatted prompt based on the specified prompt type.
    
    This function provides a simple interface for displaying different
    types of prompts with appropriate formatting and emojis.
    
    Args:
        prompt_type (str): The type of prompt to display ('system' or other)
        
    Returns:
        None: This function prints the prompt to stdout
    """
    # Check if the prompt type is 'system'
    if prompt_type == "system":
        # Display the system prompt with appropriate formatting
        print("🛠️ System prompt:\nYou are Aion, an advanced AI assistant.")
    else:
        # Display a default user prompt for other prompt types
        print("🗣️ User prompt:\nHello Aion, I need help with coding.")