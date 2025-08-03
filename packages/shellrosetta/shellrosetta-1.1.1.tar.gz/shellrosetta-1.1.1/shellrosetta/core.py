# shellrosetta/core.py

import shlex
from typing import Optional, Tuple
from .mappings import (
    LINUX_TO_PS, PS_TO_LINUX,
    LS_FLAGS_MAP, RM_FLAGS_MAP, CP_FLAGS_MAP, MV_FLAGS_MAP,
    GREP_FLAGS_MAP, FIND_FLAGS_MAP, CAT_FLAGS_MAP
)
from .parser import parser
from .plugins import plugin_manager
from .ml_engine import ml_engine

def extract_flags_and_targets(args):
    """
    Splits an argument list into 'flags' (like -a, -l) and everything else (targets).
    Returns (flags, targets) as two lists.
    """
    flags = []
    targets = []
    for arg in args:
        if arg.startswith('-'):
            flags.append(arg)
        else:
            targets.append(arg)
    return flags, targets

def try_direct_mapping(command, mapping_dict):
    """
    Attempts to find an exact match for a full command (with args) in the mapping dict.
    Returns the mapped translation (with note, if any), or None.
    """
    if command in mapping_dict:
        cmd, note = mapping_dict[command]
        if note:
            return f"{cmd} # [{note}]"
        return cmd
    return None

def fallback_flag_translate(cmd, args):
    """
    If no exact mapping is found, try to reconstruct a translation using per-command flag maps.
    This covers most real-life flag combos (e.g. ls -alh, rm -rf).
    """
    flags, targets = extract_flags_and_targets(args)
    flagkey = "".join(sorted(flags))
    base = ""
    flagmap = None

    # Pick the right flag mapping for the command
    if cmd == "ls":
        base = "Get-ChildItem"
        flagmap = LS_FLAGS_MAP
    elif cmd == "rm":
        base = "Remove-Item"
        flagmap = RM_FLAGS_MAP
    elif cmd == "cp":
        base = "Copy-Item"
        flagmap = CP_FLAGS_MAP
    elif cmd == "mv":
        base = "Move-Item"
        flagmap = MV_FLAGS_MAP
    elif cmd == "grep":
        base = "Select-String"
        flagmap = GREP_FLAGS_MAP
    elif cmd == "find":
        base = "Get-ChildItem -Recurse"
        flagmap = FIND_FLAGS_MAP
    elif cmd == "cat":
        base = "Get-Content"
        flagmap = CAT_FLAGS_MAP

    # If we have a flag map, try to find a translation for these flags
    if flagmap is not None:
        flags_out = flagmap.get(flagkey, None)
        out = base
        if flags_out:
            out += f" {flags_out}"
        if targets:
            out += " " + " ".join(targets)
        if not flags_out and flags:
            out += f" # [No direct PowerShell equivalent for flags: {', '.join(flags)}]"
        return out.strip()

    # No flag map, so we just have to say we don't know
    return f"# [No translation available for '{cmd}' with args '{' '.join(args)}']"

def lnx2ps(command: str, use_ml: bool = True, use_plugins: bool = True) -> str:
    """
    Translates a Linux command (possibly piped) to PowerShell.
    
    Args:
        command: The Linux command to translate
        use_ml: Whether to use machine learning suggestions
        use_plugins: Whether to use plugin translations
    
    Returns:
        The PowerShell equivalent command
    """
    if not command.strip():
        return ""
    
    # Try plugin translation first
    if use_plugins:
        plugin_translation = plugin_manager.translate_with_plugins(command, "lnx2ps")
        if plugin_translation:
            ml_engine.learn_pattern(command, plugin_translation, "lnx2ps", success=True)
            return plugin_translation
    
    # Try ML translation
    if use_ml:
        ml_translation = ml_engine.get_best_translation(command, "lnx2ps")
        if ml_translation:
            return ml_translation
    
    # Parse command with AST
    ast_root = parser.parse(command)
    
    stages = [stage.strip() for stage in command.split('|')]
    translated = []
    for stage in stages:
        if not stage:
            continue
        tokens = shlex.split(stage)
        if not tokens:
            continue
        cmd = tokens[0].lower()
        args = tokens[1:]
        # Try a direct mapping first (whole command)
        trymap = " ".join([cmd] + args) if args else cmd
        direct = try_direct_mapping(trymap, LINUX_TO_PS)
        if direct:
            translated.append(direct)
        else:
            # Fallback to flag-aware translation
            fallback = fallback_flag_translate(cmd, args)
            translated.append(fallback)
    
    result = " | ".join(translated)
    
    # Learn the pattern
    if use_ml:
        ml_engine.learn_pattern(command, result, "lnx2ps", success=True)
    
    return result

def ps2lnx(command: str, use_ml: bool = True, use_plugins: bool = True) -> str:
    """
    Translates a PowerShell command (possibly piped) to Linux.
    
    Args:
        command: The PowerShell command to translate
        use_ml: Whether to use machine learning suggestions
        use_plugins: Whether to use plugin translations
    
    Returns:
        The Linux equivalent command
    """
    if not command.strip():
        return ""
    
    # Try plugin translation first
    if use_plugins:
        plugin_translation = plugin_manager.translate_with_plugins(command, "ps2lnx")
        if plugin_translation:
            ml_engine.learn_pattern(command, plugin_translation, "ps2lnx", success=True)
            return plugin_translation
    
    # Try ML translation
    if use_ml:
        ml_translation = ml_engine.get_best_translation(command, "ps2lnx")
        if ml_translation:
            return ml_translation
    
    # Parse command with AST
    ast_root = parser.parse(command)
    
    stages = [stage.strip() for stage in command.split('|')]
    translated = []
    for stage in stages:
        if not stage:
            continue
        direct = try_direct_mapping(stage, PS_TO_LINUX)
        if direct:
            translated.append(direct)
        else:
            # fallback: try base command match
            words = stage.split()
            if words:
                first_word = words[0]
                base_direct = try_direct_mapping(first_word, PS_TO_LINUX)
                if base_direct:
                    translated.append(base_direct)
                else:
                    translated.append(f"# [No Linux equivalent for: {stage}]")
            else:
                translated.append(f"# [No Linux equivalent for: {stage}]")
    
    result = " | ".join(translated)
    
    # Learn the pattern
    if use_ml:
        ml_engine.learn_pattern(command, result, "ps2lnx", success=True)
    
    return result
