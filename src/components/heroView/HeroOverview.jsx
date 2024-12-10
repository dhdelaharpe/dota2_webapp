import React, {useEffect,useState} from 'react';
import { useNavigate } from 'react-router-dom';

import HeroOverviewFilter from './HeroOverviewFilter';
import HeroOverviewGrid from './HeroOverviewGrid';
import {useHeroes} from './HeroesContext';


export const fetchHeroes = async()=>{
    const response = await fetch('/api/graphql',{
        method:'POST',
        headers:{
            'Content-Type':'application/json'
        },
        body: JSON.stringify(
            {
                query:`
                {
                    allHeroes{
                        heroId
                        imgSmall
                        imgFull
                        animated
                        localizedName
                        facets
                        roles
                        roleLevels
                        attribute
                        aliases
                        similar
                        description
                        name
                        abilities
                        talents
                    }
                }`
            })
    });
    const dataRes = await response.json();
    const data = dataRes.data.allHeroes;
    return data;
};

const HeroOverview = ()=>{
    const {heroes, setHeroes} = useHeroes();
    const navigate = useNavigate();
    const [selectedAttributes, setSelectedAttributes] = useState([]);
    const [selectedRoles, setSelectedRoles] = useState([]);
    const [nameFilter, setNameFilter] = useState('');
    useEffect(()=>{
        const getHeroes= async () =>{
            const data= await fetchHeroes();
            setHeroes(data);
        }
      getHeroes();  
    },[setHeroes]);

    const handleOnClick=(heroId)=>{
        navigate(`/hero/${heroId}`);
    };
    const toggleAttributes = (value)=>{
        setSelectedAttributes((prev)=>
        prev.includes(value)? prev.filter((filter)=>filter!==value): [...prev, value]);
    };
    const toggleRoles = (value)=>{
        setSelectedRoles(value||[]);
    }

    const handleNameFilter=(text)=>{
        setNameFilter(text);
    }
    const roleOptions = [...new Set(heroes.flatMap(hero=>hero.roles))].map(role=>{
        return {value:role, label:role}
    });
    const filtered = heroes.filter((hero)=>{
        const attributeMatch = selectedAttributes.length? selectedAttributes.includes(hero.attribute):true;
        const roleMatch = selectedRoles.length? selectedRoles.every((selectedRole)=>hero.roles.includes(selectedRole.value)):true;
        const nameMatch = nameFilter.length? (hero.localizedName.toLowerCase().includes(nameFilter.toLowerCase())|| (hero.aliases.some((alias)=> alias.includes(nameFilter.toLowerCase())))):true;
        return attributeMatch && roleMatch && nameMatch;

    })

    return(
        <div className='hero-overview'>
            <HeroOverviewFilter roleOptions={roleOptions} selectedAttributes={selectedAttributes} toggleAttributes={toggleAttributes} selectedRoles={selectedRoles} toggleRoles={toggleRoles} handleNameFilter={handleNameFilter}/>
            <HeroOverviewGrid heroes={filtered} handleOnClick={handleOnClick}/>
        </div>
        
    );
};


export default HeroOverview;