# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WSL Storage Manager Suite - A dual-tool system for complete WSL storage management:
- **storage_manager.py** (Linux/WSL): Menu-driven tool for analyzing and cleaning up files inside WSL
- **windows_storage_manager.py** (Windows): Companion tool for compacting VHDX files to reclaim disk space on Windows

The architecture reflects WSL's fundamental behavior: virtual disks (VHDX) grow automatically but never shrink automatically, requiring both cleanup inside WSL and compaction on Windows.

## Common Development Commands

### Testing the Linux Tool (in WSL/Ubuntu)
```bash
# Run the Linux storage manager
python3 storage_manager.py
# or
./storage_manager.py

# Test with sudo access (for full system operations)
sudo python3 storage_manager.py
```

### Testing the Windows Tool (in Windows PowerShell as Administrator)
```powershell
# Run the Windows storage manager
python windows_storage_manager.py

# Or use the batch file launcher
.\run_windows_manager.bat
```

### Code Quality
```bash
# No linting/testing framework currently configured
# Manual testing through menu navigation is the primary method
```

## Architecture & Design

### Two-Step Process Architecture

The entire system is built around WSL's two-step cleanup requirement:

1. **Step 1 (Linux side)**: Delete files in WSL using `storage_manager.py`
   - Frees space inside the Linux filesystem
   - VHDX file on Windows remains unchanged

2. **Step 2 (Windows side)**: Compact VHDX using `windows_storage_manager.py`
   - Shrinks VHDX file to match actual used space
   - Reclaims disk space on Windows C: drive

### Tool Design Patterns

Both tools share common design patterns:

**Color-Coded CLI Interface**:
- GREEN: Safe operations (no data loss)
- YELLOW: Caution required
- RED: Dangerous operations (potential data loss)
- Uses ANSI color codes via `Colors` class

**Menu-Driven Flow**:
- Main menu → Sub-menus → Operation
- All destructive operations require confirmation
- Preview before delete pattern
- Educational prompts explaining each operation

**Safety-First Approach**:
- Never delete without confirmation
- Double confirmation for dangerous operations (e.g., Docker volume deletion)
- Show what will be deleted before proceeding
- Always provide "cancel" option

### Linux Tool (storage_manager.py)

**Core Architecture**:
- ~1,200 lines of Python
- Menu hierarchy: Main → 6 sub-menus → Individual operations
- Uses subprocess to execute shell commands
- Checks for tool availability before use

**Key Modules**:
1. **Storage Visualization**: ncdu, du, df, dust, duf integration
2. **System Cleanup**: APT cache, journals, temp files, user caches
3. **Docker Management**: Container/image/volume/network cleanup with safety levels
4. **Advanced Analysis**: Large files, old files, file type analysis, duplicates
5. **Tool Management**: Check and install ncdu, duf, dust

**Important Functions**:
- `run_command()`: Execute shell commands with error handling
- `check_sudo()`: Verify sudo access for system operations
- `check_tool_installed()`: Verify external tool availability
- Menu functions: `show_*_menu()` pattern for each submenu

### Windows Tool (windows_storage_manager.py)

**Core Architecture**:
- ~1,000 lines of Python
- PowerShell integration for WSL/Windows operations
- VHDX file detection and management
- Administrator privilege checking

**Key Modules**:
1. **WSL Distribution Management**: List, shutdown, status check
2. **VHDX Discovery**: Find and identify all VHDX files
3. **Compaction Methods**: Modern (wsl --manage), Diskpart, Optimize-VHD
4. **Quick Compact All**: One-click automation
5. **Verification**: Before/after size comparison

**Critical Functions**:
- `run_powershell()`: Execute PowerShell commands from Python
- `get_wsl_distributions()`: Enumerate WSL distros
- `find_vhdx_files()`: Locate all VHDX files
- `compact_*()`: Three different compaction strategies
- `is_admin()`: Check for Administrator privileges

**Compaction Methods (Ordered by Preference)**:
1. **Modern Method** (`wsl --manage --set-sparse`): Fast, requires WSL 2.0+
2. **Diskpart Method**: Slower but works on all WSL versions, most compatible
3. **Optimize-VHD Method**: Requires Hyper-V, most thorough

### Platform-Specific Considerations

**Windows PowerShell Integration**:
- All Windows operations execute via PowerShell subprocess calls
- PowerShell output parsing handles UTF-16, null chars, BOM markers
- Administrator check required before VHDX operations
- WSL shutdown required before compaction (file locking)

