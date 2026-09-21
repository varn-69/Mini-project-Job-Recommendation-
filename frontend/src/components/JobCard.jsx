import React from 'react'
import './JobCard.css'

const JobCard = ({ job, rank, onSelect }) => {
  const matchPercentage = (job.final_score * 100).toFixed(0)

  return (
    <div className="job-card" onClick={onSelect}>
      <div className="job-rank">#{rank}</div>
      <div className="job-header">
        <h3 className="job-title">{job.job_title}</h3>
        <div className="match-badge">{matchPercentage}% Match</div>
      </div>

      <div className="job-company">{job.company}</div>

      <div className="job-details">
        <div className="job-detail">
          <span className="detail-label">Location:</span>
          <span className="detail-value">{job.location}</span>
        </div>
        <div className="job-detail">
          <span className="detail-label">Experience:</span>
          <span className="detail-value">{job.experience_required} years</span>
        </div>
        <div className="job-detail">
          <span className="detail-label">Salary:</span>
          <span className="detail-value">
            ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
          </span>
        </div>
      </div>

      <div className="job-skills-preview">
        <span className="skills-label">Skills:</span>
        <div className="skills-tags">
          {job.matched_skills.slice(0, 3).map((skill, index) => (
            <span key={index} className="skill-tag matched">{skill}</span>
          ))}
          {job.missing_skills.length > 0 && (
            <span className="skill-tag missing">+{job.missing_skills.length} more</span>
          )}
        </div>
      </div>

      <button className="view-details-button">View Details →</button>
    </div>
  )
}

export default JobCard
