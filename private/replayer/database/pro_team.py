from pprint import pprint

class ProTeam:
    def __init__(self, static_data):
        self._static_data = static_data

    def _get_name(self):
        return self._static_data['teamName']

    def _get_tag(self):
        return self._static_data['teamTag']

    def _get_image(self):
        return self._static_data['image']['full']

    name = property(fget=_get_name)
    tag = property(fget=_get_tag)
    image = property(fget=_get_image)
