import os
import logging

from typing import Dict, Any
from template_loader import TemplateLoader
from exceptions import ResolveError
from resolver_utils import expand_env_vars, contains_wildcard, expand_wildcards
from hooks import HookManager


class PathResolver:
    """
        Path resolution using YAML templates.
        This class resolves paths based on templates defined in a YAML file.
        It supports context validation, environment variable expansion,
        wildcard expansion, and hook management.

        :param loader: An instance of TemplateLoader to load templates.
        :param strict: If True, raises an error if the context is missing required keys.
        :param auto_create_folders: If True, automatically creates folders for resolved paths.
    """
    def __init__(
        self,
        loader: TemplateLoader,
        strict: bool = True,
        auto_create_folders: bool = False,
        logger: logging.Logger = None,
    ):
        """
            Initializes the PathResolver with a TemplateLoader instance.

            :param loader: An instance of TemplateLoader to load templates.
            :param strict: If True, raises an error if the context is missing required keys.
            :param auto_create_folders: If True, automatically creates folders for resolved paths.
            :param logger: An optional external logger. If not provided, a default logger is created.

            raises: TypeError: If loader is not an instance of TemplateLoader.
        """
        # Use the provided logger or create a default one
        self.logger = logger or self._create_default_logger()

        if loader:
            if not isinstance(loader, TemplateLoader):
                raise TypeError("loader must be an instance of TemplateLoader")

        else:
            loader = TemplateLoader(logger=self.logger)

        self.loader = loader
        self.hooks = HookManager()
        self.strict = strict
        self.auto_create_folders = auto_create_folders

    def _create_default_logger(self) -> logging.Logger:
        """
            Creates a default logger for the PathResolver.
        """
        logger = logging.getLogger("PathResolver")
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)

        return logger

    def resolve(self, template_name: str, context: Dict[str, Any]) -> str:
        """
            Resolves a path template with given context.

            :param template_name: The name of the template to resolve.
            :param context: A dictionary containing the context for the template.
            :return: The resolved path as a string.
        """
        self.logger.debug(f"Resolving template '{template_name}' with context: {context}")
        template = self.loader.get(template_name)
        full_context = template.apply_defaults(context)

        if self.strict:
            template.validate_context(full_context)

        # HOOKS — BEFORE RESOLVE
        self.hooks.run_before("resolve", full_context)

        try:
            resolved_path = template.get_resolved_pattern().format(**full_context)
        except KeyError as e:
            raise ResolveError(f"Missing key '{e.args[0]}' in context for template '{template_name}'")

        resolved_path = expand_env_vars(resolved_path)

        if contains_wildcard(resolved_path):
            matches = expand_wildcards(resolved_path)
            if not matches:
                raise ResolveError(f"No matches found for wildcard path: {resolved_path}")
            resolved_path = matches[0]

        # Prepend the root if it exists
        if template.root:
            resolved_path = os.path.join(template.root, resolved_path)

        # Create the directory if it doesn't exist
        if self.auto_create_folders:
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            self.logger.info(f"Created directories for path: {os.path.dirname(resolved_path)}")

        # HOOKS — AFTER RESOLVE
        self.hooks.run_after("resolve", resolved_path, full_context)

        self.logger.info(f"Resolved path: {resolved_path}")

        return resolved_path

    def resolve_from_dict(self, pattern: str, context: Dict[str, Any]) -> str:
        """
            Resolves a raw pattern with given context.

            :param pattern: The raw pattern to resolve.
            :param context: A dictionary containing the context for the pattern.
            :return : The resolved path as a string.
            :raises ResolveError: If a key in the pattern is missing in the context or if no matches
                                are found for a wildcard path.
        """
        try:
            resolved_path = pattern.format(**context)
        except KeyError as e:
            if self.strict:
                raise ResolveError(f"Missing key '{e.args[0]}' in context for raw pattern")
            resolved_path = pattern

        resolved_path = expand_env_vars(resolved_path)

        if contains_wildcard(resolved_path):
            matches = expand_wildcards(resolved_path)
            if not matches:
                raise ResolveError(f"No wildcard match found for: {resolved_path}")
            resolved_path = matches[0]

        return resolved_path
