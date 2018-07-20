from .match import LiveMatch

class ClashLiveMatch(LiveMatch):
    def __init__(self, platform_id, game_id, encryption_key, db):
        LiveMatch.__init__(platform_id, game_id, encryption_key, db)

    def getTitle(self, db):
        title = super()._generate_match_title(db)
        return 'Clash Live! {}'.format(title)