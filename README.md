# WSL Storage Manager Suite

**Complete storage management for WSL - Two powerful tools for Linux and Windows**

A comprehensive suite of menu-driven CLI tools to visualize, clean up, and reclaim storage space in WSL environments.

## 📦 What's Included

This repository contains **TWO complementary tools**:

1. **`storage_manager.py`** (Linux/WSL) - Analyze and clean up files inside WSL
2. **`windows_storage_manager.py`** (Windows) - Compact disks to reclaim space on Windows

**You need BOTH tools for complete storage management!**

## ⚠️ IMPORTANT: Two-Step Process

WSL storage cleanup is a **TWO-step process**:

### Step 1: Clean Files in WSL (Linux Side)
Use `storage_manager.py` inside WSL/Ubuntu to:
- Find what's using space
- Clean up system files, caches, logs
- Remove Docker images and containers
- Delete old files

### Step 2: Compact Disks in Windows (Windows Side)
Use `windows_storage_manager.py` on Windows to:
- Compact the VHDX virtual disk files
- Actually reclaim the space on your C: drive
- Verify space was reclaimed

**Why both steps?** WSL virtual disks (VHDX files) grow automatically when you use space, but they **DO NOT automatically shrink** when you delete files. Even after freeing up 150GB inside WSL, Windows will still show the disk using that space until you manually compact it.

---

## 🚀 Quick Start

### Complete Workflow (Recommended):

**1. In WSL/Ubuntu** (Install and run the Linux tool):
```bash
cd ~/projects
git clone <your-repo-url> linuxStorageCleanup
cd linuxStorageCleanup
chmod +x storage_manager.py
./storage_manager.py
# Select Option 7 → Common space hogs (see what's using space)
# Select Option 2 → Option 8 (Run all safe cleanups)
# Select Option 3 → Option 11 (Docker safe cleanup)
```

**2. In Windows PowerShell as Administrator** (Run the Windows tool):
```powershell
# Copy the repo to Windows or clone it there
cd C:\path\to\linuxStorageCleanup

# Run the Windows tool
python windows_storage_manager.py
# Select Option 7 (Quick Compact All)
# Wait for completion (5-30 minutes)
# Check your C: drive - space should be reclaimed!
```

**Or use the Windows tool with GUI launcher:**
- Right-click `run_windows_manager.bat`
- Select "Run as administrator"
- Follow the menu

### Alternative: Manual Compaction (Windows PowerShell as Admin)

If you prefer command-line only:

```powershell
# Shutdown all WSL instances
wsl --shutdown

# Wait for shutdown
Start-Sleep -Seconds 10

# Compact Ubuntu disk
wsl --manage Ubuntu-22.04 --set-sparse true

# Compact Docker disk (if using Docker)
wsl --manage docker-desktop-data --set-sparse true
```

