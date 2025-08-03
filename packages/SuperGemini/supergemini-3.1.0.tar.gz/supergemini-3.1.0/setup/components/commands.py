"""
Commands component for SuperGemini slash command definitions
"""

from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import re

from ..base.component import Component

class CommandsComponent(Component):
    """SuperGemini slash commands component"""
    
    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize commands component"""
        super().__init__(install_dir, Path("commands/sg"))
    
    def get_metadata(self) -> Dict[str, str]:
        """Get component metadata"""
        return {
            "name": "commands",
            "version": "3.0.0",
            "description": "SuperGemini slash command definitions",
            "category": "commands"
        }
    
    def get_metadata_modifications(self) -> Dict[str, Any]:
        """Get metadata modifications for commands component"""
        return {
            "components": {
                "commands": {
                    "version": "3.0.0",
                    "installed": True,
                    "files_count": len(self.component_files)
                }
            },
            "commands": {
                "enabled": True,
                "version": "3.0.0",
                "auto_update": False
            }
        }
    
    def _install(self, config: Dict[str, Any]) -> bool:
        """Install commands component"""
        self.logger.info("Installing SuperGemini command definitions...")

        # Check for and migrate existing commands from old location
        self._migrate_existing_commands()

        return super()._install(config);

    def _post_install(self):
        # Convert MD files to TOML for Gemini CLI compatibility
        self._convert_md_to_toml()
        
        # Update metadata
        try:
            metadata_mods = self.get_metadata_modifications()
            self.settings_manager.update_metadata(metadata_mods)
            self.logger.info("Updated metadata with commands configuration")

            # Add component registration to metadata
            self.settings_manager.add_component_registration("commands", {
                "version": "3.0.0",
                "category": "commands",
                "files_count": len(self.component_files)
            })
            self.logger.info("Updated metadata with commands component registration")
        except Exception as e:
            self.logger.error(f"Failed to update metadata: {e}")
            return False

        return True
    
    def uninstall(self) -> bool:
        """Uninstall commands component"""
        try:
            self.logger.info("Uninstalling SuperGemini commands component...")
            
            # Remove command files from sg subdirectory
            commands_dir = self.install_dir / "commands" / "sg"
            removed_count = 0
            
            for filename in self.component_files:
                file_path = commands_dir / filename
                if self.file_manager.remove_file(file_path):
                    removed_count += 1
                    self.logger.debug(f"Removed {filename}")
                else:
                    self.logger.warning(f"Could not remove {filename}")
            
            # Also check and remove any old commands in root commands directory
            old_commands_dir = self.install_dir / "commands"
            old_removed_count = 0
            
            for filename in self.component_files:
                old_file_path = old_commands_dir / filename
                if old_file_path.exists() and old_file_path.is_file():
                    if self.file_manager.remove_file(old_file_path):
                        old_removed_count += 1
                        self.logger.debug(f"Removed old {filename}")
                    else:
                        self.logger.warning(f"Could not remove old {filename}")
            
            if old_removed_count > 0:
                self.logger.info(f"Also removed {old_removed_count} commands from old location")
            
            removed_count += old_removed_count
            
            # Remove sg subdirectory if empty
            try:
                if commands_dir.exists():
                    remaining_files = list(commands_dir.iterdir())
                    if not remaining_files:
                        commands_dir.rmdir()
                        self.logger.debug("Removed empty sc commands directory")
                        
                        # Also remove parent commands directory if empty
                        parent_commands_dir = self.install_dir / "commands"
                        if parent_commands_dir.exists():
                            remaining_files = list(parent_commands_dir.iterdir())
                            if not remaining_files:
                                parent_commands_dir.rmdir()
                                self.logger.debug("Removed empty parent commands directory")
            except Exception as e:
                self.logger.warning(f"Could not remove commands directory: {e}")
            
            # Update metadata to remove commands component
            try:
                if self.settings_manager.is_component_installed("commands"):
                    self.settings_manager.remove_component_registration("commands")
                    # Also remove commands configuration from metadata
                    metadata = self.settings_manager.load_metadata()
                    if "commands" in metadata:
                        del metadata["commands"]
                        self.settings_manager.save_metadata(metadata)
                    self.logger.info("Removed commands component from metadata")
            except Exception as e:
                self.logger.warning(f"Could not update metadata: {e}")
            
            self.logger.success(f"Commands component uninstalled ({removed_count} files removed)")
            return True
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during commands uninstallation: {e}")
            return False
    
    def get_dependencies(self) -> List[str]:
        """Get dependencies"""
        return ["core"]
    
    def update(self, config: Dict[str, Any]) -> bool:
        """Update commands component"""
        try:
            self.logger.info("Updating SuperGemini commands component...")
            
            # Check current version
            current_version = self.settings_manager.get_component_version("commands")
            target_version = self.get_metadata()["version"]
            
            if current_version == target_version:
                self.logger.info(f"Commands component already at version {target_version}")
                return True
            
            self.logger.info(f"Updating commands component from {current_version} to {target_version}")
            
            # Create backup of existing command files
            commands_dir = self.install_dir / "commands" / "sg"
            backup_files = []
            
            if commands_dir.exists():
                for filename in self.component_files:
                    file_path = commands_dir / filename
                    if file_path.exists():
                        backup_path = self.file_manager.backup_file(file_path)
                        if backup_path:
                            backup_files.append(backup_path)
                            self.logger.debug(f"Backed up {filename}")
            
            # Perform installation (overwrites existing files)
            success = self.install(config)
            
            if success:
                # Remove backup files on successful update
                for backup_path in backup_files:
                    try:
                        backup_path.unlink()
                    except Exception:
                        pass  # Ignore cleanup errors
                
                self.logger.success(f"Commands component updated to version {target_version}")
            else:
                # Restore from backup on failure
                self.logger.warning("Update failed, restoring from backup...")
                for backup_path in backup_files:
                    try:
                        original_path = backup_path.with_suffix('')
                        backup_path.rename(original_path)
                        self.logger.debug(f"Restored {original_path.name}")
                    except Exception as e:
                        self.logger.error(f"Could not restore {backup_path}: {e}")
            
            return success
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during commands update: {e}")
            return False
    
    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate commands component installation"""
        errors = []
        
        # Check if sc commands directory exists
        commands_dir = self.install_dir / "commands" / "sg"
        if not commands_dir.exists():
            errors.append("SG commands directory not found")
            return False, errors
        
        # Check if all command files exist
        for filename in self.component_files:
            file_path = commands_dir / filename
            if not file_path.exists():
                errors.append(f"Missing command file: {filename}")
            elif not file_path.is_file():
                errors.append(f"Command file is not a regular file: {filename}")
        
        # Check metadata registration
        if not self.settings_manager.is_component_installed("commands"):
            errors.append("Commands component not registered in metadata")
        else:
            # Check version matches
            installed_version = self.settings_manager.get_component_version("commands")
            expected_version = self.get_metadata()["version"]
            if installed_version != expected_version:
                errors.append(f"Version mismatch: installed {installed_version}, expected {expected_version}")
        
        return len(errors) == 0, errors
    
    def _get_source_dir(self) -> Path:
        """Get source directory for command files"""
        # Assume we're in SuperGemini/setup/components/commands.py
        # and command files are in SuperGemini/SuperGemini/Commands/
        project_root = Path(__file__).parent.parent.parent
        return project_root / "SuperGemini" / "Commands"
    
    def get_size_estimate(self) -> int:
        """Get estimated installation size"""
        total_size = 0
        source_dir = self._get_source_dir()
        
        for filename in self.component_files:
            file_path = source_dir / filename
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        # Add overhead for directory and settings
        total_size += 5120  # ~5KB overhead
        
        return total_size
    
    def get_installation_summary(self) -> Dict[str, Any]:
        """Get installation summary"""
        return {
            "component": self.get_metadata()["name"],
            "version": self.get_metadata()["version"],
            "files_installed": len(self.component_files),
            "command_files": self.component_files,
            "estimated_size": self.get_size_estimate(),
            "install_directory": str(self.install_dir / "commands" / "sg"),
            "dependencies": self.get_dependencies()
        }
    
    def _migrate_existing_commands(self) -> None:
        """Migrate existing commands from old location to new sg subdirectory"""
        try:
            old_commands_dir = self.install_dir / "commands"
            new_commands_dir = self.install_dir / "commands" / "sg"
            
            # Check if old commands exist in root commands directory
            migrated_count = 0
            commands_to_migrate = []
            
            if old_commands_dir.exists():
                for filename in self.component_files:
                    old_file_path = old_commands_dir / filename
                    if old_file_path.exists() and old_file_path.is_file():
                        commands_to_migrate.append(filename)
            
            if commands_to_migrate:
                self.logger.info(f"Found {len(commands_to_migrate)} existing commands to migrate to sg/ subdirectory")
                
                # Ensure new directory exists
                if not self.file_manager.ensure_directory(new_commands_dir):
                    self.logger.error(f"Could not create sc commands directory: {new_commands_dir}")
                    return
                
                # Move files from old to new location
                for filename in commands_to_migrate:
                    old_file_path = old_commands_dir / filename
                    new_file_path = new_commands_dir / filename
                    
                    try:
                        # Copy file to new location
                        if self.file_manager.copy_file(old_file_path, new_file_path):
                            # Remove old file
                            if self.file_manager.remove_file(old_file_path):
                                migrated_count += 1
                                self.logger.debug(f"Migrated {filename} to sg/ subdirectory")
                            else:
                                self.logger.warning(f"Could not remove old {filename}")
                        else:
                            self.logger.warning(f"Could not copy {filename} to sg/ subdirectory")
                    except Exception as e:
                        self.logger.warning(f"Error migrating {filename}: {e}")
                
                if migrated_count > 0:
                    self.logger.success(f"Successfully migrated {migrated_count} commands to /sg: namespace")
                    self.logger.info("Commands are now available as /sg:analyze, /sg:build, etc.")
                    
                    # Try to remove old commands directory if empty
                    try:
                        if old_commands_dir.exists():
                            remaining_files = [f for f in old_commands_dir.iterdir() if f.is_file()]
                            if not remaining_files:
                                # Only remove if no user files remain
                                old_commands_dir.rmdir()
                                self.logger.debug("Removed empty old commands directory")
                    except Exception as e:
                        self.logger.debug(f"Could not remove old commands directory: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Error during command migration: {e}")
    
    def _convert_md_to_toml(self) -> None:
        """Convert MD command files to TOML format for Gemini CLI compatibility"""
        try:
            commands_dir = self.install_dir / "commands" / "sg"
            if not commands_dir.exists():
                self.logger.warning("Commands directory not found for TOML conversion")
                return
            
            converted_count = 0
            
            for md_file in commands_dir.glob("*.md"):
                try:
                    # Read MD content
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Extract front matter
                    description = ""
                    main_content = content
                    
                    front_matter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                    if front_matter_match:
                        front_matter = front_matter_match.group(1)
                        main_content = content[front_matter_match.end():]
                        
                        # Extract description
                        desc_match = re.search(r'description:\s*"([^"]+)"', front_matter)
                        if desc_match:
                            description = desc_match.group(1)
                    
                    # Clean up content - remove Gemini Code specific sections
                    main_content = re.sub(r'## Gemini Code Integration.*', '', main_content, flags=re.DOTALL)
                    
                    # Build TOML content
                    prompt = f"SuperGemini {main_content.strip()}"
                    
                    toml_content = f'''prompt = """{prompt}"""

description = "{description}"'''
                    
                    # Write TOML file
                    toml_file = md_file.with_suffix('.toml')
                    toml_file.write_text(toml_content, encoding='utf-8')
                    
                    # Remove MD file
                    md_file.unlink()
                    
                    converted_count += 1
                    self.logger.debug(f"Converted {md_file.name} to TOML format")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to convert {md_file.name}: {e}")
            
            if converted_count > 0:
                self.logger.info(f"Converted {converted_count} command files to TOML format for Gemini CLI")
                
        except Exception as e:
            self.logger.warning(f"Error during MD to TOML conversion: {e}")
