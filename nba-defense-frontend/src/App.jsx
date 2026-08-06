import { useState, useEffect, useRef } from 'react'
import './App.css'

const API = window.location.hostname === 'localhost'
  ? 'http://127.0.0.1:8000'
  : 'https://nbadefense-production.up.railway.app'

function App() {
  const [searchName, setSearchName] = useState('')
  const [player, setPlayer] = useState(null)
  const [question, setQuestion] = useState('')
  const [explanation, setExplanation] = useState('')
  const [allPlayers, setAllPlayers] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [highlightIndex, setHighlightIndex] = useState(-1)
  const blurTimeoutRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/players`)
      .then((r) => r.json())
      .then(setAllPlayers)
      .catch((error) => console.error('Error fetching players:', error))
  }, [])

  const suggestions = searchName.trim()
    ? allPlayers
        .filter((p) =>
          p.player_name.toLowerCase().startsWith(searchName.trim().toLowerCase())
        )
        .slice(0, 8)
    : []

  const handleSearch = async (name = searchName) => {
    const query = name.trim()
    if (!query) return
    setShowSuggestions(false)
    setHighlightIndex(-1)
    setQuestion('')
    setExplanation('')
    try {
      const response = await fetch(`${API}/players/${encodeURIComponent(query)}`)
      const data = await response.json()
      setPlayer(data)
      console.log(data)
    } catch (error) {
      console.error('Error fetching player:', error)
    }
  }

  const selectPlayer = (name) => {
    setSearchName(name)
    setShowSuggestions(false)
    setHighlightIndex(-1)
    handleSearch(name)
  }

  const handleSearchKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'Enter') handleSearch()
      return
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setHighlightIndex((i) => (i + 1) % suggestions.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setHighlightIndex((i) => (i <= 0 ? suggestions.length - 1 : i - 1))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (highlightIndex >= 0) {
        selectPlayer(suggestions[highlightIndex].player_name)
      } else {
        handleSearch()
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
      setHighlightIndex(-1)
    }
  }

  const handleAskQuestion = async () => {
    try {
      const url = `${API}/players/${encodeURIComponent(searchName)}/explain?question=${encodeURIComponent(question)}`
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
        <h1>NBA Defensive Scouting Report</h1>
        <p>defensive category grades</p>
      </header>

      <div className="search-row">
        <div className="search-input-wrap">
          <input
            value={searchName}
            onChange={(e) => {
              setSearchName(e.target.value)
              setShowSuggestions(true)
              setHighlightIndex(-1)
            }}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => {
              blurTimeoutRef.current = setTimeout(() => {
                setShowSuggestions(false)
                setHighlightIndex(-1)
              }, 150)
            }}
            onKeyDown={handleSearchKeyDown}
            placeholder="Search a player..."
            autoComplete="off"
            role="combobox"
            aria-expanded={showSuggestions && suggestions.length > 0}
            aria-autocomplete="list"
          />
          {showSuggestions && suggestions.length > 0 && (
            <ul className="suggestions" role="listbox">
              {suggestions.map((p, index) => (
                <li
                  key={p.player_id}
                  role="option"
                  aria-selected={index === highlightIndex}
                  className={index === highlightIndex ? 'suggestion-active' : undefined}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => {
                    clearTimeout(blurTimeoutRef.current)
                    selectPlayer(p.player_name)
                  }}
                  onMouseEnter={() => setHighlightIndex(index)}
                >
                  <span className="suggestion-name">{p.player_name}</span>
                  <span className="suggestion-team">{p.team}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <button onClick={() => handleSearch()}>Search</button>
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
