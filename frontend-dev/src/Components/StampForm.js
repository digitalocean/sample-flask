import React from "react";
import EosLogo from "../Assets/eos-logo.png";
import AldLogo from "../Assets/ald-logo.png";

function StampForm({
  project,
  setProject,
  projectNumber,
  setProjectNumber,
  preparedFor,
  setPreparedFor,
  preparedBy,
  setPreparedBy,
  issueDate,
  setIssueDate,
  revisionNumber,
  setRevisionNumber,
  revisionDate,
  setRevisionDate,
  showRevision,
  setShowRevision,

  jobPhase,
  setJobPhase,
  dateFormat,
  setDateFormat,
}) {
  const formatDateForInput = (date) => {
    return `${date.year}-${date.month.padStart(2, "0")}-${date.day.padStart(
      2,
      "0"
    )}`;
  };

  const handleDateChange = (e, dateType) => {
    const [year, month, day] = e.target.value.split("-");
    if (dateType === "issueDate") {
      setIssueDate({ year, month, day });
    } else {
      setRevisionDate({ year, month, day });
    }
  };

  const twoYearsAgo = new Date();
  twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);
  const minDate = twoYearsAgo.toISOString().split("T")[0];

  const selectPreparedBy = (choice) => {
    setPreparedBy(choice);
  };

  return (
    <div className="stamp-form-div">
      <h2>Stamp Settings</h2>
      <div className="form-section">
        <h3>Prepared by:</h3>
        <div className="image-button-group">
          <button
            className={`image-button ${
              preparedBy === "Eos Lightmedia" ? "selected" : ""
            }`}
            onClick={() => selectPreparedBy("Eos Lightmedia")}
            style={{ backgroundImage: `url(${EosLogo})` }}
          />
          <button
            className={`image-button ${
              preparedBy === "Abernathy Lighting Design" ? "selected" : ""
            }`}
            onClick={() => selectPreparedBy("Abernathy Lighting Design")}
            style={{ backgroundImage: `url(${AldLogo})` }}
          />
        </div>
      </div>

      <div className="form-section">
        <h3>Project Information:</h3>
        <label>
          Project:
          <input
            type="text"
            value={project}
            onChange={(e) => setProject(e.target.value)}
            placeholder="Enter project name"
          />
        </label>
        <label>
          Project #:
          <input
            type="text"
            value={projectNumber}
            onChange={(e) => setProjectNumber(e.target.value)}
            placeholder="Enter job code"
          />
        </label>
        <label>
          Prepared for:
          <input
            type="text"
            value={preparedFor}
            onChange={(e) => setPreparedFor(e.target.value)}
            placeholder="Enter client"
          />
        </label>
        <label>
          Job Phase:
          <select
            value={jobPhase}
            onChange={(e) => setJobPhase(e.target.value)}
          >
            <option value="For Bid">For Bid</option>
            <option value="For Review / Approval">For Review / Approval</option>
            <option value="Coordination">Coordination</option>
          </select>
        </label>
      </div>

      <div className="form-section">
        <h3>Document Dates:</h3>
        <label>
          Issue Date:
          <input
            type="date"
            value={formatDateForInput(issueDate)}
            onChange={handleDateChange}
            min={minDate}
          />
        </label>
        <div className="radio-group">
          <label>Date Format:</label>
          <div className="date-format-div">
            <input
              type="radio"
              id="format1"
              name="dateFormat"
              value="YYYY/MM/DD"
              onChange={(e) => setDateFormat(e.target.value)}
              checked={dateFormat === "YYYY/MM/DD"}
            />
            <label htmlFor="format1">YYYY/MM/DD</label>
            <input
              type="radio"
              id="format2"
              name="dateFormat"
              value="MM/DD/YYYY"
              onChange={(e) => setDateFormat(e.target.value)}
              checked={dateFormat === "MM/DD/YYYY"}
            />
            <label htmlFor="format2">MM/DD/YYYY</label>
            <input
              type="radio"
              id="format3"
              name="dateFormat"
              value="DD/MM/YYYY"
              onChange={(e) => setDateFormat(e.target.value)}
              checked={dateFormat === "DD/MM/YYYY"}
            />
            <label htmlFor="format3">DD/MM/YYYY</label>
          </div>
        </div>
      </div>
      <div className="form-section">
        <h3>Revisions:</h3>
        <label>
          Revision Date:
          <input
            type="date"
            value={formatDateForInput(revisionDate)}
            onChange={handleDateChange}
            min={minDate}
          />
        </label>
        <label>
          Show Revision Date?
          <input
            type="checkbox"
            checked={showRevision}
            onChange={(e) => setShowRevision(e.target.checked)}
          />
        </label>
        <label>
          Revision Number:
          <input
            type="number"
            value={revisionNumber}
            onChange={(e) => setRevisionNumber(e.target.value)}
          />
        </label>
      </div>
    </div>
  );
}

export default StampForm;
