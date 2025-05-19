# application/pipelines/ifc_import_pipeline.py
from dataclasses import dataclass
from typing import Callable, List

@dataclass
class Step:
    name: str
    action: Callable[..., dict]

class IfcImportPipeline:
    def __init__(self, steps: List[Step]):
        self.steps = steps
    def run(self, file_path: str):
        context = {"path": file_path}
        for step in self.steps:
            context.update(step.action(**context))
        return context
