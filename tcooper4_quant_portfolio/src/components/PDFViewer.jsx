import { motion } from "framer-motion";

function PDFViewer() {
  return (
    <motion.div id="pdf" className="section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
      <h2>Quant Interview Notes (Embedded)</h2>
      <iframe
        src="/prep/Quant_Interview_Notes.pdf"
        width="100%"
        height="600px"
        style={{ border: "1px solid #ccc", borderRadius: "8px" }}
        title="Interview Notes"
      />
      <p style={{ marginTop: "1rem" }}>
        <a href="/prep/Quant_Interview_Notes.pdf" target="_blank" rel="noopener noreferrer">
          <button>Download PDF</button>
        </a>
      </p>
    </motion.div>
  );
}

export default PDFViewer;
