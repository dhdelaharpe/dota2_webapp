import React from 'react';
import './HeroOverview.css';
const HeroOverviewGrid=({heroes, handleOnClick})=>{
    
  
    return(
        <div className='hero-card-container'>
        {heroes.map(hero=>(
            <div
                key={hero.heroId}
                className='hero-card'
                onClick={()=>handleOnClick(hero.heroId)} 
            >
                <img src={hero.imgFull} alt={hero.localizedName} width='280' height='140' />
                <div className='name-container'> 
                    <h3>{hero.localizedName}</h3>
                    <div className='role-container'>
                    {hero.roles.map((role, index)=>(
                    <div key={index} className='role'>    
                        <div className='role-name'>{role}</div>
                        <div className='role-bar' style={{width: `${65*((hero.roleLevels[index])/3).toFixed(2)}%`}}> 

                        </div>
                    </div>
                    ))}
                    </div>
                </div>
            </div>
        ))}
        </div>
    );
};

export default HeroOverviewGrid;