# interface_adapters/gateways/ifc_openshell_gateway.py

import ifcopenshell
from typing import Any, Dict

class IfcOpenShellGateway:
    """Acceso fino a IfcOpenShell, aislado tras la puerta de enlace."""

    def open(self, file_path: str) -> Any:
        return ifcopenshell.open(file_path)

    def elements_by_type(self, ifc_file: Any, ifc_type: str):
        return ifc_file.by_type(ifc_type)

    def to_dict(self, element) -> Dict[str, Any]:
        """
        Devuelve un dict con todos los atributos que IFCOpenShell conoce.
        element.get_info() ya es un dict {attr: valor}, así evitamos getattr().
        """
        return element.get_info()
