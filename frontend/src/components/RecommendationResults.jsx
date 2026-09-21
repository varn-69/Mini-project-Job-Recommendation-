import React, { useState } from 'react'
import axios from 'axios'
import JobCard from './JobCard'
import JobDetails from './JobDetails'
import './RecommendationResults.css'

const RecommendationResults = ({ recommendations, candidateName, onBack }) => {
  const [selectedJob, setSelectedJob] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleJobSelect = (job) => {
    setSelectedJob(job)
  }

  const handleBack = () => {
    setSelectedJob(null)
  }

  const handleExplain = async (job) => {
    setLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/api/explain', {
        candidate_profile: {
          name: candidateName,
          skills: job.matched_skills.join(', ') + ', ' + job.missing_skills.join(', '),
          education: job.education,
          experience: job.experience_required,
          location: job.location,
          expected_salary: job.salary_min
        },
        job: job
      })

      setSelectedJob({
        ...job,
        explanation: response.data.explanation,
        learning_roadmap: response.data.learning_roadmap
      })
    } catch (err) {
      console.error('Error getting explanation:', err)
      alert('Failed to get explanation. Make sure OpenAI API key is configured.')
    } finally {
      setLoading(false)
    }
  }

  if (selectedJob) {
    return (
      <JobDetails
        job={selectedJob}
        onBack={handleBack}
        onExplain={handleExplain}
        loading={loading}
      />
    )
  }

  return (
    <div className="recommendation-results">
      <div className="results-header">
        <button onClick={onBack} className="back-button">← Back</button>
        <h2>Top Job Recommendations for {candidateName}</h2>
        <p className="results-count">Found {recommendations.length} matching jobs</p>
      </div>

      <div className="jobs-grid">
        {recommendations.map((job, index) => (
          <JobCard
            key={job.job_id}
            job={job}
            rank={index + 1}
            onSelect={() => handleJobSelect(job)}
          />
        ))}
      </div>
    </div>
  )
}

export default RecommendationResults
