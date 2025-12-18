#!/usr/bin/env python3
"""
Windows WSL Storage Manager - Companion Tool for Windows
Handles WSL disk compaction to reclaim space on Windows after Linux cleanup
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Set
import platform

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")

def _ps_escape_double_quotes(value: str) -> str:
    return value.replace('`', '``').replace('"', '`"')

def _parse_wsl_quiet_list(output: str) -> List[str]:
    distros: List[str] = []
    for raw in output.splitlines():
        cleaned = raw.replace('\x00', '').strip().lstrip('\ufeff')
        if cleaned:
            distros.append(cleaned)

    # De-duplicate while preserving order
    seen = set()
    unique: List[str] = []
    for d in distros:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique

def _is_wsl_manage_unsupported(output: str) -> bool:
    output_lower = (output or "").lower()
    return (
        "unknown option" in output_lower
        or "unrecognized option" in output_lower
        or "parameter is incorrect" in output_lower
        or "invalid command line option" in output_lower
    )

def _try_get_wsl_vhdx_path_from_registry(distro: str) -> Optional[str]:
    distro_arg = _ps_escape_double_quotes(distro)
    ps_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$name = \"{distro_arg}\"
$key = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss'
$item = Get-ChildItem -Path $key | ForEach-Object {{ Get-ItemProperty $_.PSPath }} | Where-Object {{ $_.DistributionName -eq $name }} | Select-Object -First 1
if ($null -eq $item) {{ exit 2 }}
$base = $item.BasePath
if ([string]::IsNullOrWhiteSpace($base)) {{ exit 3 }}
$vhdx = Join-Path -Path $base -ChildPath 'ext4.vhdx'
Write-Output $vhdx
"""
    code, output = run_powershell(ps_script, capture=True)

    if code != 0:
        return None

    path = (output or "").strip().splitlines()[-1].strip() if (output or "").strip() else ""
    if not path:
        return None
    if not os.path.exists(path):
        return None
    return path

def _try_get_docker_desktop_vhdx_path() -> Optional[str]:
    localappdata = os.environ.get('LOCALAPPDATA', '')
    if not localappdata:
        return None
    candidate = os.path.join(localappdata, 'Docker', 'wsl', 'data', 'ext4.vhdx')
    if os.path.exists(candidate):
        return candidate
    return None

def run_powershell(command: str, capture: bool = True, check: bool = False) -> Tuple[int, str]:
    """
    Run a PowerShell command and return exit code and output
    """
    try:
        ps_command = ['powershell', '-NoProfile', '-Command', command]

        if capture:
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                check=check,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode, result.stdout + result.stderr
        else:
            result = subprocess.run(ps_command, check=check)
            return result.returncode, ""
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e)
    except Exception as e:
        return 1, str(e)

