# yaapp-core

**Minimal core functionality for yaapp framework**

## What's included:

### ✅ Core Framework
- `app.py` - Main Yaapp class
- `core.py` - YaappCore functionality  
- `expose.py` - @expose decorator
- `result.py` - Result type (Ok/Err)
- `async_compat.py` - Async compatibility
- `execution_strategy.py` - Execution strategies
- `context_tree.py` - Context management
- `exposers/` - Complete exposer system
- `reflection.py` - CLI reflection system
- `config.py` - Configuration management
- `discovery.py` - Plugin discovery
- `run.py` - Main run function

### ✅ Example Runner
- `runners/click/` - Click CLI runner

### ✅ Example Plugin  
- `plugins/calculator/` - Simple calculator plugin

## Usage:

### Basic Example:
```python
from yaapp import run
run()  # Auto-discovers plugins and runs CLI
```

### Manual Example:
```python
from yaapp.app import Yaapp

app = Yaapp(auto_discover=False)

# Load calculator plugin manually
import yaapp.plugins.calculator.plugin
from yaapp.expose import apply_pending_registrations
apply_pending_registrations(app)

# Use programmatically
result = app._execute_from_registry("calculator")
calc = result.unwrap()
print(calc.add(2, 3))  # 5
```

### CLI Usage:
```bash
python cli_example.py calculator add --x 5 --y 3
python cli_example.py calculator get-history --limit 5
```

## Dependencies:
- `click` (for CLI runner)
- `pyyaml` (for config)

## What's NOT included:
- Other runners (prompt, rich, server, etc.)
- Other plugins (storage, docker, etc.)
- CLI builders and complex discovery
- Non-essential utilities

This is the **minimal working core** that demonstrates:
1. ✅ Plugin system working
2. ✅ Runner system working  
3. ✅ Exposer system working
4. ✅ CLI generation working