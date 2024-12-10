#some maintenance/setup scripts that can be scheduled if desired
import sys 
sys.path.append('./api/handlers')
sys.path.append('./api/handlers/vdf_parser/src')

import parseData 
import apiHandler
import dbHandler
import os 
import re
import json
import base64

import asyncio 
import aiohttp


async def fetchHeroAbilitiesAsync(session, hero, heroId, parser,api,a_ids_data):
    ''' helper function to handle concurrent fetching of abilities ''' 
    url = api.fetchHeroAbilities(hero)
    async with session.get(url) as response:
        abilities_vdf = await response.text()
        abilities_vdf = re.sub(r'"ItemRequirements"\s*""', '"ItemRequirements"\t\t"1"', abilities_vdf)
        abilities_vdf = re.sub(r'"has_flying_movement"\s*""', '"has_flying_movement"\t\t"1"', abilities_vdf)
        abilities_vdf = re.sub(r'"damage_reduction"\s*""', '"damage_reduction"\t\t"1"',abilities_vdf)
        abilities_json = parser.vdfToJson(abilities_vdf)["DOTAAbilities"]
        del abilities_json["Version"]
        parser.replace_values_with_strings(abilities_json)
        abilities_json=parser.parseAbilities(abilities_json,heroId,hero,a_ids_data)
        return hero, abilities_json

async def dispatchAbilitiesUpdates(heroAbilitiesToFetch,parser,api,a_ids_data):
    ''' creates session and schedules tasks to update abilities''' 
    abilitiesCollection={} 
    async with aiohttp.ClientSession() as session:
        tasks =[] 
        for hero, heroId in heroAbilitiesToFetch:
            task = asyncio.create_task(fetchHeroAbilitiesAsync(session,hero,heroId,parser,api,a_ids_data  ))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        for hero,abilities_json in results:
            abilitiesCollection[hero]=abilities_json
    return abilitiesCollection

async def updateHeroAndAbilityDetailed(): #should be deleting tables first as often keys are slightly renamed instead of replaced causing duplicates
    '''fetches and updates hero and ability details for the db'''
    #instantiate handlers
    api = apiHandler.ApiHandler()
    parser = parseData.parseData()
    #get heroes 
    heroes_url = api.fetchHeroesDetailed()
    heroes_vdf = api.sendRequest(heroes_url,{"Response-Type":"text"})
    heroes_json = parser.vdfToJson(heroes_vdf)["DOTAHeroes"]
    hero_lore_url = api.fetchHeroLore()
    hero_lore = json.loads(api.sendRequest(hero_lore_url))
    #clean
    try:
        #del heroes_json['DOTAHeroes']
        del heroes_json['Version']
        del heroes_json['npc_dota_hero_base']
        del heroes_json['npc_dota_hero_target_dummy']
    except Exception as e:
        print('Cleaning failed')

    # the vdf files do not contain IDs so we source ability ids from odota 
    aIdsUrl = api.fetchAbilityIds()
    a_ids_data = json.loads(api.sendRequest(aIdsUrl))
    #reverse the dictionary since we want to lookup by value and prefer 0(1) time of keylookup
    a_ids_data = {v:k for k,v in a_ids_data.items()}
    #deal with data 
    detailedHeroes, heroAbilitiesToFetch=parser.parseHeroesDetailed(heroes_json,hero_lore,a_ids_data)
    dbM = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
    dbM.connect(dbName="dota2", collectionName="heroes_live")
    dbM.updateBulkData(detailedHeroes,"hero_id")
    
 

    #send all api requests concurrently to fetch abilities
    abilitiesCollection = await dispatchAbilitiesUpdates(heroAbilitiesToFetch,parser,api,a_ids_data)


    dbA = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
    dbA.connect(dbName="dota2", collectionName="abilities",id="hero_id")
    dbA.updateBulkData(abilitiesCollection,"hero_id")

def updateItems():
    '''fetches and updates items collection in db''' 
    api=apiHandler.ApiHandler()
    parser = parseData.parseData()
    itemUrl = api.fetchItems()
    res = api.sendRequest(itemUrl)
    if(res['type'] == 'file'):
        encodingType = res['encoding']
        if(encodingType=='base64'):
            items=base64.b64decode(res['content']) #decode to bytes
            items=items.decode('utf-8') #decode to str
    items=json.loads(items) #load as dict/json 
    items = parser.parseItems(items) #update urls 
    dbI = dbHandler.dbHandler(os.getenv("MONGO_CONNECTION_STR"))
    dbI.connect(dbName='dota2',collectionName='items')
    dbI.updateBulkData(items,'item_id') #store 

def updateAbilitiesLocalization():
    api = apiHandler.ApiHandler()
    parser = parseData.parseData()
    localizationUrl = api.fetchAbilityLocalization()
    localVdf = api.sendRequest(localizationUrl,{'Response-Type':'text'})
    localJson = parser.vdfToJson(localVdf)['lang']
    with(open('api/static/lang_en.json','w') as f):
        json.dump(localJson,f)
    
def migrateDb():
    print('TODO')
    
from bs4 import BeautifulSoup
import os
import requests
import time
def imgScraper(dir,url):
    
    if not os.path.exists(dir):
        os.makedirs(dir)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    item_images = soup.find_all('img')

    def sanitize_filename(filename):
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    for img in item_images:
        time.sleep(5)
        img_url = img['src']
        
        if not img_url.startswith('http'):
            img_url = 'https:' + img_url
        
        # Get the image name from the URL
        img_name = os.path.basename(img_url.split('?')[0])  
        img_name = sanitize_filename(img_name)  
        img_name_path = os.path.join('dota2_images', img_name)
        
        try:
            img_data = requests.get(img_url).content
            with open(img_name, 'wb') as handler:
                handler.write(img_data)
            print(f'Downloaded: {img_name}')
        except Exception as e:
            print(f'Failed to download {img_url}. Reason: {e}')

    print("All images downloaded!")
def gameDataUpdates():
    ''' run whenever dota2 patches occur -- preferably ensure relevant db collections are cleared first ''' 
    asyncio.run(updateHeroAndAbilityDetailed())
    updateItems()
    updateAbilitiesLocalization()



if __name__=="__main__":
    print('running scripts')
    #asyncio.run(updateHeroAndAbilityDetailed())
    fillInData()