See the [Complete WSL Disk Compaction Guide](#wsl-disk-compaction) below for alternative methods if this doesn't work.

---

## 📋 Linux Tool Features (storage_manager.py)

### Storage Visualization
- **Interactive disk usage (ncdu)** - Navigate directories interactively (RECOMMENDED)
- **Quick directory analysis (du)** - Fast directory size overview
- **Filesystem overview (df)** - See disk usage and inode information
- **Modern tools (dust, duf)** - Beautiful, modern alternatives for disk analysis
- **Quick space hogs check** - Instantly see common locations using space

### Safe System Cleanup
- APT package cache cleanup
- Old journal logs cleanup (keeps recent logs)
- Temporary files cleanup (/tmp, /var/tmp)
- User cache cleanup (~/.cache)
- Thumbnail cache cleanup
- npm cache cleanup (if installed)
- pip cache cleanup (if installed)
- One-click safe cleanup option

### Docker Management
- Docker storage visualization
- List all containers, images, and volumes
- Safe cleanup options:
  - Remove stopped containers
  - Remove dangling images
  - Remove unused networks
  - Remove build cache
- Advanced options with warnings:
  - Remove all unused images
  - Remove unused volumes (with data loss warnings)
- One-click safe Docker cleanup

### Advanced Analysis
- Find largest files in the system
- Find largest directories with customizable depth
- Find old files not accessed in N days
- Search for specific file types and calculate total size
- Find potential duplicate files by size
- Analyze directory growth

### Tool Management
- Check installation status of all tools
- One-click installation of recommended tools
- WSL disk compaction instructions

---

## 💻 Windows Tool Features (windows_storage_manager.py)

### WSL Distribution Management
- List all WSL distributions and their status
- Show disk usage for each distribution
- Shutdown WSL instances safely

### VHDX File Management
- Automatically find all VHDX files
- Show file sizes and locations
- Identify which distribution each belongs to
- Display before/after compaction sizes

### Compaction Methods (3 Options)
1. **Modern WSL Method** - Fast, uses `wsl --manage --set-sparse`
2. **Diskpart Method** - Compatible with all WSL versions, most reliable
3. **Optimize-VHD Method** - Requires Hyper-V, most thorough

### One-Click Operations
- **Quick Compact All** - Compacts everything with one command (recommended!)
- Automatic WSL shutdown before compaction
- Progress tracking and status updates
- Verification of space reclaimed

### Safety Features
- Administrator privilege checking
- Automatic WSL shutdown to prevent file locks
- Before/after size comparison
- Detailed error messages and troubleshooting

### Documentation & Help
- Built-in troubleshooting guide
- Step-by-step instructions for each method
- Common issues and solutions
- Links to official documentation

**📖 See [README_WINDOWS.md](README_WINDOWS.md) for complete Windows tool documentation**

---

## 📥 Installation

### Linux Tool Installation (In WSL/Ubuntu)

1. Clone or download this repository
2. Make the script executable (if not already):
```bash
chmod +x storage_manager.py
```

3. Run the tool:
```bash
./storage_manager.py
```

Or with Python directly:
```bash
python3 storage_manager.py
```

### Windows Tool Installation (On Windows Host)

1. **Clone or copy this repository to Windows:**
   ```powershell
   # Option 1: Clone directly on Windows
   git clone <your-repo-url>
   cd linuxStorageCleanup

   # Option 2: Copy from WSL to Windows
   # In WSL: cp -r ~/projects/linuxStorageCleanup /mnt/c/Users/YourUsername/
   ```

2. **Verify Python is installed:**
   ```powershell
   python --version
   ```
   If not installed: Download from https://www.python.org/downloads/

3. **Run the tool (as Administrator):**

   **Method A - Using the batch file (easiest):**
   - Right-click `run_windows_manager.bat`
   - Select "Run as administrator"

   **Method B - Using PowerShell:**
   - Press `Win + X` → Select "Terminal (Admin)"
   - Navigate to the directory
   - Run: `python windows_storage_manager.py`

**📖 See [README_WINDOWS.md](README_WINDOWS.md) for detailed Windows installation and usage instructions**

---

## Recommended Tools (Linux)

The script works with built-in commands but is enhanced with these optional tools:

### Essential (Highly Recommended)
- **ncdu** - Interactive disk usage analyzer
  ```bash
  sudo apt-get install ncdu
  ```

### Nice to Have
- **duf** - Modern disk usage overview
  ```bash
  sudo apt-get install duf
  ```

- **dust** - Modern directory size analyzer
  ```bash
  sudo snap install dust
  ```

You can also use the built-in tool installer (Option 5 in main menu) to install these automatically.

## Usage

### Basic Usage

Simply run the script and navigate through the menus:

```bash
./storage_manager.py
```

### Quick Start Guide - Complete Workflow

**Follow ALL 4 steps to fully reclaim disk space:**

1. **First Time Users** - Check what's using space (In WSL/Ubuntu):
   - Run `./storage_manager.py`
   - Choose Option 1 (Storage Visualization)
   - Choose Option 1 (ncdu) - if not installed, the tool will offer to install it
   - Navigate through your directories to find space hogs

2. **Quick Cleanup** - Safe system cleanup (In WSL/Ubuntu):
   - Choose Option 2 (System Cleanup)
   - Choose Option 8 (Run ALL safe cleanups)
   - Confirm when prompted

3. **Docker Cleanup** - If you use Docker (In WSL/Ubuntu):
   - Choose Option 3 (Docker Management)
   - Choose Option 11 (Safe Docker cleanup) for a safe all-in-one cleanup
   - Or choose Option 9 to remove unused images (can save 100+ GB)

4. **⚠️ CRITICAL: Compact WSL Disk** - Actually reclaim the space (In Windows PowerShell as Admin):
   ```powershell
   wsl --shutdown
   wsl --manage Ubuntu-22.04 --set-sparse true
   wsl --manage docker-desktop-data --set-sparse true
   ```
   **Without this step, Windows will NOT reclaim the freed space!**

### Safety Features

The tool includes multiple safety features:

- **Color-coded warnings**: Red for dangerous operations, yellow for caution
- **Confirmation prompts**: All destructive operations require confirmation
- **Preview before delete**: Shows what will be deleted before proceeding
- **Double confirmation**: Dangerous operations (like volume deletion) require explicit confirmation
- **Educational messages**: Explains what each operation does

### Running with Sudo

For complete system visibility, run with sudo privileges:

```bash
sudo ./storage_manager.py
```

However, the tool will work without sudo for user-specific operations.

**Note**: The tool checks for sudo at startup. If you don't have sudo access, some features (like system-wide scans and cleanups) will be limited.

## Menu Structure

### Main Menu
1. Storage Visualization
2. System Cleanup (Safe)
3. Docker Management
4. Advanced Analysis
5. Check & Install Tools
6. WSL Disk Compaction Info
0. Exit

### Storage Visualization Menu
- Interactive ncdu (RECOMMENDED)
- du analysis with custom depth
- df filesystem overview
- Modern tools (dust, duf)
- Top 20 largest directories
- Common space hogs check

### System Cleanup Menu
All operations include size checks and confirmations:
- APT cache cleanup
- Journal logs cleanup (keeps last N days)
- Temporary files cleanup
- User cache cleanup
- Thumbnail cache cleanup
- Language-specific caches (npm, pip)
- Run all safe cleanups at once

### Docker Management Menu
- Show detailed storage information
- List containers, images, volumes
- Safe cleanups (no data loss)
- Advanced cleanups with warnings
- One-click safe cleanup option

### Advanced Analysis Menu
- Find largest files
- Find largest directories
- Find old/unused files
- Analyze file types
- Find duplicates
- Directory size analysis

## Common Space Hogs

The tool automatically checks these common locations:

- `/var/lib/docker` - Docker storage
- `/var/log` - System logs
- `/var/cache/apt` - APT package cache
- `/var/lib/apt` - APT library
- `/var/lib/snapd` - Snap packages
- `/tmp` - Temporary files
- `/var/tmp` - Variable temporary files
- `/home/*` - User home directories

## WSL Disk Compaction

### Why This Step is Critical

When you delete files inside WSL (Ubuntu, Docker, etc.), the space is freed **inside** the Linux environment, but Windows doesn't automatically reclaim it. The WSL virtual disk file (VHDX) grows automatically as you use space, but it **never shrinks automatically**.

**Example:** If your WSL disk grew to 200GB, then you cleaned up 150GB of files, the VHDX file on Windows will still be 200GB until you manually compact it.

### Before You Start

1. **Verify you freed up space in WSL first** - Run `df -h` in WSL to confirm you have free space
2. **Close all WSL terminals** - Make sure no WSL windows are open
3. **Open Windows PowerShell as Administrator**:
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

### Method 1 - Modern WSL (Recommended) ⭐

**Best for:** WSL 2.0+ (Windows 11 or Windows 10 with recent updates)

```powershell
# Step 1: Shutdown ALL WSL instances (REQUIRED)
wsl --shutdown

# Step 2: Wait 5-10 seconds for complete shutdown
Start-Sleep -Seconds 10

# Step 3: Compact Ubuntu-22.04 disk
wsl --manage Ubuntu-22.04 --set-sparse true

# Step 4: Compact Docker Desktop data (if you use Docker)
wsl --manage docker-desktop-data --set-sparse true

# Step 5: Check result - list your WSL distributions
wsl --list --verbose
```

**Expected Result:** After compaction completes (may take a few minutes), check your Windows disk space - it should reflect the cleanup you did in WSL.

**Troubleshooting Method 1:**
- If you get "The parameter is incorrect", your WSL version may not support this command - use Method 2
- If you get "distribution not found", run `wsl --list` to see your exact distribution names
- Make sure you fully shutdown WSL first: `wsl --shutdown`

### Method 2 - Diskpart (Manual Compaction)

**Best for:** Older WSL versions or when Method 1 fails

```powershell
# Step 1: Shutdown WSL
wsl --shutdown

# Step 2: Wait for shutdown
Start-Sleep -Seconds 10

# Step 3: Launch Diskpart
diskpart
```

**Then in the diskpart prompt, run these commands:**

For Ubuntu 22.04:
```
select vdisk file="%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx"
compact vdisk
detach vdisk
```

For Docker Desktop:
```
select vdisk file="%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx"
compact vdisk
detach vdisk
```

Exit diskpart:
```
exit
```

**Note:** The path may vary depending on your installation. Common locations:
- Ubuntu 22.04: `%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx`
- Ubuntu 20.04: `%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu20.04onWindows_79rhkp1fndgsc\LocalState\ext4.vhdx`
- Docker: `%LOCALAPPDATA%\Docker\wsl\data\ext4.vhdx`

**Troubleshooting Method 2:**
- If path not found, search for `ext4.vhdx` in Windows Explorer: `%LOCALAPPDATA%`
- The compaction process may take 5-30 minutes depending on disk size
- You'll see a progress indicator in diskpart

### Method 3 - Optimize-VHD (Advanced)

**Best for:** Systems with Hyper-V installed (Windows Pro/Enterprise)

```powershell
# Shutdown WSL
wsl --shutdown

# Wait for shutdown
Start-Sleep -Seconds 10

# Compact Ubuntu disk
Optimize-VHD -Path "$env:LOCALAPPDATA\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx" -Mode Full

# Compact Docker disk (if applicable)
Optimize-VHD -Path "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx" -Mode Full
```

**Note:** Requires Hyper-V feature installed. If you get "command not found", use Method 1 or 2 instead.

### How to Find Your VHDX File Location

If the default paths don't work, find your VHDX file:

1. **Using PowerShell:**
   ```powershell
   Get-ChildItem -Path "$env:LOCALAPPDATA" -Filter "ext4.vhdx" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
   ```

2. **Using Windows Explorer:**
   - Press `Win + R`
   - Type: `%LOCALAPPDATA%`
   - Search for `ext4.vhdx`

### Verifying the Compaction Worked

1. **Check VHDX file size in Windows:**
   ```powershell
   Get-Item "$env:LOCALAPPDATA\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx" | Select-Object Name, Length
   ```

2. **Compare before/after:**
   - Note the file size before compaction
   - Run the compaction
   - Check the file size after - it should be significantly smaller

3. **Check Windows disk space:**
   - Open File Explorer
   - Check C: drive (or wherever WSL is installed)
   - Space should be reclaimed

### Common Issues and Solutions

**Problem:** "The process cannot access the file because it is being used by another process"
- **Solution:** Make sure ALL WSL instances are shut down: `wsl --shutdown`, then close all Terminal/WSL windows

**Problem:** Compaction doesn't seem to free up much space
- **Solution:** Make sure you actually deleted files in WSL first. Run `df -h` in WSL to verify free space exists

**Problem:** Can't find the ext4.vhdx file
- **Solution:** Use the PowerShell search command above, or check if WSL is installed in a custom location

**Problem:** "Access is denied" error
- **Solution:** Make sure you're running PowerShell or diskpart as Administrator

**Problem:** Docker disk won't compact
- **Solution:**
  1. Shutdown Docker Desktop completely (right-click system tray → Quit Docker Desktop)
  2. Run `wsl --shutdown`
  3. Wait 30 seconds
  4. Try compaction again

### Best Practices

- **Compact regularly** - After major cleanups, always compact to reclaim space
- **Shutdown WSL completely** - `wsl --shutdown` ensures all instances are closed
- **Be patient** - Large disks (100GB+) can take 10-30 minutes to compact
- **Monitor progress** - Watch the VHDX file size in Windows Explorer during compaction
- **Schedule it** - Set a monthly reminder to cleanup + compact

## Docker Cleanup Safety

### Safe Operations (No Data Loss)
- Remove stopped containers
- Remove dangling images (untagged)
- Remove unused networks
- Remove build cache

### Operations That Can Cause Data Loss
- **Remove all unused images** - Removes images not in use by ANY container (running or stopped)
- **Remove unused volumes** - Can delete databases and persistent data

### Recommendation
Use Option 11 (Safe Docker cleanup) which combines all safe operations without risking data loss.

## Examples

### Example 1: First-time system analysis
```
1. Run ./storage_manager.py
2. Choose 1 (Storage Visualization)
3. Choose 1 (ncdu)
4. Navigate to find large directories
5. Note what's using space
6. Return to main menu
7. Choose 7 (Common space hogs quick check)
```

### Example 2: Quick cleanup
```
1. Run ./storage_manager.py
2. Choose 2 (System Cleanup)
3. Choose 8 (Run ALL safe cleanups)
4. Confirm when prompted
5. Check disk usage before/after
```

### Example 3: Docker cleanup
```
1. Run ./storage_manager.py
2. Choose 3 (Docker Management)
3. Review Docker storage (shows automatically)
4. Choose 11 (Safe Docker cleanup)
5. Confirm when prompted
```

### Example 4: Find large files
```
1. Run ./storage_manager.py
2. Choose 4 (Advanced Analysis)
3. Choose 1 (Find largest files)
4. Enter path and count
5. Review results
```

## Requirements

- Ubuntu 22.04 (or similar Linux distribution)
- Python 3 (pre-installed on Ubuntu 22)
- sudo privileges (recommended for full functionality)

### Optional but Recommended
- ncdu
- duf
- dust
- docker (if managing Docker storage)

## Troubleshooting

### "Permission denied" errors
Run with sudo for system-wide operations:
```bash
sudo ./storage_manager.py
```

### ncdu not found
Install it via the tool (Option 5) or manually:
```bash
sudo apt-get update
sudo apt-get install ncdu
```

### Docker commands not working
Make sure Docker is installed and you're in the docker group:
```bash
sudo usermod -aG docker $USER
```
Then log out and log back in.

### Disk space not reclaimed after cleanup
You need to compact the WSL virtual disk from Windows PowerShell:
```powershell
wsl --shutdown
wsl --manage Ubuntu-22.04 --set-sparse true
```

## Safety Notes

- Always review what will be deleted before confirming
- The tool never deletes without confirmation
- Docker volume operations are marked as DANGEROUS with multiple warnings
- Backup important data before major cleanups
- WSL disk compaction requires all WSL instances to be shut down

## Contributing

This tool was generated based on the storage cleanup requirements in `discoveryChat.md`. Feel free to extend it with additional features or improvements.

## License

This tool is provided as-is for storage management on Ubuntu systems.

## Credits

Based on common Linux storage management tools:
- ncdu (NCurses Disk Usage)
- du/df (disk usage utilities)
- dust (modern du alternative)
- duf (modern df alternative)
- Docker CLI

Inspired by the storage cleanup guide in discoveryChat.md.