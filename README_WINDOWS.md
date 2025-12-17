# Windows WSL Storage Manager

**Windows-side companion tool for reclaiming disk space after WSL cleanup**

This tool completes the second part of the WSL storage cleanup process by compacting the virtual disk files (VHDX) to actually reclaim space on Windows.

## ⚠️ Two-Step Process

WSL storage cleanup requires **TWO steps**:

1. **Step 1 (In WSL/Linux)**: Delete files using `storage_manager.py`
2. **Step 2 (In Windows)**: Compact disks using `windows_storage_manager.py` ← **THIS TOOL**

**Without Step 2, Windows will NOT reclaim the freed space!**

## Why You Need This Tool

When you delete files inside WSL (Ubuntu, Docker containers, etc.), the space is freed **inside** the Linux environment, but the VHDX file on Windows stays the same size. WSL virtual disks grow automatically but never shrink automatically.

**Example:**
- WSL disk grows to 200 GB over time
- You clean up 150 GB of files in WSL
- VHDX file on Windows is still 200 GB ❌
- You run this tool to compact it
- VHDX file shrinks to 50 GB ✓
- Windows reclaims 150 GB of disk space ✓

## Requirements

- **Windows 10/11** with WSL 2 installed
- **Python 3.6+** (usually pre-installed with Windows 10/11)
- **Administrator privileges** (required for compaction)
- **PowerShell** (built into Windows)

## Installation

### On Windows (Host Machine):

1. **Clone or copy this repository to Windows:**
   ```powershell
   # Option 1: Clone the repo on Windows
   git clone <your-repo-url>
   cd linuxStorageCleanup

   # Option 2: Copy from WSL to Windows
   # In WSL: cp -r ~/projects/linuxStorageCleanup /mnt/c/Users/YourUsername/
   ```

2. **Verify Python is installed:**
   ```powershell
   python --version
   ```

   If not installed, download from: https://www.python.org/downloads/

3. **No additional packages needed** - uses only Python standard library

## How to Run

### Method 1: Run as Administrator (Recommended)

1. **Open Windows Terminal or PowerShell as Administrator:**
   - Press `Win + X` on your keyboard
   - Select **"Terminal (Admin)"** or **"Windows PowerShell (Admin)"**
   - Click "Yes" if UAC prompts you

2. **Navigate to the project directory:**
   ```powershell
   cd C:\path\to\linuxStorageCleanup
   ```

3. **Run the tool:**
   ```powershell
   python windows_storage_manager.py
   ```

### Method 2: Right-click to Run as Admin

1. Right-click on `windows_storage_manager.py`
2. Select **"Run with PowerShell"** or **"Run as administrator"**

## Quick Start - Recommended Workflow

### The Complete Process:

1. **First, clean files in WSL** (Step 1):
   - Open Ubuntu/WSL
   - Run `./storage_manager.py`
   - Clean up files, Docker images, etc.
   - Note how much space you freed

2. **Then, compact disks in Windows** (Step 2):
   - Open PowerShell as Admin on Windows
   - Run `python windows_storage_manager.py`
   - Select **Option 7** (Quick Compact All) ← **Easiest option!**
   - Wait for completion (5-30 minutes)
   - Check Windows disk space - it should increase!

### Quick Compact All (Option 7) - Recommended

This is the easiest and most common option:

```
1. Runs as Administrator
2. Select Option 7 (Quick Compact All)
3. Confirm when prompted
4. Wait for compaction (shows progress)
5. Done! Space is reclaimed
```

This will:
- Shutdown all WSL instances
- Compact all WSL distributions
- Compact Docker Desktop (if installed)
- Show results

## Features & Menu Options

### Main Menu:

