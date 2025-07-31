import importlib
import pkgutil
import sys
import pathlib
import tomllib
from typing import Any, Dict

from zenx.settings import Settings


_settings_instance = None


def load_config() -> Dict[str, Any] | None:
    current_dir = pathlib.Path.cwd()
    config_path = current_dir / "zenx.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            return config


def discover_local_module(module_name: str):
    config = load_config()
    if not config:
        return
    project_root = pathlib.Path.cwd()
    project_name: str | Any = config.get("project")
    module_dir = project_root / project_name / module_name
    
    if not module_dir.is_dir():
        return

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        module = importlib.import_module(f"{project_name}.{module_name}")
        for _,name,_ in pkgutil.iter_modules(module.__path__):
            importlib.import_module(f".{name}", module.__name__)
    except ImportError:
        pass


def load_settings() -> Settings:
    global _settings_instance
    if _settings_instance:
        return _settings_instance

    project_root = pathlib.Path.cwd()
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    config_path = project_root / 'zenx.toml'
    config = tomllib.loads(config_path.read_text())
    project_name = config['project']

    try:
        settings_module = importlib.import_module(f"{project_name}.settings")
        SettingsClass = getattr(settings_module, "UserSettings")
    except (ImportError, AttributeError) as e:
        SettingsClass = Settings

    _settings_instance = SettingsClass()
    return _settings_instance