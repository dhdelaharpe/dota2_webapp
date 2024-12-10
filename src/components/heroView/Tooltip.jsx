import React, { useState } from 'react';

const Tooltip = ({ content, children ,ability}) => {
  const [isHovered, setIsHovered] = useState(false);

  if(ability){ //create custom layout for abilities 
    const behaviors = Array.isArray(ability.AbilityBehavior)
                            ? ability.AbilityBehavior
                            : [ability.AbilityBehavior];
    
    
    //const abilityValues = ability.AbilityValues && typeof ability.AbilityValues === 'object' ? ability.AbilityValues : {};
    
    
    //console.log(ability)
    //console.log(ability.tooltip)
    //  <h6>{(valid_damage_key)?`Damage: ${ability.AbilityValues[damage_key].value?ability.AbilityValues[damage_key].value: ability.AbilityValues[damage_key]}`:''}</h6>
    return(
        <div 
        onMouseEnter={()=>setIsHovered(true)}
        onMouseLeave={()=>setIsHovered(false)}
        >
            {children}
            {isHovered &&(
                <div className='tooltip-ability'>
                    <div className='tooltip-ability-title' >
                        <h6>{ability.tooltip.name}</h6>
                        
                    </div>
                    <div className='tooltip-ability-description'>
                        {ability.IsGrantedByShard==='1' &&
                            <h6>Granted by Shard</h6>
                        }
                        <h6>{ability.tooltip.description}</h6>
                        
                    </div>
                    <div className='tooltip-ability-data'>
                        <h6>Ability: {behaviors.join('/')}</h6> 
                        {(behaviors.some((b)=>'Unit Target'===b))
                        ? <h6>Affects: {ability.AbilityUnitTargetTeam} {Array.isArray(ability?.AbilityUnitTargetType)?' Units':'Heroes'}</h6>
                        :''
                        }
                        <h6>{ability.SpellImmunityType?`Pierces Spell Immunity: ${ability.SpellImmunityType}`: ''}</h6>
                      

                    </div>
                    <div className='tooltip-ability-data2'>
                      {Object.keys(ability.tooltip).map(entry=>{
                        if(entry==='name' || entry==='description' || entry==='lore' || entry.startsWith('dota_tooltip')|| entry.startsWith('facet')){
                          return null;
                        }
                        
                        if(entry==='shard_description' || entry.startsWith('note') || entry==='scepter_description'){
                          return (
                            <div key={entry} className='tooltip-data'>
                              <h6>{entry.toUpperCase()}: {ability.tooltip[entry]}</h6>
                            </div>
                          )  
                        }
                        
                        
                        const add_perc = ability.tooltip[entry].startsWith('%') 
                        return (
                          <div key={entry} className='tooltip-data'>
                            <h6>
                              {add_perc? ability.tooltip[entry].slice(1,ability.tooltip[entry].length): ability.tooltip[entry]} {typeof(ability.AbilityValues[entry])==='object'? ability.AbilityValues[entry].value : ability.AbilityValues[entry]} {add_perc? '%':''}
                            </h6>
                            
                          </div>
                        );
                      })}    
                    </div>

                </div>
            )}
        </div>
    )
  }
  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ display: 'inline-block', position: 'relative' }}
    >
      {children}
      {isHovered && (
        <div
          className="tooltip"
          
          dangerouslySetInnerHTML={{ __html: content }} // Use dangerouslySetInnerHTML for HTML rendering
        />
      )}
    </div>
  );
};
export default Tooltip;