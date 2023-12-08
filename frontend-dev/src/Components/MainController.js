import React, { useState } from "react";
import Header from "./Header";
import StampForm from "./StampForm";
import StampPreview from "./StampPreview";
import FileUploader from "./FileUploader";
import StampButton from "./StampButton";
import Footer from "./Footer";

function MainController() {
  const [projectName, setProjectName] = useState("");
  const [jobCode, setJobCode] = useState("");
  const [client, setClient] = useState("");
  const [preparedBy, setPreparedBy] = useState("");
  const [issuedDate, setIssuedDate] = useState("");
  const [dateFormat, setDateFormat] = useState("YYYY/MM/DD");
  const [productType, setProductType] = useState("");
  const [pageNumber, setPageNumber] = useState(1);
  const [revisionNumber, setRevisionNumber] = useState("");
  const [revisionDate, setRevisionDate] = useState("");

  return (
    <div className="all-content-div">
      <header>
        <Header />
      </header>
      <div className="inner-content-div">
        <div className="left-col-div">
          <StampForm
            projectName={projectName}
            setProjectName={setProjectName}
            jobCode={jobCode}
            setJobCode={setJobCode}
            client={client}
            setClient={setClient}
            preparedBy={preparedBy}
            setPreparedBy={setPreparedBy}
            issuedDate={issuedDate}
            setIssuedDate={setIssuedDate}
            dateFormat={dateFormat}
            setDateFormat={setDateFormat}
            productType={productType}
            setProductType={setProductType}
            pageNumber={pageNumber}
            setPageNumber={setPageNumber}
            revisionNumber={revisionNumber}
            setRevisionNumber={setRevisionNumber}
            revisionDate={revisionDate}
            setRevisionDate={setRevisionDate}
          />
        </div>
        <div className="right-col-div">
          <StampPreview
            projectName={projectName}
            jobCode={jobCode}
            client={client}
            preparedBy={preparedBy}
            issuedDate={issuedDate}
            dateFormat={dateFormat}
            productType={productType}
            pageNumber={pageNumber}
            revisionNumber={revisionNumber}
            revisionDate={revisionDate}
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
