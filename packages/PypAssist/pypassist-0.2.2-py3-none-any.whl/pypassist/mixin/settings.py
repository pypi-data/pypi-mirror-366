#!/usr/bin/env python3
"""
Common mixin to handle settings.
"""

import dataclasses
import logging
import copy
from contextlib import contextmanager

from ..utils.export import export_string
from ..fallback.typing import NoneType

LOGGER = logging.getLogger(__name__)


def create_settings_snapshot(settings, fallback_value=None):
    """
    Create a safe snapshot of settings for later comparison.

    Creates a dictionary representation of the settings that can be safely stored
    and compared later, even when the original settings contain non-copyable objects.

    Args:
        settings: Settings dataclass to snapshot
        fallback_value: Value to use when an object cannot be copied (default: None)

    Returns:
        Dict: Dictionary representation of settings suitable for comparison

    Raises:
        None: Function handles all exceptions internally using fallback values

    Note:
        - Recursively handles nested dataclasses
        - For Cacheable objects, stores their .settings instead of the object itself
        - Uses fallback_value for non-copyable objects that don't have .settings
    """
    snapshot = {}

    for field in dataclasses.fields(settings):
        field_value = getattr(settings, field.name)

        method_name = f"__snapshot_{field.name}__"  # Magic method for custom snapshot
        custom_snapshot_method = getattr(settings, method_name, None)
        if callable(custom_snapshot_method):
            snapshot[field.name] = custom_snapshot_method()
            continue

        if dataclasses.is_dataclass(field_value):  # nested dataclass
            snapshot[field.name] = create_settings_snapshot(field_value, fallback_value)
            continue

        if hasattr(field_value, "is_cachable"):  # Handle non-copyable objects
            ## use the settings for comparison, if available
            fallback_value = getattr(field_value, "settings", fallback_value)
            field_value_copy = fallback_value
            snapshot[field.name] = create_settings_snapshot(field_value_copy)
            continue

        ## -- normal deepcopy
        snapshot[field.name] = copy.deepcopy(field_value)

    return snapshot


