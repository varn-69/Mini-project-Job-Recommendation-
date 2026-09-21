import React, { useState } from 'react'
import ProfileForm from './components/ProfileForm'
import RecommendationResults from './components/RecommendationResults'
import './App.css'

function App() {
  const [recommendations, setRecommendations] = useState(null)
  const [candidateName, setCandidateName] = useState('')

  const handleRecommendations = (data) => {
    setRecommendations(data.recommendations)
    setCandidateName(data.candidate_name)
  }

  const handleBack = () => {
    setRecommendations(null)
    setCandidateName('')
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Job Recommendation System</h1>
        <p className="subtitle">Find your perfect job match using ML-powered recommendations</p>
      </header>

      <main className="app-main">
        {!recommendations ? (
          <ProfileForm onRecommendations={handleRecommendations} />
        ) : (
          <RecommendationResults
            recommendations={recommendations}
            candidateName={candidateName}
            onBack={handleBack}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>College Mini Project | 5th Semester</p>
      </footer>
    </div>
  )
}

export default App
