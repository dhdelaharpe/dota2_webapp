import React, {useState, useCallback} from 'react';
import Select from 'react-select';
import Slider from 'react-slider';
import {debounce} from 'lodash';

export const columnOptions = [//used to show/hide columns
   // { value: 'hero', label: 'Hero' },
    { value: 'win rate', label: 'Win Rate' },
    { value: 'radiant win rate', label: 'Radiant Win Rate' },
    { value: 'dire win rate', label: 'Dire Win Rate' },
    {value: 'radiant diff', label:'Radiant diff'},
    {value: 'contest rate', label:'Contest rate'}
];
const HeroTableFilter = ({setFilterValue , maxGames, setVisibleColumns}) => {

    const rankOptions = [ //ranks
        {value: 1, label: "Herald"},
        {value: 2, label: "Guardian"},
        {value: 3, label: "Crusader"},
        {value: 4, label: "Archon"},
        {value: 5, label: "Legend"},
        {value: 6, label: "Ancient"},
        {value: 7, label: "Divine"},
        {value: 8, label: "Immortal"}
    ];
    

    //const [showDropDown, setShowDropDown] = useState(false);
    //const [selectedFilters, setSelectedFilters] = useState([]);
    //filter states 
    //const [rankTier, setRankTier] =useState('');
    const [minPlayed, setMinPlayed]= useState(0);
    const [minWin, setMinWin]= useState(0);
    //const [minPlayedRadiant, setMinPlayedRadiant] = useState(0);
    //const [minWinRadiant, setMinWinRadiant] = useState(0);
    //const [minPlayedDire, setMinPlayedDire] = useState(0);
    //const [minWinDire, setMinWinDire] = useState(0);
    //column control state
    const [selectedColumns, setSelectedColumns] = useState(columnOptions);



    //rudimentary debouncing
    /*
    const useDebounce =(value, delay)=>{
        const [debouncedValue, setDebouncedValue] = useState(value);
        useEffect(()=>{
            const timer =setTimeout(()=>setDebouncedValue(value),delay);
            return ()=>{
                clearTimeout(timer);
            };
        
        }, [value,delay]);
        return debouncedValue;
    }*/

    //use lodash to debounce sliders -> linter warning here seems irrelevant 
    const debouncedUpdatePlayed = useCallback(
        debounce((newMinPlayed)=>{
            setFilterValue(prev=> ({...prev, min_played: newMinPlayed}))
        }, 300),[setFilterValue]
    );

    const debounceUpdateMinWin = useCallback(
        debounce((newMinWin)=>{
            setFilterValue(prev=> ({...prev,min_win:newMinWin}))
        },300),[setFilterValue]
    );

    const handleColumnChange = (selected)=>{
        setSelectedColumns(selected);
        setVisibleColumns(selected.map(opt=>opt.value));
    }
    const handleRankChange = (selectedOption) => {
        const rankValue = selectedOption ? selectedOption.value : '';
        //setRankTier(rankValue);
        setFilterValue(prev => ({ ...prev, avg_rank_tier: rankValue }));
    };
    const handleMinPlayedChange = (value) => {
        setMinPlayed(value);
        //setFilterValue(prev => ({ ...prev, min_played: value }));
        debouncedUpdatePlayed(value);
    };

    const handleMinWinChange = (value) => {
        setMinWin(value);
        //setFilterValue(prev => ({ ...prev, min_win: value }));
        debounceUpdateMinWin(value);
    };

    /*
    const handleMinPlayedRadiantChange = (value) => {
        setMinPlayedRadiant(value);
        setFilterValue(prev => ({ ...prev, min_played_radiant: value }));
    };

    const handleMinWinRadiantChange = (value) => {
        setMinWinRadiant(value);
        setFilterValue(prev => ({ ...prev, min_win_radiant: value }));
    };

    const handleMinPlayedDireChange = (value) => {
        setMinPlayedDire(value);
        setFilterValue(prev => ({ ...prev, min_played_dire: value }));
    };

    const handleMinWinDireChange = (value) => {
        setMinWinDire(value);
        setFilterValue(prev => ({ ...prev, min_win_dire: value }));
    };

    const handleClearFilter= (filterType) =>{
        setSelectedFilters(filters=>filters.filter(filter=>filter.type!== filterType));
        setFilterValue(prev=>({...prev,[filterType]:0}));
    };

    const updateFilters= (type, value)=>{
        setSelectedFilters(filters=>{
            const existing = filters.find(filter=>filter.type===type);
            if(existing){
                return filters.map(filter=> filter.type===type? {...filter,value}:filter);
            }
            return [...filters, {type,value}];
        });
        setFilterValue(prev=>({...prev, [type]:value}));
    };
    */
    const customStyles = { //using for react select element
        container: (provided) => ({
          ...provided,
          width: '100%',
        }),
        control: (provided) => ({
            ...provided,
            backgroundColor: 'var(--background-color)', 
            borderColor: 'var(--border-color)', 
            boxShadow: 'none',
            color: '#aa9f9f',
            fontSize:'var(--font-size)',
            '&:hover': {
              borderColor: 'var(--hover-border-color)', 
            },    
          }),
          indicatorSeparator: (provided) =>({
            ...provided,
            display:'none',
          }),
          value: (provided) => ({
            ...provided,
            color: '#aa9f9f',
            fontSize:'calc(8px + 1vmin)',
          }),
          singleValue: (provided) => ({
            ...provided,
            color: '#aa9f9f',
            fontSize:'calc(8px + 1vmin)',
            
          }),
          multiValue: (provided) => ({
            ...provided,
            backgroundColor: 'var(--background-color)',
            borderRadius: '4px',
            border: '1px solid grey', 
            fontSize:'calc(8px + 1vmin)',
          }),
          multiValueLabel: (provided) => ({
            ...provided,
            color: '#aa9f9f',
            fontSize:'var(--font-size)',
          }),
          multiValueRemove: (provided) => ({
            ...provided,
            color: '#aa9f9f',
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
          }),
          menuList: (provided) => ({
            ...provided,
            backgroundColor: 'black',
            fontSize:'calc(8px + 1vmin)',
          }),
          option: (provided, state) => ({
            ...provided,
            backgroundColor: state.isSelected ? 'var(--selected-background-color)' : 'var(--background-color)',
            color: state.isSelected ? 'var(--selected-text-color)' : '#aa9f9f',
            ':hover': {
              backgroundColor: 'grey',
              color: 'var(--hover-text-color)',
            },
            fontSize:'calc(8px + 1vmin)',
          }),
        
      };
      
    return (
        <div className='filter-container'>    
            <div className='filter-group'>
                <Select className='react-select' options={rankOptions} onChange={handleRankChange} placeholder="Select rank" isClearable styles={customStyles}/>
            
                <label>
                    Minimum games
                    <Slider value={minPlayed} onChange={handleMinPlayedChange} thumbClassName="slider-thumb" trackClassName="slider-track" activeTrackClassName="slider-track-active" min={0} max={maxGames} step={10}/>
                    <div>{minPlayed}</div>
                </label>
            
                <label>
                    Minimum win rate
                    <Slider value={minWin} onChange={handleMinWinChange} thumbClassName="slider-thumb" trackClassName="slider-track" activeTrackClassName="slider-track-active" min={0} max={100} step={1}/>
                    <div>{minWin}%</div>
                </label>
            </div>
        
            <div className='filter-group'>
                <Select className='react-select'
                    options={columnOptions}
                    onChange={handleColumnChange}
                    value={selectedColumns}
                    isMulti
                    closeMenuOnSelect={true}
                    isClearable={false} 
                    placeholder="Select columns"
                    styles={customStyles}
                    />
            </div>
        </div>
    );
};

export default HeroTableFilter;