class SettingsMixin:
    """
    Enhanced mixin for handling settings with nested updates support.
    Allows cache invalidation if settings change.

    Attributes:
        SETTINGS_DATACLASS: The dataclass to be used for settings.
    """

    SETTINGS_DATACLASS = NoneType

    def __init__(self, settings):
        settings = self._check_settings_type(settings)
        self._settings = settings
        self._cached_settings_snapshot = None

    @property
    def settings(self):
        """Get the current settings."""
        if self.SETTINGS_DATACLASS is NoneType:
            LOGGER.warning(
                "%s does not have settings. Returning None", self.__class__.__name__
            )
            return None

        if self._cached_settings_snapshot is None:  # not cached
            self._cached_settings_snapshot = create_settings_snapshot(self._settings)

        return self._settings

    def view_settings(self, format_type="yaml", **kwargs):
        """
        Return a read-only view of the current settings for display purposes.

        Args:
            format_type: The format in which to display the settings.
            **kwargs: Additional display options.
        """
        return self.settings.view(format_type=format_type, **kwargs)

    @contextmanager
    def with_tmp_settings(self, **kwargs):
        """
        Temporarily override settings within a context.
        Does not trigger cache clearing since changes are temporary.

        Args:
            **kwargs: Individual settings to temporarily override.

        Usage:
            with obj.with_tmp_settings(title="temp title"):
                result = obj.some_method()
            # settings are restored after the context
        """
        if self.SETTINGS_DATACLASS is NoneType:
            LOGGER.warning(
                "%s does not have settings. Context manager will do nothing",
                self.__class__.__name__,
            )
            yield self
            return

        # Backup current settings
        original_settings = dataclasses.replace(self._settings)

        try:
            # Apply temporary changes without triggering cache clearing
            if kwargs:
                self._apply_settings_updates(None, **kwargs, trigger_cache_clear=False)
            yield self
        finally:
            # Restore original settings
            self._settings = original_settings

    def update_settings(self, settings=None, **kwargs):
        """
        Permanently update the settings either with a new settings object or individual values.

        Args:
            settings: New settings object to update from
            **kwargs: Individual settings to update using dot notation for nested attributes
        """
        if self.SETTINGS_DATACLASS is NoneType:
            LOGGER.warning(
                "%s does not have settings. Ignoring update_settings call",
                self.__class__.__name__,
            )
            return

        if self._cached_settings_snapshot is None:  # not cached
            self._cached_settings_snapshot = create_settings_snapshot(self._settings)

        self._apply_settings_updates(settings, **kwargs, trigger_cache_clear=True)

    def _apply_settings_updates(
        self, settings=None, trigger_cache_clear=True, **kwargs
    ):
        """
        Internal method to apply settings updates.

        Args:
            settings: New settings object to update from
            trigger_cache_clear: Whether to trigger cache clearing after updates
            **kwargs: Individual settings to update using dot notation for nested attributes
        """
        self._replace_settings_if_not_none(settings)

        if not kwargs:
            return

        updates = {}
        nested_updates = {}

        for key, value in kwargs.items():
            if "." in key:
                nested_updates[key] = value
            else:
                updates[key] = value

        if updates:
            try:
                self._settings = dataclasses.replace(self._settings, **updates)
            except (AttributeError, TypeError) as err:
                raise ValueError(f"Invalid settings update: {err}") from err

        for path, value in nested_updates.items():
            try:
                self._update_nested_attribute(path, value)
            except AttributeError as err:
                LOGGER.warning("Failed to update nested setting `%s`: %s", path, err)

        self._trigger_post_init()

        if trigger_cache_clear:
            self._clear_cache_if_exists()

    def _replace_settings_if_not_none(self, new_settings):
        """Replace settings if the new settings are not None."""
        if new_settings is not None:
            self._check_settings_type(new_settings)
            self._settings = dataclasses.replace(new_settings)

    def export_settings(
        self, output_dir, format_type="yaml", exist_ok=False, makedirs=False
    ):
        """
        Export the settings to a file.

        Args:
            output_dir: Directory where to export the settings
            format_type: Format to use for export (default: yaml)
            exist_ok: Whether to overwrite existing files (default: False)
            makedirs: Whether to create directories if they don't exist (default: False)
        """
        if self.SETTINGS_DATACLASS is NoneType:
            LOGGER.info(
                "%s does not have settings. Skipping settings export.",
                self.__class__.__name__,
            )
            return

        content = self.settings.to_str(
            format_type=format_type,
            output_dir=output_dir,
            detailed=False,
            exist_ok=exist_ok,
        )
        filepath = output_dir / f"{self.__class__.__name__.lower()}_settings.txt"
        export_string(content, filepath=filepath, exist_ok=exist_ok, makedirs=makedirs)

    def _update_nested_attribute(self, path, value):
        """
        Update a nested attribute using dot notation.

        Args:
            path: Dot-separated path to the attribute (e.g., "optimizer.params.lr")
            value: New value to set
        """
        attrs = path.split(".")
        current = self._settings

        for attr in attrs[:-1]:
            if not hasattr(current, attr):
                raise AttributeError(f"Invalid nested attribute `{attr}` in `{path}`")
            current = getattr(current, attr)

        last_attr = attrs[-1]
        if not hasattr(current, last_attr):
            raise AttributeError(f"Invalid final attribute `{last_attr}` in `{path}`")

        if dataclasses.is_dataclass(current):
            setattr(current, last_attr, value)
            current = dataclasses.replace(current, **{last_attr: value})
        else:
            setattr(current, last_attr, value)

    def _check_settings_type(self, settings=None):
        """
        Validate settings type and convert dict to proper settings instance if needed.
        """
        # Handle NoneType class (no settings)
        if self.SETTINGS_DATACLASS is NoneType:
            LOGGER.info(
                "%s does not support settings. Returning None.", self.__class__.__name__
            )
            return None

        if isinstance(settings, dict):
            try:
                settings = self.SETTINGS_DATACLASS(**settings)  # pylint: disable=E1102
            except (TypeError, ValueError) as err:
                raise TypeError(f"Invalid settings dictionary: {err}") from err

        if not isinstance(settings, self.SETTINGS_DATACLASS):  # pylint: disable=W1116
            raise TypeError(
                f"Invalid settings type: {type(settings).__name__}. "
                f"Expected: {self.SETTINGS_DATACLASS.__name__}"
            )

        return settings

    def _trigger_post_init(self):
        """Trigger post_init if available on the settings."""
        if hasattr(self._settings, "__post_init__"):
            self._settings.__post_init__()

    def have_settings_changed(self):
        """
        Quickly checks if settings have changed to determine cache invalidation.

        Returns:
            bool: True if settings have changed, False otherwise.
        """
        current_settings = self._settings
        cached_snapshot = self._cached_settings_snapshot
        return self._compare_settings_with_snapshot(current_settings, cached_snapshot)

    def _clear_cache_if_exists(self):
        """Clear the cache if it exists and if settings have changed."""
        if not hasattr(self, "clear_cache"):
            # Not Cacheable class
            return

        if self.have_settings_changed():
            self.clear_cache()
            self._cached_settings_snapshot = create_settings_snapshot(self._settings)

    def _compare_settings_with_snapshot(self, current_settings, cached_snapshot):
        """
        Compare current settings with a previously created snapshot to detect changes.

        This function is optimized for cache invalidation scenarios where we need to
        quickly determine if settings have been modified since the last cache update.

        Args:
            current_settings: Current settings dataclass instance
            cached_snapshot: Previously cached settings snapshot (dict created by
                            create_settings_snapshot)

        Returns:
            bool: True if settings have changed, False if identical

        Note:
            - Handles Cacheable objects by comparing their .settings attribute
            - Uses recursive comparison for nested dataclasses
            - Returns True immediately on first difference found (fast exit)
        """
        if not dataclasses.is_dataclass(current_settings):
            return current_settings != cached_snapshot

        for field in dataclasses.fields(current_settings):
            current_value = getattr(current_settings, field.name)
            if isinstance(cached_snapshot, dict):
                cached_value = cached_snapshot.get(field.name, None)
            else:
                cached_value = cached_snapshot

            method_name = (
                f"__snapshot_{field.name}__"  # Magic method for custom snapshot
            )
            custom_snapshot_method = getattr(current_settings, method_name, None)
            if callable(custom_snapshot_method):
                current_value = custom_snapshot_method()

            if hasattr(current_value, "is_cachable"):  # Handle non-copyable objects
                # Extract settings for comparison (same logic as create_settings_snapshot)
                current_value = getattr(current_value, "settings", None)

            if dataclasses.is_dataclass(current_value):
                # Recursive comparison for nested dataclasses
                if self._compare_settings_with_snapshot(current_value, cached_value):
                    return True
            else:
                # Direct comparison for primitive types
                if current_value != cached_value:
                    return True

        return False
