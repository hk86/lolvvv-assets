

# coding: utf-8

import collections
import copy
import os
import pymongo
import requests
import time

from riotwatcher import RiotWatcher
from snippets import match_reducer


def store_match(match, pro_mapping, spell_maxrank):
    if match['queueId'] in [4, 6, 42, 410, 420, 440]:
        #print(match['gameId'], match['platformId'])
        match_reducer.reduce_match(match, spell_maxrank, pro_mapping)
        db['fact_matches'].update_one(
            {'platformId': match['platformId'],
             'gameId': match['gameId']},
            {"$set": match},
            upsert=True)
        for i, participant in enumerate(match['participants']):
            #participant_identity = match['participantIdentities'][i]
            participant_identity = list(
                filter(
                    lambda partIdent: partIdent['participantId'] == participant['participantId']
                    , match['participantIdentities']))[0]

            team = list(filter(lambda team: team['teamId'] == participant['teamId'], match['teams']))[0]
            account_id = participant_identity['player']['currentAccountId']
            platform_id = participant_identity['player']['currentPlatformId']
            pro_map_key = '{}{}'.format(platform_id, account_id)
            pro_id = pro_mapping[pro_map_key]['proId'] if pro_map_key in pro_mapping.keys() else None
            if pro_id:
                od = collections.OrderedDict([
                    ('gameId', match['gameId']),
                    ('platformId', match['platformId']),
                    ('gameCreation', match['gameCreation']),
                    ('gameDuration', match['gameDuration']),
                    ('gameEnding', match['gameEnding']),
                    ('queueId', match['queueId']),
                    ('mapId', match['mapId']),
                    ('seasonId', match['seasonId']),
                    ('gameVersion', match['gameVersion']),
                    ('gameMode', match['gameMode']),
                    ('gameType', match['gameType']),
                    ('matchUp', match['matchUp']),
                    ('team', team),
                    ('participant', participant),
                    ('participantIdentity', participant_identity),
                ])
                db['fact_matches_pro'].update_one({
                    'platformId': match['platformId'],
                    'gameId': match['gameId'],
                    'participantIdentity.pro.proId': pro_id},
                    {"$set": od},
                    upsert=True)

if __name__ == "__main__":

    print('START')

    api_key = 'RGAPI-73bc3720-31df-4065-ad74-f577dc21873d'
    watcher = RiotWatcher(api_key)


    # Database
    uri = 'mongodb://root:ZTgh67gth1@172.31.92.174:27017/meteor?authSource=admin'
    mc = pymongo.MongoClient(uri)
    db = mc['meteor']

    uri = 'mongodb://localhost:27017'
    mc = pymongo.MongoClient(uri)
    db_f = mc['factdata']
    db_s = mc['staticdata']

    # Match Reducer
    pro_mapping = {}
    pros_accounts = {}
    for pro in db_s['static_pros'].find({}):
        if 'accounts' in pro and pro['accounts']:
            for platform_id, accounts in pro['accounts'].items():
                if accounts:
                    for account in accounts:
                        pro_mapping['{}{}'.format(platform_id, account)] = pro
                        if platform_id in pros_accounts:
                            pros_accounts[platform_id].append(account)
                        else:
                            pros_accounts[platform_id] = [account]

    spell_maxrank = {}
    for spell in db_s['static_champions_spells'].find({}):
        spell_maxrank[spell['id']] = spell['maxrank']

    # TODO Collect only a few queueIds [4, 6, 42, 410, 420, 440]
    i = 5
    while True:
        for platform_id in pros_accounts.keys():
            #print(platform_id)
            for account_id in pros_accounts[platform_id]:
                try:
                    matchlist = watcher.match.matchlist_by_account(platform_id, account_id)
                    for simple_match in matchlist['matches'][:i]:
                        match_found = db_f['matches'].count(
                            {'platformId': simple_match['platformId'], 'gameId': simple_match['gameId']}) > 0
                        if not match_found:
                            match = watcher.match.by_id(simple_match['platformId'], simple_match['gameId'])
                            timeline = watcher.match.timeline_by_match(simple_match['platformId'], simple_match['gameId'])
                            #print('--', 'Store game {} {}'.format(simple_match['platformId'], simple_match['gameId']))

                            match['timeline'] = timeline
                            db_f['matches'].insert_one(match)
                            store_match(match, pro_mapping, spell_maxrank)
                except requests.HTTPError as e:
                    #if e.response.status_code == 429:
                    #    time.sleep(int(e.headers['Retry-After']))
                    #else:
                    pass
        i = min(i+5, 100)

