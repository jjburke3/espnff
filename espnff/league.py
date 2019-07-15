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


        self.teams = data['teams']


    def _fetch_draft_data(self, data):
        teams = data['teams']
        
    

    def _fetch_teams(self, data):
        '''Fetch teams in league'''
        teams = data['teams']

        for team in teams:
            self.teams.append(Team(teams[team]))

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup == opponent.team_id:
                        team.schedule[week] = opponent

        # calculate margin of victory
        for team in self.teams:
            for week, opponent in enumerate(team.schedule):
                mov = team.scores[week] - opponent.scores[week]
                team.mov.append(mov)

        # sort by team ID
        self.teams = sorted(self.teams, key=lambda x: x.team_id, reverse=False)

    def _fetch_settings(self, data):
        self.settings = Settings(data)

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
        print(teamData)
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
