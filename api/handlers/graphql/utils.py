import re
def build_filters(args):
    filters={}
    if 'hero_id' in args:
        filters['picks_bans.hero_id']=args['hero_id']
    if 'avg_rank_tier' in args:
        league = args['avg_rank_tier']
        filters['avg_rank_tier']= {
            '$gt': league*10,
            '$lt': (1+league)*10
        }
    if 'min_played_overall' in args:
        filters['total_games'] = {'$gte': args['min_played_overall']}

    if 'min_win_overall' in args:
        filters['overall_win_rate'] = {'$gte': args['min_win_overall']}
    
    if 'min_played_radiant' in args:
        filters['total_radiant_games'] = {'$gte': args['min_played_radiant']}
    
    if 'min_played_dire' in args:
        filters['total_dire_games'] = {'$gte': args['min_played_dire']}
    
    if 'min_win_radiant' in args:
        filters['radiant_win_rate'] = {'$gte': args['min_win_radiant']}
    
    if 'min_win_dire' in args:
        filters['dire_win_rate'] = {'$gte': args['min_win_dire']}
    return filters 

def map_localization_for_ability(ability_name, localization,abilities,talents):# TODO redo this with recursion similar to redone version of talent localization mapping 
  ''' 
    fetch entries of ability_name from localization file
    extract all placeholders from the results 
    iterate through the placeholders to find their replacement values
  '''
  
  ability_name = ability_name.lower() #we force lower case on localization and name as the localization file has inconsistent capitalization 
  if(localization.get(f"dota_tooltip_facet_{ability_name}")):
    options='facet'
  else:
    options='ability'


  #handle data mismatches -> vdf file and data sourced from API have some mismatches, these can be added here 
  #outside of unique invoker case, the rest of these are facets that have been changed since introduction, likely this problem is resolved internally soon and refreshing data from API sources fixes it
  if(ability_name== 'drow_ranger_high_ground'):
    ability_name='drow_ranger_vantage_point'
  elif(ability_name=='juggernaut_agigain'):
    ability_name='juggernaut_bladeform'
  elif(ability_name=='batrider_buff_on_displacement'):
    ability_name='batrider_stoked'
  elif(ability_name=='morphling_str'):
    ability_name='morphling_flow'
  elif(ability_name =='sven_strscaling'):
    ability_name='sven_wrath_of_god'
  elif(ability_name=='vvengefulspirit_melee'): #this even has a typo 
    ability_name='vengefulspirit_soul_strike'
  if(ability_name=='special_bonus_unique_invoker_13'):
    result = {
      'name': '2xQuas/Wex/Exort active/passive effects' # need to force this until the developers update the game files 
    }
    return result 

  base_key=f'dota_tooltip_{options}'
  
  #fetch all keys associated with ability_name 
  local_keys = [key for key in localization if ability_name in key]
  

  #extract relevant keys 
  local_keys = [key for key in local_keys if key.startswith(base_key)]

  #extend base key to contain the ability_name
  base_key=f'{base_key}_{ability_name}'

  #construct result 
  result = {}
  for key in local_keys:
    if key == base_key:
      result['name']=localization.get(key,'')
    else:
      result_key = key.replace(f'{base_key}_','')
      result[result_key] = localization.get(key,'')
  

  #loop through result cleaning and finding placeholders then dealing with them 
  for key,value in result.items(): 
    result[key]=result[key].replace('<br>', '') #sometimes <br> characters are in the notes/description but not consistent 
    pattern1 = r'{s:([^}]+)}'  #match {s:someplaceholder}
    pattern2 = r'%([^\s%]+)%'     #match %someplaceholder% 
    placeholders = re.findall(pattern1,value) + re.findall(pattern2,value) #collect placeholders in value 

    replacement_values=[]
    for ph in placeholders: #attempt to find replacement values under abilities 
      replacement_values.append(find_placeholder(abilities,ph, ability_name))
    for i,repVal in enumerate(replacement_values):
      if(repVal is not None):
        result[key] = result[key].replace(f'{{s:{placeholders[i]}}}', str(repVal)) #replace {s:val}
        result[key] = result[key].replace(f'%{placeholders[i]}%', str(repVal))     #replace %val% 
      result[key] =re.sub(r'(\W)\1+', r'\1', result[key]) ## this just replaces any occurance of 2 symbols e.g. ++ xx -- as these are sometimes in dataset 
  return result 

