# Updates Needed for linuxStorageCleanup Application

## Executive Summary
Based on the successful manual cleanup that reclaimed **131+ GB** from a Windows system with Docker, this document outlines the specific features and improvements needed for the linuxStorageCleanup application to automate this process.

---

## 1. Docker Storage Analysis and Cleanup

### 1.1 Docker Disk Usage Analysis
**Priority: HIGH**

**Requirements:**
- Execute `docker system df` to get total space usage
- Execute `docker system df -v` for detailed breakdown including:
  - Images (tagged and untagged)
  - Containers (running and stopped)
  - Volumes (attached and orphaned)
  - Build cache
- Display results in a user-friendly format showing:
  - Total space used
  - Reclaimable space
  - Percentage breakdown by type

**Implementation Notes:**
```powershell
# Command to use
docker system df -v
```

### 1.2 Image Management
**Priority: HIGH**

**Requirements:**
- List ALL Docker images including intermediates: `docker images -a`
- Identify and flag:
  - Images with **0 containers** (completely unused) - HIGH priority for removal
  - Images with only **exited/stopped** containers - MEDIUM priority
  - Old images (>6 months, >1 year, >2 years) - Flag for review
- Show image sizes in GB for easy assessment
- Provide bulk removal capability for:
  - All dangling images: `docker image prune -f`
  - All unused images: `docker image prune -a -f`
  - Specific images by age or pattern

**Key Learning:**
Our cleanup removed images like:
- pytorch/pytorch (10.9 GB, 2 years old, 0 containers)
- milvusdb/milvus (1.29 GB, 23 months old, 0 containers)
- nvidia/cuda (338 MB, 2 years old, 0 containers)

### 1.3 Container Cleanup
**Priority: MEDIUM**

**Requirements:**
- List all containers with status (running/exited)
- Show container size (writeable layer)
- Identify containers stopped for >30 days
- Provide options to:
  - Remove all stopped containers: `docker container prune -f`
  - Remove specific containers by age or pattern
  - Preserve important containers (allow user-defined exclusion list)

**Command:**
```powershell
docker container prune -f
```

### 1.4 Volume Management
**Priority: HIGH**

**Requirements:**
- List all volumes with:
  - Size (in GB)
  - Number of links (attached containers)
  - Last modified date
- Identify orphaned volumes (0 links) - These are prime for deletion
- Show volume size breakdown
- Warn user before removing volumes (data loss risk!)
- Provide options to:
  - Remove all unused volumes: `docker volume prune -f`
  - Remove specific volumes by name or pattern

**Key Learning:**
Our cleanup identified volumes like:
- localai_ollama_storage (4.96 GB)
- localai_langfuse_clickhouse_data (2.46 GB)
- localai_open-webui (2.01 GB)

### 1.5 Build Cache Cleanup
**Priority: MEDIUM**

**Requirements:**
- Display build cache size
- Option to clear all build cache: `docker builder prune -a -f`
- This is often a hidden space hog!

---

## 2. Docker VHDX Management (Windows-specific)

### 2.1 VHDX Location Detection
**Priority: CRITICAL**

**Requirements:**
- Auto-detect Docker VHDX file location:
  - Primary: `C:\Users\<username>\AppData\Local\Docker\wsl\disk\docker_data.vhdx`
  - Fallback: Search for `*.vhdx` in Docker-related paths
- Display current VHDX file size
- Calculate potential savings (VHDX size - actual Docker data usage)

**Implementation:**
```powershell
# Find VHDX files
Get-ChildItem -Path "$env:LOCALAPPDATA\Docker" -Filter "*.vhdx" -Recurse -ErrorAction SilentlyContinue

# Check specific location
Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
```

### 2.2 VHDX Compaction
**Priority: CRITICAL**

**Requirements:**
- **CRITICAL INSIGHT:** VHDX files do NOT shrink automatically after Docker cleanup!
- Must implement VHDX compaction after cleanup
- Detect if Hyper-V is available
- Provide multiple compaction methods:

#### Method 1: Hyper-V (if available)
```powershell
# Stop Docker Desktop
Stop-Process -Name "Docker Desktop" -Force
Start-Sleep -Seconds 10

# Compact VHDX
Optimize-VHD -Path "C:\Users\winadmin\AppData\Local\Docker\wsl\disk\docker_data.vhdx" -Mode Full
```

#### Method 2: WSL (fallback)
```powershell
# Shutdown WSL
wsl --shutdown

# Set sparse flag
wsl --manage docker-desktop-data --set-sparse true
```

