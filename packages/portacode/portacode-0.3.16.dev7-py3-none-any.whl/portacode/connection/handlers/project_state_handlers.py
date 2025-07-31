"""Project state handlers for maintaining project folder structure and git metadata."""

import asyncio
import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, asdict
import platform

from .base import AsyncHandler, SyncHandler

# Import GitPython with fallback
try:
    import git
    from git import Repo, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception

# Cross-platform file system monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

logger = logging.getLogger(__name__)


@dataclass
class FileItem:
    """Represents a file or directory item with metadata."""
    name: str
    path: str
    is_directory: bool
    parent_path: str
    size: Optional[int] = None
    modified_time: Optional[float] = None
    is_git_tracked: Optional[bool] = None
    git_status: Optional[str] = None
    is_hidden: bool = False
    is_ignored: bool = False
    children: Optional[List['FileItem']] = None
    is_expanded: bool = False
    is_loaded: bool = False


@dataclass
class ProjectState:
    """Represents the complete state of a project."""
    project_id: str
    project_folder_path: str
    items: List[FileItem]
    is_git_repo: bool = False
    git_branch: Optional[str] = None
    git_status_summary: Optional[Dict[str, int]] = None
    open_files: Set[str] = None
    active_file: Optional[str] = None
    
    def __post_init__(self):
        if self.open_files is None:
            self.open_files = set()


class GitManager:
    """Manages Git operations for project state."""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.repo: Optional[Repo] = None
        self.is_git_repo = False
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize Git repository if available."""
        if not GIT_AVAILABLE:
            logger.warning("GitPython not available, Git features disabled")
            return
        
        try:
            self.repo = Repo(self.project_path)
            self.is_git_repo = True
            logger.info("Initialized Git repo for project: %s", self.project_path)
        except (InvalidGitRepositoryError, Exception) as e:
            logger.debug("Not a Git repository or Git error: %s", e)
    
    def get_branch_name(self) -> Optional[str]:
        """Get current Git branch name."""
        if not self.is_git_repo or not self.repo:
            return None
        
        try:
            return self.repo.active_branch.name
        except Exception as e:
            logger.debug("Could not get Git branch: %s", e)
            return None
    
    def get_file_status(self, file_path: str) -> Dict[str, Any]:
        """Get Git status for a specific file."""
        if not self.is_git_repo or not self.repo:
            return {"is_tracked": False, "status": None, "is_ignored": False}
        
        try:
            # Convert to relative path from repo root
            rel_path = os.path.relpath(file_path, self.repo.working_dir)
            
            # Check if file is ignored
            is_ignored = False
            try:
                # Use git check-ignore to see if file is ignored
                self.repo.git.check_ignore(rel_path)
                is_ignored = True
            except Exception:
                is_ignored = False
            
            # Check if file is tracked
            try:
                self.repo.git.ls_files(rel_path, error_unmatch=True)
                is_tracked = True
            except Exception:
                is_tracked = False
            
            # Get status
            status = None
            if is_tracked:
                # Check for modifications
                if self.repo.is_dirty(path=rel_path):
                    status = "modified"
                else:
                    status = "clean"
            elif is_ignored:
                status = "ignored"
            else:
                # Check if it's untracked
                if os.path.exists(file_path):
                    status = "untracked"
            
            return {"is_tracked": is_tracked, "status": status, "is_ignored": is_ignored}
            
        except Exception as e:
            logger.debug("Error getting Git status for %s: %s", file_path, e)
            return {"is_tracked": False, "status": None, "is_ignored": False}
    
    def get_status_summary(self) -> Dict[str, int]:
        """Get summary of Git status."""
        if not self.is_git_repo or not self.repo:
            return {}
        
        try:
            status = self.repo.git.status(porcelain=True).strip()
            if not status:
                return {"clean": 0}
            
            summary = {"modified": 0, "added": 0, "deleted": 0, "untracked": 0}
            
            for line in status.split('\n'):
                if len(line) >= 2:
                    index_status = line[0]
                    worktree_status = line[1]
                    
                    if index_status == 'A' or worktree_status == 'A':
                        summary["added"] += 1
                    elif index_status == 'M' or worktree_status == 'M':
                        summary["modified"] += 1
                    elif index_status == 'D' or worktree_status == 'D':
                        summary["deleted"] += 1
                    elif index_status == '?' and worktree_status == '?':
                        summary["untracked"] += 1
            
            return summary
            
        except Exception as e:
            logger.debug("Error getting Git status summary: %s", e)
            return {}


class FileSystemWatcher:
    """Watches file system changes for project folders."""
    
    def __init__(self, project_manager: 'ProjectStateManager'):
        self.project_manager = project_manager
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[FileSystemEventHandler] = None
        self.watched_paths: Set[str] = set()
        
        if WATCHDOG_AVAILABLE:
            self._initialize_watcher()
    
    def _initialize_watcher(self):
        """Initialize file system watcher."""
        if not WATCHDOG_AVAILABLE:
            logger.warning("Watchdog not available, file monitoring disabled")
            return
        
        class ProjectEventHandler(FileSystemEventHandler):
            def __init__(self, manager):
                self.manager = manager
            
            def on_any_event(self, event):
                # Debounce rapid file changes
                asyncio.create_task(self.manager._handle_file_change(event))
        
        self.event_handler = ProjectEventHandler(self.project_manager)
        self.observer = Observer()
    
    def start_watching(self, path: str):
        """Start watching a specific path."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            return
        
        if path not in self.watched_paths:
            try:
                self.observer.schedule(self.event_handler, path, recursive=False)
                self.watched_paths.add(path)
                logger.debug("Started watching path: %s", path)
                
                if not self.observer.is_alive():
                    self.observer.start()
            except Exception as e:
                logger.error("Error starting file watcher for %s: %s", path, e)
    
    def stop_watching(self, path: str):
        """Stop watching a specific path."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            return
        
        if path in self.watched_paths:
            # Note: watchdog doesn't have direct path removal, would need to recreate observer
            self.watched_paths.discard(path)
            logger.debug("Stopped watching path: %s", path)
    
    def stop_all(self):
        """Stop all file watching."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            self.watched_paths.clear()


