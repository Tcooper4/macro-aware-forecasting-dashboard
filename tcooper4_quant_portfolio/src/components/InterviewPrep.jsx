import { motion } from "framer-motion";
import FadeInWhenVisible from './FadeInWhenVisible';

function InterviewPrep() {
  return (
    <FadeInWhenVisible>
      <motion.div id="prep" className="section">
        <h2>Interview Prep Pack</h2>
        <ul>
          <li>Probability & Statistics</li>
          <li>Stochastic Calculus</li>
          <li>Time-Series Modeling</li>
          <li>Machine Learning for Finance</li>
        </ul>
        <p>
          <a href="/prep/Quant_Interview_Notes.pdf" target="_blank" rel="noopener noreferrer">
            <button>Download Interview Prep Notes</button>
          </a>
        </p>
      </motion.div>
    </FadeInWhenVisible>
  );
}

export default InterviewPrep;
