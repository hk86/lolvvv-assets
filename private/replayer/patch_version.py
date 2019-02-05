from database.meteor import Meteor


class PatchVersion:
    def __init__(self, meteor_db: Meteor):
        self._meteor_db = meteor_db

    @staticmethod
    def version_to_patch(version: str):
        granulate = version.split('.')
        return '{}.{}'.format(granulate[0], granulate[1])

    def client_patch(self, client_version: str):
        matching_version = self._meteor_db.get_patch_version(
            client_version)
        if matching_version:
            return self.version_to_patch(matching_version)