def find_placeholder(data,placeholder,ability_name):
  '''
  There are a large number of variations here. Often the placeholder is found under AbilityValues, this can be as a key to an object that contains some field like value or directly as a str
  Sometimes it is under other categories  
  Since creating this cases were fonund with %CAPITAL LETTERS VALUE 
  these may require extra adaption -> though translating them is not yet necessary as these seem to be for ability values which we already translate on front end in a separate manner 
  '''
  
  if placeholder in data.keys() or placeholder.replace('bonus_','') in data.keys():
    res = data.get(placeholder) or data.get(placeholder.replace('bonus_',''))
    # now this can be under ability_name, value, special_bonus_scepter or just res so just handle various edge cases here
    if(isinstance(res,dict)):
      if(ability_name in res):
        return res.get(ability_name) #can this be dict in any edge case? 
      elif(f'special_bonus_facet_{ability_name}' in res):
        return res.get(f'special_bonus_facet_{ability_name}')
      elif('scepter' in ability_name and 'special_bonus_scepter' in res):
        return res.get('special_bonus_scepter')
      elif('value' in res):
        return res.get('value')
    elif(isinstance(res,str)):
      return res 
  elif placeholder in (key.lower() for key in data.keys()): #some placeholders have incorrect casing - this method may open potential bugs
    lower_data = {key.lower():value for key,value in data.items()}
    
    res = lower_data.get(placeholder,False)
    if(isinstance(res,str)):
      return res
    else:
      return None
  for sub_data in data.values():
    if(isinstance(sub_data,dict)): #recur
      res= find_placeholder(sub_data,placeholder, ability_name)
      if res: #res found so return value 
        return res
  return None 


    

#keeping this here until completing tests on new method 
''' 
def map_localization_for_ability(ability_name, localization,abilities,talents):# TODO redo this with recursion similar to redone version of talent localization mapping 
  ''' ''' important that it does not fetch unintended values. e.g. special_bonus_unique_hero should not fetch ..._hero_1 etc as these are different abilities. 
      similarly ..._otherability
      this also needs to replace the placeholder values that were in the vdfs 
      special case for invoker hero-- special_bonus_unique_invoker_13 does not have a translation in localization, instead it has _13_facetName -> these are not displayed even on valves dota2 website 

  '''''' 
  # Base key to lookup in the localization file
  
  ability_name = ability_name.lower()
  if(localization.get(f"dota_tooltip_facet_{ability_name}")):
    options='facet'
  else:
    options='ability'
  if(ability_name== 'drow_ranger_high_ground'): #hero/localization data mismatch
    ability_name='drow_ranger_vantage_point'
  if(ability_name=='juggernaut_agigain'):
    ability_name='juggernaut_bladeform'
  base_key = f"dota_tooltip_{options}_{ability_name}"
  
  if(ability_name=='special_bonus_unique_invoker_13'):
    result = {
      'name': '2xQuas/Wex/Exort active/passive effects' # need to force this until the developers update the game files 
    }
    return result 
  
  result = { ## add 
      'name': localization.get(f"{base_key}", ""),
      'description': localization.get(f"{base_key}_description", ""),
      'lore': localization.get(f"{base_key}_lore", ""),
  }
  
  def replace_placeholders(text,ability_name): #denoted by s{:text}
    #this is becoming incredibly convoluted, however, this is due to each hero having slightly different methods of storing ph values/descriptions/behaviors. 
    
    
    #placeholders = re.findall(r'{s:([^\}]+)\}', text)
    placeholders = re.findall(r'{s:([^}]+)\}|%\s*([^%\s]+)\s*%', text)

    placeholders = [p1 if p1 else p2 for p1, p2 in placeholders]
    
    for ph in placeholders:  
      if(ph=='value'):
        
        field = talents.get(ability_name)
        if(not field): ### fields that do not effect abilities usually have the value at the end of the ability name
          
          text = text.replace(f"{{s:{ph}}}",ability_name.split('_')[-1]) #### update to re.sub to account for both placeholders

        else: ### some heroes have the effect in an object in the talent -- weird inconsistency 
          newVal = field.get('AbilityValues').get('value')
          
          if(isinstance(newVal,dict)):
            newVal = newVal.get('value')
          text = re.sub(rf'{{s:{ph}\}}|%{ph}%', newVal, text)
      else:
        phText = ph#.removeprefix('bonus_')
        for a,v in abilities.items():   #we can't directly target abilities[phText] as sometimes effects are listed under other abilities 
          abilityKeys = [key.lower() for key in abilities.get(a).keys()] #sometimes the placeholder value is stored directly in ability instead of in ability values
          
          if(phText in abilityKeys): #if in ability 
            values = abilities.get(a)
          else: #else in ability.AbilityValues
            values = v.get('AbilityValues')
          if(values is None): continue
          valuesLower = {key.lower():value for key,value in values.items()} #sometimes these may be in differing cases so we are using this as a fallback 
          if((phText in values or phText in valuesLower) and ability_name) :
            field = values.get(phText, valuesLower.get(phText))
            if(isinstance(field,str)): #if str we have the new value
              newVal=field 
            else:   #find the new value
              newVal = field.get(ability_name) or field.get('special_bonus_scepter') or field.get('value')
            toRep=''
            try:
                toRep = str(abs(float(newVal))) #Attempt to abs ###TODO check if necessary since the changed re.sub 
            except:
                toRep=newVal or ''
            text = re.sub(rf's:{ph}\}}|%{ph}%', toRep, text)
            break
    text = re.sub(r'(\W)\1+', r'\1', text) #there is little consistency for duplicate symbols, so using this to replace them 
       
    return text
  
  
  
  for key, value in localization.items():
    # If the key starts with the ability name and isn't mapped already, treat it as a stat unless it contains Note or note
    if key.startswith(base_key) and key not in result.values() and len(key.replace(f"{base_key}_",""))>1:
      if '_Note' in key or '_note' in key: 
        note_name = key.replace(f"{base_key}_","")
        result[note_name]=value
      elif '_stat' in key or '_Stat' in key: #treat as stat
        stat_name = key.replace(f"{base_key}_", "")  
        result[stat_name]=value

  for key,value in result.items():
    result[key] = replace_placeholders(value,ability_name)
    result[key]=result[key].replace('<br>', '') #sometimes <br> characters are in the notes/description but not consistent 
  
  return result
''' 

