import { motion } from "framer-motion";

function About() {
  return (
    <motion.div className="section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
      <h2>About Me</h2>
      <p>Quantitative Analyst with experience in model development, automation, and machine learning applied to financial problems.</p>
      <p>
        <a href="/prep/Quant_Interview_Notes.pdf" target="_blank" rel="noopener noreferrer">
          <button>Download Interview Prep Notes</button>
        </a>
      </p>
    </motion.div>
  );
}

export default About;
