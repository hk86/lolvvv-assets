class Summoner:

    def __init__(self, account_id, platform_id):
        self._ACCOUNT_ID = account_id
        self._PLATFORM_ID = platform_id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__
        
    def _get_platform_id(self):
        return self._PLATFORM_ID

    def _get_account_id(self):
        return self._ACCOUNT_ID

    platform_id = property(fget=_get_platform_id)
    account_id = property(fget=_get_account_id)