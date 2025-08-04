_C='Nom de la métrique.'
_B='forbid'
_A=None
from pydantic import BaseModel,Field
class ReaderTxtMetricsConfig(BaseModel,extra=_B):name:str|_A=Field(default=_A,description=_C);pattern:str=Field(default=_A,description='Expression régulière pour identifier la métrique.');number_position:int=Field(default=1,description='Position du nombre dans le tableau de nombres de la ligne.')
class ReaderColsMetricsConfig(BaseModel,extra=_B):name:str|_A=Field(default=_A,description=_C);col:int|str|_A=Field(default=_A,description="Index de la colonne pour la métrique (index `1` pour la première colonne). Si `String`, nom de la colonne pour la métrique. Si la colonne n'existe pas, il n'y aura pas de parsing. (Valide seulement si la première ligne est les en-têtes)");aggregation:str=Field(default='sum',description="Méthode d'agrégation pour la métrique. Peut être `mean`, `sum`, `min`, `max`.")