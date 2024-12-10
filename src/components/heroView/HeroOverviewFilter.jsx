import React, {useState, useEffect} from 'react';
import Select from 'react-select';
import makeAnimted, { Input } from 'react-select/animated';

export const columnOptions=[
  {value:'AGILITY', label:"Agility", icon:'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/icons/hero_agility.png'},
  {value:'STRENGTH',label:'Strength', icon:'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/icons/hero_strength.png'},
  {value:'INTELLIGENCE',label:'Intelligence', icon:'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/icons/hero_intelligence.png'},
  {value:'UNIVERSAL', label:'Universal',icon:'https://cdn.akamai.steamstatic.com/apps/dota2/images/dota_react/icons/hero_universal.png'}
];
const HeroOverviewFilter=({selectedAttributes, toggleAttributes,selectedRoles, toggleRoles, roleOptions, handleNameFilter})=>{
    
    const animatedComponents = makeAnimted();
    
    
    const handleTextChange=(event)=>{
        handleNameFilter(event.target.value);
    }
    
    const customStyles = { //using for react select element
        container: (provided) => ({
          ...provided,
          width:'40%',
          margin:'8px',
          
          
        }),
        control: (provided) => ({
            ...provided,
            backgroundColor: 'var(--background-color)', 
            borderColor: 'var(--border-color)', 
            boxShadow: 'none',
            color: '#d9caca',
            fontSize:'var(--font-size)',
            '&:hover': {
              borderColor: 'var(--hover-border-color)', 
              
            },    
          }),
          input:(provided)=>({
            ...provided,
            color:'#d9caca',
          }),
          indicatorSeparator: (provided) =>({
            ...provided,
            display:'none',
          }),
          value: (provided) => ({
            ...provided,
            color: '#d9caca',
            fontSize:'calc(8px + 1vmin)',
          }),
          singleValue: (provided) => ({
            ...provided,
            color: '#d9caca',
            fontSize:'calc(8px + 1vmin)',
            
          }),
          multiValue: (provided) => ({
            ...provided,
            backgroundColor: 'var(--background-color)',
            borderRadius: '4px',
            border: '1px solid grey', 
            fontSize:'calc(8px + 1vmin)',
            color:'#d9caca',
          }),
          multiValueLabel: (provided) => ({
            ...provided,
            color: '#d9caca',
            fontSize:'var(--font-size)',
          }),
          multiValueRemove: (provided) => ({
            ...provided,
            color: '#d9caca',
            ':hover': {
              backgroundColor: 'grey', // Change color on hover
              color: 'var(--hover-text-color)', 
            },
          }),
          menu: (provided) => ({
            ...provided,
            backgroundColor: 'var(--background-color)',
            borderColor: 'var(--border-color)',
            fontSize:'calc(8px + 1vmin)',
            color:'#d9caca',
            zIndex:10,
          }),
          menuList: (provided) => ({
            ...provided,
            backgroundColor: 'black',
            fontSize:'calc(8px + 1vmin)',
            color:'#d9caca',
          }),
          option: (provided, state) => ({
            ...provided,
            backgroundColor: state.isSelected ? 'var(--selected-background-color)' : 'var(--background-color)',
            color: state.isSelected ? 'var(--selected-text-color)' : '#d9caca',
            ':hover': {
              backgroundColor: 'grey',
              color: 'var(--hover-text-color)',
            },
            fontSize:'calc(8px + 1vmin)',
          }),
        
      };
    return(
        <div className='hero-overview-filter-group'>
            <div style={{flexDirection:'row', display:'flex', width:'100%', alignItems:'center', justifyContent:'center'}}> 
            {columnOptions.map(opt=>(
                <div key={opt.value} className={`attribute-icon ${selectedAttributes.includes(opt.value)?'selected':'unselected'}`} onClick={()=>toggleAttributes(opt.value)} style={{cursor:'pointer'}} >
                    <img src={opt.icon} alt={opt.label}/>
                </div>
            ))}
            <Select
            options={roleOptions}
            components={animatedComponents}
            value={selectedRoles}
            isMulti={true}
            styles={customStyles}
            onChange={toggleRoles}
            
            />
            </div>
            <input className='text-filter'type='text' placeholder='Search by name ...' onChange={handleTextChange} />
        </div>
    );
};

export default HeroOverviewFilter;