```
1. Show WSL Distributions & Disk Usage
   - Lists all WSL distributions
   - Shows running/stopped status
   - Displays disk usage for each

2. Find & Show VHDX Files
   - Locates all VHDX files
   - Shows file sizes
   - Identifies which distribution each belongs to

3. Shutdown WSL
   - Safely shuts down all WSL instances
   - Required before compaction

4. Compact WSL Disks (Modern Method)
   - Uses 'wsl --manage --set-sparse' command
   - Best for recent WSL versions
   - Select specific or all distributions

5. Compact Using Diskpart (Manual)
   - Uses Windows diskpart tool
   - Works on all WSL versions
   - Good fallback if Method 4 fails

6. Compact Using Optimize-VHD (Hyper-V)
   - Uses PowerShell Optimize-VHD cmdlet
   - Requires Hyper-V (Windows Pro/Enterprise)
   - Most thorough compaction

7. Quick Compact All (Recommended) ⭐
   - One-click solution
   - Compacts everything automatically
   - Best for most users

8. Verify Compaction Results
   - Shows VHDX file sizes
   - Displays Windows disk space
   - Confirms compaction worked

9. Troubleshooting & Help
   - Common issues and solutions
   - Step-by-step guides
   - Links to documentation
```

## Usage Examples

### Example 1: First-time Complete Cleanup

**In WSL/Ubuntu:**
```bash
# Clean up files
./storage_manager.py
# Select Option 2 → Option 8 (Run all safe cleanups)
# Select Option 3 → Option 11 (Safe Docker cleanup)
```

**In Windows (as Admin):**
```powershell
# Compact disks
python windows_storage_manager.py
# Select Option 7 (Quick Compact All)
# Wait for completion
# Select Option 8 (Verify) to confirm
```

### Example 2: Compact Specific Distribution

**In Windows (as Admin):**
```powershell
python windows_storage_manager.py
# Select Option 4 (Compact WSL Disks - Modern)
# Select 'S' (Select specific distribution)
# Enter the number for your distribution
# Wait for completion
```

### Example 3: Using Diskpart (if modern method fails)

**In Windows (as Admin):**
```powershell
python windows_storage_manager.py
# Select Option 3 (Shutdown WSL) first
# Wait 10 seconds
# Select Option 5 (Compact Using Diskpart)
# Choose the VHDX file(s) to compact
# Wait for completion (may take 10-30 minutes)
```

## Common Workflows

### Scenario 1: Regular Maintenance (Monthly)

```powershell
# Clean in WSL, then compact in Windows
python windows_storage_manager.py
→ Option 7 (Quick Compact All)
```

### Scenario 2: Docker Cleanup (After removing images)

```powershell
# After Docker cleanup in WSL
python windows_storage_manager.py
→ Option 2 (Find VHDX files)
→ Note Docker VHDX size
→ Option 5 (Diskpart) → Select Docker VHDX
→ Wait for compaction
→ Option 8 (Verify)
```

### Scenario 3: Troubleshooting (Modern method failed)

```powershell
python windows_storage_manager.py
→ Option 3 (Shutdown WSL)
→ Option 5 (Diskpart method)
→ Select distribution
→ Wait for completion
```

## Troubleshooting

### Problem: "Not running as Administrator"

**Solution:**
1. Close the program
2. Press `Win + X`
3. Select "Terminal (Admin)" or "PowerShell (Admin)"
4. Navigate to the directory
5. Run: `python windows_storage_manager.py`

### Problem: "The parameter is incorrect" (Modern method)

**Solution:** Your WSL version doesn't support the modern method.

**Fix:**
- Use **Option 5** (Diskpart method) instead
- Or update WSL: `wsl --update` in PowerShell

### Problem: "Process cannot access the file"

**Solution:** WSL is still running.

**Fix:**
1. Close ALL WSL/Ubuntu windows
2. Run **Option 3** (Shutdown WSL)
3. Wait 30 seconds
4. Try compaction again
5. If using Docker, quit Docker Desktop completely

### Problem: Compaction doesn't free much space

**Solution:** Make sure you deleted files in WSL first!

**Fix:**
1. Go back to WSL
2. Run `./storage_manager.py`
3. Actually clean up files
4. Come back to Windows and compact

### Problem: Can't find Python

**Solution:** Python not installed or not in PATH.

**Fix:**
1. Download Python from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart PowerShell
4. Try again

### Problem: Diskpart takes forever

**Explanation:** Large VHDX files (100GB+) can take 10-30 minutes to compact.

**What to do:**
- Be patient - it's working!
- Monitor Task Manager - diskpart.exe should be using disk I/O
- Don't interrupt the process

## Understanding the Output

### VHDX File Sizes

```
1. Ubuntu 22.04
   Size: 45.23 GB
   Path: C:\Users\...\Ubuntu22.04LTS_...\ext4.vhdx
```