def run_wsl_command(command: str, capture: bool = True) -> Tuple[int, str]:
    """Run a WSL command"""
    try:
        if capture:
            result = subprocess.run(
                ['wsl', '--'] + command.split(),
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode, result.stdout + result.stderr
        else:
            result = subprocess.run(['wsl', '--'] + command.split(), check=False)
            return result.returncode, ""
    except Exception as e:
        return 1, str(e)

def check_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == 'Windows'

def check_admin() -> bool:
    """Check if running as administrator"""
    try:
        code, output = run_powershell(
            '([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)',
            capture=True
        )
        return code == 0 and 'True' in output
    except:
        return False

def get_file_size_gb(path: str) -> float:
    """Get file size in GB"""
    try:
        size_bytes = os.path.getsize(path)
        return size_bytes / (1024 ** 3)
    except:
        return 0.0

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

class WindowsStorageManager:
    def __init__(self):
        self.is_admin = check_admin()
        self.wsl_distributions = []
        self.vhdx_files = {}

    def show_main_menu(self):
        """Display the main menu"""
        while True:
            print_header("Windows WSL Storage Manager")

            # Show admin status
            if self.is_admin:
                print_success("Running as Administrator - All features available")
            else:
                print_error("NOT running as Administrator - Some features unavailable")
                print_warning("Please run as Administrator for full functionality")

            print(f"\n{Colors.BOLD}Main Menu:{Colors.ENDC}")
            print(f"{Colors.CYAN}1.{Colors.ENDC} Show WSL Distributions & Disk Usage")
            print(f"{Colors.CYAN}2.{Colors.ENDC} Find & Show VHDX Files")
            print(f"{Colors.CYAN}3.{Colors.ENDC} Shutdown WSL")
            print(f"{Colors.CYAN}4.{Colors.ENDC} Compact WSL Disks (Modern Method)")
            print(f"{Colors.CYAN}5.{Colors.ENDC} Compact Using Diskpart (Manual)")
            print(f"{Colors.CYAN}6.{Colors.ENDC} Compact Using Optimize-VHD (Hyper-V)")
            print(f"{Colors.CYAN}7.{Colors.ENDC} Quick Compact All (Recommended)")
            print(f"{Colors.CYAN}8.{Colors.ENDC} Verify Compaction Results")
            print(f"{Colors.CYAN}9.{Colors.ENDC} Troubleshooting & Help")
            print(f"{Colors.RED}0.{Colors.ENDC} Exit")

            choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

            if choice == "1":
                self.show_wsl_distributions()
            elif choice == "2":
                self.find_and_show_vhdx_files()
            elif choice == "3":
                self.shutdown_wsl()
            elif choice == "4":
                self.compact_modern_method()
            elif choice == "5":
                self.compact_diskpart_method()
            elif choice == "6":
                self.compact_optimize_vhd()
            elif choice == "7":
                self.quick_compact_all()
            elif choice == "8":
                self.verify_compaction()
            elif choice == "9":
                self.show_troubleshooting()
            elif choice == "0":
                print_info("Exiting Windows Storage Manager. Goodbye!")
                sys.exit(0)
            else:
                print_error("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def show_wsl_distributions(self):
        """Show all WSL distributions and their status"""
        print_header("WSL Distributions")

        print_info("Checking WSL distributions...")
        code, output = run_powershell("wsl --list --verbose", capture=True)

        if code != 0:
            print_error("Failed to get WSL distributions")
            print_error("Make sure WSL is installed and configured")
            return

        print(f"\n{Colors.BOLD}WSL Distributions:{Colors.ENDC}")
        print(output)

        # Get disk usage for each distribution
        print(f"\n{Colors.BOLD}Disk Usage in Distributions:{Colors.ENDC}")
        code, output = run_powershell("wsl --list --quiet", capture=True)

        if code == 0:
            distros = _parse_wsl_quiet_list(output)
            for distro in distros:
                if distro:
                    # Try to get disk usage from within the distro
                    print(f"\n{Colors.CYAN}{distro}:{Colors.ENDC}")
                    distro_arg = _ps_escape_double_quotes(distro)
                    code, usage = run_powershell(f"wsl -d \"{distro_arg}\" df -h /", capture=True)
                    if code == 0:
                        print(usage)
                    else:
                        print_warning(f"Could not get disk usage for {distro}")

    def find_and_show_vhdx_files(self):
        """Find and display all VHDX files"""
        print_header("Finding VHDX Files")

        print_info("Searching for VHDX files (this may take a minute)...")

        localappdata = os.environ.get('LOCALAPPDATA', '')
        if not localappdata:
            print_error("Could not find LOCALAPPDATA directory")
            return

        # Search for VHDX files
        vhdx_files = []

        print_info(f"Searching in: {localappdata}")

        # Common locations
        search_paths = [
            os.path.join(localappdata, 'Packages'),
            os.path.join(localappdata, 'Docker'),
        ]

        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.lower().endswith('.vhdx'):
                            full_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(full_path)
                                vhdx_files.append({
                                    'path': full_path,
                                    'size': size,
                                    'name': file
                                })
                            except:
                                pass

        if not vhdx_files:
            print_warning("No VHDX files found")
            return

        # Sort by size (largest first)
        vhdx_files.sort(key=lambda x: x['size'], reverse=True)

        print(f"\n{Colors.BOLD}Found {len(vhdx_files)} VHDX file(s):{Colors.ENDC}\n")

        self.vhdx_files = {}
        for idx, vhdx in enumerate(vhdx_files, 1):
            size_str = format_size(vhdx['size'])
            size_gb = vhdx['size'] / (1024 ** 3)

            # Try to identify the distribution
            distro_name = "Unknown"
            path = vhdx['path']

            if 'Ubuntu' in path:
                if 'Ubuntu22' in path or 'Ubuntu-22' in path:
                    distro_name = "Ubuntu 22.04"
                elif 'Ubuntu20' in path or 'Ubuntu-20' in path:
                    distro_name = "Ubuntu 20.04"
                else:
                    distro_name = "Ubuntu"
            elif 'docker-desktop-data' in path.lower():
                distro_name = "Docker Desktop Data"
            elif 'docker' in path.lower():
                distro_name = "Docker"

            print(f"{Colors.CYAN}{idx}. {distro_name}{Colors.ENDC}")
            print(f"   Size: {Colors.BOLD}{size_str}{Colors.ENDC} ({size_gb:.2f} GB)")
            print(f"   Path: {path}\n")

            self.vhdx_files[idx] = vhdx

    def shutdown_wsl(self):
        """Shutdown all WSL instances"""
        print_header("Shutdown WSL")

        print_warning("This will shutdown ALL running WSL distributions")
        print_info("Any unsaved work in WSL will be lost!")

        if input("\nProceed with shutdown? (y/n): ").lower() != 'y':
            print_warning("Shutdown cancelled")
            return

        print_info("Shutting down WSL...")
        code, output = run_powershell("wsl --shutdown", capture=True)

        if code == 0:
            print_success("WSL shutdown successfully")
            print_info("Waiting 5 seconds for complete shutdown...")
            time.sleep(5)
        else:
            print_error(f"Failed to shutdown WSL: {output}")

    def compact_modern_method(self):
        """Compact using modern WSL method"""
        if not self.is_admin:
            print_error("This operation requires Administrator privileges")
            print_info("Please restart this program as Administrator")
            return

        print_header("Compact WSL Disks (Modern Method)")

        # Get list of distributions
        code, output = run_powershell("wsl --list --quiet", capture=True)
        if code != 0:
            print_error("Failed to get WSL distributions")
            return

        distros = _parse_wsl_quiet_list(output)

        if not distros:
            print_warning("No WSL distributions found")
            return

        print(f"{Colors.BOLD}Available distributions:{Colors.ENDC}")
        for idx, distro in enumerate(distros, 1):
            print(f"{idx}. {distro}")

        print(f"\n{Colors.BOLD}Options:{Colors.ENDC}")
        print("A. Compact all distributions")
        print("S. Select specific distribution")
        print("C. Cancel")

        choice = input("\nYour choice: ").strip().upper()

        if choice == 'C':
            print_warning("Compaction cancelled")
            return

        # Shutdown WSL first
        print_info("Shutting down WSL first...")
        run_powershell("wsl --shutdown", capture=True)
        print_info("Waiting 10 seconds for complete shutdown...")
        time.sleep(10)

        distributions_to_compact = []

        if choice == 'A':
            distributions_to_compact = distros
        elif choice == 'S':
            try:
                idx = int(input("Enter distribution number: ")) - 1
                if 0 <= idx < len(distros):
                    distributions_to_compact = [distros[idx]]
                else:
                    print_error("Invalid selection")
                    return
            except ValueError:
                print_error("Invalid input")
                return
        else:
            print_error("Invalid choice")
            return

        print(f"\n{Colors.BOLD}Compacting distributions...{Colors.ENDC}\n")

        for distro in distributions_to_compact:
            print(f"{Colors.CYAN}Compacting: {distro}{Colors.ENDC}")

            distro_arg = _ps_escape_double_quotes(distro)

            code, output = run_powershell(
                f"wsl --manage \"{distro_arg}\" --set-sparse true",
                capture=True
            )

            if code == 0:
                print_success(f"Successfully compacted {distro}")
            else:
                output_str = (output or "").strip()
                output_lower = output_str.lower()
                if "parameter is incorrect" in output_lower or "unknown option" in output_lower:
                    print_warning(f"Modern method not supported for {distro}")
                    print_info("Try using Diskpart method (Option 5) instead")
                else:
                    if output_str:
                        print_error(f"Failed to compact {distro}: {output_str}")
                    else:
                        print_error(f"Failed to compact {distro} (exit code {code})")

        print_success("\nCompaction process completed!")
        print_info("Check your disk space to verify space was reclaimed")

    def compact_diskpart_method(self):
        """Provide instructions for manual diskpart compaction"""
        if not self.is_admin:
            print_error("This operation requires Administrator privileges")
            print_info("Please restart this program as Administrator")
            return

        print_header("Compact Using Diskpart (Manual Method)")

        # First, find VHDX files if not already found
        if not self.vhdx_files:
            print_info("Finding VHDX files first...")
            self.find_and_show_vhdx_files()

        if not self.vhdx_files:
            print_error("No VHDX files found to compact")
            return

        print(f"\n{Colors.BOLD}Select VHDX file to compact:{Colors.ENDC}")
        for idx, vhdx in self.vhdx_files.items():
            size_gb = vhdx['size'] / (1024 ** 3)
            print(f"{idx}. {vhdx['name']} ({size_gb:.2f} GB)")

        print("A. Compact all")
        print("C. Cancel")

        choice = input("\nYour choice: ").strip().upper()

        if choice == 'C':
            print_warning("Compaction cancelled")
            return

        # Shutdown WSL
        print_info("\nShutting down WSL first...")
        run_powershell("wsl --shutdown", capture=True)
        print_info("Waiting 10 seconds...")
        time.sleep(10)

        files_to_compact = []

        if choice == 'A':
            files_to_compact = list(self.vhdx_files.values())
        else:
            try:
                idx = int(choice)
                if idx in self.vhdx_files:
                    files_to_compact = [self.vhdx_files[idx]]
                else:
                    print_error("Invalid selection")
                    return
            except ValueError:
                print_error("Invalid input")
                return

        print(f"\n{Colors.BOLD}Compacting VHDX files using Diskpart...{Colors.ENDC}\n")

        for vhdx in files_to_compact:
            path = vhdx['path']

            print(f"{Colors.CYAN}Compacting: {vhdx['name']}{Colors.ENDC}")
            print(f"Path: {path}")
            print(f"Size before: {format_size(vhdx['size'])}")
            print_info("Running diskpart (this may take several minutes)...")

            ok, err = self._compact_vhdx_diskpart(path)
            if ok:
                try:
                    new_size = os.path.getsize(path)
                    old_size = vhdx['size']
                    saved = old_size - new_size

                    print_success("Compaction completed!")
                    print(f"Size after: {format_size(new_size)}")
                    print(f"Space saved: {format_size(saved)}")
                except:
                    print_success("Compaction completed!")
            else:
                if err:
                    print_error(f"Diskpart failed: {err}")
                else:
                    print_error("Diskpart failed")

            print()

    def _is_optimize_vhd_available(self) -> bool:
        code, output = run_powershell(
            "Get-Command Optimize-VHD -ErrorAction SilentlyContinue | Select-Object -First 1",
            capture=True,
        )
        return code == 0 and bool((output or "").strip())

    def _compact_vhdx_optimize_vhd(self, path: str) -> Tuple[bool, str]:
        code, output = run_powershell(
            f'Optimize-VHD -Path "{path}" -Mode Full',
            capture=True,
        )
        if code == 0:
            return True, ""
        return False, (output or "").strip()

    def _compact_vhdx_diskpart(self, path: str) -> Tuple[bool, str]:
        diskpart_script = f"""select vdisk file=\"{path}\"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"""
        try:
            process = subprocess.Popen(
                ['diskpart'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(input=diskpart_script, timeout=1800)
            if process.returncode == 0:
                return True, ""
            combined = ((stdout or "") + "\n" + (stderr or "")).strip()
            return False, combined
        except subprocess.TimeoutExpired:
            return False, "Diskpart timed out (file too large or disk busy)"
        except Exception as e:
            return False, str(e)

    def compact_optimize_vhd(self):
        """Compact using Optimize-VHD cmdlet"""
        if not self.is_admin:
            print_error("This operation requires Administrator privileges")
            print_info("Please restart this program as Administrator")
            return

        print_header("Compact Using Optimize-VHD (Hyper-V Method)")

        print_info("Checking if Optimize-VHD is available (requires Hyper-V)...")

        code, output = run_powershell(
            "Get-Command Optimize-VHD -ErrorAction SilentlyContinue",
            capture=True
        )

        if code != 0 or not output.strip():
            print_error("Optimize-VHD cmdlet not found")
            print_warning("This requires Hyper-V to be installed")
            print_info("Install Hyper-V or use Diskpart method (Option 5) instead")
            return

        # Find VHDX files if not already found
        if not self.vhdx_files:
            print_info("Finding VHDX files first...")
            self.find_and_show_vhdx_files()

        if not self.vhdx_files:
            print_error("No VHDX files found to compact")
            return

        print(f"\n{Colors.BOLD}Select VHDX file to compact:{Colors.ENDC}")
        for idx, vhdx in self.vhdx_files.items():
            size_gb = vhdx['size'] / (1024 ** 3)
            print(f"{idx}. {vhdx['name']} ({size_gb:.2f} GB)")

        print("A. Compact all")
        print("C. Cancel")

        choice = input("\nYour choice: ").strip().upper()

        if choice == 'C':
            print_warning("Compaction cancelled")
            return

        # Shutdown WSL
        print_info("\nShutting down WSL first...")
        run_powershell("wsl --shutdown", capture=True)
        print_info("Waiting 10 seconds...")
        time.sleep(10)

        files_to_compact = []

        if choice == 'A':
            files_to_compact = list(self.vhdx_files.values())
        else:
            try:
                idx = int(choice)
                if idx in self.vhdx_files:
                    files_to_compact = [self.vhdx_files[idx]]
                else:
                    print_error("Invalid selection")
                    return
            except ValueError:
                print_error("Invalid input")
                return

        print(f"\n{Colors.BOLD}Optimizing VHDX files...{Colors.ENDC}\n")

        for vhdx in files_to_compact:
            path = vhdx['path']
            print(f"{Colors.CYAN}Optimizing: {vhdx['name']}{Colors.ENDC}")
            print(f"Size before: {format_size(vhdx['size'])}")

            print_info("Running Optimize-VHD (this may take several minutes)...")

            code, output = run_powershell(
                f'Optimize-VHD -Path "{path}" -Mode Full',
                capture=True
            )

            if code == 0:
                try:
                    new_size = os.path.getsize(path)
                    old_size = vhdx['size']
                    saved = old_size - new_size

                    print_success("Optimization completed!")
                    print(f"Size after: {format_size(new_size)}")
                    print(f"Space saved: {format_size(saved)}")
                except:
                    print_success("Optimization completed!")
            else:
                print_error(f"Optimize-VHD failed: {output}")

            print()

    def quick_compact_all(self):
        """Quick compact all distributions using the best available method"""
        if not self.is_admin:
            print_error("This operation requires Administrator privileges")
            print_info("Please restart this program as Administrator")
            return

        print_header("Quick Compact All WSL Disks")

        print_warning("This will compact ALL WSL distributions to reclaim disk space")
        print_info("This is the recommended option after cleaning up files in WSL")
        print()
        print(f"{Colors.BOLD}This will:{Colors.ENDC}")
        print("  1. Shutdown all WSL instances")
        print("  2. Compact all WSL distribution disks")
        print("  3. Compact Docker Desktop disk (if present)")
        print()
        print_warning("Estimated time: 5-30 minutes depending on disk sizes")
        print()

        if input("Proceed with compaction? (y/n): ").lower() != 'y':
            print_warning("Compaction cancelled")
            return

        # Get distributions
        code, output = run_powershell("wsl --list --quiet", capture=True)
        if code != 0:
            print_error("Failed to get WSL distributions")
            return

        distros = _parse_wsl_quiet_list(output)

        if not distros:
            print_warning("No WSL distributions found")
            return

        # Shutdown WSL
        print_info("\nStep 1: Shutting down WSL...")
        run_powershell("wsl --shutdown", capture=True)
        print_info("Waiting 10 seconds for complete shutdown...")
        time.sleep(10)
        print_success("WSL shutdown complete")

        # Compact distributions
        print(f"\n{Colors.BOLD}Step 2: Compacting distributions...{Colors.ENDC}\n")

        success_count = 0
        failed_count = 0

        compacted_paths: Set[str] = set()
        optimize_vhd_available = self._is_optimize_vhd_available()

        def compact_vhdx_path(label: str, vhdx_path: str) -> bool:
            if vhdx_path in compacted_paths:
                return True
            before_size = get_file_size_gb(vhdx_path)
            if optimize_vhd_available:
                ok, err = self._compact_vhdx_optimize_vhd(vhdx_path)
            else:
                ok, err = self._compact_vhdx_diskpart(vhdx_path)
            if ok:
                compacted_paths.add(vhdx_path)
                after_size = get_file_size_gb(vhdx_path)
                saved = max(0.0, before_size - after_size)
                print_success(f"{label} compacted ({saved:.2f} GB saved)")
                return True
            if err:
                print_error(f"Failed to compact {label}: {err}")
            else:
                print_error(f"Failed to compact {label}")
            return False

        for distro in distros:
            print(f"{Colors.CYAN}Compacting: {distro}{Colors.ENDC}")

            distro_arg = _ps_escape_double_quotes(distro)

            code, output = run_powershell(
                f"wsl --manage \"{distro_arg}\" --set-sparse true",
                capture=True
            )

            if code == 0:
                print_success(f"{distro} compacted successfully")
                success_count += 1
            else:
                output_str = (output or "").strip()
                if _is_wsl_manage_unsupported(output_str):
                    print_warning(f"Modern method not supported for {distro}")
                else:
                    if output_str:
                        print_warning(f"Modern method failed for {distro}: {output_str}")
                    else:
                        print_warning(f"Modern method failed for {distro} (exit code {code})")

                vhdx_path = _try_get_wsl_vhdx_path_from_registry(distro)
                if not vhdx_path:
                    print_error(f"Could not locate VHDX for {distro}")
                    failed_count += 1
                    continue

                if compact_vhdx_path(distro, vhdx_path):
                    success_count += 1
                else:
                    failed_count += 1

        docker_vhdx = _try_get_docker_desktop_vhdx_path()
        if docker_vhdx:
            print(f"\n{Colors.BOLD}Step 3: Compacting Docker Desktop disk...{Colors.ENDC}\n")
            if compact_vhdx_path("Docker Desktop", docker_vhdx):
                success_count += 1
            else:
                failed_count += 1

        print(f"\n{Colors.BOLD}Compaction Summary:{Colors.ENDC}")
        print(f"  Successfully compacted: {success_count}")
        if failed_count > 0:
            print(f"  Failed: {failed_count}")

        print_success("\nCompaction process completed!")
        print_info("Check your Windows disk space to see reclaimed space")
        print_info("Run Option 8 (Verify Compaction Results) to confirm")

    def verify_compaction(self):
        """Verify compaction results"""
        print_header("Verify Compaction Results")

        print_info("Checking VHDX file sizes and disk space...")

        # Find VHDX files
        self.find_and_show_vhdx_files()

        # Get Windows disk space
        print(f"\n{Colors.BOLD}Windows Disk Space:{Colors.ENDC}")
        code, output = run_powershell(
            "Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -ne $null} | Format-Table Name, @{Label='Used(GB)';Expression={[math]::Round($_.Used/1GB,2)}}, @{Label='Free(GB)';Expression={[math]::Round($_.Free/1GB,2)}}, @{Label='Total(GB)';Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}} -AutoSize",
            capture=True
        )
        if code == 0:
            print(output)

        print(f"\n{Colors.BOLD}Tips:{Colors.ENDC}")
        print("• Compare VHDX file sizes with what you expect after cleanup")
        print("• Check Windows C: drive free space - it should have increased")
        print("• If space wasn't reclaimed, try the Diskpart method (Option 5)")

    def show_troubleshooting(self):
        """Show troubleshooting information"""
        print_header("Troubleshooting & Help")

        print(f"{Colors.BOLD}Common Issues and Solutions:{Colors.ENDC}\n")

        print(f"{Colors.CYAN}1. \"Not running as Administrator\"{Colors.ENDC}")
        print("   Solution: Close this program and re-run it as Administrator")
        print("   • Press Win+X → Select 'Terminal (Admin)' or 'PowerShell (Admin)'")
        print("   • Or right-click the script → 'Run as administrator'\n")

        print(f"{Colors.CYAN}2. \"The parameter is incorrect\" (Modern method){Colors.ENDC}")
        print("   Solution: Your WSL version doesn't support the modern method")
        print("   • Use Option 5 (Diskpart method) instead")
        print("   • Or update WSL: Run 'wsl --update' in PowerShell\n")

        print(f"{Colors.CYAN}3. \"Process cannot access the file\"{Colors.ENDC}")
        print("   Solution: WSL is still running or file is in use")
        print("   • Make sure all WSL/Ubuntu windows are closed")
        print("   • Run Option 3 (Shutdown WSL) first")
        print("   • Wait 30 seconds, then try again")
        print("   • If using Docker, quit Docker Desktop completely\n")

        print(f"{Colors.CYAN}4. Compaction doesn't free much space{Colors.ENDC}")
        print("   Solution: Make sure you deleted files in WSL first!")
        print("   • Run the Linux storage manager in WSL first")
        print("   • Clean up files, Docker images, etc.")
        print("   • Then come back and compact on Windows\n")

        print(f"{Colors.CYAN}5. Can't find VHDX files{Colors.ENDC}")
        print("   Solution: Use Option 2 to locate them")
        print("   • Common locations:")
        print("     %LOCALAPPDATA%\\Packages\\*Ubuntu*\\LocalState\\ext4.vhdx")
        print("     %LOCALAPPDATA%\\Docker\\wsl\\data\\ext4.vhdx\n")

        print(f"{Colors.CYAN}6. Optimize-VHD not found{Colors.ENDC}")
        print("   Solution: Hyper-V is not installed")
        print("   • Use Option 4 (Modern method) or Option 5 (Diskpart) instead")
        print("   • Or install Hyper-V feature (Windows Pro/Enterprise only)\n")

        print(f"{Colors.BOLD}Recommended Workflow:{Colors.ENDC}")
        print("1. Clean up files in WSL using the Linux storage manager")
        print("2. Come to Windows and run Option 7 (Quick Compact All)")
        print("3. Run Option 8 (Verify) to confirm space was reclaimed")
        print("4. If modern method fails, use Option 5 (Diskpart) instead\n")

        print(f"{Colors.BOLD}Need more help?{Colors.ENDC}")
        print("• Check README.md for detailed documentation")
        print("• WSL documentation: https://docs.microsoft.com/en-us/windows/wsl/")

def main():
    """Main entry point"""

    # Check if running on Windows
    if not check_windows():
        print_error("This tool must be run on Windows!")
        print_info("This is the Windows-side companion to the Linux storage manager")
        print_info("Use storage_manager.py on Linux/WSL instead")
        sys.exit(1)

    # Check admin status
    is_admin = check_admin()

    print_header("Windows WSL Storage Manager")
    print(f"{Colors.BOLD}Windows-side companion tool for WSL disk compaction{Colors.ENDC}\n")

    if not is_admin:
        print_warning("WARNING: Not running as Administrator!")
        print_warning("Most features require Administrator privileges")
        print()
        print(f"{Colors.BOLD}To run as Administrator:{Colors.ENDC}")
        print("1. Press Win+X on your keyboard")
        print("2. Select 'Terminal (Admin)' or 'Windows PowerShell (Admin)'")
        print("3. Navigate to this directory and run the script again")
        print()

        if input("Continue anyway? (y/n): ").lower() != 'y':
            print_info("Please restart as Administrator for full functionality")
            sys.exit(0)

    # Check WSL is installed
    code, _ = run_powershell("wsl --list", capture=True)
    if code != 0:
        print_error("WSL does not appear to be installed or configured")
        print_info("Install WSL first: https://docs.microsoft.com/en-us/windows/wsl/install")
        sys.exit(1)

    manager = WindowsStorageManager()
    manager.show_main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
