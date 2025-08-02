"""JASPER core integration stub."""

class JasperCore:
    """Placeholder for Codex model wrapper."""

    def __init__(self) -> None:
        self.ready = False

    def load(self) -> None:
        self.ready = True

    def run(self, code: str) -> str:
        if not self.ready:
            raise RuntimeError("JASPER core not loaded")
        return "// TODO: process code"

__all__ = ["JasperCore"]
