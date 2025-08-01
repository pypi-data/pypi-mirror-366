
class ModelDto(dict):
    """
    The base class for all model DTOs.
    """

    def __init__(self, **kwargs):
        super(ModelDto, self).__init__(**kwargs)

    def _prop_to_dto(self, key, dto):
        """
        Map the property to DTO
        :rtype Optional[ModelDto]:
        """
        obj = self.get(key)

        if obj is not None and len(obj.keys()):
            return dto(**obj)
        else:
            return None

    def _prop_list_to_dto(self, key, dto) -> list:
        """
        Map the property to the list of DTOs
        :rtype list:
        """
        list_of_dict = self.get(key)

        if list_of_dict:
            return list(map(lambda obj_dict: dto(**obj_dict), list_of_dict))
        else:
            return []
