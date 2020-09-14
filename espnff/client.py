import requests
from espnff import League
from espnff.exception import AuthorizationError


class ESPNFF:
    def __init__(self, username=None, password=None, swid = None, s2=None):
        self.__username = username
        self.__password = password
        self.__auth_swid = swid
        self.__auth_s2 = s2

    def authorize(self):
        x = 0

        #self.__auth_s2 = '{0282073E-8F66-4F3E-B31E-DD2F2A2B0C68}'
        #self.__auth_swid = 'AEBdtvvK%2F7HwrYzxOASS4zkjta3llBEO9ePglR1sg8upF%2Bhb9nhL7HYC80YRF%2B3Z%2F3Y1dfoDEtZiI2ExoY606OITOxWeBs0Pp%2F1xD5TJn8Xpf1tQ9%2FQBQPBZ3YnAYBWlm1alX755pr5R9te6vqGBvBh330USgJgk%2FSx4YdgeDwnA%2FK%2BX3DC%2FFoY5t4FWe%2B8LkiVE3afeg2wUr31rLFD%2FKMYvTkvYJ1jVOeHciTBEPAKwQWeghd3A7BZpBuc6%2Bhecrdp0ZLfhr%2FIZ3ISNxDNurwLN'
        
    def get_league(self, league_id, year):
        return League(league_id, year, self.__auth_s2, self.__auth_swid)
