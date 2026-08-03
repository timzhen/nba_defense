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

  const categoryScores = player
    ? [
        { label: 'Rim Protection', score: player.rim_protection_score },
        { label: 'Shot Contesting', score: player.shot_contesting_score },
        { label: 'Ball Disruption', score: player.ball_disruption_score },
        { label: 'On-Ball Matchup', score: player.on_ball_matchup_def_score },
        { label: 'Defensive Rebounding', score: player.def_reb_score },
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
            {categoryScores.map(({ label, score }) => (
              <div className="stat-row" key={label}>
                <span className="stat-label">{label}</span>
                <div className="stat-bar-track">
                  <div
                    className="stat-bar-fill"
                    style={{ width: `${Math.min(100, Math.max(0, Number(score) || 0))}%` }}
                  />
                </div>
                <span className="stat-value">{score}</span>
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
