
import sys
#sys.path.append('./vdf_parser/src')
import vdf_parser
import pandas as pd
import urls 
import json
import os
from time import strftime, localtime 
import re
class parseData:

    def __init__(self, logging=None):
        if(logging):
            import logging
            logging.basicConfig(level=logging.NOTSET)
            self.logger=logging.getLogger(__name__)
        else:
            self.logger=None
        self.dota_ability_strings = { #TODO:update to lang desc 
            "DOTA_ABILITY_BEHAVIOR_NONE": "None",
            "DOTA_ABILITY_BEHAVIOR_PASSIVE": "Passive",
            "DOTA_ABILITY_BEHAVIOR_UNIT_TARGET": "Unit Target",
            "DOTA_ABILITY_BEHAVIOR_CHANNELLED": "Channeled",
            "DOTA_ABILITY_BEHAVIOR_POINT": "Point Target",
            "DOTA_ABILITY_BEHAVIOR_ROOT_DISABLES": "Root",
            "DOTA_ABILITY_BEHAVIOR_AOE": "AOE",
            "DOTA_ABILITY_BEHAVIOR_NO_TARGET": "No Target",
            "DOTA_ABILITY_BEHAVIOR_AUTOCAST": "Autocast",
            "DOTA_ABILITY_BEHAVIOR_ATTACK": "Attack Modifier",
            "DOTA_ABILITY_BEHAVIOR_IMMEDIATE": "Instant Cast",
            "DOTA_ABILITY_BEHAVIOR_HIDDEN": "Hidden",
            "DAMAGE_TYPE_PHYSICAL": "Physical",
            "DAMAGE_TYPE_MAGICAL": "Magical",
            "DAMAGE_TYPE_PURE": "Pure",
            "SPELL_IMMUNITY_ENEMIES_YES": "Yes",
            "SPELL_IMMUNITY_ENEMIES_NO": "No",
            "SPELL_IMMUNITY_ALLIES_YES": "Yes",
            "SPELL_IMMUNITY_ALLIES_NO": "No",
            "SPELL_DISPELLABLE_YES": "Yes",
            "SPELL_DISPELLABLE_YES_STRONG": "Strong Dispels Only",
            "SPELL_DISPELLABLE_NO": "No",
            "DOTA_UNIT_TARGET_TEAM_BOTH": "Both",
            "DOTA_UNIT_TARGET_TEAM_ENEMY": "Enemy",
            "DOTA_UNIT_TARGET_TEAM_FRIENDLY": "Friendly",
            "DOTA_UNIT_TARGET_HERO": "Hero",
            "DOTA_UNIT_TARGET_BASIC": "Basic",
            "DOTA_UNIT_TARGET_BUILDING": "Building",
            "DOTA_UNIT_TARGET_TREE": "Tree"
        }
        
    def parseHeroesSteam(self,jsonDump):
        '''parse hero response from Steam API
        params---
        json:dict: response from steamAPI
        returns---
        parsed heroes w/ image url added:dict
        ''' 
        heroes = jsonDump['result']['heroes']
        df = pd.DataFrame.from_dict(heroes)
        df['image_full']= df.apply(self.__createHeroPortraitUrlFull,axis=1) #add image column with corresponding url in steam cdn
        df['image_small']=df.apply(self.__createHeroPortraitUrlSmall,axis=1)
        if(self.logger):
            self.logger.info('Portrait URLS added to heroes')
        return df.to_dict(orient='records')
        

    #helper function for parseHeroes
    def __createHeroPortraitUrlFull(self,row):
        return "{}{}_full.png".format(urls.BASE_HERO_IMAGES_URL,row['name'].replace('npc_dota_hero_',''))

    def __createHeroPortraitUrlSmall(self,row):
        return "https://cdn.cloudflare.steamstatic.com//apps/dota2/images/dota_react/heroes/icons/{}.png".format(row['name'].replace('npc_dota_hero_',''))

    def parseMatchesSteam(self,jsonDump):
        '''parse match response from SteamAPI 
        params---
        json:dict:response from api
        returns---
        parsed matches:dict
    '''
        return jsonDump['result']['matches']
        
    def _has_leaver(self,players,code):
        ''' check for leavers in players 
        :param players: (list) element of matches pd.df 
        :param code: (int) any equal or high value is removed
        :return (bool): 
        ''' 
        return any(player['leaver_status'] <=code for player in players) 
    
    def parsePublicMatches(self,jsonDump):
        '''
        version of parsePublicMatches without using dataframes  
        '''
        matches = [match for match in jsonDump if match.get('game_mode') == 22]
        if(self.logger):
            self.logger.info('Filtered for game mode')

        matches = [match for match in matches if match.get('lobby_type') in [6, 7]]
        if(self.logger):
            self.logger.info('Filtered for lobby type')

        matches = [match for match in matches if match.get('duration', 0) > 900]
        if(self.logger):
            self.logger.info('Filtered for duration>15min')
        def convertTime(match):
            match['start_time'] =self.__convertUnixTime(match)
            return match 
        matches = [convertTime(match) for match in matches]
        if(self.logger):
            self.logger.info('Match start time converted to datetime')

        return matches  
    def parsePublicMatchesOpenDota(self,jsonDump):
        '''parse match response from Open Dota /publicMatches endpoint
        remove non ranked games: https://github.com/odota/dotaconstants/blob/master/json/lobby_type.json shows types
        remove games less than 15minutes: study https://cosx.org/2017/05/rdota2-seattle-prediction/
        params--
        json: api response 
        return: parsed data: dict
        ''' 
        
        matches = pd.DataFrame.from_dict(jsonDump)
        matches = matches.loc[matches['game_mode']==22] #only keep ranked matches
        if(self.logger):
            self.logger.info('Filtered for game mode')
        matches = matches.loc[(matches['lobby_type']==7)| (matches['lobby_type']==6) ] #only keep ranked lobbies 6=forced solo mm 7=normal ranked lobby
        if(self.logger):
            self.logger.info('Filtered for lobby type')
        matches = matches.loc[matches['duration']>900] #only keep games >15minutes
        if(self.logger):
            self.logger.info('Filtered for duration>15min')
        #helper function for parseMatches ## convert unix epoch time to datetime 
        #matches = matches[matches['players'].apply(lambda x: _has_leaver(x,1))] #1 and 0 indicate on leaver ###removed for now. filter for leavers later if needed -- currently miniscule relevance on overall data and should be equal for both teams
        matches['start_time']=matches.apply(self.__convertUnixTime,axis=1) #convert time 
        if(self.logger):
            self.logger.info('Match start time converted to datetime')
        return matches.to_dict(orient='records')

    def transformFacetIcon(self,facets):
        return {
            key:{
                'Icon': 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/icons/facets/'+value.get('Icon')+'.png',
                'Color': value.get('Color'),
                'GradientID': value.get('GradientID')
            }
            for key, value in facets.items()
        }

    def parseItems(self,items):
        ''' takes raw items dict and parses to prep for db -- currently just adjusting image urls'''
        updated_items = {
            key: {
                **{k: v for k, v in value.items() if k != 'id'},  # Unpack all fields except 'id'
                'img': 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items/{}_lg.png'.format(key),
                'item_id': value['id']  # Rename 'id' to 'item_id'
            }
            for key, value in items.items()
         }
        return updated_items
         
    def parseHeroesDetailed(self,heroes_json,hero_lore=None,a_ids_data=None):
        '''takes heroes dict and filters for data to be sent to db
        :returns dict: formatted to be added to db 
        :returns list: hero names in form to be used to fetch their abilities 
        ''' 
        heroesDetailed={}    
        abilitiesList=[] #storing names to be used to fetch abilities later 
        for heroName in heroes_json:
            heroDetails = {}
            abilitiesList.append((heroName, heroes_json[heroName]['HeroID'])) #so that they can be fetched later 
            heroDetails['hero_id']=int(heroes_json[heroName]['HeroID'])
            heroDetails['localized_name']= heroes_json[heroName].get('workshop_guide_name','')
            heroDetails['name']=heroName
            if(hero_lore):
                heroDetails['description'] = hero_lore[heroName.replace('npc_dota_hero_','')]
            attr= heroes_json[heroName].get('AttributePrimary').replace('DOTA_ATTRIBUTE_','')
            if(attr == 'ALL'): attr='UNIVERSAL'
            if(attr=='INTELLECT'): attr="INTELLIGENCE"
            heroDetails['attribute']= attr 
            heroDetails['img_full'] = "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/heroes/{}.png".format(heroName.replace('npc_dota_hero_','')) #TODO migrate these URLS to url file correctly. Old ones do not work
            heroDetails['img_small'] = "https://cdn.cloudflare.steamstatic.com//apps/dota2/images/dota_react/heroes/icons/{}.png".format(heroName.replace('npc_dota_hero_',''))
            heroDetails['facets'] = self.transformFacetIcon(heroes_json[heroName]['Facets'])
            heroDetails['roles'] = heroes_json[heroName]['Role'].split(',')
            heroDetails['role_levels'] = [int(x) for x in heroes_json[heroName]['Rolelevels'].split(',') if x.strip()] #using x.strip to avoid casting empty strings
            heroDetails['aliases'] = str(heroes_json[heroName].get('NameAliases',"")).split(';')
            heroDetails['similar'] = [int(x) for x in heroes_json[heroName].get('SimilarHeroes',"").split(',') if x.strip()]
            heroDetails['animated'] = 'https://cdn.akamai.steamstatic.com/apps/dota2/videos/dota_react/heroes/renders/{}.webm'.format(heroName.replace('npc_dota_hero_',''))
            heroDetails['abilities']=[]
            heroDetails['talents']={ #talents are stored at their available level, each level should have 2 options 
                "10":[],
                "15":[],
                "20":[],
                "25":[]
            }
            #ability handling
            ''' 
            Heroes may have any number of abilities in their entry. Labelled Ability1 Ability2 etc
            Starting from 10 these are talents by default, however, some heroes have AbilityTalentStart which indicates where the talents start 

            match keys that have Ability# in them> if no TalentStart index key, default to treating everything at 10+ as talents 
            talents grouped into 2 in order appeared
            '''
            talentIndex = heroes_json[heroName].get('AbilityTalentStart',None)
            talentIndex=10 if talentIndex is None else int(talentIndex)
            talentLevel = 10
            talentsInCurrentLevel = 0
            talentCount=0
            talentSwitch=False
            keys = self.extract_ability_keys(heroes_json[heroName]) 
            for key in keys:
                num = int(key[7:])
                if(num==talentIndex): talentSwitch=True #this presumes abilities come before talents which appears to be the case for now, using num<talentIndex doesn't work for invoker whos innate is ability 25 

                if(not talentSwitch or talentCount==8):
                    heroDetails['abilities'].append({'name':keys[key], 'ability_id':int(a_ids_data.get(keys[key],-1))})
                else:
                    heroDetails['talents'][str(talentLevel)].append({'name':keys[key],'ability_id':int(a_ids_data.get(keys[key],-1))})
                    talentCount+=1
                    talentsInCurrentLevel +=1
                    if(talentsInCurrentLevel==2):
                        talentLevel+=5
                        talentsInCurrentLevel=0
            heroesDetailed[heroName]= heroDetails
            if(self.logger):
                self.logger.info("Created hero entry {}\n\n adding to collection".format(heroDetails))
        return heroesDetailed, abilitiesList
            
    def parseAbilities(self,abilities_json,heroId,hero,a_ids_data):
        #for graphql queries these need to have a field name
        entry={}
        abilities = {} 
        talents = {} 
        for ability in abilities_json:
            if(ability[:7]=="special"):
                talentId = int(a_ids_data.get(ability,-1)) #TODO: replace -1 with logic to find correct fallback --- 
                if(isinstance(abilities_json[ability],list)): #dealing with timbersaw reactive armor that has duplicate entry in a list
                    if(abilities_json[ability][0] ==abilities_json[ability][1]):
                        abilities_json[ability] = abilities_json[ability][0]
                talents[ability] = {**abilities_json[ability], 'ability_id':talentId}  
                continue
            abilities_json[ability]['img']=f'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/{ability}.png'
            ability_id = int(a_ids_data.get(ability))
            abilities[ability]={**abilities_json[ability], 'ability_id':ability_id}
        entry['hero_id']= int(heroId)
        entry['hero_name']=hero
        entry['abilities']=abilities
        entry['talents']=talents
        return entry

    def vdfToJson(self,vdfDump):
        vdfh = vdf_parser.VDF({"types":False})
        return vdfh.parseVdf(vdfDump)

        

    def jsonToVdf(self,jsonDump):
        vdfh = vdf_parser.VDF({"types":False})
        return vdfh.dump(vdf)
    
    def replace_values_with_strings(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self.replace_values_with_strings(v)
            elif isinstance(v, list):
                # Recursive call to handle lists and nested lists
                d[k] = self._process_list(v)
            elif isinstance(v, str):
                d[k] = self._replace_string_values(v)
    #helper function @replace_values_with_strings -- not cleanest solution
    def _process_list(self, lst):
        for i, item in enumerate(lst):
            if isinstance(item, dict):
                self.replace_values_with_strings(item)
            elif isinstance(item, list):
                # Recursive call for nested lists
                lst[i] = self._process_list(item)
            elif isinstance(item, str):
                lst[i] = self._replace_string_values(item)
        return lst
    #helper function @replace_values_with_strings --> handle strings with separators e.g. | 
    def _replace_string_values(self,string):
        parts = string.split('|') 
        translated = [self.dota_ability_strings.get(part.strip(),part.strip()) for part in parts]
        if(len(translated)>1):
            return translated
        return translated[0]
    def extract_ability_keys(self, d):
        ability_pattern = re.compile(r'^Ability\d+$')
        return {k:v for k,v in d.items() if ability_pattern.match(k)}    
    def __convertUnixTime(self,row):
        return strftime('%Y-%m-%d %H:%M:%S',localtime(row['start_time']))


'''Testing inserting heroes 
db= dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
db.connect(dbName="dota2",collectionName="heroes")
f=open("dumpHeroes.json","r")
data =json.load(f)
pars = parseData()
data = pars.parseHeroesSteam(data)
print(data)
db.insertData(data,many=True)
'''
