# template_loader.py

import os
import yaml
import logging
from typing import Dict, List, Optional
from template import Template
from exceptions import InvalidTemplateError, TemplateNotFoundError


class TemplateLoader:
    """
        A class to load and manage templates from YAML files. It supports resolving
        inheritance between templates and provides access to templates by name.

        Attributes:
            template_files (List[str]): List of YAML files to load templates from.
            _templates (Dict[str, Template]): Dictionary of resolved templates by name.
            _raw_data (Dict[str, dict]): Raw template data loaded from YAML files.
            _loaded_files (set): Set of file paths that have already been loaded.
    """

    def __init__(self, template_files: Optional[List[str]] = None, logger: logging.Logger = None):
        """
           Initializes the TemplateLoader with a list of YAML files.

            :param template_files: List of YAML file paths to load templates from.
        """
        self.template_files = template_files or []
        self._templates: Dict[str, Template] = {}
        self._raw_data: Dict[str, dict] = {}
        self._loaded_files = set()

        # Use the provided logger or create a default one
        self.logger = logger or self._create_default_logger()

        for file in self.template_files:
            self.logger.debug(f"TemplateLoader: Loading template file: {file}")
            self._load_from_file(file)

        self._resolve_all_templates()

    def _create_default_logger(self) -> logging.Logger:
        """
            Creates a default logger for the TemplateLoader.
        """
        logger = logging.getLogger("TemplateLoader")
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)

        return logger

    def _load_from_file(self, file_path: str):
        """
            Loads a YAML file and adds its templates to the loader.

            :param file_path: Path to the YAML file.

            :raises TemplateNotFoundError: If the file does not exist.
            :raises InvalidTemplateError: If a template in the file is missing a required "pattern".
        """
        file_path = os.path.abspath(file_path)  # Resolve to absolute path

        # Skip if the file has already been loaded
        if file_path in self._loaded_files:
            self.logger.debug(f"Skipping already loaded file: {file_path}")
            return

        if not os.path.isfile(file_path):
            raise TemplateNotFoundError(f"Template file not found: {file_path}")

        self.logger.debug(f"Loading template file: {file_path}")
        with open(file_path, "r") as f:
            data = yaml.safe_load(f) or {}

        for name, entry in data.items():
            if not isinstance(entry, dict) or "pattern" not in entry:
                raise InvalidTemplateError(f"Template '{name}' in {file_path} is missing a pattern")
            self._raw_data[name] = entry  # Later files override earlier ones

        self.template_files.append(file_path)
        self._loaded_files.add(file_path)  # Mark this file as loaded

    def _resolve_all_templates(self):
        """
            Resolves all templates, including their inheritance, and stores them in the `_templates` dictionary.
        """
        self._templates.clear()
        for name in self._raw_data:
            self._templates[name] = self._build_template(name)

    def _build_template(self, name: str, seen: Optional[List[str]] = None) -> Template:
        """
            Recursively builds a template, resolving inheritance.

            :param name : Name of the template to build.
            :param seen : Names of templates already seen in this resolution path
                                            (to detect circular inheritance).

            :returns: Template: The resolved Template object.
        """
        if name in self._templates:
            return self._templates[name]

        if name not in self._raw_data:
            raise TemplateNotFoundError(f"Template '{name}' not found")

        seen = seen or []
        if name in seen:
            raise InvalidTemplateError(f"Circular inheritance detected for template '{name}'")

        data = dict(self._raw_data[name])
        parent_name = data.get("parent")

        if parent_name:
            parent = self._build_template(parent_name, seen + [name])
            parent_dict = {
                "pattern": parent.pattern,
                "defaults": parent.defaults or {},
                "root": parent.root,
                "tags": parent.tags,
                "metadata": parent.metadata,
                "parent": parent.parent
            }
            parent_dict.update(data)
            data = parent_dict

        return Template(
            name=name,
            pattern=data["pattern"],
            defaults=data.get("defaults"),
            root=data.get("root"),
            parent=data.get("parent"),
            tags=data.get("tags"),
            metadata=data.get("metadata"),
        )

    def get(self, name: str) -> Template:
        """
            Retrieves a resolved template by name.

            Args:
                name (str): Name of the template to retrieve.

            Returns:
                Template: The resolved Template object.

            Raises:
                TemplateNotFoundError: If the template is not found.
        """
        if name not in self._templates:
            raise TemplateNotFoundError(f"Template '{name}' not found")
        return self._templates[name]

    def all(self) -> Dict[str, Template]:
        """
            Returns all loaded templates.

            Returns:
                Dict[str, Template]: Dictionary of all resolved templates by name.
        """
        return self._templates

    def add_template_file(self, file_path: str):
        """
            Dynamically adds a template YAML file and refreshes the template cache.

            :param file_path: Path to the YAML file.
        """
        self._load_from_file(file_path)
        self._resolve_all_templates()

    def add_template_files_from_directory(self, directory: str):
        """
            Dynamically adds all template YAML files from a directory and refreshes the template cache.

            :param directory: Path to the directory containing YAML files.
        """
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        for file_name in os.listdir(directory):
            if file_name.endswith(".yaml"):
                self.add_template_file(os.path.join(directory, file_name))
