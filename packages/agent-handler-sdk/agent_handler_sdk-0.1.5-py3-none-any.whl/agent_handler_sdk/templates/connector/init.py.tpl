import pkgutil
import importlib
from agent_handler_sdk.connector import Connector

# single Connector instance for this package
{name} = Connector(namespace="{name}")

# auto-import all modules in tools/
package = __name__ + ".tools"
path = f"{{__path__[0]}}/tools"
for _, m, _ in pkgutil.iter_modules([path]):
    importlib.import_module(f"{{package}}.{{m}}")
