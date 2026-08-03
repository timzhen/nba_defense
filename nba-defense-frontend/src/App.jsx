import { useState } from 'react'

function App() {
  const [searchName, setSearchName] = useState('')
  const [player, setPlayer] = useState(null)

  const handleSearch = async () => {
    try {
      const response = await fetch(`https://nbadefense-production.up.railway.app/players/${encodeURIComponent(searchName)}`)
      const data = await response.json()
      setPlayer(data)
    } catch (error) {
      console.error('Error fetching player:', error)
    }
  }

  return (
    <div>
      <h1>NBA Defensive Rater</h1>
      <input 
        value={searchName} 
        onChange={(e) => setSearchName(e.target.value)} 
        placeholder="Search a player..."
      />
      <button onClick={handleSearch}>Search</button>

      {player && (
        <div>
          <h2>{player.player_name}</h2>
          <p>Team: {player.team}</p>
          <p>Rim Protection: {player.rim_protection_score}</p>
          <p>Shot Contesting: {player.shot_contesting_score}</p>
          <p>Ball Disruption: {player.ball_disruption_score}</p>
          <p>On-Ball Matchup: {player.on_ball_matchup_def_score}</p>
          <p>Defensive Rebounding: {player.def_reb_score}</p>      
        </div>
      )}
    </div>
  )
}

export default App