from pprint import pprint

class StaticPro:

    def __init__(self, static_data):
        self._static_data = static_data

    def _get_nickname(self):
        return self._static_data['nickName']

    def _get_id(self):
        return self._static_data['proId']

    def _get_image(self):
        return self._static_data['image']['full']

    def _get_team_id(self):
        return self._static_data['teamId']

    def __hash__(self):
        return hash(self._get_id())

    id = property(fget=_get_id)
    nickname = property(fget=_get_nickname)
    image = property(fget=_get_image)
    team_id = property(fget=_get_team_id)