import React, { useState } from "react";
import Header from "./Header";
import StampForm from "./StampForm";
import StampPreview from "./StampPreview";
import FileUploader from "./FileUploader";
import StampButton from "./StampButton";
import Footer from "./Footer";

function MainController() {
  const [project, setProject] = useState("");
  const [projectNumber, setProjectNumber] = useState("");
  const [preparedFor, setPreparedFor] = useState("");
  const [preparedBy, setPreparedBy] = useState("");
  const [revisionNumber, setRevisionNumber] = useState("");
  const [jobPhase, setJobPhase] = useState("");
  const [dateFormat, setDateFormat] = useState("");
  const [showRevisionDate, setShowRevisionDate] = useState(true);
  const [issueDate, setIssueDate] = useState({
    year: new Date().getFullYear().toString(),
    month: (new Date().getMonth() + 1).toString().padStart(2, "0"),
    day: new Date().getDate().toString().padStart(2, "0"),
  });
  const [revisionDate, setRevisionDate] = useState({
    year: new Date().getFullYear().toString(),
    month: (new Date().getMonth() + 1).toString().padStart(2, "0"),
    day: new Date().getDate().toString().padStart(2, "0"),
  });

  return (
    <div className="all-content-div">
      <header>
        <Header />
      </header>
      <div className="inner-content-div">
        <div className="left-col-div">
          <StampForm
            project={project}
            setProject={setProject}
            projectNumber={projectNumber}
            setProjectNumber={setProjectNumber}
            preparedFor={preparedFor}
            setPreparedFor={setPreparedFor}
            preparedBy={preparedBy}
            setPreparedBy={setPreparedBy}
            issueDate={issueDate}
            setIssueDate={setIssueDate}
            revisionDate={revisionDate}
            setRevisionDate={setRevisionDate}
            revisionNumber={revisionNumber}
            setRevisionNumber={setRevisionNumber}
            jobPhase={jobPhase}
            setJobPhase={setJobPhase}
            dateFormat={dateFormat}
            setDateFormat={setDateFormat}
            showRevisionDate={showRevisionDate}
            setShowRevisionDate={setShowRevisionDate}
          />
        </div>
        <div className="right-col-div">
          <StampPreview
            project={project}
            projectNumber={projectNumber}
            preparedFor={preparedFor}
            preparedBy={preparedBy}
            issueDate={issueDate}
            revisionDate={revisionDate}
            revisionNumber={revisionNumber}
            jobPhase={jobPhase}
            dateFormat={dateFormat}
          />
          <FileUploader />
          <StampButton />
        </div>
      </div>
      <footer>
        <Footer />
      </footer>
    </div>
  );
}

export default MainController;
