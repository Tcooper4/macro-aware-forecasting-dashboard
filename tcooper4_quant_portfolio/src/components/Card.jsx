import { motion } from "framer-motion";

function Card({ title, children }) {
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <h3>{title}</h3>
      <p>{children}</p>
    </motion.div>
  );
}

export default Card;
