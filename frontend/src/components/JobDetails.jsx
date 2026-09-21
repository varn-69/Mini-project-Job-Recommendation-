import React from 'react'
import './JobDetails.css'

const JobDetails = ({ job, onBack, onExplain, loading }) => {
  const matchPercentage = (job.final_score * 100).toFixed(0)

  return (
    <div className="job-details">
      <button onClick={onBack} className="back-button">← Back to Results</button>

      <div className="details-card">
        <div className="details-header">
          <div>
            <h1 className="details-title">{job.job_title}</h1>
            <p className="details-company">{job.company}</p>
          </div>
          <div className="match-badge-large">{matchPercentage}% Match</div>
        </div>

        <div className="details-section">
          <h2>Job Details</h2>
          <div className="details-grid">
            <div className="detail-item">
              <span className="detail-label">Location</span>
              <span className="detail-value">{job.location}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Experience Required</span>
              <span className="detail-value">{job.experience_required} years</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Salary Range</span>
              <span className="detail-value">
                ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Education</span>
              <span className="detail-value">{job.education}</span>
            </div>
          </div>
        </div>

        <div className="details-section">
          <h2>Description</h2>
          <p className="details-description">{job.description}</p>
        </div>

        <div className="details-section">
          <h2>Required Skills</h2>
          <div className="skills-list">
            {job.skills.map((skill, index) => (
              <span key={index} className="skill-tag">{skill}</span>
            ))}
          </div>
        </div>

        <div className="details-section">
          <h2>Score Breakdown</h2>
          <div className="score-breakdown">
            <div className="score-item">
              <span className="score-label">Overall Match</span>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{ width: `${matchPercentage}%` }}
                />
              </div>
              <span className="score-value">{matchPercentage}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">Skill Match</span>
              <div className="score-bar">
                <div
                  className="score-fill skill"
                  style={{ width: `${(job.skill_score * 100).toFixed(0)}%` }}
                />
              </div>
              <span className="score-value">{(job.skill_score * 100).toFixed(0)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">Experience</span>
              <div className="score-bar">
                <div
                  className="score-fill experience"
                  style={{ width: `${(job.experience_score * 100).toFixed(0)}%` }}
                />
              </div>
              <span className="score-value">{(job.experience_score * 100).toFixed(0)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">Location</span>
              <div className="score-bar">
                <div
                  className="score-fill location"
                  style={{ width: `${(job.location_score * 100).toFixed(0)}%` }}
                />
              </div>
              <span className="score-value">{(job.location_score * 100).toFixed(0)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">Salary</span>
              <div className="score-bar">
                <div
                  className="score-fill salary"
                  style={{ width: `${(job.salary_score * 100).toFixed(0)}%` }}
                />
              </div>
              <span className="score-value">{(job.salary_score * 100).toFixed(0)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">Education</span>
              <div className="score-bar">
                <div
                  className="score-fill education"
                  style={{ width: `${(job.education_score * 100).toFixed(0)}%` }}
                />
              </div>
              <span className="score-value">{(job.education_score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        <div className="details-section">
          <h2>Skill Analysis</h2>
          <div className="skill-analysis">
            <div className="skill-group">
              <h3>Matched Skills</h3>
              <div className="skills-list">
                {job.matched_skills.length > 0 ? (
                  job.matched_skills.map((skill, index) => (
                    <span key={index} className="skill-tag matched">{skill}</span>
                  ))
                ) : (
                  <p className="no-skills">No matched skills</p>
                )}
              </div>
            </div>
            <div className="skill-group">
              <h3>Missing Skills</h3>
              <div className="skills-list">
                {job.missing_skills.length > 0 ? (
                  job.missing_skills.map((skill, index) => (
                    <span key={index} className="skill-tag missing">{skill}</span>
                  ))
                ) : (
                  <p className="no-skills">No missing skills - you're fully qualified!</p>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="details-section">
          <h2>AI Explanation</h2>
          {!job.explanation ? (
            <button
              onClick={() => onExplain(job)}
              className="explain-button"
              disabled={loading}
            >
              {loading ? 'Generating Explanation...' : 'Explain Why This Job Matches'}
            </button>
          ) : (
            <div className="explanation-content">
              <div className="explanation-section">
                <h3>Why This Role Matches You</h3>
                <p>{job.explanation}</p>
              </div>
              <div className="explanation-section">
                <h3>Learning Roadmap</h3>
                <p style={{ whiteSpace: 'pre-line' }}>{job.learning_roadmap}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default JobDetails
