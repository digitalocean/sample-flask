import React from "react";

function StampPreview({
  projectName,
  jobCode,
  client,
  issuedDate,
  dateFormat,
  productType,
  pageNumber,
  revisionNumber,
  revisionDate,
}) {
  return (
    <div className="stamp-preview-div">
      <h2>Stamp Preview</h2>
      <div className="stamp-preview-content">
        <div className="stamp-preview-column">
          <p>
            <span className="label">Project Name:</span> {projectName}
          </p>
          <p>
            <span className="label">Job Code:</span> {jobCode}
          </p>
          <p>
            <span className="label">Prepared for/Client:</span> {client}
          </p>
        </div>
        <div className="stamp-preview-column">
          <p>
            <span className="label">Issued Date:</span> {issuedDate} (Format:{" "}
            {dateFormat})
          </p>
          <p>
            <span className="label">Product Type:</span> {productType}
          </p>
          <p>
            <span className="label">Page Number:</span> {pageNumber}
          </p>
          <p>
            <span className="label">Revision Number:</span> {revisionNumber}
          </p>
          <p>
            <span className="label">Revision Date:</span> {revisionDate}
          </p>
        </div>
        <div className="stamp-preview-column">{/* Reserved for logo */}</div>
      </div>
    </div>
  );
}

export default StampPreview;