**Linux/WSL Operations**:
- Sudo check at startup affects available operations
- Docker operations require Docker installation and group membership
- External tools (ncdu, duf, dust) are optional but enhance functionality

## Important Implementation Details

### Docker Cleanup Safety Levels

The Docker menu implements three safety tiers:

1. **Safe (GREEN)**: No data loss
   - Remove stopped containers
   - Remove dangling images (untagged)
   - Remove unused networks
   - Remove build cache

2. **Warning (YELLOW)**: Can remove useful images
   - Remove all unused images (not in use by ANY container)

3. **Dangerous (RED)**: Potential data loss
   - Remove unused volumes (can delete databases)
   - Requires explicit "DANGEROUS" confirmation

### VHDX Path Discovery Strategy

Windows tool uses multiple methods to find VHDX files:

1. **Registry lookup**: Query `HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss`
2. **Common locations**: Check standard WSL install paths
3. **Recursive search**: Fallback to scanning `%LOCALAPPDATA%`

### Error Handling Patterns

Both tools use consistent error handling:
```python
code, output = run_command(cmd, capture=True)
if code != 0:
    print_error("Operation failed")
    return False
print_success("Operation completed")
return True
```

## File Organization

```
linuxStorageCleanup/
├── storage_manager.py          # Linux tool (~1,200 lines)
├── windows_storage_manager.py  # Windows tool (~1,000 lines)
├── run_windows_manager.bat     # Windows launcher with admin check
├── README.md                   # Main documentation (650 lines)
├── README_WINDOWS.md           # Windows-specific docs (460 lines)
├── QUICKSTART.md              # Quick start guide (140 lines)
└── PROJECT_SUMMARY.md         # Project overview (315 lines)
```

## Adding New Features

### Adding a Linux Cleanup Operation

1. Add menu option in appropriate `show_*_menu()` function
2. Create operation function following pattern:
   ```python
   def cleanup_something(self):
       print_header("Cleanup Something")
       # Check if files exist
       # Show what will be deleted
       # Confirm with user
       # Execute cleanup
       # Report results
   ```
3. Use color coding: GREEN (safe), YELLOW (caution), RED (dangerous)
4. Always require confirmation before destructive operations

### Adding a Windows Compaction Method

1. Implement compaction function in `WindowsStorageManager` class
2. Follow the pattern: shutdown WSL → compact → verify results
3. Handle errors gracefully (WSL still running, path not found, etc.)
4. Add to main menu with appropriate description
5. Update troubleshooting guide if new failure modes exist

## Testing Strategies

### Linux Tool Testing
- Test without sudo (limited operations should work)
- Test with sudo (full system access)
- Test with/without Docker installed
- Test with/without optional tools (ncdu, duf, dust)
- Verify confirmation prompts appear for destructive operations
- Test cancellation (Ctrl+C) at various points

### Windows Tool Testing
- Test without Administrator (should show error and exit)
- Test with WSL running (should shutdown before compaction)
- Test each compaction method independently
- Test with missing distributions
- Verify VHDX path discovery works across different WSL versions
- Test "Quick Compact All" end-to-end workflow

## Common Gotchas

1. **VHDX Compaction Timing**: Large disks (100GB+) can take 30+ minutes to compact using Diskpart. This is normal.

2. **WSL File Locking**: VHDX files cannot be compacted while WSL is running. Always `wsl --shutdown` first.

3. **Docker Desktop**: Has separate VHDX file (`docker-desktop-data`) that also needs compaction. Must quit Docker Desktop completely, not just close windows.

4. **Sudo Caching**: Linux tool's `check_sudo()` may return false negative if sudo password timeout expired. User must run with `sudo` prefix.

5. **PowerShell Output Parsing**: WSL commands return UTF-16 with BOM and null chars. Always strip these: `.replace('\x00', '').strip().lstrip('\ufeff')`

6. **Color Codes on Windows**: ANSI color codes work on Windows 10+ but may not work on older systems. Tools remain functional without colors.

## Safety Considerations

**Never Implement**:
- Automatic deletion without confirmation
- Silent cleanup operations
- Operations that bypass confirmation prompts
- Hardcoded paths that might not exist on all systems

**Always Implement**:
- Preview before delete
- Clear confirmation prompts
- Explanatory text about what will happen
- "Are you sure?" for dangerous operations
- Cancellation options at every step
