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
  const [leaderboard, setLeaderboard] = useState([])
  const [searchError, setSearchError] = useState('')
  const [allPlayers, setAllPlayers] = useState([])
  const [activeTab, setActiveTab] = useState('search')
  const [teams, setTeams] = useState([])
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [roster, setRoster] = useState([])
  const [selectedPlayer, setSelectedPlayer] = useState(null)
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
    setSearchError('')
    try {
      const response = await fetch(`${API}/players/${encodeURIComponent(query)}`)
      const data = await response.json()
      if (data.error) {
        setSearchError(`No player found for "${query}"`)
        return
      }
      setPlayer(data)
    } catch (error) {
      console.error('Error fetching player:', error)
    }
  }

  const goHome = () => {
    setPlayer(null)
    setSearchName('')
    setQuestion('')
    setExplanation('')
    setSearchError('')
    setShowSuggestions(false)
    setHighlightIndex(-1)
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

  const handleAskQuestion = async (name) => {
    try {
      const url = `${API}/players/${encodeURIComponent(name)}/explain?question=${encodeURIComponent(question)}`
      const response = await fetch(url)
      const data = await response.json()
      setExplanation(data.answer)
    } catch (error) {
      console.error('Error fetching explanation:', error)
    }
  }

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${API}/dpoy-leaderboard`)
      const data = await response.json()
      setLeaderboard(data)
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    }
  }

  const fetchTeams = async () => {
    try {
      const response = await fetch(`${API}/teams`)
      const data = await response.json()
      setTeams(data)
    } catch (error) {
      console.error('Error fetching teams:', error)
    }
  }

  const handleSelectTeam = async (teamAbbr) => {
    try {
      const response = await fetch(`${API}/teams/${teamAbbr}/roster`)
      const data = await response.json()
      setRoster(data)
      setSelectedTeam(teamAbbr)
      setSelectedPlayer(null)
      setQuestion('')
      setExplanation('')
    } catch (error) {
      console.error('Error fetching roster:', error)
    }
  }

  const handleSelectRosterPlayer = (p) => {
    setSelectedPlayer(p)
    setQuestion('')
    setExplanation('')
  }

  const backToTeams = () => {
    setSelectedTeam(null)
    setRoster([])
    setSelectedPlayer(null)
    setQuestion('')
    setExplanation('')
  }

  const backToRoster = () => {
    setSelectedPlayer(null)
    setQuestion('')
    setExplanation('')
  }

  useEffect(() => {
    fetchLeaderboard()
    fetchTeams()
  }, [])

  const buildStats = (p) =>
    p
      ? [
          { label: 'Rim Protection', value: p.rim_protection_score, percentile: p.rim_protection_percentile, badge: p.rim_protection_label },
          { label: 'Shot Contesting', value: p.shot_contesting_score, percentile: p.shot_contesting_percentile, badge: p.shot_contesting_label },
          { label: 'Ball Disruption', value: p.ball_disruption_score, percentile: p.ball_disruption_percentile, badge: p.ball_disruption_label },
          { label: 'On-Ball Matchup', value: p.on_ball_matchup_def_score, percentile: p.on_ball_matchup_def_percentile, badge: p.on_ball_matchup_def_label },
          { label: 'Defensive Rebounding', value: p.def_reb_score, percentile: p.def_reb_percentile, badge: p.def_reb_label },
        ]
      : []

  const renderPlayerCard = (p) => (
    <div className="player-card">
      <h2>{p.player_name}</h2>
      <img
        key={p.player_id}
        src={`https://cdn.nba.com/headshots/nba/latest/1040x760/${p.player_id}.png`}
        alt={p.player_name}
        className="player-headshot"
        onError={(e) => { e.target.style.display = 'none' }}
      />
      <p className="player-team">Team: {p.team}</p>

      <div className="stat-sheet">
        {buildStats(p).map((stat) => (
          <div className="stat-row" key={stat.label}>
            <span className="stat-label">{stat.label}</span>
            <div className="stat-bar-track">
              <div className="stat-bar-fill" style={{ width: `${stat.percentile ?? 0}%` }} />
            </div>
            <span className="stat-badge">{stat.badge ?? 'N/A'}</span>
            <span className="stat-value">
              {stat.percentile == null ? 'N/A' : `${stat.percentile}th percentile`}
            </span>
          </div>
        ))}
      </div>

      <div className="ask-section">
        <h3 className="ask-section-title">Ask about this player</h3>
        <div className="ask-row">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleAskQuestion(p.player_name) }}
            placeholder="Ask a question about this player..."
          />
          <button onClick={() => handleAskQuestion(p.player_name)}>Ask</button>
        </div>

        {explanation && (
          <p className="explanation">{explanation}</p>
        )}
      </div>
    </div>
  )

  return (
    <div className="app">
      <header className="app-header">
        <h1>NBA Defensive Scouting Report</h1>
        <p>defensive category ratings</p>
      </header>

      <div className="tab-nav">
        <button
          className={activeTab === 'search' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('search')}
        >
          Search Player
        </button>
        <button
          className={activeTab === 'teams' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('teams')}
        >
          Team Browser
        </button>
        <button
          className={activeTab === 'leaderboard' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('leaderboard')}
        >
          DPOY Leaderboard
        </button>
      </div>

      {activeTab === 'search' && (
        <>
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

      {searchError && <p className="search-error">{searchError}</p>}

      {player && (
        <>
        <button className="back-button" onClick={goHome}>← New search</button>
        {renderPlayerCard(player)}
        </>
      )}
        </>
      )}

      {activeTab === 'teams' && (
        <div className="teams-section">
          {!selectedTeam && (
            <div className="teams-grid">
              {teams.map((team) => (
                <button
                  key={team.TEAM_ABBREVIATION}
                  className="team-button"
                  onClick={() => handleSelectTeam(team.TEAM_ABBREVIATION)}
                >
                  <img
                    src={`https://cdn.nba.com/logos/nba/${team.TEAM_ID}/global/L/logo.svg`}
                    alt={team.team_name}
                    className="team-logo"
                    onError={(e) => { e.target.style.display = 'none' }}
                  />
                  {team.team_name}
                </button>
              ))}
            </div>
          )}

          {selectedTeam && !selectedPlayer && (
            <>
              <button className="back-button" onClick={backToTeams}>← All teams</button>
              <h2 className="roster-title">
                {teams.find((t) => t.TEAM_ABBREVIATION === selectedTeam)?.team_name ?? selectedTeam}
              </h2>
              <div className="roster-list">
                {roster.map((p) => (
                  <div
                    className="roster-row"
                    key={p.player_id}
                    onClick={() => handleSelectRosterPlayer(p)}
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="roster-name">{p.player_name}</span>
                    <span className="roster-score">Rim: {p.rim_protection_score}</span>
                    <span className="roster-score">Disruption: {p.ball_disruption_score}</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {selectedPlayer && (
            <>
              <button className="back-button" onClick={backToRoster}>
                ← Back to {teams.find((t) => t.TEAM_ABBREVIATION === selectedTeam)?.team_name ?? 'roster'}
              </button>
              {renderPlayerCard(selectedPlayer)}
            </>
          )}
        </div>
      )}

      {activeTab === 'leaderboard' && (
        <>
        <div className="leaderboard-card">
          <h2 className="leaderboard-title">2025-26 DPOY Predictor</h2>
          <p className="leaderboard-subtitle">Defensive signal strength, based on category scores validated against real historical DPOY voting — reflects statistical similarity to past award recipients, not a literal probability</p>
          {leaderboard.map((entry, index) => (
            <div className="leaderboard-row" key={entry.player_id}>
              <span className="leaderboard-rank">{index + 1}</span>
              <span className="leaderboard-name">{entry.player_name}</span>
              <span className="leaderboard-team">{entry.team}</span>
              <span className="leaderboard-prob">{entry.dpoy_probability}%</span>
            </div>
          ))}
        </div>
        </>
      )}
    </div>
  )
}

export default App
