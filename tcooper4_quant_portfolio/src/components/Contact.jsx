import { motion } from "framer-motion";
import FadeInWhenVisible from './FadeInWhenVisible';

function Contact() {
  return (
    <FadeInWhenVisible>
      <motion.div id="contact" className="section">
        <h2>Contact</h2>
        <p>Email: Tcooper4@binghamton.edu</p>
        <p>GitHub: <a href="https://github.com/Tcooper4" target="_blank" rel="noopener noreferrer">Tcooper4</a></p>
        <p>LinkedIn: <a href="https://www.linkedin.com/in/thomas-cooper-074/" target="_blank" rel="noopener noreferrer">LinkedIn</a></p>
      </motion.div>
    </FadeInWhenVisible>
  );
}

export default Contact;
