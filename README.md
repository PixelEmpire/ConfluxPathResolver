# ConfluxPathResolver

**ConfluxPathResolver** is a powerful, flexible path resolving library designed for production pipelines. 
It uses YAML-based templates to resolve filesystem paths dynamically using tokenized context.
It supports strict and lazy resolution, wildcard expansion, environment variable interpolation, 
auto folder creation, and custom hooks for extensibility.
It is designed to be used in production environments, particularly in VFX and animation studios, 
where complex directory structures and file naming conventions are common.

---

## 📁 Project Structure

conflux_path_resolver/
├── __init__.py # Package initialization
├── resolver.py # Core path resolver logic 
├── template.py # Template class for pattern, defaults, and validation 
├── template_loader.py # Loads YAML-based templates from directories 
├── hooks.py # Hook manager for before/after resolution logic 
├── exceptions.py # Custom exception classes 
├── utils.py # Token parsing, wildcard, env var expansion helpers 
├── templates/ # YAML files defining path templates 
│   └── shot_templates.yaml # Example path templates 
├── examples/ 
│   └── run_resolver.py # Sample CLI interface or direct usage 
└── README.md # You're here!

---

## 🔧 What It Does

ConfluxPathResolver resolves filesystem paths from templates using token-based context like:

```yaml
shot_work_path:
  pattern: "{project_root}/shots/{sequence}/{shot}/{task}/v{version:0>3}/{shot}_{task}.nk"
  defaults:
    version: 1
    task: comp
```
This will resolve to something like:

```
/mnt/projects/dragonfire/shots/SQ001/SH010/comp/v004/SH010_comp.nk
```

# ✨ Features

### -✅ Tokenized path resolution

### 🧠 Default values

### 🛡️ Strict vs Lazy mode

### 🌐 Environment variable expansion

### 🔁 Wildcard support

### 📂 Auto-create directories

### 🪝 Before/After Hook system (hooks.py or inline via resolver)

### 🔍 Manual resolve_from_dict() support



## 🚀 Quick Start
### 1. Setup a Template YAML
### templates/shot_templates.yaml
```yaml
shot_output:
  pattern: "{project_root}/shots/{sequence}/{shot}/output/v{version:0>3}/{shot}_{task}.{ext}"
  defaults:
    task: comp
    ext: nk
    version: 1
```

### 2. Load and Resolve

```python
from resolver import PathResolver
from template_loader import TemplateLoader

loader = TemplateLoader(["./templates"])
resolver = PathResolver(loader, strict=True, auto_create_folders=True)

context = {
    "project_root": "/mnt/projects/dragonfire",
    "sequence": "SQ001",
    "shot": "SH010",
    "task": "comp",
    "version": 4,
    "ext": "nk"
}

path = resolver.resolve("shot_output", context)
print("Resolved path:", path)
```

## 🪝 Hook System
Hooks let you validate or modify context before and after path resolution.

### Using the HookManager
``` python
from hooks import HookManager

hook_mgr = HookManager()

def validate_version(context):
    if context["version"] < 1:
        raise ValueError("Version must be >= 1")

hook_mgr.register("before", "shot_output", validate_version)

```
Then During resolution, the hook will be called:
``` python
hook_mgr.run_before("shot_output", context)
path = resolver.resolve("shot_output", context)
hook_mgr.run_after("shot_output", path, context)
```

## 🧩 Advanced
### Lazy Mode
Use `strict=False` to allow partial context resolution:
```python
resolver = PathResolver(loader, strict=False)
```

### Wildcard Matching
Supports glob-style wildcards in resolved paths.
``` yaml
latest_comp:
  pattern: "{project_root}/shots/{sequence}/{shot}/comp/v*/{shot}_comp.nk"

```
### Frame Padding Support
You can use Python formatting for padding:
``` yaml
image_seq:
  pattern: "{project_root}/images/{shot}/{shot}_{frame:04d}.exr"
```
Provide `frame=7` → `SH010_0007.exr`

### 📂 Template Organization
You can group templates per asset type, shot, publish type, etc.
```yaml
asset_work:
  pattern: "{project_root}/assets/{asset_type}/{asset_name}/work/{task}/v{version:03}/{asset_name}_{task}.{ext}"
```
Or split into multiple YAMLs and load via multiple paths in `TemplateLoader`.

### 🛠️ CLI Example (Optional)
```bash
python examples/run_resolver.py \
  --template shot_output \
  --context '{"project_root":"/mnt/projects/dragonfire","sequence":"SQ001","shot":"SH010","task":"comp","version":4,"ext":"nk"}'

```
## 🧪 Testing
### Unit Tests
Run unit tests using pytest:
```bash
pytest tests/
```
Unit tests can be written for:

* Template loading and defaults

* Strict vs lazy behavior

* Hook execution

* Wildcard resolution

