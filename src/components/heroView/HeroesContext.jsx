import  {createContext, useState, useContext} from 'react';

const HeroesContext = createContext();//not really needed for this but using context for the sake of it


export const HeroesProvider=({children})=>{
    const [heroes,setHeroes] = useState([]);
    console.log('provider mounted with: ', heroes)
    return(
        <HeroesContext.Provider value={{heroes,setHeroes}}>
            {children}
        </HeroesContext.Provider>
    );
};
export const useHeroes=()=>{
    return useContext(HeroesContext);
};