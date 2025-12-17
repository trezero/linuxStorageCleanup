# Quick Start Guide

## ⚠️ IMPORTANT: Two-Step Process

Storage cleanup in WSL requires **TWO steps**:
1. **Delete files in WSL** (using this tool)
2. **Compact disk in Windows** (using PowerShell)

**Without step 2, Windows will NOT reclaim the freed space!**

---

## First Time Setup

1. Make the script executable (already done):
```bash
chmod +x storage_manager.py
```

2. Run the tool:
```bash
./storage_manager.py
```

Or with sudo for full system access:
```bash
sudo ./storage_manager.py
```

---

## Complete Cleanup Workflow (FOLLOW ALL STEPS)

### Step 1: Find What's Using Space (In WSL)
1. Run `./storage_manager.py`
2. Select **1** (Storage Visualization)
3. Select **1** (ncdu) - Most user-friendly option
   - If not installed, the tool will offer to install it
4. Navigate with arrow keys to explore directories
5. Press 'q' to quit ncdu when done

### Step 2: Clean Up Files (In WSL)
1. Run `./storage_manager.py`
2. Select **2** (System Cleanup)
3. Select **8** (Run ALL safe cleanups)
4. Confirm when prompted
5. Note how much space was freed

### Step 3: Docker Cleanup - Optional (In WSL)
If you use Docker:
1. Run `./storage_manager.py`
2. Select **3** (Docker Management)
3. Choose one of:
   - **11** (Safe Docker cleanup) - No data loss, frees ~10-20GB
   - **9** (Remove unused images) - Can free 100+ GB, safe but removes images

### Step 4: ⚠️ COMPACT WSL DISK (In Windows - REQUIRED!)

**This is the most important step!** Without this, Windows won't reclaim the space.

#### How to Do It:

1. **Close all WSL/Ubuntu windows completely**

2. **Open Windows PowerShell as Administrator:**
   - Press `Win + X` on your keyboard
   - Click "Windows PowerShell (Admin)" or "Terminal (Admin)"
   - If prompted by UAC, click "Yes"

3. **Run these commands in PowerShell:**
   ```powershell
   # Shutdown all WSL instances
   wsl --shutdown

   # Wait 10 seconds
   Start-Sleep -Seconds 10

   # Compact Ubuntu disk (this reclaims the space!)
   wsl --manage Ubuntu-22.04 --set-sparse true

   # If you use Docker, also compact Docker disk
   wsl --manage docker-desktop-data --set-sparse true
   ```

4. **Wait for completion** (may take 5-30 minutes for large disks)

5. **Verify space was reclaimed:**
   - Open File Explorer
   - Check C: drive free space - it should have increased!

#### Alternative Methods (If Above Doesn't Work):

**Method 2 - Using Diskpart:**
```powershell
wsl --shutdown
diskpart
```

Then in diskpart:
```
select vdisk file="%LOCALAPPDATA%\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx"
compact vdisk
detach vdisk
exit
```

For full details and troubleshooting, see `README.md` section "WSL Disk Compaction"

## Menu Overview

```
Main Menu:
├─ 1. Storage Visualization     ← Start here to see what's using space
├─ 2. System Cleanup (Safe)     ← Clean up system files safely
├─ 3. Docker Management         ← Clean Docker if installed
├─ 4. Advanced Analysis         ← Find large/old files
├─ 5. Check & Install Tools     ← Install ncdu, duf, dust
└─ 6. WSL Compaction Info       ← How to reclaim space on Windows
```

## Safety Tips

- Green text = Safe operations
- Yellow text = Caution
- Red text = Potentially dangerous
- All destructive operations require confirmation
- The tool NEVER deletes without asking first

## Recommended First-Time Flow

1. **Analyze** - Use ncdu to see what's using space
2. **Cleanup** - Run safe system cleanup
3. **Docker** - Clean Docker if you use it
4. **Compact** - Compact WSL disk from Windows PowerShell

## Getting Help

- View full documentation: `cat README.md`
- Each menu shows what operations do
- All operations have confirmation prompts
- Press Ctrl+C to cancel at any time