class ProjectStateManager:
    """Manages project state for client sessions."""
    
    def __init__(self, control_channel, context: Dict[str, Any]):
        self.control_channel = control_channel
        self.context = context
        self.projects: Dict[str, ProjectState] = {}
        self.git_managers: Dict[str, GitManager] = {}
        self.file_watcher = FileSystemWatcher(self)
        self.debug_mode = False
        self.debug_file_path: Optional[str] = None
        
        # Debouncing for file changes
        self._change_debounce_timer: Optional[asyncio.Task] = None
        self._pending_changes: Set[str] = set()
    
    def set_debug_mode(self, enabled: bool, debug_file_path: Optional[str] = None):
        """Enable or disable debug mode with JSON output."""
        self.debug_mode = enabled
        self.debug_file_path = debug_file_path
        if enabled:
            logger.info("Project state debug mode enabled, output to: %s", debug_file_path)
    
    def _write_debug_state(self):
        """Write current state to debug JSON file."""
        if not self.debug_mode or not self.debug_file_path:
            return
        
        try:
            debug_data = {}
            for project_id, state in self.projects.items():
                debug_data[project_id] = {
                    "project_folder_path": state.project_folder_path,
                    "is_git_repo": state.is_git_repo,
                    "git_branch": state.git_branch,
                    "git_status_summary": state.git_status_summary,
                    "open_files": list(state.open_files),
                    "active_file": state.active_file,
                    "items": [self._serialize_file_item(item) for item in state.items]
                }
            
            with open(self.debug_file_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error("Error writing debug state: %s", e)
    
    def _serialize_file_item(self, item: FileItem) -> Dict[str, Any]:
        """Serialize FileItem for JSON output."""
        result = asdict(item)
        if item.children:
            result["children"] = [self._serialize_file_item(child) for child in item.children]
        return result
    
    async def initialize_project_state(self, client_session: str, project_folder_path: str) -> ProjectState:
        """Initialize project state for a client session."""
        project_id = f"{client_session}_{hash(project_folder_path)}"
        
        if project_id in self.projects:
            return self.projects[project_id]
        
        logger.info("Initializing project state for: %s", project_folder_path)
        
        # Initialize Git manager
        git_manager = GitManager(project_folder_path)
        self.git_managers[project_id] = git_manager
        
        # Create project state
        project_state = ProjectState(
            project_id=project_id,
            project_folder_path=project_folder_path,
            items=[],
            is_git_repo=git_manager.is_git_repo,
            git_branch=git_manager.get_branch_name(),
            git_status_summary=git_manager.get_status_summary()
        )
        
        # Load initial file structure with flattened items
        await self._build_flattened_items_structure(project_state)
        
        # Start watching the project folder
        self.file_watcher.start_watching(project_folder_path)
        
        self.projects[project_id] = project_state
        self._write_debug_state()
        
        return project_state
    
    async def _load_directory_items(self, project_state: ProjectState, directory_path: str, is_root: bool = False, parent_item: Optional[FileItem] = None):
        """Load directory items with Git metadata."""
        git_manager = self.git_managers.get(project_state.project_id)
        
        try:
            items = []
            
            # Use os.scandir for better performance
            with os.scandir(directory_path) as entries:
                for entry in entries:
                    try:
                        # Skip .git folders and their contents
                        if entry.name == '.git' and entry.is_dir():
                            continue
                            
                        stat_info = entry.stat()
                        is_hidden = entry.name.startswith('.')
                        
                        # Get Git status if available
                        git_info = {"is_tracked": False, "status": None, "is_ignored": False}
                        if git_manager:
                            git_info = git_manager.get_file_status(entry.path)
                        
                        # Check if this directory is expanded
                        is_expanded = False
                        
                        file_item = FileItem(
                            name=entry.name,
                            path=entry.path,
                            is_directory=entry.is_dir(),
                            parent_path=directory_path,
                            size=stat_info.st_size if entry.is_file() else None,
                            modified_time=stat_info.st_mtime,
                            is_git_tracked=git_info["is_tracked"],
                            git_status=git_info["status"],
                            is_hidden=is_hidden,
                            is_ignored=git_info["is_ignored"],
                            is_expanded=is_expanded,
                            is_loaded=not entry.is_dir()  # Files are always "loaded", directories need expansion
                        )
                        
                        items.append(file_item)
                        
                    except (OSError, PermissionError) as e:
                        logger.debug("Error reading entry %s: %s", entry.path, e)
                        continue
            
            # Sort items: directories first, then files, both alphabetically
            items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
            
            if is_root:
                project_state.items = items
            elif parent_item:
                parent_item.children = items
                parent_item.is_loaded = True
                
        except (OSError, PermissionError) as e:
            logger.error("Error loading directory %s: %s", directory_path, e)
    
    async def _build_flattened_items_structure(self, project_state: ProjectState):
        """Build a flattened items structure including all visible items and one level down from expanded folders."""
        all_items = []
        
        # Load root items
        root_items = await self._load_directory_items_list(project_state.project_folder_path, project_state.project_folder_path)
        
        for item in root_items:
            all_items.append(item)
            
            # Always load one level down from root folders (project root is always "expanded")
            # OR if this folder is explicitly expanded, add its children and one level down
            if item.is_directory and (item.parent_path == project_state.project_folder_path or item.is_expanded):
                children = await self._load_directory_items_list(item.path, item.path)
                for child in children:
                    all_items.append(child)
                    
                    # If child is a directory, load one level down
                    if child.is_directory:
                        grandchildren = await self._load_directory_items_list(child.path, child.path)
                        all_items.extend(grandchildren)
        
        project_state.items = all_items
    
    async def _load_directory_items_list(self, directory_path: str, parent_path: str) -> List[FileItem]:
        """Load directory items and return as a list with parent_path."""
        git_manager = None
        for manager in self.git_managers.values():
            if directory_path.startswith(manager.project_path):
                git_manager = manager
                break
        
        items = []
        
        try:
            with os.scandir(directory_path) as entries:
                for entry in entries:
                    try:
                        # Skip .git folders and their contents
                        if entry.name == '.git' and entry.is_dir():
                            continue
                            
                        stat_info = entry.stat()
                        is_hidden = entry.name.startswith('.')
                        
                        # Get Git status if available
                        git_info = {"is_tracked": False, "status": None, "is_ignored": False}
                        if git_manager:
                            git_info = git_manager.get_file_status(entry.path)
                        
                        # Check if this directory is expanded by finding it in current items
                        is_expanded = False
                        if entry.is_dir():
                            # Check if this folder is expanded by looking for existing items with this path as parent
                            is_expanded = self._is_folder_expanded(entry.path)
                        
                        file_item = FileItem(
                            name=entry.name,
                            path=entry.path,
                            is_directory=entry.is_dir(),
                            parent_path=parent_path,
                            size=stat_info.st_size if entry.is_file() else None,
                            modified_time=stat_info.st_mtime,
                            is_git_tracked=git_info["is_tracked"],
                            git_status=git_info["status"],
                            is_hidden=is_hidden,
                            is_ignored=git_info["is_ignored"],
                            is_expanded=is_expanded,
                            is_loaded=not entry.is_dir()
                        )
                        
                        items.append(file_item)
                        
                    except (OSError, PermissionError) as e:
                        logger.debug("Error reading entry %s: %s", entry.path, e)
                        continue
            
            # Sort items: directories first, then files, both alphabetically
            items.sort(key=lambda x: (not x.is_directory, x.name.lower()))
            
        except (OSError, PermissionError) as e:
            logger.error("Error loading directory %s: %s", directory_path, e)
        
        return items
    
    def _is_folder_expanded(self, folder_path: str) -> bool:
        """Check if a folder is expanded by looking at existing items."""
        # During initial load, no folders are expanded
        # During updates, check if any items have this folder as parent_path
        for project_state in self.projects.values():
            for item in project_state.items:
                if item.parent_path == folder_path:
                    return True
        return False
    
    async def expand_folder(self, project_id: str, folder_path: str) -> bool:
        """Expand a folder and load its contents."""
        if project_id not in self.projects:
            return False
        
        project_state = self.projects[project_id]
        
        # Find the folder item and mark it as expanded
        folder_item = self._find_item_by_path(project_state.items, folder_path)
        if not folder_item or not folder_item.is_directory:
            return False
        
        folder_item.is_expanded = True
        
        # Start watching this folder
        self.file_watcher.start_watching(folder_path)
        
        # Rebuild the entire flattened structure to include new expanded content
        await self._build_flattened_items_structure(project_state)
        
        self._write_debug_state()
        return True
    
    async def collapse_folder(self, project_id: str, folder_path: str) -> bool:
        """Collapse a folder."""
        if project_id not in self.projects:
            return False
        
        project_state = self.projects[project_id]
        
        # Find the folder item and mark it as collapsed
        folder_item = self._find_item_by_path(project_state.items, folder_path)
        if not folder_item or not folder_item.is_directory:
            return False
        
        folder_item.is_expanded = False
        
        # Stop watching collapsed folders (except root)
        if folder_path != project_state.project_folder_path:
            self.file_watcher.stop_watching(folder_path)
        
        # Rebuild the flattened structure to remove collapsed content
        await self._build_flattened_items_structure(project_state)
        
        self._write_debug_state()
        return True
    
    def _find_item_by_path(self, items: List[FileItem], target_path: str) -> Optional[FileItem]:
        """Find a file item by its path recursively."""
        for item in items:
            if item.path == target_path:
                return item
            if item.children:
                found = self._find_item_by_path(item.children, target_path)
                if found:
                    return found
        return None
    
    async def open_file(self, project_id: str, file_path: str) -> bool:
        """Mark a file as open."""
        if project_id not in self.projects:
            return False
        
        project_state = self.projects[project_id]
        project_state.open_files.add(file_path)
        self._write_debug_state()
        return True
    
    async def close_file(self, project_id: str, file_path: str) -> bool:
        """Mark a file as closed."""
        if project_id not in self.projects:
            return False
        
        project_state = self.projects[project_id]
        project_state.open_files.discard(file_path)
        
        # Clear active file if it was the closed file
        if project_state.active_file == file_path:
            project_state.active_file = None
        
        self._write_debug_state()
        return True
    
    async def set_active_file(self, project_id: str, file_path: Optional[str]) -> bool:
        """Set the currently active file."""
        if project_id not in self.projects:
            return False
        
        project_state = self.projects[project_id]
        project_state.active_file = file_path
        
        # Ensure active file is also marked as open
        if file_path:
            project_state.open_files.add(file_path)
        
        self._write_debug_state()
        return True
    
    async def _handle_file_change(self, event):
        """Handle file system change events with debouncing."""
        self._pending_changes.add(event.src_path)
        
        # Cancel existing timer
        if self._change_debounce_timer:
            self._change_debounce_timer.cancel()
        
        # Set new timer
        self._change_debounce_timer = asyncio.create_task(self._process_pending_changes())
    
    async def _process_pending_changes(self):
        """Process pending file changes after debounce delay."""
        await asyncio.sleep(0.5)  # Debounce delay
        
        if not self._pending_changes:
            return
        
        # Process changes for each affected project
        affected_projects = set()
        for change_path in self._pending_changes:
            for project_id, project_state in self.projects.items():
                if change_path.startswith(project_state.project_folder_path):
                    affected_projects.add(project_id)
        
        # Refresh affected projects
        for project_id in affected_projects:
            await self._refresh_project_state(project_id)
        
        self._pending_changes.clear()
    
    async def _refresh_project_state(self, project_id: str):
        """Refresh project state after file changes."""
        if project_id not in self.projects:
            return
        
        project_state = self.projects[project_id]
        git_manager = self.git_managers[project_id]
        
        # Update Git status
        if git_manager:
            project_state.git_status_summary = git_manager.get_status_summary()
        
        # Reload visible directory structures
        await self._reload_visible_structures(project_state)
        
        # Send update to clients
        await self._send_project_state_update(project_state)
        
        self._write_debug_state()
    
    async def _reload_visible_structures(self, project_state: ProjectState):
        """Reload all visible structures with flattened items."""
        await self._build_flattened_items_structure(project_state)
    
    async def _send_project_state_update(self, project_state: ProjectState):
        """Send project state update to clients."""
        payload = {
            "event": "project_state_update",
            "project_id": project_state.project_id,
            "project_folder_path": project_state.project_folder_path,
            "is_git_repo": project_state.is_git_repo,
            "git_branch": project_state.git_branch,
            "git_status_summary": project_state.git_status_summary,
            "open_files": list(project_state.open_files),
            "active_file": project_state.active_file,
            "items": [self._serialize_file_item(item) for item in project_state.items],
            "timestamp": time.time()
        }
        
        # Send via control channel with client session awareness
        await self.control_channel.send(payload)
    
    def cleanup_project(self, project_id: str):
        """Clean up project state and resources."""
        if project_id in self.projects:
            project_state = self.projects[project_id]
            
            # Stop watching all folders for this project
            self.file_watcher.stop_watching(project_state.project_folder_path)
            # Stop watching all expanded folders
            for item in project_state.items:
                if item.is_directory and item.is_expanded:
                    self.file_watcher.stop_watching(item.path)
            
            # Clean up managers
            self.git_managers.pop(project_id, None)
            self.projects.pop(project_id, None)
            
            logger.info("Cleaned up project state: %s", project_id)
            self._write_debug_state()


# Helper function for other handlers to get/create project state manager
def _get_or_create_project_state_manager(context: Dict[str, Any], control_channel) -> 'ProjectStateManager':
    """Get or create project state manager with debug setup."""
    if "project_state_manager" not in context:
        manager = ProjectStateManager(control_channel, context)
        
        # Set up debug mode if enabled
        if context.get("debug", False):
            debug_file_path = os.path.join(os.getcwd(), "project_state_debug.json")
            manager.set_debug_mode(True, debug_file_path)
        
        context["project_state_manager"] = manager
        return manager
    else:
        return context["project_state_manager"]


# Handler classes
class ProjectStateFolderExpandHandler(AsyncHandler):
    """Handler for expanding project folders."""
    
    @property
    def command_name(self) -> str:
        return "project_state_folder_expand"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Expand a folder in project state."""
        project_id = message.get("project_id")
        folder_path = message.get("folder_path")
        
        if not project_id:
            raise ValueError("project_id is required")
        if not folder_path:
            raise ValueError("folder_path is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        success = await manager.expand_folder(project_id, folder_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_id]
            await manager._send_project_state_update(project_state)
        
        return {
            "event": "project_state_folder_expand_response",
            "project_id": project_id,
            "folder_path": folder_path,
            "success": success
        }


class ProjectStateFolderCollapseHandler(AsyncHandler):
    """Handler for collapsing project folders."""
    
    @property
    def command_name(self) -> str:
        return "project_state_folder_collapse"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Collapse a folder in project state."""
        project_id = message.get("project_id")
        folder_path = message.get("folder_path")
        
        if not project_id:
            raise ValueError("project_id is required")
        if not folder_path:
            raise ValueError("folder_path is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        success = await manager.collapse_folder(project_id, folder_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_id]
            await manager._send_project_state_update(project_state)
        
        return {
            "event": "project_state_folder_collapse_response",
            "project_id": project_id,
            "folder_path": folder_path,
            "success": success
        }


class ProjectStateFileOpenHandler(AsyncHandler):
    """Handler for opening files in project state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_file_open"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Open a file in project state."""
        project_id = message.get("project_id")
        file_path = message.get("file_path")
        set_active = message.get("set_active", True)
        
        if not project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        success = await manager.open_file(project_id, file_path)
        
        if success and set_active:
            await manager.set_active_file(project_id, file_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_id]
            await manager._send_project_state_update(project_state)
        
        return {
            "event": "project_state_file_open_response",
            "project_id": project_id,
            "file_path": file_path,
            "success": success,
            "set_active": set_active
        }


class ProjectStateFileCloseHandler(AsyncHandler):
    """Handler for closing files in project state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_file_close"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Close a file in project state."""
        project_id = message.get("project_id")
        file_path = message.get("file_path")
        
        if not project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        success = await manager.close_file(project_id, file_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_id]
            await manager._send_project_state_update(project_state)
        
        return {
            "event": "project_state_file_close_response",
            "project_id": project_id,
            "file_path": file_path,
            "success": success
        }


class ProjectStateSetActiveFileHandler(AsyncHandler):
    """Handler for setting active file in project state."""
    
    @property
    def command_name(self) -> str:
        return "project_state_set_active_file"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Set active file in project state."""
        project_id = message.get("project_id")
        file_path = message.get("file_path")  # Can be None to clear active file
        
        if not project_id:
            raise ValueError("project_id is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        success = await manager.set_active_file(project_id, file_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_id]
            await manager._send_project_state_update(project_state)
        
        return {
            "event": "project_state_set_active_file_response",
            "project_id": project_id,
            "file_path": file_path,
            "success": success
        }