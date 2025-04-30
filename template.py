# template.py

from typing import Dict, Optional, List, Any
from exceptions import InvalidTemplateError, ContextValidationError
from resolver_utils import extract_tokens


class Template:
    """
        Represents a path template with optional inheritance, metadata, and validation.
    """

    def __init__(
        self,
        name: str,
        pattern: str,
        defaults: Optional[Dict[str, Any]] = None,
        root: Optional[str] = None,
        parent: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.name = name # Template name
        self.pattern = pattern # Template pattern string
        self.defaults = defaults or {} # Default values for tokens
        self.root = root # Root path for the template
        self.parent = parent # Parent template name for inheritance
        self.tags = tags or [] # Tags associated with the template
        self.metadata = metadata or {} # Metadata dictionary for additional information
        self.tokens = extract_tokens(pattern) # Extract tokens from the pattern

    def validate_context(self, context: Dict[str, Any]):
        """
            Ensure all required tokens are present in the context.

            :param context: The context dictionary to validate.
            :raises ContextValidationError: If any required tokens are missing.
        """
        missing = [token for token in self.tokens if token not in context]
        if missing:
            raise ContextValidationError(
                f"Template '{self.name}' missing context keys: {missing}"
            )

    def apply_defaults(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
            Return a new context with defaults merged into missing keys.

            :param context: The context dictionary to merge with defaults.
            :return: A new context dictionary with defaults applied.
        """
        merged = dict(self.defaults)
        merged.update(context)
        return merged

    def get_resolved_pattern(self) -> str:
        """
            Return the raw pattern string.
            This is useful for debugging or logging purposes.
        """
        return self.pattern

    def describe(self) -> Dict[str, Any]:
        """
            Return a summary of this template.
            This includes its name, pattern, tokens, root, parent, tags, metadata, and defaults.

            :return: A dictionary containing the template's details.
        """
        return {
            "name": self.name,
            "pattern": self.pattern,
            "tokens": self.tokens,
            "root": self.root,
            "parent": self.parent,
            "tags": self.tags,
            "metadata": self.metadata,
            "defaults": self.defaults,
        }
