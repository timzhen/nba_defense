import { useState } from 'react'
import './App.css'

function App() {
  const [searchName, setSearchName] = useState('')
  const [player, setPlayer] = useState(null)
  const [question, setQuestion] = useState('')
  const [explanation, setExplanation] = useState('')

  const handleSearch = async () => {
    try {
      const response = await fetch(`https://nbadefense-production.up.railway.app/players/${encodeURIComponent(searchName)}`)
      const data = await response.json()
      setPlayer(data)
      console.log(data)
    } catch (error) {
      console.error('Error fetching player:', error)
    }
  }

  const handleAskQuestion = async () => {
    try {
      const url = `https://nbadefense-production.up.railway.app/players/${encodeURIComponent(searchName)}/explain?question=${encodeURIComponent(question)}`
      const response = await fetch(url)
      const data = await response.json()
      setExplanation(data.answer)
    } catch (error) {
      console.error('Error fetching explanation:', error)
    }
  }

  const stats = player
    ? [
        { label: 'Rim Protection', value: player.rim_protection_score, percentile: player.rim_protection_percentile, badge: player.rim_protection_label },
        { label: 'Shot Contesting', value: player.shot_contesting_score, percentile: player.shot_contesting_percentile, badge: player.shot_contesting_label },
        { label: 'Ball Disruption', value: player.ball_disruption_score, percentile: player.ball_disruption_percentile, badge: player.ball_disruption_label },
        { label: 'On-Ball Matchup', value: player.on_ball_matchup_def_score, percentile: player.on_ball_matchup_def_percentile, badge: player.on_ball_matchup_def_label },
        { label: 'Defensive Rebounding', value: player.def_reb_score, percentile: player.def_reb_percentile, badge: player.def_reb_label },
      ]
    : []

  return (
    <div className="app">
      <header className="app-header">
        <h1>NBA Defensive Rater</h1>
        <p>Scouting report · defensive category grades</p>
      </header>

      <div className="search-row">
        <input
          value={searchName}
          onChange={(e) => setSearchName(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSearch() }}
          placeholder="Search a player..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {player && (
        <div className="player-card">
          <h2>{player.player_name}</h2>
          <img
            key={player.player_id}
            src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${player.player_id}.png`}
            alt={player.player_name}
            className="player-headshot"
            onError={(e) => { e.target.style.display = 'none' }}
          />
          <p className="player-team">Team: {player.team}</p>

          <div className="stat-sheet">
            {stats.map((stat) => (
              <div className="stat-row" key={stat.label}>
                <span className="stat-label">{stat.label}</span>
                <div className="stat-bar-track">
                  <div className="stat-bar-fill" style={{ width: `${stat.percentile}%` }} />
                </div>
                <span className="stat-badge">{stat.badge}</span>
                <span className="stat-value">{stat.percentile}th</span>
              </div>
            ))}
          </div>

          <div className="ask-section">
            <h3 className="ask-section-title">Ask about this player</h3>
            <div className="ask-row">
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleAskQuestion() }}
                placeholder="Ask a question about this player..."
              />
              <button onClick={handleAskQuestion}>Ask</button>
            </div>

            {explanation && (
              <p className="explanation">{explanation}</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
