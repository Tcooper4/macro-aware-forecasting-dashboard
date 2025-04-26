import { motion } from "framer-motion";

const posts = [
  {
    title: "Term Structure Modeling in Python",
    desc: "A practical guide to building yield curve models using Nelson-Siegel and spline methods.",
  },
  {
    title: "Regime-Switching for Asset Returns",
    desc: "Use Markov models to detect market regimes and apply them to portfolio risk.",
  },
  {
    title: "ML for Portfolio Optimization",
    desc: "Applying random forests and XGBoost for robust asset allocation strategies.",
  },
  {
    title: "Volatility Forecasting with ARIMA-GARCH",
    desc: "Blend traditional time-series with volatility models for tactical trading signals.",
  }
];

function Blog() {
  return (
    <motion.div id="blog" className="section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
      <h2>Quant Blog & Research</h2>
      <div className="card-grid">
        {posts.map((post, i) => (
          <div className="card" key={i}>
            <h3>{post.title}</h3>
            <p>{post.desc}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default Blog;
