import React from "react";

function StampForm({
  projectName,
  setProjectName,
  jobCode,
  setJobCode,
  client,
  setClient,
  issuedDate,
  setIssuedDate,
  dateFormat,
  setDateFormat,
  productType,
  setProductType,
  revisionNumber,
  setRevisionNumber,
  revisionDate,
  setRevisionDate,
}) {
  return (
    <div className="stamp-form-div">
      <h2>Customize Stamp</h2>
      <label>
        Project Name:
        <input
          type="text"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          placeholder="Project Name"
        />
      </label>
      <label>
        Job Code #:
        <input
          type="text"
          value={jobCode}
          onChange={(e) => setJobCode(e.target.value)}
          placeholder="Job Code #"
        />
      </label>
      <label>
        Prepared for / Client:
        <input
          type="text"
          value={client}
          onChange={(e) => setClient(e.target.value)}
          placeholder="Client"
        />
      </label>
      <label>
        Issued Date (YYYY/MM/DD):
        <input
          type="text"
          value={issuedDate}
          onChange={(e) => setIssuedDate(e.target.value)}
          placeholder="Issued Date"
        />
      </label>
      <label>
        Date Format:
        <input
          type="text"
          value={dateFormat}
          onChange={(e) => setDateFormat(e.target.value)}
          placeholder="Date Format"
        />
      </label>
      <label>
        Product Type:
        <input
          type="text"
          value={productType}
          onChange={(e) => setProductType(e.target.value)}
          placeholder="Product Type"
        />
      </label>
      <label>
        Revision Number:
        <input
          type="number"
          value={revisionNumber}
          onChange={(e) => setRevisionNumber(e.target.value)}
          placeholder="Revision Number"
        />
      </label>

      <label>
        Revision Date:
        <input
          type="text"
          value={revisionDate}
          onChange={(e) => setRevisionDate(e.target.value)}
          placeholder="Revision Date"
        />
      </label>
    </div>
  );
}

export default StampForm;
