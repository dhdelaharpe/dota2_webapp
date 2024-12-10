
import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import {useState} from 'react';

//components
import HeroSelect from './components/HeroSelect';
import ChartContainerRadiant from './components/charts/ChartContainerRadiant';
import ChartContainerHero from './components/charts/ChartContainerHero';
import Navbar from './components/nav/Navbar';
import Tables from './components/tables/Tables';
import HeroOverview from './components/heroView/HeroOverview';
import GraphQLTables from './components/tables/GraphQLTables';
import HeroInfo from './components/heroView/HeroInfo';

import { HeroesProvider } from './components/heroView/HeroesContext';
function App() {
  const [selectedHero, setSelectedHero] = useState(null);
  const [totalGames, setTotalGames]= useState(null);
  return (
    <>
      <Router>
          <div className='app'>
            <header>
              <h1>DOTA2 Stats</h1>
              <Navbar />
            </header>
            <div className='inner'>
            <HeroesProvider>
              <Routes>
                <Route path='/' element={
              <div className='chart'>
              
                <div className='page-header'>
                  <div>
                    <h1 id='page-header-title'>Win rate charts</h1>
                    <p id='page-header-description'>Based on {totalGames? `${totalGames} games`:'....'}</p>
                    
                  </div>
                </div>
                <HeroSelect onSelectHero={setSelectedHero}/>
                {selectedHero?(<ChartContainerHero heroId={selectedHero.hero_id} setTotalGames={setTotalGames}/>):(<ChartContainerRadiant setTotalGames={setTotalGames}/>)}
                
              </div>
                }/>
              <Route path="/tables" element={<Tables/>}/>
              <Route path="/tablesGQL" element={<GraphQLTables/>}/>
              
              <Route path="/heroOverview" element={<HeroOverview/>}/>
              <Route path="/hero/:heroId" element={<HeroInfo/>}/>
              
              
              </Routes>
              </HeroesProvider>
            </div>
          </div>
          </Router>
    </>
  )
}

export default App
