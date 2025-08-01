from enum import Enum
from sqlmodel import SQLModel, Field

class LayoutName(str, Enum):
    SHELL = "SHELL"
    PLANAR = "PLANAR"
    RANDOM = "RANDOM"
    SPIRAL = "SPIRAL"
    SPRING = "SPRING"
    CIRCULAR = "CIRCULAR"
    SPECTRAL = "SPECTRAL"
    BIPARTITE = "BIPARTITE"
    KAMADA_KAWAI = "KAMADA_KAWAI"
    MULTIPARTITE = "MULTIPARTITE"

class CytoscapeElements(SQLModel, table=True):
    concept_graph_name: str = Field(primary_key=True, description="The AGE name of the concept graph")
    layout_name: LayoutName = Field(primary_key=True, sa_column_kwargs={"nullable": False}, description="The graph layout name")
    s3_key: str = Field(nullable=True, description="the s3 key for the cytoscape json object")
