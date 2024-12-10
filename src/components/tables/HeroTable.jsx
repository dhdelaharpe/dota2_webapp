import {useMemo} from 'react';
import {useTable, useSortBy} from 'react-table';

const HeroTable = ({data, filterValue, visibleColumns,totalGames})=>{ //map data into table
    
    const columns = useMemo(()=>{
   
        const columns= [//declare table entries
            {
                Header: 'Hero',
                accessor: 'hero.localized_name',
                Cell:({row})=>(
                    <div className='name-container'>
                        <img src={row.original.hero.img_small} alt={row.original.hero.localized_name}/>
                        <span>{row.original.hero.localized_name}</span>
                    </div>
                )
            },
            {
                Header: 'Win rate',
                accessor: 'heroData.overall_win_rate',
                Cell:({value,row})=>(
                    <>
                        <span className={value >= 50 ? 'text-green' : 'text-red'}>
                            {value ? value.toFixed(2) : '~'}%
                        </span>
                        <span className="text-grey">({row.original.heroData.total_games || 0})</span>
                    </>
                )
            },
            {
                Header: 'Radiant win rate',
                accessor: 'heroData.radiant_win_rate',
                Cell:({value,row})=>(
                    <>
                        <span className={value >= 50 ? 'text-green' : 'text-red'}>
                            {value ? value.toFixed(2) : '~'}%
                        </span>
                        <span className="text-grey">({row.original.heroData.total_radiant_games || 0})</span>
                    </>
                )
            },
            {
                Header: 'Dire win rate',
                accessor: 'heroData.dire_win_rate',
                Cell:({value,row})=>(
                    <>
                        <span className={value >= 50 ? 'text-green' : 'text-red'}>
                            {value ? value.toFixed(2) : '~'}%
                        </span>
                        <span className="text-grey">({row.original.heroData.total_dire_games || 0})</span>
                    </>
                )
            },
            {
                Header: 'Radiant diff',
                accessor:'heroData.radiant_diff',
                Cell:({row})=>{
                    const rad = row.original.heroData.radiant_win_rate||0;
                    const dire = row.original.heroData.dire_win_rate ||0;
                    const diff = rad-dire;
                    return(<>
                        <span className={diff>0?'text-green': diff<0?'text-red': 'text-grey'}>{diff.toFixed(2)}%</span>
                    </>
                    );
                },
                sortType: (a, b)=>{ //define custom sort as not working as default for some reason? Would think useSortBy would work perhaps due to dynamic nature of this column
                    const diff = ((a.original.heroData.radiant_win_rate||0) - (a.original.heroData.dire_win_rate||0)) - ((b.original.heroData.radiant_win_rate||0) - (b.original.heroData.dire_win_rate||0));
                    return diff
                }
            },
            {
                Header:'Contest rate',
                accessor:'heroData.total_contested',
                Cell:({value})=>{
                    const contest_rate = value /totalGames*100;
                    return(<>
                        <span className='text-grey'>{(contest_rate).toFixed(2)}%</span>
                    </>
                    );
                },
                tip:'% games picked or banned'
            }
        ];
    
    return [columns.find(col=>col.Header==='Hero'), ...columns.filter(col=>visibleColumns.includes(col.Header.toLowerCase()))];
    },[visibleColumns,totalGames]);
    //filter data according to filterValue -- this exists to remove entries when games played gets too low (considered adding win rate too but naturally these get to NAN values at the same time)
    const filteredData = useMemo(() => {
        return data.filter(({ heroData }) => {
            const { total_games, total_radiant_games, total_dire_games } = heroData;
            
            return (
                total_games >= filterValue.min_played &&
                total_dire_games >= filterValue.min_played_dire &&
                total_radiant_games>=filterValue.min_played_radiant 
            );
        });
    }, [data, filterValue]);
    
    const {getTableProps, getTableBodyProps, headerGroups, rows, prepareRow}= useTable({columns,data:filteredData},useSortBy);

    
    return (
        <table {...getTableProps()}>
            <thead>
            {headerGroups.map(headerGroup => {
                const { key: headerGroupKey, ...headerGroupProps } = headerGroup.getHeaderGroupProps();
                return (
                    <tr key={headerGroupKey} {...headerGroupProps}>
                        {headerGroup.headers.map((column, index) => {
                            const { key: columnKey, ...columnProps } = column.getHeaderProps(column.getSortByToggleProps({title:column.tip||''}));
                            return (
                                <th key={columnKey} {...columnProps}>
                                    {column.render('Header')}

                                    <span style={{cursor:'pointer'}} title={column.isSorted?(column.isSortedDesc?'Switch to ascending':'Switch to descending'):'click to sort'}>
                                        {column.isSorted ? (column.isSortedDesc ? '↑' : '↓') : '↕'}
                                    </span>
                                </th>
                            );
                        })}
                    </tr>
                
                );
            })}
            </thead>
            <tbody {...getTableBodyProps()}>
                {rows.map(row => {
                    prepareRow(row);
                    const {key, ...rest} = row.getRowProps(); // Handle key separately
                    return (
                        <tr key={key} {...rest}>
                            {row.cells.map(cell => {
                                const {key: cellKey, ...cellRest} = cell.getCellProps(); // Handle cell key separately
                                return (
                                    <td key={cellKey} {...cellRest}>
                                        {cell.render('Cell')}
                                    </td>
                                );
                            })}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};

export default HeroTable;