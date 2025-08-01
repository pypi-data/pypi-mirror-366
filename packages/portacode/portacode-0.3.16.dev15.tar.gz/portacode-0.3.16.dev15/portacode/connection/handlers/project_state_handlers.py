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

logger = logging.getLogger(__name__)

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
    logger.info("Watchdog library available for file system monitoring")
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    logger.warning("Watchdog library not available - file system monitoring disabled")


@dataclass
class MonitoredFolder:
    """Represents a folder that is being monitored for changes."""
    folder_path: str
    is_expanded: bool = False

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
    client_session_key: str  # The composite key: client_session_id + "_" + hash(project_folder_path)
    project_folder_path: str
    items: List[FileItem]
    monitored_folders: List[MonitoredFolder] = None
    is_git_repo: bool = False
    git_branch: Optional[str] = None
    git_status_summary: Optional[Dict[str, int]] = None
    open_files: Set[str] = None
    active_file: Optional[str] = None
    
    def __post_init__(self):
        if self.open_files is None:
            self.open_files = set()
        if self.monitored_folders is None:
            self.monitored_folders = []
    
    @property
    def client_session_id(self) -> str:
        """Extract the clean client session ID from the composite key."""
        return self.client_session_key.split('_')[0]


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
                super().__init__()
            
            def on_any_event(self, event):
                # Skip directory events for .git to avoid noise
                if '.git' in event.src_path:
                    return
                
                logger.info("File system event: %s - %s", event.event_type, event.src_path)
                
                # Create async task to handle the change
                try:
                    asyncio.create_task(self.manager._handle_file_change(event))
                except RuntimeError as e:
                    # Handle case where event loop might not be running
                    logger.warning("Could not create async task for file change: %s", e)
        
        self.event_handler = ProjectEventHandler(self.project_manager)
        self.observer = Observer()
    
    def start_watching(self, path: str):
        """Start watching a specific path."""
        if not WATCHDOG_AVAILABLE or not self.observer:
            logger.warning("Watchdog not available, cannot start watching: %s", path)
            return
        
        if path not in self.watched_paths:
            try:
                # Use recursive=True to watch subdirectories as well
                self.observer.schedule(self.event_handler, path, recursive=True)
                self.watched_paths.add(path)
                logger.info("Started watching path (recursive): %s", path)
                
                if not self.observer.is_alive():
                    self.observer.start()
                    logger.info("Started file system observer")
            except Exception as e:
                logger.error("Error starting file watcher for %s: %s", path, e)
        else:
            logger.debug("Path already being watched: %s", path)
    
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
        logger.info("_write_debug_state called: debug_mode=%s, debug_file_path=%s", self.debug_mode, self.debug_file_path)
        if not self.debug_mode or not self.debug_file_path:
            logger.info("Debug mode not enabled or no debug file path, skipping debug write")
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
                    "monitored_folders": [asdict(mf) for mf in state.monitored_folders],
                    "items": [self._serialize_file_item(item) for item in state.items]
                }
            
            with open(self.debug_file_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, default=str)
            
            logger.info("Debug state written successfully to: %s", self.debug_file_path)
            logger.info("Debug data summary: %d projects", len(debug_data))
            for project_id, data in debug_data.items():
                logger.info("Project %s: %d monitored_folders, %d items", 
                           project_id, len(data.get('monitored_folders', [])), len(data.get('items', [])))
                
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
        client_session_key = f"{client_session}_{hash(project_folder_path)}"
        
        if client_session_key in self.projects:
            return self.projects[client_session_key]
        
        logger.info("Initializing project state for client session: %s, folder: %s", client_session, project_folder_path)
        
        # Initialize Git manager
        git_manager = GitManager(project_folder_path)
        self.git_managers[client_session_key] = git_manager
        
        # Create project state
        project_state = ProjectState(
            client_session_key=client_session_key,
            project_folder_path=project_folder_path,
            items=[],
            is_git_repo=git_manager.is_git_repo,
            git_branch=git_manager.get_branch_name(),
            git_status_summary=git_manager.get_status_summary()
        )
        
        # Initialize monitored folders with project root and its immediate subdirectories
        await self._initialize_monitored_folders(project_state)
        
        # Sync all dependent state (items, watchdog)
        await self._sync_all_state_with_monitored_folders(project_state)
        
        self.projects[client_session_key] = project_state
        self._write_debug_state()
        
        return project_state
    
    async def _initialize_monitored_folders(self, project_state: ProjectState):
        """Initialize monitored folders with project root (expanded) and its immediate subdirectories (collapsed)."""
        # Add project root as expanded
        project_state.monitored_folders.append(
            MonitoredFolder(folder_path=project_state.project_folder_path, is_expanded=True)
        )
        
        # Scan project root for immediate subdirectories and add them as collapsed
        try:
            with os.scandir(project_state.project_folder_path) as entries:
                for entry in entries:
                    if entry.is_dir() and entry.name != '.git':  # Only exclude .git, allow other dot folders
                        project_state.monitored_folders.append(
                            MonitoredFolder(folder_path=entry.path, is_expanded=False)
                        )
        except (OSError, PermissionError) as e:
            logger.error("Error scanning project root for subdirectories: %s", e)
    
    async def _start_watching_monitored_folders(self, project_state: ProjectState):
        """Start watching all monitored folders."""
        for monitored_folder in project_state.monitored_folders:
            self.file_watcher.start_watching(monitored_folder.folder_path)
    
    async def _sync_watchdog_with_monitored_folders(self, project_state: ProjectState):
        """Ensure watchdog is monitoring the project folder recursively."""
        # Since we're using recursive=True, we only need to watch the project root
        # This will automatically catch all changes in monitored folders
        self.file_watcher.start_watching(project_state.project_folder_path)
        
        logger.info("Watchdog synchronized: watching project root recursively: %s", project_state.project_folder_path)
    
    async def _sync_all_state_with_monitored_folders(self, project_state: ProjectState):
        """Synchronize all dependent state (watchdog, items) with monitored_folders changes."""
        logger.info("_sync_all_state_with_monitored_folders called")
        logger.info("Current monitored_folders count: %d", len(project_state.monitored_folders))
        
        # Sync watchdog monitoring
        logger.info("Syncing watchdog monitoring")
        await self._sync_watchdog_with_monitored_folders(project_state)
        
        # Rebuild items structure from all monitored folders
        logger.info("Rebuilding items structure")
        await self._build_flattened_items_structure(project_state)
        logger.info("Items count after rebuild: %d", len(project_state.items))
        
        # Update debug state
        logger.info("Writing debug state")
        self._write_debug_state()
        logger.info("_sync_all_state_with_monitored_folders completed")
    
    async def _add_subdirectories_to_monitored(self, project_state: ProjectState, parent_folder_path: str):
        """Add all subdirectories of a folder to monitored_folders if not already present."""
        logger.info("_add_subdirectories_to_monitored called for: %s", parent_folder_path)
        try:
            existing_paths = {mf.folder_path for mf in project_state.monitored_folders}
            logger.info("Existing monitored paths: %s", existing_paths)
            added_any = False
            
            with os.scandir(parent_folder_path) as entries:
                for entry in entries:
                    if entry.is_dir() and entry.name != '.git':  # Only exclude .git, allow other dot folders
                        logger.info("Found subdirectory: %s", entry.path)
                        if entry.path not in existing_paths:
                            logger.info("Adding new monitored folder: %s", entry.path)
                            new_monitored = MonitoredFolder(folder_path=entry.path, is_expanded=False)
                            project_state.monitored_folders.append(new_monitored)
                            added_any = True
                        else:
                            logger.info("Subdirectory already monitored: %s", entry.path)
            
            logger.info("Added any new folders: %s", added_any)
            # If we added any new folders, sync all dependent state
            if added_any:
                logger.info("Calling sync_all_state_with_monitored_folders from _add_subdirectories_to_monitored")
                await self._sync_all_state_with_monitored_folders(project_state)
                
        except (OSError, PermissionError) as e:
            logger.error("Error scanning folder %s for subdirectories: %s", parent_folder_path, e)
    
    def _find_monitored_folder(self, project_state: ProjectState, folder_path: str) -> Optional[MonitoredFolder]:
        """Find a monitored folder by path."""
        for monitored_folder in project_state.monitored_folders:
            if monitored_folder.folder_path == folder_path:
                return monitored_folder
        return None
    
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
        """Build a flattened items structure including ALL items from ALL monitored folders."""
        all_items = []
        
        # Create a set of expanded folder paths for quick lookup
        expanded_paths = {mf.folder_path for mf in project_state.monitored_folders if mf.is_expanded}
        
        # Load items from ALL monitored folders
        for monitored_folder in project_state.monitored_folders:
            # Load direct children of this monitored folder
            children = await self._load_directory_items_list(monitored_folder.folder_path, monitored_folder.folder_path)
            
            # Mark directories as expanded if they are in expanded_paths and add all items
            for child in children:
                if child.is_directory and child.path in expanded_paths:
                    child.is_expanded = True
                all_items.append(child)
        
        # Remove duplicates (items might be loaded multiple times due to nested monitoring)
        # Use a dict to deduplicate by path while preserving the last loaded state
        items_dict = {}
        for item in all_items:
            items_dict[item.path] = item
        
        # Convert back to list and sort for consistent ordering
        project_state.items = list(items_dict.values())
        project_state.items.sort(key=lambda x: (x.parent_path, not x.is_directory, x.name.lower()))
    
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
                            is_expanded=False,
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
    
    async def expand_folder(self, client_session_key: str, folder_path: str) -> bool:
        """Expand a folder and load its contents."""
        logger.info("expand_folder called: client_session_key=%s, folder_path=%s", client_session_key, folder_path)
        
        if client_session_key not in self.projects:
            logger.error("Project state not found for key: %s", client_session_key)
            return False
        
        project_state = self.projects[client_session_key]
        logger.info("Found project state. Current monitored_folders count: %d", len(project_state.monitored_folders))
        
        # Debug: log all monitored folders
        for i, mf in enumerate(project_state.monitored_folders):
            logger.info("Monitored folder %d: path=%s, is_expanded=%s", i, mf.folder_path, mf.is_expanded)
        
        # Update the monitored folder to expanded state
        monitored_folder = self._find_monitored_folder(project_state, folder_path)
        if not monitored_folder:
            logger.error("Monitored folder not found for path: %s", folder_path)
            return False
        
        logger.info("Found monitored folder: %s, current is_expanded: %s", monitored_folder.folder_path, monitored_folder.is_expanded)
        monitored_folder.is_expanded = True
        logger.info("Set monitored folder to expanded: %s", monitored_folder.is_expanded)
        
        # Add all subdirectories of the expanded folder to monitored folders
        logger.info("Adding subdirectories to monitored for: %s", folder_path)
        await self._add_subdirectories_to_monitored(project_state, folder_path)
        
        # Sync all dependent state (this will update items and watchdog)
        logger.info("Syncing all state with monitored folders")
        await self._sync_all_state_with_monitored_folders(project_state)
        
        logger.info("expand_folder completed successfully")
        return True
    
    async def collapse_folder(self, client_session_key: str, folder_path: str) -> bool:
        """Collapse a folder."""
        if client_session_key not in self.projects:
            return False
        
        project_state = self.projects[client_session_key]
        
        # Update the monitored folder to collapsed state
        monitored_folder = self._find_monitored_folder(project_state, folder_path)
        if not monitored_folder:
            return False
        
        monitored_folder.is_expanded = False
        
        # Note: We keep monitoring collapsed folders for file changes
        # but don't stop watching them as we want to detect new files/folders
        
        # Sync all dependent state (this will update items with correct expansion state)
        await self._sync_all_state_with_monitored_folders(project_state)
        
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
    
    async def open_file(self, client_session_key: str, file_path: str) -> bool:
        """Mark a file as open."""
        if client_session_key not in self.projects:
            return False
        
        project_state = self.projects[client_session_key]
        project_state.open_files.add(file_path)
        self._write_debug_state()
        return True
    
    async def close_file(self, client_session_key: str, file_path: str) -> bool:
        """Mark a file as closed."""
        if client_session_key not in self.projects:
            return False
        
        project_state = self.projects[client_session_key]
        project_state.open_files.discard(file_path)
        
        # Clear active file if it was the closed file
        if project_state.active_file == file_path:
            project_state.active_file = None
        
        self._write_debug_state()
        return True
    
    async def set_active_file(self, client_session_key: str, file_path: Optional[str]) -> bool:
        """Set the currently active file."""
        if client_session_key not in self.projects:
            return False
        
        project_state = self.projects[client_session_key]
        project_state.active_file = file_path
        
        # Ensure active file is also marked as open
        if file_path:
            project_state.open_files.add(file_path)
        
        self._write_debug_state()
        return True
    
    async def _handle_file_change(self, event):
        """Handle file system change events with debouncing."""
        logger.info("Processing file change: %s - %s", event.event_type, event.src_path)
        
        self._pending_changes.add(event.src_path)
        
        # Cancel existing timer
        if self._change_debounce_timer:
            self._change_debounce_timer.cancel()
        
        # Set new timer
        logger.info("Starting debounce timer for file changes")
        self._change_debounce_timer = asyncio.create_task(self._process_pending_changes())
    
    async def _process_pending_changes(self):
        """Process pending file changes after debounce delay."""
        logger.info("Processing %d pending file changes after debounce", len(self._pending_changes))
        await asyncio.sleep(0.5)  # Debounce delay
        
        if not self._pending_changes:
            logger.info("No pending changes to process")
            return
        
        logger.info("Pending changes: %s", list(self._pending_changes))
        
        # Process changes for each affected project
        affected_projects = set()
        for change_path in self._pending_changes:
            logger.info("Checking change path: %s", change_path)
            for client_session_key, project_state in self.projects.items():
                if change_path.startswith(project_state.project_folder_path):
                    logger.info("Change affects project: %s", client_session_key)
                    affected_projects.add(client_session_key)
        
        logger.info("Refreshing %d affected projects", len(affected_projects))
        
        # Refresh affected projects
        for client_session_key in affected_projects:
            logger.info("Refreshing project state: %s", client_session_key)
            await self._refresh_project_state(client_session_key)
        
        self._pending_changes.clear()
        logger.info("Finished processing file changes")
    
    async def _refresh_project_state(self, client_session_key: str):
        """Refresh project state after file changes."""
        if client_session_key not in self.projects:
            return
        
        project_state = self.projects[client_session_key]
        git_manager = self.git_managers[client_session_key]
        
        # Update Git status
        if git_manager:
            project_state.git_status_summary = git_manager.get_status_summary()
        
        # Check if any new directories were added that should be monitored
        await self._detect_and_add_new_directories(project_state)
        
        # Sync all dependent state (items, watchdog)
        await self._sync_all_state_with_monitored_folders(project_state)
        
        # Send update to clients
        await self._send_project_state_update(project_state)
    
    async def _detect_and_add_new_directories(self, project_state: ProjectState):
        """Detect new directories in monitored folders and add them to monitoring."""
        # For each currently monitored folder, check if new subdirectories appeared
        monitored_folder_paths = [mf.folder_path for mf in project_state.monitored_folders]
        
        for folder_path in monitored_folder_paths:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                await self._add_subdirectories_to_monitored(project_state, folder_path)
    
    async def _reload_visible_structures(self, project_state: ProjectState):
        """Reload all visible structures with flattened items."""
        await self._build_flattened_items_structure(project_state)
    
    async def _send_project_state_update(self, project_state: ProjectState, server_project_id: str = None):
        """Send project state update to the specific client session only."""
        payload = {
            "event": "project_state_update",
            "project_id": server_project_id or project_state.client_session_key,  # Use server ID if provided
            "project_folder_path": project_state.project_folder_path,
            "is_git_repo": project_state.is_git_repo,
            "git_branch": project_state.git_branch,
            "git_status_summary": project_state.git_status_summary,
            "open_files": list(project_state.open_files),
            "active_file": project_state.active_file,
            "items": [self._serialize_file_item(item) for item in project_state.items],
            "timestamp": time.time(),
            "client_sessions": [project_state.client_session_id]  # Target only this client session
        }
        
        # Send via control channel with client session targeting
        await self.control_channel.send(payload)
    
    def cleanup_project(self, client_session_key: str):
        """Clean up project state and resources."""
        if client_session_key in self.projects:
            project_state = self.projects[client_session_key]
            
            # Stop watching all monitored folders for this project
            for monitored_folder in project_state.monitored_folders:
                self.file_watcher.stop_watching(monitored_folder.folder_path)
            
            # Clean up managers
            self.git_managers.pop(client_session_key, None)
            self.projects.pop(client_session_key, None)
            
            logger.info("Cleaned up project state: %s", client_session_key)
            self._write_debug_state()
    
    def cleanup_projects_by_client_session(self, client_session_id: str):
        """Clean up all project states for a specific client session."""
        logger.info("Cleaning up all project states for client session: %s", client_session_id)
        
        # Find all project states that belong to this client session
        keys_to_remove = []
        for client_session_key in self.projects.keys():
            if client_session_key.startswith(client_session_id):
                keys_to_remove.append(client_session_key)
        
        # Clean up each project state
        for client_session_key in keys_to_remove:
            self.cleanup_project(client_session_key)
        
        logger.info("Cleaned up %d project states for client session: %s", len(keys_to_remove), client_session_id)
    
    def cleanup_all_projects(self):
        """Clean up all project states. Used for shutdown or reset."""
        logger.info("Cleaning up all project states")
        
        keys_to_remove = list(self.projects.keys())
        for client_session_key in keys_to_remove:
            self.cleanup_project(client_session_key)
        
        logger.info("Cleaned up %d project states", len(keys_to_remove))