#### Method 3: Diskpart (universal fallback)
```powershell
# Create diskpart script
@"
select vdisk file="C:\Users\<username>\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@ | Out-File -FilePath "$env:TEMP\compact-docker.txt" -Encoding ASCII

# Execute
diskpart /s "$env:TEMP\compact-docker.txt"
```

**WARNING:** Application must:
1. Verify Docker Desktop is fully stopped before compaction
2. Warn user that compaction may take 10-30+ minutes
3. Show progress if possible
4. Verify Docker restarts successfully after compaction

### 2.3 Other VHDX Files
**Priority: MEDIUM**

**Requirements:**
- Search for ALL `.vhdx` files on system
- Common locations:
  - `C:\Users\<username>\AppData\Local\Packages\*Ubuntu*`
  - `C:\Users\<username>\AppData\Local\Packages\*Docker*`
  - `C:\ProgramData\Docker`
- Report WSL distro VHDX files separately
- Offer to compact WSL distros as well

---

## 3. Pagefile Management (Windows)

### 3.1 Pagefile Detection and Sizing
**Priority: MEDIUM**

**Requirements:**
- Detect current pagefile.sys location(s) and size
- Check system RAM amount
- Provide recommendations:
  - System with 16+ GB RAM: Reduce to 2-4 GB or move to another drive
  - System with 8-16 GB RAM: Reduce to 4-8 GB
  - System with <8 GB RAM: Keep system-managed

### 3.2 Pagefile Configuration UI
**Priority: MEDIUM**

**Requirements:**
- Provide GUI/wizard to:
  - Disable pagefile on C: drive
  - Move pagefile to another drive (if available)
  - Set custom size (initial and maximum)
  - Restore to system-managed
- Warn user that restart is required
- Provide instructions for manual configuration via System Properties

