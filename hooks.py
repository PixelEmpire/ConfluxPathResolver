# hooks.py
import importlib
from typing import Callable, Dict, List, Any
from exceptions import HookExecutionError


class HookManager:
    """
        A simple manager to register and run before/after hooks.
        Hooks can modify the context or raise errors to block resolution.
    """

    def __init__(self):
        self._before_hooks: Dict[str, List[Callable]] = {}
        self._after_hooks: Dict[str, List[Callable]] = {}

    def register(self, phase: str, name: str, func: Callable):
        """
            Register a hook function to be called before or after a specific event.
            :param phase: "before" or "after"
            :param name: The name of the hook
            :param func: The function to call
        """
        if phase == "before":
            self._before_hooks.setdefault(name, []).append(func)
        elif phase == "after":
            self._after_hooks.setdefault(name, []).append(func)
        else:
            raise ValueError(f"Invalid hook type '{phase}'")

    def unregister(self, phase: str, name: str, func: Callable):
        """
        Unregister a hook function from the specified phase and name.
        :param phase: "before" or "after"
        :param name: The name of the hook
        :param func: The function to unregister
        """
        if phase == "before":
            if name in self._before_hooks:
                self._before_hooks[name].remove(func)
        elif phase == "after":
            if name in self._after_hooks:
                self._after_hooks[name].remove(func)
        else:
            raise ValueError(f"Invalid hook type '{phase}'")

    def run_before(self, name: str, data: Dict[str, Any]):
        """
            Run all before hooks registered under the given name.

            :param name: The name of the hook to run
            :param data: The data to pass to the hook functions
        """
        for func in self._before_hooks.get(name, []):
            try:
                func(data)
            except Exception as e:
                raise HookExecutionError(f"Before hook '{name}' failed: {e}")

    def run_after(self, name: str, path: str, context: Dict[str, Any]):
        """
            Run all after hooks registered under the given name.

            :param name: The name of the hook to run
            :param path: The path to pass to the hook functions
            :param context: The context to pass to the hook functions
        """
        for func in self._after_hooks.get(name, []):
            try:
                func(path, context)
            except Exception as e:
                raise HookExecutionError(f"After hook '{name}' failed: {e}")

    def load_from_dict(self, data: Dict[str, Any]):
        """
        Load hook registrations from a dictionary like from parsed YAML.
        """
        for phase in ("before", "after"):
            phase_data = data.get("hooks", {}).get(phase, {})
            for name, hook_list in phase_data.items():
                for hook_path in hook_list:
                    func = self._import_func(hook_path)
                    self.register(phase, name, func)

    def _import_func(self, dotted_path: str) -> Callable:
        """
        Import a function from a dotted path, e.g. 'my_hooks.log_final_path'
        """
        module_path, func_name = dotted_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)

    def clear_hooks(self):
        """
        Clear all registered hooks.
        """
        self._before_hooks.clear()
        self._after_hooks.clear()

    def list_hooks(self):
        """
        List all registered hooks.
        """
        return {
            "before": self._before_hooks,
            "after": self._after_hooks
        }

# Example usage of a hook function
def example_hook(data):
    print(f"Before hook executed with data: {data}")
