#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import shutil

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
RED = '\033[0;31m'
DEFAULT = '\033[0m'

def show_help():
    print("Usage: update_comfyui.py [OPTIONS]")
    print()
    print("Update ComfyUI projects and custom nodes.")
    print()
    print("Options:")
    print("  -h, --help     Show this help message and exit")
    print("  -v, --verbose  Run in verbose mode")
    print("  -f, --force    Force update, discarding local changes")
    print()
    print("When run without options, the script updates all projects")
    print("with minimal output. Use -v for more detailed progress information.")
    print("Use -f to forcefully update, discarding any local changes.")
    print()
    print("If run from within a project directory, only that project will be updated.")

def update_progress(current, total, folder):
    width = 50
    percent = int(current * 100 / total)
    completed = int(width * current / total)
    
    sys.stdout.write('\r')
    sys.stdout.write(f"Updating: {folder:<40}")
    sys.stdout.write("[")
    sys.stdout.write("=" * completed)
    sys.stdout.write(" " * (width - completed))
    sys.stdout.write(f"] {percent:3d}%")
    sys.stdout.flush()

def run_git_command(command, directory):
    process = subprocess.Popen(command, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

def git_pull_with_resolve(directory, verbose, force):
    os.chdir(directory)
    issues = []

    # Check if it's a git repository
    if not os.path.exists(os.path.join(directory, '.git')):
        if verbose:
            print(f"\n{YELLOW}Skipping {directory} (not a git repository){DEFAULT}")
        return issues

    # Check for stashes
    returncode, stdout, _ = run_git_command("git stash list", directory)
    if stdout.strip():
        if verbose:
            print(f"\n{YELLOW}Stashed changes found in {directory}. Attempting to apply...{DEFAULT}")
        returncode, _, _ = run_git_command("git stash apply", directory)
        if returncode != 0:
            issues.append(f"Failed to apply stashed changes in {directory}")

    # Check for uncommitted changes
    returncode, _, _ = run_git_command("git diff --quiet HEAD", directory)
    if returncode != 0:
        if force:
            if verbose:
                print(f"\n{YELLOW}Uncommitted changes found. Force option is set. Discarding changes...{DEFAULT}")
            run_git_command("git reset --hard HEAD", directory)
        else:
            if verbose:
                print(f"\n{YELLOW}Uncommitted changes found. Stashing changes...{DEFAULT}")
            run_git_command("git stash", directory)

    # Try to pull
    returncode, _, _ = run_git_command("git pull --rebase", directory)
    if returncode != 0:
        if verbose:
            print(f"\n{YELLOW}Conflicts detected in {directory}. Attempting to resolve...{DEFAULT}")
        
        if force:
            if verbose:
                print("Force rebasing...")
            run_git_command("git fetch --all", directory)
            run_git_command("git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)", directory)
        else:
            if verbose:
                print("Attempting to resolve conflicts by favoring incoming changes...")
            returncode, _, _ = run_git_command("git rebase --strategy-option=theirs", directory)
            
            if returncode != 0:
                issues.append(f"Unable to resolve conflicts in {directory}. Manual intervention required.")
                run_git_command("git rebase --abort", directory)

    if verbose and not issues:
        print(f"{GREEN}Update successful for {directory}{DEFAULT}")

    return issues

def update_project(project_dir, verbose, force):
    project_name = os.path.basename(project_dir)
    issues = []
    
    if verbose:
        print(f"\n{GREEN}Updating project: {project_name}{DEFAULT}")
    
    # Update comfyui directory
    comfyui_dir = os.path.join(project_dir, "comfyui")
    if os.path.isdir(comfyui_dir):
        if verbose:
            print(f"{GREEN}Updating MainApp...{DEFAULT}")
        issues.extend(git_pull_with_resolve(comfyui_dir, verbose, force))
        
        # Update custom nodes
        custom_nodes_dir = os.path.join(comfyui_dir, "custom_nodes")
        if os.path.isdir(custom_nodes_dir):
            if verbose:
                print(f"{GREEN}Updating custom nodes...{DEFAULT}")
            for node_dir in os.listdir(custom_nodes_dir):
                node_path = os.path.join(custom_nodes_dir, node_dir)
                if os.path.isdir(node_path) and node_dir != "__pycache__":
                    if verbose:
                        print(f"{GREEN}Updating {node_dir}...{DEFAULT}")
                    issues.extend(git_pull_with_resolve(node_path, verbose, force))
    
    if verbose:
        print(f"{GREEN}Finished updating {project_name}{DEFAULT}")
        print("----------------------------------------")
    
    return issues

def main():
    parser = argparse.ArgumentParser(description="Update ComfyUI projects and custom nodes.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Run in verbose mode")
    parser.add_argument("-f", "--force", action="store_true", help="Force update, discarding local changes")
    args = parser.parse_args()

    all_issues = []

    if "/comfyui-launcher/server/projects/" in os.getcwd().replace("\\", "/"):
        update_progress(1, 1, os.path.basename(os.getcwd()))
        all_issues.extend(update_project(os.getcwd(), args.verbose, args.force))
    else:
        projects_dir = os.path.expanduser("~/comfyui-launcher/server/projects")
        projects = [os.path.join(projects_dir, d) for d in os.listdir(projects_dir) 
                    if os.path.isdir(os.path.join(projects_dir, d))]
        total = len(projects)

        for i, project in enumerate(projects, 1):
            project_name = os.path.basename(project)
            update_progress(i, total, project_name)
            all_issues.extend(update_project(project, args.verbose, args.force))

    print(f"\n{GREEN}All projects updated successfully!{DEFAULT}")

    if all_issues:
        print(f"\n{YELLOW}Summary of issues:{DEFAULT}")
        for issue in all_issues:
            print(f"- {issue}")

if __name__ == "__main__":
    main()
