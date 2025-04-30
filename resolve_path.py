import json
import argparse
import os
import logging
from typing import Dict, Any
from resolver import PathResolver
from template_loader import TemplateLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_context_arg(data_arg: str) -> Dict[str, Any]:
    """
        Parses the context argument, which can be a JSON file, a JSON string, or key=value pairs.

        :param data_arg: The context data as a file path, JSON string, or key=value pairs.

        :returns: Parsed context data as a dictionary.

        :raises ValueError: If the input format is invalid.
    """
    if os.path.isfile(data_arg):
        with open(data_arg, 'r') as f:
            return json.load(f)

    try:
        return json.loads(data_arg)
    except json.JSONDecodeError:
        context = {}
        for pair in data_arg.strip().split():
            if "=" not in pair:
                raise ValueError(f"Invalid context pair: '{pair}' (expected key=value)")
            key, value = pair.split("=", 1)
            context[key.strip()] = value.strip()
        return context

def validate_template_files(template_files: list) -> None:
    """
        Validates that all template files exist.

        :param template_files: List of template file paths.

        :raises FileNotFoundError: If any template file does not exist.
    """
    for file in template_files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Template file '{file}' does not exist.")

def main():
    parser = argparse.ArgumentParser(description="Resolve a path using a template and context.")
    parser.add_argument("--template", required=True, help="Name of the template to use.")
    parser.add_argument("--templates", nargs="+", required=True, help="List of template files.")
    parser.add_argument("--data", required=True, help="Context data (JSON file, JSON string, or key=value pairs).")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode.")
    args = parser.parse_args()

    try:
        validate_template_files(args.templates)
        context = parse_context_arg(args.data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        logging.error(f"Error: {e}")
        exit(1)

    loader = TemplateLoader(args.templates)
    resolver = PathResolver(loader=loader, strict=args.strict)

    try:
        resolved_path = resolver.resolve(args.template, context)
        logging.info(f"Resolved Path: {resolved_path}")
    except Exception as e:
        logging.error(f"Failed to resolve path: {e}")
        exit(1)

if __name__ == "__main__":
    main()