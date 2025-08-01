from datetime import datetime, timedelta
from typing import Dict, Generator, Union, List

from cyjax.resources.model_dto import ModelDto


ModelIdType = Union[int, str]
ModelResponseType = Union[ModelDto, Dict[str, any]]

ListResponseType = List[Union[ModelDto, Dict[str, any], any]]

PaginationResponseType = Generator[ModelResponseType, None, None]
PaginatedPageResponseType = List[ModelResponseType]

ApiDateType = Union[datetime, timedelta, str]
