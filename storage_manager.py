#!/usr/bin/env python3
"""
Linux Storage Manager - Comprehensive CLI Tool
A menu-driven tool to visualize and manage storage space on Ubuntu 22 WSL
"""

import os
import sys
import subprocess
import shutil
from typing import Optional, List, Tuple
from pathlib import Path

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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

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

def run_command(cmd: str, shell: bool = True, capture: bool = False) -> Tuple[int, str]:
    """
    Run a shell command and return exit code and output
    """
    try:
        if capture:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, result.stdout + result.stderr
        else:
            result = subprocess.run(cmd, shell=shell, check=False)
            return result.returncode, ""
    except Exception as e:
        return 1, str(e)

def check_tool_installed(tool: str) -> bool:
    """Check if a command-line tool is installed"""
    return shutil.which(tool) is not None

def check_sudo() -> bool:
    """Check if user has sudo privileges"""
    code, _ = run_command("sudo -n true 2>/dev/null", capture=True)
    return code == 0

def get_disk_usage() -> str:
    """Get disk usage summary"""
    code, output = run_command("df -h /", capture=True)
    return output if code == 0 else "Unable to get disk usage"

def install_tool(tool: str) -> bool:
    """Attempt to install a missing tool"""
    print_info(f"Installing {tool}...")
    code, _ = run_command(f"sudo apt-get update && sudo apt-get install -y {tool}")
    return code == 0