This shows:
- **Distribution name**: Ubuntu 22.04
- **Current file size**: How much space it's using on Windows
- **Path**: Where the file is located

**After compaction, this size should decrease significantly.**

### Compaction Results

```
✓ Successfully compacted Ubuntu-22.04
Size before: 125.5 GB
Size after: 32.8 GB
Space saved: 92.7 GB
```

This means:
- **92.7 GB was reclaimed** on your Windows C: drive
- You can now use that space for other things

## Security & Safety

### What This Tool Does:
- ✅ Reads VHDX file information
- ✅ Runs Windows built-in tools (wsl, diskpart, Optimize-VHD)
- ✅ Compacts virtual disks to reclaim space

### What This Tool Does NOT Do:
- ❌ Delete any files in WSL
- ❌ Modify Linux distributions
- ❌ Delete Docker containers or images
- ❌ Change any WSL configurations

### Safety Notes:
- **Always shutdown WSL before compaction** - the tool does this automatically
- **Compaction is safe** - it only reclaims unused space
- **No data loss** - your files in WSL are not touched
- **Reversible** - disks will grow again as you use space

## Performance

### Expected Times:

| Disk Size | Compaction Time |
|-----------|-----------------|
| 10-20 GB  | 1-3 minutes     |
| 20-50 GB  | 3-10 minutes    |
| 50-100 GB | 10-20 minutes   |
| 100-200 GB| 20-30 minutes   |
| 200+ GB   | 30-60 minutes   |

**Note:** Diskpart method is slower than modern method, but more thorough.

## Advanced Usage

### Finding VHDX Files Manually

Common locations:
```
Ubuntu 22.04:
%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx

Ubuntu 20.04:
%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu20.04onWindows_79rhkp1fndgsc\LocalState\ext4.vhdx

Docker Desktop:
%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx
```

### Manual Compaction via PowerShell

If you prefer command-line:

```powershell
# Modern method
wsl --shutdown
Start-Sleep -Seconds 10
wsl --manage Ubuntu-22.04 --set-sparse true

# Diskpart method
wsl --shutdown
diskpart
# Then in diskpart:
select vdisk file="C:\Users\...\ext4.vhdx"
compact vdisk
detach vdisk
exit

# Optimize-VHD method
wsl --shutdown
Optimize-VHD -Path "C:\Users\...\ext4.vhdx" -Mode Full
```

## Integration with Linux Tool

This tool is designed to work with `storage_manager.py` on the Linux/WSL side:

**Recommended Workflow:**

1. **In WSL** - Run `storage_manager.py`:
   - Analyze storage usage
   - Clean up files
   - Remove Docker images
   - Note how much space freed

2. **In Windows** - Run `windows_storage_manager.py`:
   - Compact the disks
   - Verify space reclaimed
   - Confirm Windows disk space increased

**Both tools together give you complete control over WSL storage!**

## FAQ

**Q: Do I need to run this every time I delete files in WSL?**
A: No, only when you've freed up significant space (10+ GB) and want to reclaim it on Windows.

**Q: Will this delete my files?**
A: No, this only compacts the virtual disk. Your files in WSL are safe.

**Q: Can I run this while WSL is running?**
A: No, the tool automatically shuts down WSL before compaction.

**Q: Which compaction method should I use?**
A: Start with Option 7 (Quick Compact All). If that fails, use Option 5 (Diskpart).

**Q: How often should I compact?**
A: Monthly or after major cleanups (removing large Docker images, old projects, etc.).

**Q: Is it safe to interrupt compaction?**
A: It's best not to, but if you must, the worst case is that compaction doesn't complete. Your data is safe.

**Q: Why does Windows show my C: drive full even after WSL cleanup?**
A: Because you haven't compacted the VHDX files yet! That's why this tool exists.

## Support

- **Documentation**: See `README.md` for complete WSL storage management guide
- **WSL Documentation**: https://docs.microsoft.com/en-us/windows/wsl/
- **Issues**: Check the troubleshooting section (Option 9 in the tool)

## Credits

This tool uses Windows built-in utilities:
- `wsl.exe` - WSL command-line tool
- `diskpart.exe` - Windows disk partition utility
- `Optimize-VHD` - Hyper-V PowerShell cmdlet (optional)

Part of the Linux Storage Manager suite for comprehensive WSL storage management.
