class StaticPro:

    def __init__(self, static_data):
        self._static_data = static_data

    def get_nickname(self):
        return self._static_data['nickName']