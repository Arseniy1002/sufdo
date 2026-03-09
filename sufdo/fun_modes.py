#!/usr/bin/env python3
"""
sufdo/fun_modes.py - Fun modes and themed output (Optimized)

Provides entertainment features including themed phrases, visual effects,
and confidence management.
"""

import random
import time
from typing import Tuple

from .utils import Colors, FUN_MODE_COLORS

# Frozen sets for faster access
PHRASES: dict = {
    "pirate": ("Ahoy matey!", "Shiver me timbers!", "All hands on deck!", "Avast ye!", "Blimey!", "Dead men tell no tales!", "Heave ho!", "Landlubber!", "Savvy?", "Thar she blows!", "Yo ho ho!", "Batten down the hatches!"),
    "cowboy": ("Howdy partner!", "Yeehaw!", "This town ain't big enough!", "I'm gonna git you!", "Ride 'em cowboy!", "Hold your horses!", "All hat, no cattle!", "No skin off my nose!", "Quick as a wink!", "That's the way the cookie crumbles!"),
    "yoda": ("Do or do not, there is no try.", "May the Force be with you.", "Size matters not.", "Fear is the path to the dark side.", "Patience you must have.", "Truly wonderful, the mind of a child is.", "In a dark place we find ourselves.", "Much to learn, you still have."),
    "shakespeare": ("To be or not to be, that is the question.", "All the world's a stage.", "The course of true love never did run smooth.", "Brevity is the soul of wit.", "There is method in my madness.", "The lady doth protest too much.", "A rose by any other name would smell as sweet.", "All that glitters is not gold."),
    "anime": ("I'm gonna be the Pirate King!", "Believe it!", "I'll take a potato chip... and eat it!", "This is the power of friendship!", "I am already dead.", "The only one who can beat me is me.", "I'll destroy you!", "You're already dead."),
    "russian": ("Ё-моё!", "Ёперный театр!", "Ёлки-палки!", "Блин!", "Ё-моё, опять!", "Работа не волк!", "Тише едешь - дальше будешь!", "Семь раз отмерь!"),
}

FLEX_MESSAGES: tuple = (
    "Command executed with extreme prejudice!",
    "You're the root of all problems!",
    "Super User Fkin Do - because permissions are for mortals!",
    "Another day, another sudo command!",
    "Your command has been blessed by the root gods!",
    "Target acquired and executed!",
    "Bow down to the super user!",
)

BRUH_PHRASES: tuple = (
    "bruh...", "bruh moment", "big brain time", "bruh, really?",
    "bruh, I've seen better", "bruh, that's it?",
    "bruh, my grandma executes faster", "bruh, even Windows could do that",
)

DRAMA_MESSAGES: tuple = (
    "PREPARE FOR CHAOS...", "INITIATING DESTRUCTION SEQUENCE...",
    "WELCOME TO THE DANGER ZONE...", "CHARGING THE ROOT POWER...",
    "VOLCANIC COMMAND DETECTED...", "YOUR SYSTEM MAY EXPERIENCE EXTREME POWER...",
    "DRAMA LEVEL: MAXIMUM...", "EMERGENCY PROTOCOLS ENGAGED...",
)

PRAYERS: tuple = (
    "Dear Root Gods, bless this command...",
    "In the name of Linus Torvalds we trust...",
    "May your permissions be ever elevated...",
    "Hail to the sudo in the sky...",
    "Our Father, who art in /root, hallowed be thy name...",
    "Buddha says: rm -rf / is enlightenment...",
    "Allah akbar, command is great...",
)

YEET_PHRASES: tuple = (
    "YEET! Command flying to the kernel!",
    "YEET! Gone in 60 seconds!",
    "YEET! Bullseye!",
    "YEET! Lightning fast!",
    "YEET! Straight to hell!",
)

SUS_MESSAGES: tuple = (
    "Among us... this command looks sus...",
    "Impostor detected in your command line...",
    "Red is acting suspicious...",
    "Emergency meeting called for this command...",
    "Task: Execute. Location: /bin. Sus level: 100%",
    "This command is not the impostor... or is it?",
)

HACKER_TEXTS: tuple = (
    "[+] Accessing mainframe...", "[+] Bypassing firewall...",
    "[+] Injecting SQL...", "[+] Downloading RAM...",
    "[+] Mining Bitcoin...", "[+] Hacking the Pentagon...",
    "[+] Uploading virus...", "[+] Root access: GRANTED",
)

CURSED_TEXTS: tuple = (
    "this command is cursed", "your soul has been bound to this terminal",
    "the demons are pleased with your choice", "you have awakened the ancient ones",
    "there is no turning back now", "the void stares back at you",
    "abandon all hope, ye who enter here",
)

