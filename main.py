# main.py
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd

from application.pipelines.ifc_import_pipeline import IfcImportPipeline, Step
from interface_adapters.gateways.ifc_openshell_gateway import IfcOpenShellGateway


# ---------- utils -----------------------------------------------------------------

def element_to_record(element) -> Dict[str, Any]:
    """
    Convierte una entidad IFC en un dict {columna: valor} que incluye:
      • Atributos estándar (get_info())
      • Todas las propiedades de todos los PropertySets (nombre_columna = "Pset.Prop")
    """
    record = element.get_info().copy()

    # Recorremos Property Sets (incluidos los personalizados de Revit)
    for rel in getattr(element, "IsDefinedBy", []):
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        pset = rel.RelatingPropertyDefinition
        if not pset.is_a("IfcPropertySet"):
            continue
        pset_name = pset.Name
        for prop in pset.HasProperties:
            prop_name = prop.Name
            value = None
            if prop.is_a("IfcPropertySingleValue") and prop.NominalValue:
                value = prop.NominalValue.wrappedValue
            elif prop.is_a("IfcPropertyListValue") and prop.ListValues:
                value = [v.wrappedValue for v in prop.ListValues]
            # más variantes (IfcPropertyEnumeratedValue, …)
            record[f"{pset_name}.{prop_name}"] = value
    return record


def summarize_dataframe(df: pd.DataFrame, max_rows: int = 5):
    """Imprime un pequeño resumen de un DataFrame grande."""
    print(f"\nDataFrame '{df.attrs.get('entity_type', 'unknown')}' — "
          f"{len(df)} filas × {len(df.columns)} columnas")
    print(df.head(max_rows).to_string(index=False))


# ---------- main ------------------------------------------------------------------

def main():
    # 1) Localiza el IFC
    project_root = Path(__file__).parent
    ifc_path = project_root / "input" / "ifc_v4.ifc"
    if not ifc_path.exists():
        raise FileNotFoundError(f"No se encontró el IFC en {ifc_path!s}")

    # 2) Configura puerta de enlace y pipeline
    gateway = IfcOpenShellGateway()
    pipeline = IfcImportPipeline([
        Step("open_file", lambda path: {"ifc": gateway.open(path)}),
        Step("extract_walls",
             lambda ifc, **_: {"IfcWall": gateway.elements_by_type(ifc, "IfcWall")}),
    ])

    context = pipeline.run(str(ifc_path))
    walls: List[Any] = context["IfcWall"]
    print(f"\n{len(walls)} muros detectados en {ifc_path.name}")

    # 3) Genera DataFrame completo para muros
    records = [element_to_record(w) for w in walls]
    df_walls = pd.DataFrame.from_records(records)
    df_walls.attrs["entity_type"] = "IfcWall"

    # 4) Muestra un resumen rápido en consola
    summarize_dataframe(df_walls)

    # 5) Guarda a disco
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    excel_path = output_dir / "walls.xlsx"
    df_walls.to_excel(excel_path, index=False)
    print(f"\nDataFrame exportado a: {excel_path.relative_to(project_root)}")


if __name__ == "__main__":
    main()
