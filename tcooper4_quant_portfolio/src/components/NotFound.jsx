import { motion } from "framer-motion";

function NotFound() {
  return (
    <motion.div className="section" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
      <h2>404 - Page Not Found</h2>
      <p>The page you are looking for does not exist or has been moved.</p>
      <p><a href="/">Go back to Home</a></p>
    </motion.div>
  );
}

export default NotFound;