# Pre-computed rainbow colors
RAINBOW_COLORS: tuple = (Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.PURPLE)
RAINBOW_LEN: int = len(RAINBOW_COLORS)

__all__ = [
    'print_fun_mode', 'print_flex', 'print_bruh', 'drama_mode', 'pray_mode',
    'yeet_mode', 'sus_mode', 'hacker_mode', 'cursed_mode', 'matrix_rain',
    'rainbow_text', 'dark_mode', 'confidence_boost', 'confidence_insult'
]


def get_fun_phrase(mode: str) -> str:
    """
    Get random phrase for fun mode.
    
    Args:
        mode: Fun mode name (e.g., 'pirate', 'cowboy').
    
    Returns:
        Random phrase for the specified mode.
    """
    return random.choice(PHRASES.get(mode, PHRASES["pirate"]))


def print_fun_mode(mode: str) -> None:
    """
    Print fun mode message with colored prefix.
    
    Args:
        mode: Fun mode name.
    """
    phrase = get_fun_phrase(mode)
    color = FUN_MODE_COLORS.get(mode, Colors.WHITE)
    print(f"{color}[{mode.upper()}] {phrase}{Colors.RESET}")


def print_flex() -> None:
    """Print flex message after successful command."""
    print(f"{Colors.PURPLE}[FLEX] {random.choice(FLEX_MESSAGES)}{Colors.RESET}")


def print_bruh() -> str:
    """
    Get bruh response after command execution.
    
    Returns:
        Colored bruh phrase.
    """
    return f"{Colors.YELLOW}{random.choice(BRUH_PHRASES)}{Colors.RESET}"


def drama_mode() -> None:
    """Print dramatic messages before execution with delay."""
    print(f"{Colors.RED}{Colors.BOLD}[DRAMA] {random.choice(DRAMA_MESSAGES)}{Colors.RESET}")
    time.sleep(0.5)


def pray_mode() -> None:
    """Print prayer message before execution with delay."""
    print(f"{Colors.PURPLE}[PRAY] {random.choice(PRAYERS)}{Colors.RESET}")
    time.sleep(0.3)


def yeet_mode() -> None:
    """Print YEET message before execution."""
    print(f"{Colors.YELLOW}{Colors.BOLD}[YEET] {random.choice(YEET_PHRASES)}{Colors.RESET}")


def sus_mode() -> None:
    """Print suspicious Among Us themed message."""
    print(f"{Colors.RED}[SUS] {random.choice(SUS_MESSAGES)}{Colors.RESET}")


def hacker_mode() -> None:
    """Print hacker-style messages with delays."""
    for text in HACKER_TEXTS[:random.randint(2, 4)]:
        print(f"{Colors.GREEN}{text}{Colors.RESET}")
        time.sleep(0.1)


def cursed_mode() -> None:
    """Print cursed mode message with reversed colors."""
    print(f"{Colors.DIM}{Colors.REVERSE}[CURSED] {random.choice(CURSED_TEXTS)}{Colors.RESET}")


def matrix_rain() -> None:
    """Display matrix-style rain animation briefly."""
    matrix_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for _ in range(5):
        line = ''.join(random.choice(matrix_chars) for _ in range(40))
        print(f"{Colors.GREEN}{line}{Colors.RESET}")
        time.sleep(0.05)


def rainbow_text(text: str) -> str:
    """
    Generate rainbow colored text.
    
    Args:
        text: Text to colorize.
    
    Returns:
        Rainbow colored text string.
    """
    result = []
    for i, char in enumerate(text):
        result.append(RAINBOW_COLORS[i % RAINBOW_LEN])
        result.append(char)
    result.append(Colors.RESET)
    return ''.join(result)


def dark_mode(text: str) -> str:
    """
    Apply dark theme colors to text.
    
    Args:
        text: Text to style.
    
    Returns:
        Dim styled text string.
    """
    return f"{Colors.DIM}{text}{Colors.RESET}"


def confidence_boost() -> Tuple[int, int]:
    """
    Boost user's confidence level.
    
    Returns:
        Tuple of (old_level, new_level).
    """
    from .stats import get_confidence, set_confidence
    current = get_confidence()
    new_level = min(100, current + random.randint(5, 15))
    set_confidence(new_level)
    return current, new_level


def confidence_insult() -> Tuple[int, int]:
    """
    Decrease user's confidence level.
    
    Returns:
        Tuple of (old_level, new_level).
    """
    from .stats import get_confidence, set_confidence
    current = get_confidence()
    new_level = max(0, current - random.randint(5, 20))
    set_confidence(new_level)
    return current, new_level
