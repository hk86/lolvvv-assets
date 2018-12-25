from database.meteor import Meteor

if __name__ == "__main__":
    meteor_db = Meteor('mongodb://root:ZTgh67gth1@10.8.0.2:27017/meteor?authSource=admin')
    clips = meteor_db.get_all_clips()
    clips.sort(key=lambda x: x['eventType'])
    for clip in clips:
        print('{}: {}'.format(clip['eventType'], clip['uri']))