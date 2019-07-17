import requests

from .utils import (two_step_dominance,
                    power_points, )
from .team import Team
from .settings import Settings
from .matchup import Matchup
from .player import Player
from .exception import (PrivateLeagueException,
                        InvalidLeagueException,
                        UnknownLeagueException, )

from .boxCodes import (lineupSlots,
                       nflTeams,
                       nflTeamsAbbrev,
                       playerPos,
                       healthStatus)



class League(object):
    '''Creates a League instance for Public ESPN league'''
    def __init__(self, league_id, year, espn_s2=None, swid=None):
        self.league_id = league_id
        self.year = year
        self.ENDPOINT = "http://fantasy.espn.com/apis/v3/games/ffl/seasons/%d/segments/0/leagues/%d"
        self.teams = []
        self.espn_s2 = espn_s2
        self.swid = swid
        self._fetch_league()
        self._fetch_players()

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self):
        params = {
           'view':'mTeam'
        }

        cookies = None
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }
        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        ##r = requests.get('%sleagueSettings' % (self.ENDPOINT, ), params=params, cookies=cookies)

        self.status = r.status_code
        
        data = r.json()

        self.teams = []
        memberData = data['members']

        for team in data['members']:
            
            teamData = list(filter(lambda d: d['owners'][0] == team['id'],
                                   data['teams']))
            self.teams.append({
                    'teamName' : team['firstName'] + ' ' + team['lastName'],
                    'teamKey' : team['id'],
                    'teamId' : teamData[0]['id'],
                    'nickName' : teamData[0]['location'] + ' ' + teamData[0]['nickname'],
                    'waiverRank' : teamData[0]['waiverRank'],
                    'budgetSpent' : teamData[0]['transactionCounter']['acquisitionBudgetSpent'],
                    'trades' : teamData[0]['transactionCounter']['trades'],
                    'acquisitions' : teamData[0]['transactionCounter']['matchupAcquisitionTotals']
                })



    def _fetch_players(self):
        params = {
            'scoringPeriodId':0,
            'view':'players_wl'
            }
        playerEndpoint = 'http://fantasy.espn.com/apis/v3/games/ffl/seasons/%d/players'

        cookies = None
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }
        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)

        self.players = r.json()['players']


        


    def boxscore(self,week,team):
        params = {
            'view':'mBoxscore',
            'leagueId': self.league_id,
            'seasonId': self.year,
            'scoringPeriodId': week,
            'matchupPeriodId': week,
            'forTeamId' : team
        }
        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        data = r.json()
        if self.status == 401:
            raise PrivateLeagueException(data['error'][0]['message'])

        elif self.status == 404:
            raise InvalidLeagueException(data['error'][0]['message'])

        elif self.status != 200:
            raise UnknownLeagueException('Unknown %s Error' % self.status)

        boxscoreData = data['schedule']
        def checkAwayKey(obj):
            if 'away' in list(obj.keys()):
                return obj['away']['teamId']
            else:
                return 99
        
        
        boxscoreData = list(filter(lambda d: (d['matchupPeriodId'] == week and
                                     (d['home']['teamId'] == team or
                                      checkAwayKey(d) == team
                                      )), boxscoreData))
        
        if boxscoreData[0]['home']['teamId'] == team:
            d = 'home'
        else:
            d = 'away'
        teamData = boxscoreData[0][d]
        players = teamData['rosterForCurrentScoringPeriod']['entries']
        playerList = []
        for player in players:
            if 'player' in player['playerPoolEntry']:
                playerInfo = player['playerPoolEntry']['player']
                if 'appliedStatTotal' not in player['playerPoolEntry']:
                    playerPoints = 0
                else:
                    playerPoints = player['playerPoolEntry']['appliedStatTotal']
                playerData = {'playerName' : playerInfo['fullName'],
                              'playerId' : playerInfo['id'],
                              'playerTeam' : nflTeams[playerInfo['proTeamId']],
                              'slot' : lineupSlots[player['lineupSlotId']],
                              'healthStatus' : 'empty',
                              'stats' : playerInfo['stats'],
                              'playerPos' : playerInfo['eligibleSlots'],
                              'Points' : playerPoints
                              }
            else:
                playerData = {'playerName' : 'empty',
                              'playerId' : 'empty',
                              'playerTeam' : 'empty',
                              'slot' : lineupSlots[player['lineupSlotId']],
                              'healthStatus' : 'empty',
                              'stats': 'empty',
                              'playerPos' : 'empty',
                              'Points' : 0}
            playerList.append(playerData)
        result = {'teamId' : teamData['teamId'],
                  'season' : self.year,
                  'week' : week,
                  'teamName' : team,
                  'teamPoints' : teamData['rosterForCurrentScoringPeriod']['appliedStatTotal'],
                  'opponentId' : '',
                  'opponentName' : '',
                  'opponentPoints' : '',
                  'playerList' : playerList}

        return result


    def freeAgents(self, week=None):

        params = {
            'scoringPeriodId':week,
            'view':'kona_player_info'
        }

    def draftData(self):
        params = {
            'view':'mDraftDetail'
        }

        r = requests.get(self.ENDPOINT % (self.year, self.league_id), cookies=self.cookies, params = params)
        
        data = r.json()

        draftData = data['draftDetail']['picks']



        draftPicks = []
        for pick in draftData:
            playerData = list(filter(lambda d: 'player' in d
                                     and d['player']['id'] == pick['playerId'],
                                     self.players))[0]['player']

            
            pickData = {
                'round' : pick['roundId'],
                'pick' : pick['overallPickNumber'],
                'teamId' : '',
                'playerId' : playerData['fullName']

                }

            draftPicks.append(pickData)

        return draftPicks
