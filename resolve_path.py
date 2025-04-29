import json
import argparse
import os
from resolver import PathResolver
from template_loader import TemplateLoader

"""
    Console script to resolve a path using a template and context.
    Usage:
        python resolve_path.py --template <template_name> --templates <template_files> --data <context_data>
        eg1: python resolve_path.py --template my_template --templates template1.yaml template2.yaml --data '{"key": "value"}'
        eg2: python resolve_path.py --template asset_base --templates templates/pipeline_template.yaml --data tests/test.json
        
"""

def parse_context_arg(data_arg):
    """
    Accepts either a path to a JSON file, a JSON string, or key=value pairs separated by spaces.
    """
    # Check if the argument is a file path
    if os.path.isfile(data_arg):
        with open(data_arg, 'r') as f:
            return json.load(f)

    # Attempt to parse as JSON string
    try:
        return json.loads(data_arg)
    except json.JSONDecodeError:
        # Fallback to key=value parsing
        context = {}
        pairs = data_arg.strip().split()
        for pair in pairs:
            if "=" not in pair:
                raise ValueError(f"Invalid context pair: '{pair}' (expected key=value)")
            key, value = pair.split("=", 1)
            context[key.strip()] = value.strip()
        return context

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resolve a path using a template and context.")
    parser.add_argument("--template", required=True, help="Name of the template to use.")
    parser.add_argument("--templates", nargs="+", required=True, help="List of template files.")
    parser.add_argument("--data", required=True, help="Context data (JSON file, JSON string, or key=value pairs).")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode.")
    args = parser.parse_args()

    # Initialize the TemplateLoader with a list of template files
    loader = TemplateLoader(args.templates)

    try:
        context = parse_context_arg(args.data)
    except Exception as e:
        print(f"Failed to parse context data: {e}")
        exit(1)

    resolver = PathResolver(loader=loader, strict=args.strict)

    try:
        resolved_path = resolver.resolve(args.template, context)
        print(f"Resolved Path: {resolved_path}")

    except Exception as e:
        print(f"Failed to resolve path: {e}")
        exit(1)