import { motion } from "framer-motion";

const projects = [
  {
    title: "Option Pricing Engine",
    desc: "Built Black-Scholes and binomial models in Python and C++ with real-time charting."
  },
  {
    title: "Macro Forecasting",
    desc: "Modeled macroeconomic indicators using ARIMA and ML regressors."
  },
  {
    title: "Factor-Based Portfolio",
    desc: "Implemented long-short equity strategies using PCA, risk premia, and factor tilts."
  }
];

function Projects() {
  return (
    <motion.div id="projects" className="section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
      <h2>Projects</h2>
      <div className="card-grid">
        {projects.map((proj, i) => (
          <div className="card" key={i}>
            <h3>{proj.title}</h3>
            <p>{proj.desc}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default Projects;