from functools import reduce

def get_nested_attr(data, attr_path, default=None):
  """Helper function to get nested attributes safely"""
  try:
    return reduce(lambda d, key: d[key], attr_path, data)
  except (KeyError, TypeError):
    return default


def map_localization_for_talents_recur(ability_name, localization,abilities,talents):
  ability_name=ability_name.lower()
  if(localization.get(f"dota_tooltip_facet_{ability_name}")):
    options='facet'
  else:
    options='ability'
  base_key = f"dota_tooltip_{options}_{ability_name}"
  if(ability_name=='special_bonus_unique_invoker_13'):
    result = {
      'name': '2xQuas/Wex/Exort active/passive effects' # need to force this until the developers update the game files 
    }
    return result 
  
  result = { ## add 
      'name': localization.get(f"{base_key}", ""),
      'description': localization.get(f"{base_key}_description", ""),
      'lore': localization.get(f"{base_key}_lore", ""),
  }
  for key, value in localization.items():
    # If the key starts with the ability name and isn't mapped already, treat it as a stat unless it contains Note or note
    if key.startswith(base_key) and key not in result.values() and len(key.replace(f"{base_key}_",""))>1:
      if '_Note' in key or '_note' in key: 
        note_name = key.replace(f"{base_key}_","")
        result[note_name]=value
      elif '_stat' in key or '_Stat' in key: #treat as stat
        stat_name = key.replace(f"{base_key}_", "")  
        result[stat_name]=value
  
  def recursive_replace_placeholders(data,ability_name,value):
    if(ability_name in data):
      return data[ability_name]
    for val in data.values():
      if isinstance(val,dict):
        res = recursive_replace_placeholders(val, ability_name,value)
        if(res is not None):
          return res 
    
    #return value.replace(f"{{s:{ph}}}",ability_name.split('_')[-1]) 
    return None 

  for key,value in result.items():
    pattern1 = r'\{s:([^\}]+)\}'
    pattern2 = r'%([^\s%]+)%'
    placeholders = re.findall(pattern1,value) + re.findall(pattern2,value)
    
    replaced=[]
    for i,ph in enumerate(placeholders): 
      if(talents.get(ability_name)):
        val_in_talents=talents[ability_name].get('AbilityValues','')
      
      else:
        val_in_talents= {}
        
      if(ph=='value' and val_in_talents.get('value',False)): #handle cases in which values are stored in the talents object instead of under abilities (lion max hp per kill, veng some talents)
        if(isinstance(val_in_talents.get('value',False),dict)):
          toRep = val_in_talents['value'].get('value','')
        else: 
          toRep = val_in_talents.get('value','')
        replaced.append(toRep)
      else:
        replaced.append( recursive_replace_placeholders(abilities,ability_name,value))
    for i,rep in enumerate(replaced):
      if(rep is None): #catch some edge cases where replacements are part of the key 
        if(len(placeholders)==2):
          if(placeholders[0]=='crit_chance' and placeholders[1] =='crit_multiplier'):
            result[key] =result[key].replace(f"{{s:{placeholders[0]}}}", ability_name.split('_')[-3])
            result[key]= result[key].replace(f"{{s:{placeholders[1]}}}", str(float(ability_name.split('_')[-1])*100))
            break
        result[key] = result[key].replace(f"{{s:{ph}}}",ability_name.split('_')[-1])  #otherwise last part of key contains replacement value
      else:
        result[key] = result[key].replace(f'{{s:{placeholders[i]}}}', str(rep))
        result[key] = result[key].replace(f'%{placeholders[i]}%', str(rep))
      result[key] =re.sub(r'(\W)\1+', r'\1', result[key])
      
    result[key]=result[key].replace('<br>', '') #sometimes <br> characters are in the notes/description but not consistent 
  
  return result

