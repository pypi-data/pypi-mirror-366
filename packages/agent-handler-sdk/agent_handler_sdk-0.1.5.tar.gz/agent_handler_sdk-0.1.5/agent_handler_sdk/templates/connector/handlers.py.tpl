from {name}_connector import {name}

@{name}.tool(name="example", desc="Example tool")
def example():
    return {{"status": "ok"}}
