import { motion } from "framer-motion";

const skills = [
  "Python", "C++", "SQL", "R", "AWS", "Pandas", "Machine Learning", "Time-Series", "Quant Research", "Monte Carlo", "Stochastic Calc"
];

function Skills() {
  return (
    <motion.div id="skills" className="section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
      <h2>Technical Skills</h2>
      <div className="skill-badges">
        {skills.map(skill => (
          <span key={skill} className="badge">{skill}</span>
        ))}
      </div>
    </motion.div>
  );
}

export default Skills;