'''
import json
with (open('api/static/lang_en.json','r') as f ):
    localization = json.load(f)['Tokens']
localization = {key.lower():value for key,value in localization.items()} 
heroData={
  "_id": {
    "$oid": "6703a7f46dd3722b92c70044"
  },
  "hero_id": 6,
  "abilities": {
    "drow_ranger_frost_arrows": {
      "AbilityBehavior": [
        "Unit Target",
        "Autocast",
        "Attack Modifier"
      ],
      "AbilityUnitTargetTeam": "Enemy",
      "AbilityUnitTargetType": [
        "Hero",
        "Basic"
      ],
      "SpellImmunityType": "No",
      "SpellDispellableType": "Yes",
      "AbilitySound": "Hero_DrowRanger.FrostArrows",
      "AbilityUnitDamageType": "Physical",
      "HasScepterUpgrade": "1",
      "AbilityCastRange": "625",
      "AbilityCastPoint": "0.0 0.0 0.0 0.0",
      "AbilityCooldown": "0.0 0.0 0.0 0.0",
      "AbilityDuration": "1.5",
      "AbilityDamage": "0 0 0 0",
      "AbilityManaCost": "9 10 11 12",
      "AbilityValues": {
        "frost_arrows_movement_speed": "-10 -20 -30 -40",
        "damage": {
          "value": "10 15 20 25",
          "special_bonus_unique_drow_ranger_2": "+15",
          "CalculateSpellDamageTooltip": "0"
        },
        "shard_regen_reduction_pct_per_stack": {
          "value": "0",
          "special_bonus_scepter": "+10",
          "RequiresScepter": "1"
        },
        "shard_bonus_damage_per_stack": {
          "value": "0",
          "special_bonus_scepter": "+18",
          "RequiresScepter": "1"
        },
        "shard_stack_duration": {
          "value": "0",
          "special_bonus_scepter": "+7.0",
          "RequiresScepter": "1"
        },
        "shard_burst_radius": {
          "value": "0",
          "special_bonus_scepter": "+650",
          "RequiresScepter": "1",
          "affected_by_aoe_increase": "1"
        },
        "shard_burst_damage_per_stack": {
          "value": "0",
          "special_bonus_scepter": "+60",
          "DamageTypeTooltip": "Magical",
          "RequiresScepter": "1"
        },
        "shard_burst_move_slow_pct": {
          "value": "0",
          "special_bonus_scepter": "+40",
          "RequiresScepter": "1"
        },
        "shard_burst_slow_duration": {
          "value": "0",
          "special_bonus_scepter": "+2.0",
          "RequiresScepter": "1"
        },
        "shard_max_stacks": {
          "value": "0",
          "special_bonus_scepter": "+9",
          "RequiresScepter": "1"
        }
      },
      "AbilityCastAnimation": "ACT_DOTA_CAST_ABILITY_1",
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_frost_arrows.png"
    },
    "drow_ranger_multishot": {
      "AbilityBehavior": [
        "Point Target",
        "DOTA_ABILITY_BEHAVIOR_DIRECTIONAL",
        "Channeled"
      ],
      "AbilityUnitTargetTeam": "Enemy",
      "AbilityUnitTargetType": [
        "Hero",
        "Basic"
      ],
      "AbilityUnitDamageType": "Physical",
      "SpellImmunityType": "Yes",
      "FightRecapLevel": "1",
      "AbilityCastPoint": "0.0",
      "AbilityChannelTime": "1.75",
      "AbilityManaCost": "50 70 90 110",
      "AbilityValues": {
        "wave_count": {
          "value": "3",
          "special_bonus_unique_drow_ranger_8": "+1"
        },
        "arrow_count_per_wave": "4",
        "arrow_damage_pct": {
          "value": "100 120 140 160",
          "special_bonus_unique_drow_ranger_1": "+25"
        },
        "arrow_width": "90",
        "arrow_speed": "1300",
        "arrow_range_multiplier": "1.75",
        "arrow_angle": "50",
        "bypass_block": "1",
        "AbilityCooldown": {
          "value": "24 21 18 15",
          "special_bonus_unique_drow_ranger_6": "-6"
        },
        "multishot_movespeed": {
          "value": "0",
          "special_bonus_facet_drow_ranger_sidestep": "25"
        }
      },
      "AbilityCastAnimation": "ACT_DOTA_CHANNEL_ABILITY_3",
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_multishot.png"
    },
    "drow_ranger_silence": {
      "AbilityBehavior": [
        "AOE",
        "Point Target"
      ],
      "SpellImmunityType": "No",
      "SpellDispellableType": "Yes",
      "FightRecapLevel": "1",
      "AbilityCastRange": "900",
      "AbilityCastPoint": "0.4 0.4 0.4 0.4",
      "AbilityCooldown": "16 15 14 13",
      "AbilityDuration": "3.0 4.0 5.0 6.0",
      "AbilityDamage": "0 0 0 0",
      "AbilityManaCost": "90 90 90 90",
      "AbilityValues": {
        "silence_radius": "300"
      },
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_silence.png"
    },
    "drow_ranger_wave_of_silence": {
      "AbilityBehavior": "Point Target",
      "SpellImmunityType": "No",
      "SpellDispellableType": "Yes",
      "FightRecapLevel": "1",
      "AbilitySound": "Hero_DrowRanger.Silence",
      "AbilityCastRange": "900",
      "AbilityCastPoint": "0.25",
      "AbilityManaCost": "70",
      "AbilityValues": {
        "wave_speed": "2000.0",
        "wave_width": {
          "value": "250",
          "affected_by_aoe_increase": "1"
        },
        "silence_duration": "3 4 5 6",
        "knockback_distance_max": "450",
        "knockback_duration": "0.6 0.7 0.8 0.9",
        "knockback_height": "0",
        "wave_length": "900",
        "bonus_movespeed": {
          "value": "0",
          "special_bonus_unique_drow_ranger_gust_selfmovespeed": "+50"
        },
        "AbilityCooldown": {
          "value": "19 17 15 13",
          "special_bonus_unique_drow_ranger_7": "-3.5"
        },
        "miss_chance": {
          "value": "0"
        },
        "gust_reveals_invis": {
          "value": "1"
        }
      },
      "AbilityCastAnimation": "ACT_DOTA_CAST_ABILITY_2",
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_wave_of_silence.png"
    },
    "drow_ranger_trueshot": {
      "AbilityBehavior": "Passive",
      "Innate": "1",
      "MaxLevel": "1",
      "IsBreakable": "1",
      "AbilityValues": {
        "trueshot_agi_bonus_self": "2",
        "trueshot_agi_bonus_allies": "1",
        "trueshot_aspd_bonus_creeps": {
          "value": "0",
          "special_bonus_facet_1": "+3"
        },
        "radius": {
          "value": "1200",
          "affected_by_aoe_increase": "1"
        }
      },
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_trueshot.png"
    },
    "drow_ranger_marksmanship": {
      "AbilityBehavior": "Passive",
      "AbilityUnitTargetTeam": "Enemy",
      "AbilityUnitTargetType": [
        "Hero",
        "Basic"
      ],
      "AbilityType": "DOTA_ABILITY_TYPE_ULTIMATE",
      "AbilityCastAnimation": "ACT_DOTA_CAST_ABILITY_4",
      "SpellImmunityType": "Yes",
      "AbilityUnitDamageType": "Physical",
      "AbilityDraftUltShardAbility": "drow_ranger_glacier",
      "IsBreakable": "1",
      "AbilityValues": {
        "chance": {
          "value": "30 35 40",
          "special_bonus_unique_drow_ranger_3": "+10"
        },
        "bonus_damage": "50 70 90",
        "disable_range": "400"
      },
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_marksmanship.png"
    },
    "drow_ranger_glacier": {
      "AbilityBehavior": "No Target",
      "AbilityUnitTargetTeam": "Enemy",
      "AbilityUnitTargetType": [
        "Hero",
        "Basic"
      ],
      "AbilityUnitDamageType": "Magical",
      "SpellImmunityType": "No",
      "FightRecapLevel": "1",
      "IsGrantedByShard": "1",
      "MaxLevel": "1",
      "AbilitySound": "Hero_Tusk.IceShards",
      "AbilityCastRange": "400",
      "AbilityCastPoint": "0.1 0.1 0.1 0.1",
      "AbilityCooldown": "20",
      "AbilityManaCost": "50",
      "AbilityValues": {
        "shard_width": "180",
        "shard_count": "5",
        "shard_speed": "1200.0",
        "shard_duration": "8",
        "shard_angle_step": "40.0",
        "shard_distance": "125",
        "turn_rate_slow": "0",
        "end_height": "128",
        "hilltop_offset": "150",
        "ramp_radius": "150",
        "attack_range_bonus": "200",
        "multishot_arrow_bonus": "1",
        "knockback_duration": "0.1",
        "knockback_distance": "175",
        "knockback_height": "50",
        "z_speed_override": "800"
      },
      "AbilityCastAnimation": "ACT_DOTA_CAST_ABILITY_1",
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_glacier.png"
    },
    "drow_ranger_creep_rally": {
      "AbilityBehavior": [
        "Passive",
        "DOTA_ABILITY_BEHAVIOR_INNATE_UI"
      ],
      "SpellDispellableType": "No",
      "MaxLevel": "1",
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_creep_rally.png"
    },
    "drow_ranger_vantage_point": {
      "AbilityBehavior": [
        "Passive",
        "Hidden"
      ],
      "SpellDispellableType": "No",
      "MaxLevel": "1",
      "IsBreakable": "1",
      "AbilityValues": {
        "damage_bonus": "20",
        "bonus_miss_chance": "0"
      },
      "img": "https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/abilities/drow_ranger_vantage_point.png"
    }
  },
  "hero_name": "npc_dota_hero_drow_ranger",
  "talents": {
    "special_bonus_unique_drow_ranger_1": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    },
    "special_bonus_unique_drow_ranger_2": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    },
    "special_bonus_unique_drow_ranger_3": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    },
    "special_bonus_unique_drow_ranger_6": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    },
    "special_bonus_unique_drow_ranger_7": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    },
    "special_bonus_unique_drow_ranger_8": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    },
    "special_bonus_unique_drow_ranger_gust_selfmovespeed": {
      "AbilityType": "DOTA_ABILITY_TYPE_ATTRIBUTES",
      "AbilityBehavior": "Passive",
      "BaseClass": "special_bonus_base"
    }
  }
}
abilities=heroData.get('abilities')
talents = heroData.get('talents')
ability_name = 'special_bonus_attack_range_75'
print(map_localization_for_talents_recur(ability_name,localization,abilities,talents) )


#print(map_localization_for_ability(ability_name,localization,abilities,talents))
''' 