
import './Navbar.css'
import { NavLink } from 'react-router-dom';

const Navbar=()=>{
    return(
        <nav className="navbar" role="navigation">
            <NavLink to="/" className={({isActive})=>isActive?'active':''}>Charts</NavLink>
            <NavLink to="/tables" className={({isActive})=>isActive?'active':''}>Tables</NavLink>
            <NavLink to="/tablesGQL" className={({isActive})=>isActive?'active':''}>TablesGQL</NavLink>
            <NavLink to="/heroOverview" className={({isActive})=>isActive?'active':''}>Heroes</NavLink>
            
        </nav>
    );
};

export default Navbar;