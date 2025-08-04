# this_file: src/camtasio/cli/app.py
"""Unified Camtasio CLI application."""

from datetime import datetime
from pathlib import Path
from typing import Any

import fire
from loguru import logger
from rich.console import Console

from ..scaler import TscprojScaler
from ..serialization import ProjectSaver, detect_version, load_json_file
from ..transforms.engine import PropertyTransformer, TransformConfig, TransformType

console = Console()


class CamtasioCLI:
    """Camtasio command-line interface."""

    def info(self, project_path: str, detailed: bool = False) -> None:
        """Display project information and statistics.

        Args:
            project_path: Path to .tscproj file
            detailed: Show detailed analysis including media usage and complexity metrics
        """
        project_path = Path(project_path)

        try:
            # Load raw JSON data for CLI info display
            project_data = load_json_file(project_path)
            version = detect_version(project_data)

            # Extract basic info
            canvas = project_data.get("timeline", {}).get("sceneTrack", {}).get("timeline", {})
            width = canvas.get("width", "Unknown")
            height = canvas.get("height", "Unknown")
            framerate = canvas.get("framerate", "Unknown")

            console.print("[bold blue]═══ Project Information ═══[/]")
            console.print(f"[bold]Project:[/] {project_path}")
            console.print(f"[bold]Version:[/] {version}")
            console.print(f"[bold]Canvas:[/] {width}x{height} @ {framerate}fps")

            # Analyze media bin
            source_bin = project_data.get("sourceBin", [])
            media_count = len(source_bin)

            # Count media types
            media_types: dict[str, int] = {}
            missing_media = []
            total_file_size = 0

            for item in source_bin:
                media_type = item.get("_type", "Unknown")
                media_types[media_type] = media_types.get(media_type, 0) + 1

                # Check if media file exists
                if "src" in item:
                    media_path = Path(item["src"])
                    if not media_path.exists():
                        missing_media.append(str(media_path))
                    elif media_path.is_file():
                        try:
                            total_file_size += media_path.stat().st_size
                        except OSError:
                            pass

            console.print("\n[bold blue]═══ Media Analysis ═══[/]")
            console.print(f"[bold]Total Media Items:[/] {media_count}")

            if media_types:
                for media_type, count in sorted(media_types.items()):
                    console.print(f"  • {media_type}: {count}")

            if total_file_size > 0:
                size_mb = total_file_size / (1024 * 1024)
                console.print(f"[bold]Total Media Size:[/] {size_mb:.1f} MB")

            if missing_media:
                console.print(f"[red]⚠ Missing Media Files:[/] {len(missing_media)}")
                if detailed:
                    for media in missing_media[:10]:  # Show first 10
                        console.print(f"  • {media}")
                    if len(missing_media) > 10:
                        console.print(f"  ... and {len(missing_media) - 10} more")
            else:
                console.print("[green]✓ All media files found[/]")

            # Analyze timeline
            tracks = project_data.get("timeline", {}).get("sceneTrack", {}).get("scenes", [])
            if tracks:
                scene = tracks[0]
                timeline_tracks = scene.get("csml", {}).get("tracks", [])
                track_count = len(timeline_tracks)

                console.print("\n[bold blue]═══ Timeline Analysis ═══[/]")
                console.print(f"[bold]Timeline Tracks:[/] {track_count}")

                if detailed and timeline_tracks:
                    # Analyze track complexity
                    track_types: dict[str, int] = {}
                    total_clips = 0
                    total_effects = 0

                    for track in timeline_tracks:
                        track_type = track.get("trackType", "Unknown")
                        track_types[track_type] = track_types.get(track_type, 0) + 1

                        # Count track media/clips
                        track_media = track.get("medias", [])
                        total_clips += len(track_media)

                        # Count effects
                        for media in track_media:
                            effects = media.get("effects", [])
                            total_effects += len(effects)

                    console.print("[bold]Track Types:[/]")
                    for track_type, count in sorted(track_types.items()):
                        console.print(f"  • {track_type}: {count}")

                    console.print(f"[bold]Total Clips:[/] {total_clips}")
                    console.print(f"[bold]Total Effects:[/] {total_effects}")

                    # Calculate complexity score
                    complexity_score = (
                        track_count * 1 + total_clips * 2 + total_effects * 3 + media_count * 0.5
                    )

                    if complexity_score < 50:
                        complexity_level = "[green]Simple[/]"
                    elif complexity_score < 150:
                        complexity_level = "[yellow]Moderate[/]"
                    else:
                        complexity_level = "[red]Complex[/]"

                    console.print(
                        f"[bold]Project Complexity:[/] {complexity_level} (score: {complexity_score:.1f})"
                    )

            if detailed:
                # Performance recommendations
                console.print("\n[bold blue]═══ Recommendations ═══[/]")

                if missing_media:
                    console.print("[yellow]• Fix missing media files for best performance[/]")

                if media_count > 100:
                    console.print("[yellow]• Large media bin - consider organizing media[/]")

                if total_file_size > 1024 * 1024 * 1024:  # 1GB
                    console.print(
                        "[yellow]• Large project size - consider optimizing media files[/]"
                    )

                if track_count > 20:
                    console.print(
                        "[yellow]• Many tracks - consider consolidating similar content[/]"
                    )

                console.print("[green]• Project structure looks good![/]")

            logger.info(f"Project info displayed for {project_path}")

        except Exception as e:
            console.print(f"[red]Error:[/] Failed to load project: {e}")
            logger.error(f"Failed to load project {project_path}: {e}")

    def validate(self, project_path: str) -> None:
        """Check project integrity and compatibility."""
        project_path = Path(project_path)

        try:
            # Load raw JSON data for validation
            project_data = load_json_file(project_path)
            version = detect_version(project_data)

            console.print("[green]✓[/] Project loads successfully")
            console.print(f"[green]✓[/] Version {version} is supported")

            # Check for common issues
            source_bin = project_data.get("sourceBin", [])
            missing_media = []

            for item in source_bin:
                if "src" in item and not Path(item["src"]).exists():
                    missing_media.append(item["src"])

            if missing_media:
                console.print("[yellow]⚠[/] Missing media files:")
                for media in missing_media[:5]:  # Show first 5
                    console.print(f"  - {media}")
                if len(missing_media) > 5:
                    console.print(f"  ... and {len(missing_media) - 5} more")
            else:
                console.print("[green]✓[/] All media files found")

        except Exception as e:
            console.print(f"[red]✗[/] Validation failed: {e}")
            logger.error(f"Validation failed for {project_path}: {e}")

    def xyscale(
        self, input_path: str, scale: float, output_path: str | None = None, backup: bool = True
    ) -> None:
        """Scale project canvas and all elements by the given factor.

        Args:
            input_path: Path to input .tscproj file or .cmproj directory
            scale: Scale factor (e.g., 1.5 for 150%)
            output_path: Path for output file (default: overwrite input)
            backup: Create backup before modifying (default: True)
        """
        input_path = Path(input_path)

        if output_path:
            output_path = Path(output_path)
        else:
            output_path = input_path

        try:
            with console.status(f"[bold green]Scaling project by {scale}x..."):
                # Load raw JSON data for scaling
                project_data = load_json_file(input_path)

                # Create backup if requested and modifying in place
                if backup and output_path == input_path:
                    backup_path = input_path.with_suffix(f"{input_path.suffix}.backup")
                    import shutil

                    shutil.copy2(input_path, backup_path)
                    logger.debug(f"Created backup at {backup_path}")

                # Scale the project using TscprojScaler class
                scaler = TscprojScaler(scale, verbose=True)
                scaled_data = scaler._scale_object(project_data)

                # Save result
                saver = ProjectSaver()
                saver.save_dict(scaled_data, output_path)

            console.print(f"[green]✓[/] Scaled project by {scale}x")
            if output_path != input_path:
                console.print(f"[green]✓[/] Saved to {output_path}")
            logger.info(f"Successfully scaled {input_path} by {scale}x")

        except Exception as e:
            console.print(f"[red]Error:[/] Scaling failed: {e}")
            logger.error(f"Failed to scale {input_path}: {e}")

    def timescale(
        self,
        input_path: str,
        scale: float,
        output_path: str | None = None,
        backup: bool = True,
        preserve_audio: bool = True,
    ) -> None:
        """Scale project timeline duration by the given factor.

        Args:
            input_path: Path to input .tscproj file or .cmproj directory
            scale: Time scale factor (e.g., 0.5 for half speed, 2.0 for double speed)
            output_path: Path for output file (default: overwrite input)
            backup: Create backup before modifying (default: True)
            preserve_audio: Preserve audio duration when scaling (default: True)
        """
        input_path = Path(input_path)

        if output_path:
            output_path = Path(output_path)
        else:
            output_path = input_path

        try:
            with console.status(f"[bold green]Scaling timeline by {scale}x..."):
                # Load raw JSON data for temporal scaling
                project_data = load_json_file(input_path)

                # Create backup if requested and modifying in place
                if backup and output_path == input_path:
                    backup_path = input_path.with_suffix(f"{input_path.suffix}.backup")
                    import shutil

                    shutil.copy2(input_path, backup_path)
                    logger.debug(f"Created backup at {backup_path}")

                # Create temporal transform configuration
                config = TransformConfig(
                    transform_type=TransformType.TEMPORAL,
                    factor=scale,
                    preserve_audio_duration=preserve_audio,
                    verbose=True,
                )

                # Apply temporal transformation
                transformer = PropertyTransformer(config)
                scaled_data = transformer.transform_dict(project_data)

                # Save result
                saver = ProjectSaver()
                saver.save_dict(scaled_data, output_path)

            console.print(f"[green]✓[/] Scaled timeline by {scale}x")
            if preserve_audio:
                console.print("[green]✓[/] Audio duration preserved")
            if output_path != input_path:
                console.print(f"[green]✓[/] Saved to {output_path}")
            logger.info(f"Successfully scaled timeline {input_path} by {scale}x")

        except Exception as e:
            console.print(f"[red]Error:[/] Timeline scaling failed: {e}")
            logger.error(f"Failed to scale timeline {input_path}: {e}")

    def batch(self, pattern: str, operation: str, *args: Any, **kwargs: Any) -> None:
        """Process multiple files with batch operations.

        Args:
            pattern: Glob pattern to match files (e.g., "*.tscproj", "projects/**/*.tscproj")
            operation: Operation to perform (xyscale, timescale, info, validate)
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation
        """
        import glob
        from pathlib import Path

        # Find matching files
        matching_files = []
        for path in glob.glob(str(pattern), recursive=True):
            path_obj = Path(path)
            if path_obj.is_file() and path_obj.suffix == ".tscproj":
                matching_files.append(path_obj)

        if not matching_files:
            console.print(f"[yellow]No .tscproj files found matching pattern: {pattern}[/]")
            return

        console.print("[bold blue]═══ Batch Processing ═══[/]")
        console.print(f"[bold]Operation:[/] {operation}")
        console.print(f"[bold]Pattern:[/] {pattern}")
        console.print(f"[bold]Found Files:[/] {len(matching_files)}")

        if len(matching_files) > 10:
            confirm = input(f"Process {len(matching_files)} files? [y/N]: ").lower().strip()
            if confirm != "y":
                console.print("[yellow]Batch operation cancelled[/]")
                return

        success_count = 0
        error_count = 0

        for i, file_path in enumerate(matching_files, 1):
            console.print(f"\n[bold]Processing {i}/{len(matching_files)}:[/] {file_path}")

            try:
                # Call the appropriate method
                if operation == "info":
                    self.info(str(file_path), *args, **kwargs)
                elif operation == "validate":
                    self.validate(str(file_path))
                elif operation == "xyscale":
                    if not args:
                        console.print("[red]Error: xyscale requires scale factor[/]")
                        error_count += 1
                        continue
                    scale = float(args[0])
                    output_path = str(file_path.with_suffix(".scaled.tscproj"))
                    self.xyscale(str(file_path), scale, output_path, **kwargs)
                elif operation == "timescale":
                    if not args:
                        console.print("[red]Error: timescale requires scale factor[/]")
                        error_count += 1
                        continue
                    scale = float(args[0])
                    output_path = str(file_path.with_suffix(".timescaled.tscproj"))
                    self.timescale(str(file_path), scale, output_path, **kwargs)
                else:
                    console.print(f"[red]Error: Unknown operation '{operation}'[/]")
                    error_count += 1
                    continue

                success_count += 1

            except Exception as e:
                console.print(f"[red]Error processing {file_path}: {e}[/]")
                logger.error(f"Batch processing error for {file_path}: {e}")
                error_count += 1

        # Summary
        console.print("\n[bold blue]═══ Batch Results ═══[/]")
        console.print(f"[green]✓ Successful:[/] {success_count}")
        console.print(f"[red]✗ Errors:[/] {error_count}")
        console.print(f"[bold]Total:[/] {len(matching_files)}")

        if success_count > 0:
            console.print("[green]Batch operation completed successfully![/]")
        else:
            console.print("[red]Batch operation failed![/]")

    def media_ls(self, project_path: str, detailed: bool = False) -> None:
        """List media bin contents.

        Args:
            project_path: Path to .tscproj file
            detailed: Show detailed media information
        """
        project_path = Path(project_path)

        try:
            project_data = load_json_file(project_path)

            source_bin = project_data.get("sourceBin", [])

            console.print("[bold blue]═══ Media Bin Contents ═══[/]")
            console.print(f"[bold]Project:[/] {project_path}")
            console.print(f"[bold]Media Items:[/] {len(source_bin)}")

            if not source_bin:
                console.print("[yellow]No media items found[/]")
                return

            for i, item in enumerate(source_bin, 1):
                name = item.get("name", "Unnamed")
                media_type = item.get("_type", "Unknown")
                src = item.get("src", "No source")

                # Check if file exists
                if "src" in item:
                    media_path = Path(item["src"])
                    exists = "✓" if media_path.exists() else "✗"
                    status_color = "green" if media_path.exists() else "red"
                else:
                    exists = "?"
                    status_color = "yellow"

                console.print(f"[bold]{i:2d}.[/] [{status_color}]{exists}[/] {name}")

                if detailed:
                    console.print(f"     Type: {media_type}")
                    console.print(f"     Source: {src}")

                    if "src" in item and Path(item["src"]).exists():
                        try:
                            file_size = Path(item["src"]).stat().st_size
                            size_mb = file_size / (1024 * 1024)
                            console.print(f"     Size: {size_mb:.1f} MB")
                        except OSError:
                            pass
                    console.print()

        except Exception as e:
            console.print(f"[red]Error:[/] Failed to list media: {e}")
            logger.error(f"Failed to list media for {project_path}: {e}")

    def media_rm(self, project_path: str, unused_only: bool = True, backup: bool = True) -> None:
        """Remove unused media from project.

        Args:
            project_path: Path to .tscproj file
            unused_only: Only remove unused media items (default: True)
            backup: Create backup before modifying (default: True)
        """
        project_path = Path(project_path)

        try:
            project_data = load_json_file(project_path)

            source_bin = project_data.get("sourceBin", [])

            if not source_bin:
                console.print("[yellow]No media items to remove[/]")
                return

            # Find used media IDs in timeline
            used_media_ids = set()
            tracks = project_data.get("timeline", {}).get("sceneTrack", {}).get("scenes", [])

            if tracks:
                timeline_tracks = tracks[0].get("csml", {}).get("tracks", [])
                for track in timeline_tracks:
                    for media in track.get("medias", []):
                        if "src" in media:
                            used_media_ids.add(media["src"])

            # Find unused media
            unused_media = []
            for i, item in enumerate(source_bin):
                item_id = item.get("id")
                if unused_only and item_id not in used_media_ids:
                    unused_media.append((i, item))

            if not unused_media:
                console.print("[green]✓ No unused media items found[/]")
                return

            console.print("[bold blue]═══ Remove Unused Media ═══[/]")
            console.print(f"[bold]Found Unused Items:[/] {len(unused_media)}")

            for i, (_idx, item) in enumerate(unused_media[:10]):  # Show first 10
                name = item.get("name", "Unnamed")
                console.print(f"  {i + 1}. {name}")

            if len(unused_media) > 10:
                console.print(f"  ... and {len(unused_media) - 10} more")

            confirm = (
                input(f"Remove {len(unused_media)} unused media items? [y/N]: ").lower().strip()
            )
            if confirm != "y":
                console.print("[yellow]Operation cancelled[/]")
                return

            # Create backup if requested
            if backup:
                backup_path = project_path.with_suffix(f"{project_path.suffix}.backup")
                import shutil

                shutil.copy2(project_path, backup_path)
                logger.debug(f"Created backup at {backup_path}")

            # Remove unused media (in reverse order to maintain indices)
            for idx, _ in reversed(unused_media):
                del project_data["sourceBin"][idx]

            # Save modified project
            saver = ProjectSaver()
            saver.save_dict(project_data, project_path)

            console.print(f"[green]✓ Removed {len(unused_media)} unused media items[/]")

        except Exception as e:
            console.print(f"[red]Error:[/] Failed to remove media: {e}")
            logger.error(f"Failed to remove media from {project_path}: {e}")

    def media_replace(self, project_path: str, old_path: str, new_path: str, backup: bool = True) -> None:
        """Replace media file paths in project.

        Args:
            project_path: Path to .tscproj file
            old_path: Old media file path to replace
            new_path: New media file path
            backup: Create backup before modifying (default: True)
        """
        project_path = Path(project_path)
        old_path = str(old_path)
        new_path = str(new_path)

        try:
            project_data = load_json_file(project_path)

            # Create backup if requested
            if backup:
                backup_path = project_path.with_suffix(f"{project_path.suffix}.backup")
                import shutil

                shutil.copy2(project_path, backup_path)
                logger.debug(f"Created backup at {backup_path}")

            replacements = 0

            def replace_in_dict(obj):
                nonlocal replacements
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "src" and value == old_path:
                            obj[key] = new_path
                            replacements += 1
                        elif isinstance(value, dict | list):
                            replace_in_dict(value)
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, dict | list):
                            replace_in_dict(item)

            replace_in_dict(project_data)

            if replacements == 0:
                console.print(f"[yellow]No instances of '{old_path}' found[/]")
                return

            # Save modified project
            saver = ProjectSaver()
            saver.save_dict(project_data, project_path)

            console.print(
                f"[green]✓ Replaced {replacements} instances of '{old_path}' with '{new_path}'[/]"
            )

        except Exception as e:
            console.print(f"[red]Error:[/] Failed to replace media path: {e}")
            logger.error(f"Failed to replace media path in {project_path}: {e}")

    def track_ls(self, project_path: str, detailed: bool = False) -> None:
        """List timeline tracks.

        Args:
            project_path: Path to .tscproj file
            detailed: Show detailed track information
        """
        project_path = Path(project_path)

        try:
            project_data = load_json_file(project_path)

            tracks = project_data.get("timeline", {}).get("sceneTrack", {}).get("scenes", [])

            console.print("[bold blue]═══ Timeline Tracks ═══[/]")
            console.print(f"[bold]Project:[/] {project_path}")

            if not tracks:
                console.print("[yellow]No timeline tracks found[/]")
                return

            timeline_tracks = tracks[0].get("csml", {}).get("tracks", [])
            console.print(f"[bold]Total Tracks:[/] {len(timeline_tracks)}")

            for i, track in enumerate(timeline_tracks, 1):
                track_type = track.get("trackType", "Unknown")
                track_media = track.get("medias", [])
                media_count = len(track_media)

                # Calculate track duration
                track_duration = 0
                for media in track_media:
                    duration = media.get("duration", 0)
                    start = media.get("start", 0)
                    track_duration = max(track_duration, start + duration)

                console.print(f"[bold]{i:2d}.[/] {track_type} - {media_count} clips")

                if detailed:
                    console.print(f"     Duration: {track_duration / 1000:.2f}s")
                    if track_media:
                        console.print("     Clips:")
                        for j, media in enumerate(track_media[:5], 1):  # Show first 5 clips
                            media_name = media.get("name", "Unnamed")
                            start = media.get("start", 0) / 1000
                            duration = media.get("duration", 0) / 1000
                            console.print(
                                f"       {j}. {media_name} ({start:.2f}s - {start + duration:.2f}s)"
                            )
                        if len(track_media) > 5:
                            console.print(f"       ... and {len(track_media) - 5} more clips")
                    console.print()

        except Exception as e:
            console.print(f"[red]Error:[/] Failed to list tracks: {e}")
            logger.error(f"Failed to list tracks for {project_path}: {e}")

    def marker_ls(self, project_path: str) -> None:
        """List timeline markers.

        Args:
            project_path: Path to .tscproj file
        """
        project_path = Path(project_path)

        try:
            project_data = load_json_file(project_path)

            # Look for markers in timeline
            timeline = project_data.get("timeline", {})
            markers = timeline.get("markers", [])

            console.print("[bold blue]═══ Timeline Markers ═══[/]")
            console.print(f"[bold]Project:[/] {project_path}")
            console.print(f"[bold]Total Markers:[/] {len(markers)}")

            if not markers:
                console.print("[yellow]No markers found[/]")
                return

            for i, marker in enumerate(markers, 1):
                name = marker.get("name", "Unnamed")
                time = marker.get("time", 0) / 1000  # Convert to seconds
                marker_type = marker.get("type", "Unknown")

                console.print(f"[bold]{i:2d}.[/] {name} at {time:.2f}s ({marker_type})")

        except Exception as e:
            console.print(f"[red]Error:[/] Failed to list markers: {e}")
            logger.error(f"Failed to list markers for {project_path}: {e}")

    def analyze(self, project_path: str) -> None:
        """Generate comprehensive project analysis report.

        Args:
            project_path: Path to .tscproj file
        """
        project_path = Path(project_path)

        try:
            project_data = load_json_file(project_path)

            version = detect_version(project_data)

            console.print("[bold blue]═══ Project Analysis Report ═══[/]")
            console.print(f"[bold]Project:[/] {project_path}")
            console.print(f"[bold]Generated:[/] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Basic project info
            canvas = project_data.get("timeline", {}).get("sceneTrack", {}).get("timeline", {})
            width = canvas.get("width", "Unknown")
            height = canvas.get("height", "Unknown")
            framerate = canvas.get("framerate", "Unknown")

            console.print("\n[bold green]📊 Project Overview[/]")
            console.print(f"Version: {version}")
            console.print(f"Canvas: {width}x{height} @ {framerate}fps")

            # Media analysis
            source_bin = project_data.get("sourceBin", [])
            media_count = len(source_bin)
            missing_count = 0
            total_size = 0

            for item in source_bin:
                if "src" in item:
                    media_path = Path(item["src"])
                    if not media_path.exists():
                        missing_count += 1
                    elif media_path.is_file():
                        try:
                            total_size += media_path.stat().st_size
                        except OSError:
                            pass

            console.print("\n[bold green]📁 Media Summary[/]")
            console.print(f"Total Media Items: {media_count}")
            console.print(f"Missing Files: {missing_count}")
            console.print(f"Total Size: {total_size / (1024**2):.1f} MB")

            # Timeline analysis
            tracks = project_data.get("timeline", {}).get("sceneTrack", {}).get("scenes", [])
            if tracks:
                timeline_tracks = tracks[0].get("csml", {}).get("tracks", [])
                total_clips = sum(len(track.get("medias", [])) for track in timeline_tracks)

                console.print("\n[bold green]🎬 Timeline Summary[/]")
                console.print(f"Tracks: {len(timeline_tracks)}")
                console.print(f"Total Clips: {total_clips}")

                # Calculate project complexity
                complexity_score = len(timeline_tracks) * 2 + total_clips * 1 + media_count * 0.5

                if complexity_score < 30:
                    complexity = "[green]Simple[/]"
                elif complexity_score < 100:
                    complexity = "[yellow]Moderate[/]"
                else:
                    complexity = "[red]Complex[/]"

                console.print(f"Complexity: {complexity} (score: {complexity_score:.1f})")

            # Recommendations
            console.print("\n[bold green]💡 Recommendations[/]")
            if missing_count > 0:
                console.print(f"• Fix {missing_count} missing media files")
            if media_count > 50:
                console.print("• Consider organizing large media bin")
            if total_size > 1024**3:  # 1GB
                console.print("• Large project - consider media optimization")
            console.print("• Project analysis complete!")

        except Exception as e:
            console.print(f"[red]Error:[/] Analysis failed: {e}")
            logger.error(f"Failed to analyze {project_path}: {e}")

    def version(self) -> None:
        """Show version information."""
        from .. import __version__

        console.print(f"camtasio version {__version__}")


def main() -> None:
    """Main CLI entry point."""
    fire.Fire(CamtasioCLI)


if __name__ == "__main__":
    main()