**Registry paths to modify:**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management
```

---

## 4. Monitoring and Prevention

### 4.1 Real-time Monitoring
**Priority: LOW**

**Requirements:**
- Monitor Docker VHDX file size growth
- Alert when disk space falls below threshold (e.g., 20 GB free)
- Periodic scans (weekly/monthly) to identify cleanup opportunities

### 4.2 Scheduled Cleanup
**Priority: LOW**

**Requirements:**
- Schedule automatic cleanup tasks:
  - Weekly: Remove stopped containers and dangling images
  - Monthly: Remove unused images and volumes (with user confirmation)
  - After cleanup: Auto-compact VHDX

---

## 5. User Experience Improvements

### 5.1 Pre-flight Checks
**Priority: HIGH**

**Requirements:**
- Verify Docker Desktop is installed
- Check if Docker is running
- Detect OS (Windows 10/11, WSL version)
- Check for Hyper-V availability
- Warn if critical processes are running

### 5.2 Safe Mode Operations
**Priority: HIGH**

**Requirements:**
- **Never delete running containers or their volumes**
- Always show preview of what will be deleted before executing
- Provide dry-run mode showing potential savings
- Create restore points or backups before major operations
- Log all cleanup actions with timestamps

### 5.3 Progress Reporting
**Priority: MEDIUM**

**Requirements:**
- Real-time progress for long operations (cleanup, compaction)
- Estimated time remaining
- Clear success/failure messages
- Show before/after disk space comparison

### 5.4 Exclusion Management
**Priority: MEDIUM**

**Requirements:**
- Allow users to mark images/containers/volumes as "protected"
- Support pattern matching (e.g., "keep all images matching postgres*")
- Persist exclusion list across sessions

---

## 6. Error Handling

### 6.1 Common Failure Scenarios
**Priority: HIGH**

**Requirements:**
Handle these common issues we encountered:
1. **`docker system prune` hanging**
   - Implement timeout (30 minutes)
   - Offer to cancel and use step-by-step approach
   - Fallback to individual cleanup commands

2. **`Optimize-VHD` failing** (Hyper-V not installed)
   - Auto-detect and use alternative methods (WSL/diskpart)
   - Provide clear error messages

3. **Permission errors**
   - Check for Administrator privileges
   - Prompt user to run as Admin if needed

4. **Docker Desktop not responding**
   - Detect hung processes
   - Offer to force-kill and restart
   - Verify Docker is fully stopped before VHDX operations

---

## 7. Reporting and Analytics

### 7.1 Cleanup Summary Report
**Priority: MEDIUM**

**Requirements:**
Generate report showing:
- Total space reclaimed
- Breakdown by category (images, containers, volumes, VHDX compaction)
- Items removed (count and size)
- Time taken
- Before/after snapshots
- Recommendations for future cleanups

### 7.2 Export Options
**Priority: LOW**

**Requirements:**
- Export reports to:
  - Markdown
  - HTML
  - CSV
  - JSON

---

## 8. Technical Implementation Notes

### 8.1 PowerShell Integration
**Requirements:**
- All Docker commands should be executed via PowerShell
- Handle PowerShell output parsing
- Support both PowerShell 5.1 and PowerShell 7+

### 8.2 Execution Order
**CRITICAL - Must follow this sequence:**

1. **Analysis Phase:**
   - Run `docker system df -v`
   - Scan for VHDX files
   - Calculate potential savings

2. **Cleanup Phase:**
   - Stop Docker Desktop (if doing VHDX compaction)
   - Execute Docker cleanup commands in order:
     - `docker container prune -f`
     - `docker image prune -a -f`
     - `docker volume prune -f` (with confirmation!)
     - `docker builder prune -a -f`

3. **Compaction Phase:**
   - Verify Docker is stopped
   - Run `wsl --shutdown`
   - Execute VHDX compaction (one of three methods)
   - Wait for completion
   - Restart Docker Desktop

4. **Verification Phase:**
   - Re-run `docker system df`
   - Check VHDX file size
   - Compare before/after
   - Generate report

### 8.3 Multi-threading Considerations
**Requirements:**
- Long operations (cleanup, compaction) should run in background
- UI should remain responsive
- Provide cancel button (where safe)
- Log output in real-time

---

## 9. Testing Requirements

### 9.1 Test Scenarios
**Priority: HIGH**

Must test:
- ✅ Large Docker installation (100+ GB)
- ✅ Hyper-V enabled systems
- ✅ Hyper-V disabled systems (WSL-only)
- ✅ Multiple VHDX files
- ✅ Cleanup while containers are running
- ✅ Network failure during cleanup
- ✅ Insufficient permissions
- ✅ Disk full scenarios

---

## 10. Documentation

### 10.1 User Documentation
**Priority: MEDIUM**

**Requirements:**
- Quick start guide
- Troubleshooting section covering:
  - Hung cleanup operations
  - Hyper-V not available
  - Permission errors
  - VHDX compaction failures
- FAQ covering:
  - "Why didn't my disk space free up after cleanup?" (VHDX compaction!)
  - "Is it safe to remove all volumes?"
  - "What if cleanup hangs?"
  - "How often should I run this?"

### 10.2 Developer Documentation
**Priority: LOW**

**Requirements:**
- Architecture overview
- API documentation
- Contributing guide
- Testing guide

---

## Summary of Key Learnings from Manual Cleanup

### Critical Insights:
1. **VHDX files DO NOT shrink automatically** - This is the #1 reason users don't see disk space freed
2. **docker system prune can hang** on large datasets - Need timeout and fallback
3. **Three methods for VHDX compaction** needed for compatibility
4. **Volumes contain the most critical data** - Always warn before deletion
5. **Images with 0 containers** are the safest to remove
6. **Build cache is often overlooked** but can be large

### Cleanup Impact (from our session):
- Started: 420.3 GB total, 430 MB free (0.1%)
- Ended: 420.3 GB total, 131+ GB free (31%+)
- **Reclaimed: ~130 GB**

### Breakdown:
- Docker image cleanup: ~14 GB (unused images)
- Docker volume cleanup: ~10 GB (optional)
- **VHDX compaction: ~100-110 GB** (THE BIG ONE!)
- Pagefile reduction: ~4-8 GB (optional)

---

## Recommended Implementation Priority

### Phase 1 (MVP - Core Functionality):
1. Docker disk usage analysis (`docker system df -v`)
2. Docker cleanup commands (containers, images, volumes, cache)
3. VHDX compaction (all three methods with auto-detection)
4. Before/after reporting

### Phase 2 (Enhanced Safety):
1. Pre-flight checks and validation
2. Dry-run mode
3. Exclusion list management
4. Better error handling and recovery

### Phase 3 (User Experience):
1. Progress reporting
2. Scheduled cleanups
3. Monitoring and alerts
4. Export reports

### Phase 4 (Advanced Features):
1. Pagefile management
2. WSL distro management
3. Advanced analytics
4. API/CLI interface

---

## Estimated Impact

**If properly implemented, this application should:**
- Reclaim 50-150 GB on typical development systems
- Reduce cleanup time from 60+ minutes (manual) to 10-20 minutes (automated)
- Prevent common failures (hanging cleanup, missing compaction)
- Provide clear visibility into Docker storage usage
- Make VHDX compaction accessible to non-technical users

---

**Document Version:** 1.0  
**Date:** December 18, 2025  
**Based on:** Real-world cleanup session reclaiming 131+ GB