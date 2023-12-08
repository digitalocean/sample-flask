function StampButton({ text, onClick }) {
  return (
    <button className="stamp-button" onClick={onClick}>
      Stamp and Download
    </button>
  );
}

export default StampButton;