# Helper function for other handlers to get/create project state manager
def _get_or_create_project_state_manager(context: Dict[str, Any], control_channel) -> 'ProjectStateManager':
    """Get or create project state manager with debug setup."""
    logger.info("_get_or_create_project_state_manager called")
    logger.info("Context debug flag: %s", context.get("debug", False))
    
    if "project_state_manager" not in context:
        logger.info("Creating new ProjectStateManager")
        manager = ProjectStateManager(control_channel, context)
        
        # Set up debug mode if enabled
        if context.get("debug", False):
            debug_file_path = os.path.join(os.getcwd(), "project_state_debug.json")
            logger.info("Setting up debug mode with file: %s", debug_file_path)
            manager.set_debug_mode(True, debug_file_path)
        else:
            logger.info("Debug mode not enabled in context")
        
        context["project_state_manager"] = manager
        logger.info("Created and stored new manager")
        return manager
    else:
        logger.info("Returning existing project state manager")
        return context["project_state_manager"]


# Handler classes
class ProjectStateFolderExpandHandler(AsyncHandler):
    """Handler for expanding project folders."""
    
    @property
    def command_name(self) -> str:
        return "project_state_folder_expand"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Expand a folder in project state."""
        logger.info("ProjectStateFolderExpandHandler.execute called with message: %s", message)
        
        server_project_id = message.get("project_id")  # Server-side UUID (for response)
        folder_path = message.get("folder_path")
        source_client_session = message.get("source_client_session")  # This is our key
        
        logger.info("Extracted server_project_id: %s, folder_path: %s, source_client_session: %s", 
                   server_project_id, folder_path, source_client_session)
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not folder_path:
            raise ValueError("folder_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        logger.info("Getting project state manager...")
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        logger.info("Got manager: %s", manager)
        
        # Find project state using client session - we need to find which project state this client session has
        project_state_key = None
        for key in manager.projects.keys():
            if key.startswith(source_client_session):
                project_state_key = key
                break
        
        if not project_state_key:
            logger.error("No project state found for client session: %s", source_client_session)
            response = {
                "event": "project_state_folder_expand_response",
                "project_id": server_project_id,
                "folder_path": folder_path,
                "success": False
            }
            logger.info("Returning response: %s", response)
            return response
        
        logger.info("Found project state key: %s", project_state_key)
        
        logger.info("Calling manager.expand_folder...")
        success = await manager.expand_folder(project_state_key, folder_path)
        logger.info("expand_folder returned: %s", success)
        
        if success:
            # Send updated state
            logger.info("Sending project state update...")
            project_state = manager.projects[project_state_key]
            await manager._send_project_state_update(project_state, server_project_id)
            logger.info("Project state update sent")
        
        response = {
            "event": "project_state_folder_expand_response",
            "project_id": server_project_id,  # Return the server-side project ID
            "folder_path": folder_path,
            "success": success
        }
        
        logger.info("Returning response: %s", response)
        return response


class ProjectStateFolderCollapseHandler(AsyncHandler):
    """Handler for collapsing project folders."""
    
    @property
    def command_name(self) -> str:
        return "project_state_folder_collapse"
    
    async def execute(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Collapse a folder in project state."""
        server_project_id = message.get("project_id")  # Server-side UUID (for response)
        folder_path = message.get("folder_path")
        source_client_session = message.get("source_client_session")  # This is our key
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not folder_path:
            raise ValueError("folder_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        # Find project state using client session
        project_state_key = None
        for key in manager.projects.keys():
            if key.startswith(source_client_session):
                project_state_key = key
                break
        
        if not project_state_key:
            return {
                "event": "project_state_folder_collapse_response",
                "project_id": server_project_id,
                "folder_path": folder_path,
                "success": False
            }
        
        success = await manager.collapse_folder(project_state_key, folder_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_state_key]
            await manager._send_project_state_update(project_state, server_project_id)
        
        return {
            "event": "project_state_folder_collapse_response",
            "project_id": server_project_id,  # Return the server-side project ID
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
        server_project_id = message.get("project_id")  # Server-side UUID (for response)
        file_path = message.get("file_path")
        source_client_session = message.get("source_client_session")  # This is our key
        set_active = message.get("set_active", True)
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        # Find project state using client session
        project_state_key = None
        for key in manager.projects.keys():
            if key.startswith(source_client_session):
                project_state_key = key
                break
        
        if not project_state_key:
            return {
                "event": "project_state_file_open_response",
                "project_id": server_project_id,
                "file_path": file_path,
                "success": False,
                "set_active": set_active
            }
        
        success = await manager.open_file(project_state_key, file_path)
        
        if success and set_active:
            await manager.set_active_file(project_state_key, file_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_state_key]
            await manager._send_project_state_update(project_state, server_project_id)
        
        return {
            "event": "project_state_file_open_response",
            "project_id": server_project_id,  # Return the server-side project ID
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
        server_project_id = message.get("project_id")  # Server-side UUID (for response)
        file_path = message.get("file_path")
        source_client_session = message.get("source_client_session")  # This is our key
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not file_path:
            raise ValueError("file_path is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        # Find project state using client session
        project_state_key = None
        for key in manager.projects.keys():
            if key.startswith(source_client_session):
                project_state_key = key
                break
        
        if not project_state_key:
            return {
                "event": "project_state_file_close_response",
                "project_id": server_project_id,
                "file_path": file_path,
                "success": False
            }
        
        success = await manager.close_file(project_state_key, file_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_state_key]
            await manager._send_project_state_update(project_state, server_project_id)
        
        return {
            "event": "project_state_file_close_response",
            "project_id": server_project_id,  # Return the server-side project ID
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
        server_project_id = message.get("project_id")  # Server-side UUID (for response)
        file_path = message.get("file_path")  # Can be None to clear active file
        source_client_session = message.get("source_client_session")  # This is our key
        
        if not server_project_id:
            raise ValueError("project_id is required")
        if not source_client_session:
            raise ValueError("source_client_session is required")
        
        manager = _get_or_create_project_state_manager(self.context, self.control_channel)
        
        # Find project state using client session
        project_state_key = None
        for key in manager.projects.keys():
            if key.startswith(source_client_session):
                project_state_key = key
                break
        
        if not project_state_key:
            return {
                "event": "project_state_set_active_file_response",
                "project_id": server_project_id,
                "file_path": file_path,
                "success": False
            }
        
        success = await manager.set_active_file(project_state_key, file_path)
        
        if success:
            # Send updated state
            project_state = manager.projects[project_state_key]
            await manager._send_project_state_update(project_state, server_project_id)
        
        return {
            "event": "project_state_set_active_file_response",
            "project_id": server_project_id,  # Return the server-side project ID
            "file_path": file_path,
            "success": success
        }