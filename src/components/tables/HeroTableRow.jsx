
const HeroTableRow =({hero,heroData})=>{
    const{
        overall_win_rate,
        radiant_win_rate,
        dire_win_rate,
        total_games,
        total_radiant_games,
        total_dire_games
    } = heroData || {};

    return (
        <tr>
        <td>
            <div className='name-container'>
                <img src={hero.image_small} alt={hero.localized_name} />
                <a>{hero.localized_name}</a>
            </div>
        </td>
        <td>
            <span className={overall_win_rate >= 50 ? 'text-green' : 'text-red'}>
                {overall_win_rate ? overall_win_rate.toFixed(2) : '~'}%
            </span>
            <span className="text-grey">({total_games || 0})</span>
        </td>
        <td>
            <span className={radiant_win_rate >= 50 ? 'text-green' : 'text-red'}>
                {radiant_win_rate ? radiant_win_rate.toFixed(2) : '~'}%
            </span>
            <span className="text-grey">({total_radiant_games || 0})</span>
        </td>
        <td>
            <span className={dire_win_rate >= 50 ? 'text-green' : 'text-red'}>
                {dire_win_rate ? dire_win_rate.toFixed(2) : '~'}%
            </span>
            <span className='text-grey'>({total_dire_games || 0})</span>
        </td>
    </tr>
    );
};

export default HeroTableRow;