import {useState,useEffect} from 'react';

function HeroSelect({onSelectHero}){
    const [heroes, setHeroes]=useState([]);

    useEffect(()=>{

        const fetchHeroes=async ()=>{
            try{
                const response= await fetch('/api/populate_hero_list');
                if(!response.ok){
                    throw new Error(`HTTP error status ${response.status}`);
                }
                const data = await response.json();
                setHeroes(data)
            }catch(error){
                console.error('Error populating hero list',error);
            }
        }
        fetchHeroes()
    }, []);

    const handleChange=(event)=>{
        const selectedHero = heroes.find(hero=>hero.hero_id===parseInt(event.target.value));
        onSelectHero(selectedHero);
    };
    
    return(
        <div className='select-hero'>
            <label htmlFor='select-hero'>Select Hero to view</label>
            <select name="select-hero" id="select-hero" onChange={handleChange} defaultValue="" >
                <option value="All" >Radiant</option>
                {heroes.map(hero=>(
                    <option key={hero.hero_id} value={hero.hero_id}>{hero.localized_name}</option>
                ))}
            </select>
        </div>
    );
}

export default HeroSelect;