class StorageManager:
    def __init__(self):
        self.has_sudo = check_sudo()

    def show_main_menu(self):
        """Display the main menu"""
        while True:
            print_header("Linux Storage Manager")

            # Show disk usage summary
            print(f"{Colors.BOLD}Current Disk Usage:{Colors.ENDC}")
            print(get_disk_usage())

            print(f"\n{Colors.BOLD}Main Menu:{Colors.ENDC}")
            print(f"{Colors.CYAN}1.{Colors.ENDC} Storage Visualization")
            print(f"{Colors.CYAN}2.{Colors.ENDC} System Cleanup (Safe)")
            print(f"{Colors.CYAN}3.{Colors.ENDC} Docker Management")
            print(f"{Colors.CYAN}4.{Colors.ENDC} Advanced Analysis")
            print(f"{Colors.CYAN}5.{Colors.ENDC} Check & Install Tools")
            print(f"{Colors.CYAN}6.{Colors.ENDC} WSL Disk Compaction Info")
            print(f"{Colors.RED}0.{Colors.ENDC} Exit")

            if not self.has_sudo:
                print_warning("Running without sudo - some features may be limited")

            choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

            if choice == "1":
                self.storage_visualization_menu()
            elif choice == "2":
                self.system_cleanup_menu()
            elif choice == "3":
                self.docker_management_menu()
            elif choice == "4":
                self.advanced_analysis_menu()
            elif choice == "5":
                self.check_install_tools()
            elif choice == "6":
                self.show_wsl_compaction_info()
            elif choice == "0":
                print_info("Exiting Storage Manager. Goodbye!")
                sys.exit(0)
            else:
                print_error("Invalid option. Please try again.")
                input("Press Enter to continue...")

    def storage_visualization_menu(self):
        """Storage visualization submenu"""
        while True:
            print_header("Storage Visualization")

            print(f"{Colors.BOLD}Visualization Options:{Colors.ENDC}")
            print(f"{Colors.CYAN}1.{Colors.ENDC} Interactive disk usage (ncdu) - RECOMMENDED")
            print(f"{Colors.CYAN}2.{Colors.ENDC} Quick directory size overview (du)")
            print(f"{Colors.CYAN}3.{Colors.ENDC} Filesystem overview (df)")
            print(f"{Colors.CYAN}4.{Colors.ENDC} Modern disk usage (dust)")
            print(f"{Colors.CYAN}5.{Colors.ENDC} Modern filesystem overview (duf)")
            print(f"{Colors.CYAN}6.{Colors.ENDC} Top 20 largest directories")
            print(f"{Colors.CYAN}7.{Colors.ENDC} Common space hogs quick check")
            print(f"{Colors.RED}0.{Colors.ENDC} Back to main menu")

            choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

            if choice == "1":
                self.run_ncdu()
            elif choice == "2":
                self.run_du_analysis()
            elif choice == "3":
                self.run_df()
            elif choice == "4":
                self.run_dust()
            elif choice == "5":
                self.run_duf()
            elif choice == "6":
                self.show_top_directories()
            elif choice == "7":
                self.check_space_hogs()
            elif choice == "0":
                break
            else:
                print_error("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def run_ncdu(self):
        """Run ncdu interactive disk usage analyzer"""
        if not check_tool_installed("ncdu"):
            print_warning("ncdu is not installed.")
            if input("Would you like to install it? (y/n): ").lower() == 'y':
                if install_tool("ncdu"):
                    print_success("ncdu installed successfully!")
                else:
                    print_error("Failed to install ncdu")
                    return
            else:
                return

        print_info("Launching ncdu...")
        print_info("Use arrow keys to navigate, 'd' to delete, 'q' to quit")

        path = input(f"Enter path to scan (default: /): ").strip() or "/"

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""
        run_command(f"{sudo}ncdu {path}", shell=True)

    def run_du_analysis(self):
        """Run du command for directory analysis"""
        print_info("Directory Size Analysis")

        path = input(f"Enter path to analyze (default: /): ").strip() or "/"
        depth = input(f"Enter depth level (default: 1): ").strip() or "1"

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""

        print(f"\n{Colors.BOLD}Top directories in {path}:{Colors.ENDC}")
        run_command(f"{sudo}du -h -d {depth} {path} 2>/dev/null | sort -hr | head -20")

    def run_df(self):
        """Run df command for filesystem overview"""
        print(f"\n{Colors.BOLD}Filesystem Usage:{Colors.ENDC}")
        run_command("df -h")

        print(f"\n{Colors.BOLD}Inode Usage:{Colors.ENDC}")
        run_command("df -i")

    def run_dust(self):
        """Run dust for modern disk usage visualization"""
        if not check_tool_installed("dust"):
            print_warning("dust is not installed.")
            if input("Would you like to install it via snap? (y/n): ").lower() == 'y':
                print_info("Installing dust via snap...")
                code, _ = run_command("sudo snap install dust")
                if code == 0:
                    print_success("dust installed successfully!")
                else:
                    print_error("Failed to install dust")
                    return
            else:
                return

        path = input(f"Enter path to analyze (default: /): ").strip() or "/"
        depth = input(f"Enter depth level (default: 3): ").strip() or "3"

        run_command(f"dust -d {depth} {path}")

    def run_duf(self):
        """Run duf for modern filesystem overview"""
        if not check_tool_installed("duf"):
            print_warning("duf is not installed.")
            if input("Would you like to install it? (y/n): ").lower() == 'y':
                if install_tool("duf"):
                    print_success("duf installed successfully!")
                else:
                    print_error("Failed to install duf")
                    return
            else:
                return

        run_command("duf")

    def show_top_directories(self):
        """Show top 20 largest directories/files"""
        print_info("Finding top 20 largest directories and files...")
        print_warning("This may take a few minutes...")

        sudo = "sudo " if self.has_sudo else ""
        run_command(f"{sudo}du -ahx / 2>/dev/null | sort -rh | head -20")

    def check_space_hogs(self):
        """Check common locations for space hogs"""
        print_header("Common Space Hogs")

        locations = [
            ("/var/lib/docker", "Docker storage"),
            ("/var/log", "System logs"),
            ("/var/cache/apt", "APT cache"),
            ("/var/lib/apt", "APT library"),
            ("/var/lib/snapd", "Snap packages"),
            ("/tmp", "Temporary files"),
            ("/var/tmp", "Variable temporary files"),
        ]

        sudo = "sudo " if self.has_sudo else ""

        for path, description in locations:
            code, output = run_command(f"{sudo}du -sh {path} 2>/dev/null", capture=True)
            if code == 0:
                size = output.split()[0] if output else "N/A"
                print(f"{Colors.BOLD}{description:30}{Colors.ENDC} {size:>10} ({path})")

        print(f"\n{Colors.BOLD}Home directories:{Colors.ENDC}")
        run_command(f"{sudo}du -sh /home/* 2>/dev/null")

        if check_tool_installed("docker"):
            print(f"\n{Colors.BOLD}Docker system usage:{Colors.ENDC}")
            run_command("docker system df")

    def system_cleanup_menu(self):
        """System cleanup submenu"""
        while True:
            print_header("System Cleanup (Safe Operations)")

            print(f"{Colors.BOLD}Cleanup Options:{Colors.ENDC}")
            print(f"{Colors.CYAN}1.{Colors.ENDC} Clean APT package cache")
            print(f"{Colors.CYAN}2.{Colors.ENDC} Clean old journal logs")
            print(f"{Colors.CYAN}3.{Colors.ENDC} Clean temporary files")
            print(f"{Colors.CYAN}4.{Colors.ENDC} Clean user caches")
            print(f"{Colors.CYAN}5.{Colors.ENDC} Clean thumbnail cache")
            print(f"{Colors.CYAN}6.{Colors.ENDC} Clean npm cache (if installed)")
            print(f"{Colors.CYAN}7.{Colors.ENDC} Clean pip cache (if installed)")
            print(f"{Colors.CYAN}8.{Colors.ENDC} Run ALL safe cleanups")
            print(f"{Colors.RED}0.{Colors.ENDC} Back to main menu")

            choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

            if choice == "1":
                self.clean_apt_cache()
            elif choice == "2":
                self.clean_journal_logs()
            elif choice == "3":
                self.clean_temp_files()
            elif choice == "4":
                self.clean_user_cache()
            elif choice == "5":
                self.clean_thumbnails()
            elif choice == "6":
                self.clean_npm_cache()
            elif choice == "7":
                self.clean_pip_cache()
            elif choice == "8":
                self.run_all_safe_cleanups()
            elif choice == "0":
                break
            else:
                print_error("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def clean_apt_cache(self):
        """Clean APT package cache"""
        print_header("Cleaning APT Cache")

        print_info("Checking current APT cache size...")
        run_command("sudo du -sh /var/cache/apt 2>/dev/null")

        if input("\nProceed with cleanup? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        print_info("Cleaning APT cache...")
        run_command("sudo apt-get clean")
        print_success("APT clean completed")

        print_info("Removing automatically installed packages...")
        run_command("sudo apt-get autoclean")
        print_success("APT autoclean completed")

        print_info("Removing unused packages...")
        run_command("sudo apt-get autoremove -y")
        print_success("APT autoremove completed")

        print_info("New APT cache size:")
        run_command("sudo du -sh /var/cache/apt 2>/dev/null")

    def clean_journal_logs(self):
        """Clean old systemd journal logs"""
        print_header("Cleaning Journal Logs")

        print_info("Current journal disk usage:")
        run_command("sudo journalctl --disk-usage")

        days = input("\nKeep logs from last N days (default: 3): ").strip() or "3"

        if input(f"\nProceed with cleanup (keep last {days} days)? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        print_info(f"Cleaning logs older than {days} days...")
        run_command(f"sudo journalctl --vacuum-time={days}d")
        print_success("Journal cleanup completed")

        print_info("New journal disk usage:")
        run_command("sudo journalctl --disk-usage")

    def clean_temp_files(self):
        """Clean temporary files"""
        print_header("Cleaning Temporary Files")

        print_warning("This will remove all files in /tmp and /var/tmp")
        print_info("Checking current size...")
        run_command("sudo du -sh /tmp 2>/dev/null")
        run_command("sudo du -sh /var/tmp 2>/dev/null")

        if input("\nProceed with cleanup? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        print_info("Cleaning /tmp...")
        run_command("sudo rm -rf /tmp/*")
        print_success("/tmp cleaned")

        print_info("Cleaning /var/tmp...")
        run_command("sudo rm -rf /var/tmp/*")
        print_success("/var/tmp cleaned")

    def clean_user_cache(self):
        """Clean user cache directory"""
        print_header("Cleaning User Cache")

        cache_path = os.path.expanduser("~/.cache")
        print_info(f"Checking cache size at {cache_path}...")
        run_command(f"du -sh {cache_path} 2>/dev/null")

        if input("\nProceed with cleanup? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        print_info("Cleaning user cache...")
        run_command(f"rm -rf {cache_path}/*")
        print_success("User cache cleaned")

    def clean_thumbnails(self):
        """Clean thumbnail cache"""
        print_header("Cleaning Thumbnail Cache")

        thumb_path = os.path.expanduser("~/.cache/thumbnails")
        if os.path.exists(thumb_path):
            print_info(f"Checking thumbnail cache size...")
            run_command(f"du -sh {thumb_path} 2>/dev/null")

            if input("\nProceed with cleanup? (y/n): ").lower() != 'y':
                print_warning("Cleanup cancelled")
                return

            print_info("Cleaning thumbnails...")
            run_command(f"rm -rf {thumb_path}/*")
            print_success("Thumbnail cache cleaned")
        else:
            print_info("No thumbnail cache found")

    def clean_npm_cache(self):
        """Clean npm cache"""
        if not check_tool_installed("npm"):
            print_warning("npm is not installed")
            return

        print_header("Cleaning npm Cache")

        print_info("Checking npm cache...")
        run_command("npm cache verify")

        if input("\nProceed with cleanup? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        print_info("Cleaning npm cache...")
        run_command("npm cache clean --force")
        print_success("npm cache cleaned")

    def clean_pip_cache(self):
        """Clean pip cache"""
        if not check_tool_installed("pip") and not check_tool_installed("pip3"):
            print_warning("pip is not installed")
            return

        print_header("Cleaning pip Cache")

        pip_cache = os.path.expanduser("~/.cache/pip")
        if os.path.exists(pip_cache):
            print_info(f"Checking pip cache size...")
            run_command(f"du -sh {pip_cache} 2>/dev/null")

            if input("\nProceed with cleanup? (y/n): ").lower() != 'y':
                print_warning("Cleanup cancelled")
                return

            print_info("Cleaning pip cache...")
            run_command(f"rm -rf {pip_cache}/*")
            print_success("pip cache cleaned")
        else:
            print_info("No pip cache found")

    def run_all_safe_cleanups(self):
        """Run all safe cleanup operations"""
        print_header("Running All Safe Cleanups")

        print_warning("This will perform ALL safe cleanup operations:")
        print("  - APT cache cleanup")
        print("  - Journal logs (keep 3 days)")
        print("  - Temporary files")
        print("  - User caches")
        print("  - Thumbnail cache")
        print("  - npm cache (if installed)")
        print("  - pip cache (if installed)")

        if input("\nProceed with all cleanups? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        # Run all cleanups without prompting
        print_info("Starting comprehensive cleanup...")

        print("\n" + "="*70)
        print("APT Cache Cleanup")
        print("="*70)
        run_command("sudo apt-get clean")
        run_command("sudo apt-get autoclean")
        run_command("sudo apt-get autoremove -y")

        print("\n" + "="*70)
        print("Journal Logs Cleanup")
        print("="*70)
        run_command("sudo journalctl --vacuum-time=3d")

        print("\n" + "="*70)
        print("Temporary Files Cleanup")
        print("="*70)
        run_command("sudo rm -rf /tmp/*")
        run_command("sudo rm -rf /var/tmp/*")

        print("\n" + "="*70)
        print("User Cache Cleanup")
        print("="*70)
        cache_path = os.path.expanduser("~/.cache")
        run_command(f"rm -rf {cache_path}/*")

        if check_tool_installed("npm"):
            print("\n" + "="*70)
            print("npm Cache Cleanup")
            print("="*70)
            run_command("npm cache clean --force 2>/dev/null")

        pip_cache = os.path.expanduser("~/.cache/pip")
        if os.path.exists(pip_cache):
            print("\n" + "="*70)
            print("pip Cache Cleanup")
            print("="*70)
            run_command(f"rm -rf {pip_cache}/*")

        print_success("\nAll safe cleanups completed!")
        print_info("Disk usage after cleanup:")
        print(get_disk_usage())

    def docker_management_menu(self):
        """Docker management submenu"""
        if not check_tool_installed("docker"):
            print_error("Docker is not installed or not in PATH")
            input("Press Enter to continue...")
            return

        while True:
            print_header("Docker Management")

            print(f"{Colors.BOLD}Docker Storage Info:{Colors.ENDC}")
            run_command("docker system df")

            print(f"\n{Colors.BOLD}Docker Management Options:{Colors.ENDC}")
            print(f"{Colors.CYAN}1.{Colors.ENDC} Show Docker storage details")
            print(f"{Colors.CYAN}2.{Colors.ENDC} List all containers (running & stopped)")
            print(f"{Colors.CYAN}3.{Colors.ENDC} List all images")
            print(f"{Colors.CYAN}4.{Colors.ENDC} List all volumes")
            print(f"{Colors.CYAN}5.{Colors.ENDC} Remove stopped containers (SAFE)")
            print(f"{Colors.CYAN}6.{Colors.ENDC} Remove dangling images (SAFE)")
            print(f"{Colors.CYAN}7.{Colors.ENDC} Remove unused networks (SAFE)")
            print(f"{Colors.CYAN}8.{Colors.ENDC} Remove build cache (SAFE)")
            print(f"{Colors.YELLOW}9.{Colors.ENDC} Remove ALL unused images (removes images not in use)")
            print(f"{Colors.RED}10.{Colors.ENDC} Remove unused volumes (DANGEROUS - may lose data!)")
            print(f"{Colors.CYAN}11.{Colors.ENDC} Safe Docker cleanup (containers + dangling images + build cache)")
            print(f"{Colors.RED}0.{Colors.ENDC} Back to main menu")

            choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

            if choice == "1":
                self.show_docker_storage()
            elif choice == "2":
                self.list_docker_containers()
            elif choice == "3":
                self.list_docker_images()
            elif choice == "4":
                self.list_docker_volumes()
            elif choice == "5":
                self.remove_stopped_containers()
            elif choice == "6":
                self.remove_dangling_images()
            elif choice == "7":
                self.remove_unused_networks()
            elif choice == "8":
                self.remove_build_cache()
            elif choice == "9":
                self.remove_all_unused_images()
            elif choice == "10":
                self.remove_unused_volumes()
            elif choice == "11":
                self.safe_docker_cleanup()
            elif choice == "0":
                break
            else:
                print_error("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def show_docker_storage(self):
        """Show detailed Docker storage information"""
        print_header("Docker Storage Details")
        run_command("docker system df -v")

    def list_docker_containers(self):
        """List all Docker containers"""
        print_header("Docker Containers")
        run_command("docker ps -a")

    def list_docker_images(self):
        """List all Docker images"""
        print_header("Docker Images")
        run_command("docker images -a")

    def list_docker_volumes(self):
        """List all Docker volumes"""
        print_header("Docker Volumes")
        run_command("docker volume ls")

    def remove_stopped_containers(self):
        """Remove stopped containers"""
        print_header("Remove Stopped Containers")

        print_info("Listing stopped containers...")
        run_command("docker ps -a -f status=exited -f status=created")

        if input("\nRemove these stopped containers? (y/n): ").lower() != 'y':
            print_warning("Operation cancelled")
            return

        print_info("Removing stopped containers...")
        run_command("docker container prune -f")
        print_success("Stopped containers removed")

    def remove_dangling_images(self):
        """Remove dangling images"""
        print_header("Remove Dangling Images")

        print_info("Listing dangling images...")
        run_command("docker images -f dangling=true")

        if input("\nRemove these dangling images? (y/n): ").lower() != 'y':
            print_warning("Operation cancelled")
            return

        print_info("Removing dangling images...")
        run_command("docker image prune -f")
        print_success("Dangling images removed")

    def remove_unused_networks(self):
        """Remove unused networks"""
        print_header("Remove Unused Networks")

        print_info("Removing unused networks...")
        run_command("docker network prune -f")
        print_success("Unused networks removed")

    def remove_build_cache(self):
        """Remove Docker build cache"""
        print_header("Remove Build Cache")

        print_info("Checking build cache...")
        run_command("docker system df")

        if input("\nRemove all build cache? (y/n): ").lower() != 'y':
            print_warning("Operation cancelled")
            return

        print_warning("This will remove ALL build cache")
        if input("Are you sure? (y/n): ").lower() != 'y':
            print_warning("Operation cancelled")
            return

        print_info("Removing build cache...")
        run_command("docker builder prune -a -f")
        print_success("Build cache removed")

    def remove_all_unused_images(self):
        """Remove all unused images"""
        print_header("Remove ALL Unused Images")

        print_warning("This will remove ALL images not associated with a container")
        print_warning("If you have stopped containers, their images will be deleted!")
        print_info("Listing all images...")
        run_command("docker images -a")

        if input("\nProceed with removal? (y/n): ").lower() != 'y':
            print_warning("Operation cancelled")
            return

        if input("Are you ABSOLUTELY sure? This cannot be undone! (y/n): ").lower() != 'y':
            print_warning("Operation cancelled")
            return

        print_info("Removing all unused images...")
        run_command("docker image prune -a -f")
        print_success("Unused images removed")

    def remove_unused_volumes(self):
        """Remove unused volumes - DANGEROUS"""
        print_header("Remove Unused Volumes - DANGEROUS!")

        print_error("WARNING: This operation can cause DATA LOSS!")
        print_warning("Volumes contain persistent data like databases and configurations")
        print_warning("Only volumes not mounted to ANY container (running or stopped) will be removed")

        print_info("\nListing all volumes...")
        run_command("docker volume ls")

        print_info("\nListing unused volumes (would be deleted)...")
        run_command("docker volume ls -f dangling=true")

        if input("\nDo you understand this may cause data loss? (yes/no): ").lower() != 'yes':
            print_warning("Operation cancelled")
            return

        if input("Type 'DELETE VOLUMES' to confirm: ").strip() != 'DELETE VOLUMES':
            print_warning("Operation cancelled")
            return

        print_info("Removing unused volumes...")
        run_command("docker volume prune -f")
        print_success("Unused volumes removed")

    def safe_docker_cleanup(self):
        """Perform safe Docker cleanup"""
        print_header("Safe Docker Cleanup")

        print_info("This will remove:")
        print("  - Stopped containers")
        print("  - Dangling images (untagged)")
        print("  - Unused networks")
        print("  - Build cache")
        print_warning("This will NOT remove volumes or images in use")

        if input("\nProceed with safe cleanup? (y/n): ").lower() != 'y':
            print_warning("Cleanup cancelled")
            return

        print_info("Running safe Docker cleanup...")
        run_command("docker container prune -f")
        run_command("docker image prune -f")
        run_command("docker network prune -f")
        run_command("docker builder prune -a -f")

        print_success("Safe Docker cleanup completed!")
        print_info("\nDocker storage after cleanup:")
        run_command("docker system df")

    def advanced_analysis_menu(self):
        """Advanced analysis submenu"""
        while True:
            print_header("Advanced Analysis")

            print(f"{Colors.BOLD}Advanced Options:{Colors.ENDC}")
            print(f"{Colors.CYAN}1.{Colors.ENDC} Find largest files in system")
            print(f"{Colors.CYAN}2.{Colors.ENDC} Find largest directories in specific path")
            print(f"{Colors.CYAN}3.{Colors.ENDC} Find old files (not accessed in N days)")
            print(f"{Colors.CYAN}4.{Colors.ENDC} Search for specific file types and their total size")
            print(f"{Colors.CYAN}5.{Colors.ENDC} Check for duplicate files (by size)")
            print(f"{Colors.CYAN}6.{Colors.ENDC} Analyze directory growth over time")
            print(f"{Colors.RED}0.{Colors.ENDC} Back to main menu")

            choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

            if choice == "1":
                self.find_largest_files()
            elif choice == "2":
                self.find_largest_dirs()
            elif choice == "3":
                self.find_old_files()
            elif choice == "4":
                self.analyze_file_types()
            elif choice == "5":
                self.find_duplicate_files()
            elif choice == "6":
                self.analyze_directory_growth()
            elif choice == "0":
                break
            else:
                print_error("Invalid option. Please try again.")

            if choice != "0":
                input("\nPress Enter to continue...")

    def find_largest_files(self):
        """Find largest files in the system"""
        print_header("Find Largest Files")

        count = input("How many files to show? (default: 20): ").strip() or "20"
        path = input("Path to search (default: /): ").strip() or "/"

        print_warning("This may take several minutes...")
        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""

        print_info(f"Searching for {count} largest files in {path}...")
        run_command(f"{sudo}find {path} -type f -exec du -h {{}} + 2>/dev/null | sort -rh | head -n {count}")

    def find_largest_dirs(self):
        """Find largest directories in specific path"""
        print_header("Find Largest Directories")

        path = input("Path to search (default: /): ").strip() or "/"
        depth = input("Directory depth (default: 2): ").strip() or "2"
        count = input("How many directories to show? (default: 20): ").strip() or "20"

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""

        print_info(f"Finding largest directories in {path}...")
        run_command(f"{sudo}du -h --max-depth={depth} {path} 2>/dev/null | sort -rh | head -n {count}")

    def find_old_files(self):
        """Find files not accessed in N days"""
        print_header("Find Old Files")

        path = input("Path to search (default: /home): ").strip() or "/home"
        days = input("Not accessed in how many days? (default: 180): ").strip() or "180"

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""

        print_info(f"Finding files not accessed in {days} days in {path}...")
        print_warning("This may take a while...")
        run_command(f"{sudo}find {path} -type f -atime +{days} -exec ls -lh {{}} \\; 2>/dev/null | head -50")

    def analyze_file_types(self):
        """Analyze file types and their total size"""
        print_header("Analyze File Types")

        path = input("Path to search (default: ~): ").strip() or "~"
        extension = input("File extension to search (e.g., .log, .tmp, .zip): ").strip()

        if not extension:
            print_error("Extension is required")
            return

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""
        path = os.path.expanduser(path)

        print_info(f"Finding {extension} files in {path}...")
        run_command(f"{sudo}find {path} -type f -name '*{extension}' -exec ls -lh {{}} \\; 2>/dev/null | head -50")

        print_info(f"\nTotal size of {extension} files:")
        run_command(f"{sudo}find {path} -type f -name '*{extension}' -exec du -ch {{}} + 2>/dev/null | grep total$")

    def find_duplicate_files(self):
        """Find potential duplicate files by size"""
        print_header("Find Duplicate Files (by size)")

        path = input("Path to search (default: ~): ").strip() or "~"
        path = os.path.expanduser(path)

        print_info("Finding files with duplicate sizes...")
        print_warning("This only checks file size, not content")
        print_warning("This may take a while...")

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""

        # Find files, get their sizes, find duplicates
        run_command(f"{sudo}find {path} -type f -exec du -b {{}} + 2>/dev/null | sort -n | uniq -d -w 15")

    def analyze_directory_growth(self):
        """Analyze directory size"""
        print_header("Directory Size Analysis")

        path = input("Path to analyze (default: /var/log): ").strip() or "/var/log"

        sudo = "sudo " if self.has_sudo and path.startswith("/") and path != os.path.expanduser("~") else ""

        print_info(f"Analyzing {path}...")
        run_command(f"{sudo}du -h --max-depth=2 {path} 2>/dev/null | sort -rh | head -30")

    def check_install_tools(self):
        """Check and install required tools"""
        print_header("Tool Installation & Status")

        tools = {
            "ncdu": "NCurses Disk Usage - Interactive analyzer (RECOMMENDED)",
            "duf": "Modern df alternative - Better filesystem overview",
            "dust": "Modern du alternative - Tree-style disk usage (requires snap)",
        }

        print(f"{Colors.BOLD}Tool Status:{Colors.ENDC}\n")

        for tool, description in tools.items():
            installed = check_tool_installed(tool)
            status = f"{Colors.GREEN}✓ Installed{Colors.ENDC}" if installed else f"{Colors.RED}✗ Not installed{Colors.ENDC}"
            print(f"{tool:15} {status:30} - {description}")

        print(f"\n{Colors.BOLD}Optional tools:{Colors.ENDC}")
        optional_tools = ["docker", "npm", "pip", "pip3"]
        for tool in optional_tools:
            installed = check_tool_installed(tool)
            status = f"{Colors.GREEN}✓ Installed{Colors.ENDC}" if installed else f"{Colors.YELLOW}○ Not installed{Colors.ENDC}"
            print(f"{tool:15} {status}")

        print(f"\n{Colors.BOLD}Installation Options:{Colors.ENDC}")
        print(f"{Colors.CYAN}1.{Colors.ENDC} Install ncdu (recommended)")
        print(f"{Colors.CYAN}2.{Colors.ENDC} Install duf")
        print(f"{Colors.CYAN}3.{Colors.ENDC} Install dust (via snap)")
        print(f"{Colors.CYAN}4.{Colors.ENDC} Install all recommended tools")
        print(f"{Colors.RED}0.{Colors.ENDC} Back to main menu")

        choice = input(f"\n{Colors.BOLD}Select an option:{Colors.ENDC} ").strip()

        if choice == "1":
            if install_tool("ncdu"):
                print_success("ncdu installed successfully!")
            else:
                print_error("Failed to install ncdu")
        elif choice == "2":
            if install_tool("duf"):
                print_success("duf installed successfully!")
            else:
                print_error("Failed to install duf")
        elif choice == "3":
            print_info("Installing dust via snap...")
            code, _ = run_command("sudo snap install dust")
            if code == 0:
                print_success("dust installed successfully!")
            else:
                print_error("Failed to install dust")
        elif choice == "4":
            print_info("Installing all recommended tools...")
            install_tool("ncdu")
            install_tool("duf")
            run_command("sudo snap install dust")
            print_success("Installation complete!")

        if choice != "0":
            input("\nPress Enter to continue...")

    def show_wsl_compaction_info(self):
        """Show information about WSL disk compaction"""
        print_header("WSL Disk Compaction Information")

        print(f"{Colors.BOLD}Why Compaction is Needed:{Colors.ENDC}")
        print("WSL uses virtual disk files (VHDX) that grow as you use space but don't")
        print("automatically shrink when you delete files. After cleanup, you must compact")
        print("the VHDX to reclaim the space on Windows.\n")

        print(f"{Colors.BOLD}Steps to Compact WSL Disks (Run in Windows PowerShell as Admin):{Colors.ENDC}\n")

        print(f"{Colors.YELLOW}Method 1 - Modern WSL (WSL 2.0+):{Colors.ENDC}")
        print("1. Shutdown all WSL instances:")
        print("   wsl --shutdown\n")
        print("2. Compact Ubuntu-22.04 disk:")
        print("   wsl --manage Ubuntu-22.04 --set-sparse true\n")
        print("3. Compact docker-desktop-data (if using Docker):")
        print("   wsl --manage docker-desktop-data --set-sparse true\n")

        print(f"{Colors.YELLOW}Method 2 - Diskpart (if Method 1 doesn't work):{Colors.ENDC}")
        print("1. Shutdown WSL:")
        print("   wsl --shutdown\n")
        print("2. Open diskpart:")
        print("   diskpart\n")
        print("3. In diskpart, for Ubuntu:")
        print('   select vdisk file="%LOCALAPPDATA%\\Packages\\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\\LocalState\\ext4.vhdx"')
        print("   compact vdisk")
        print("   detach vdisk\n")
        print("4. For Docker:")
        print('   select vdisk file="%LOCALAPPDATA%\\Docker\\wsl\\data\\ext4.vhdx"')
        print("   compact vdisk")
        print("   detach vdisk\n")
        print("5. Exit diskpart:")
        print("   exit\n")

        print(f"{Colors.YELLOW}Method 3 - Optimize-VHD (requires Hyper-V):{Colors.ENDC}")
        print('optimize-vhd -Path "$env:LOCALAPPDATA\\Packages\\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\\LocalState\\ext4.vhdx" -Mode Full\n')

        print(f"{Colors.BOLD}Important Notes:{Colors.ENDC}")
        print("• Always run 'wsl --shutdown' before compacting")
        print("• Compaction can take several minutes")
        print("• Make sure no WSL instances are running")
        print("• The VHDX file paths may vary based on your installation")
        print("• Backup important data before compacting")

def main():
    """Main entry point"""
    if os.geteuid() == 0:
        print_warning("Warning: Running as root. Some operations may behave differently.")
        if input("Continue anyway? (y/n): ").lower() != 'y':
            sys.exit(1)

    manager = StorageManager()
    manager.show_main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)
