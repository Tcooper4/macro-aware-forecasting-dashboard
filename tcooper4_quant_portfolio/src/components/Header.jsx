import Scrollspy from 'react-scrollspy';
import { motion } from 'framer-motion';

function Header() {
  return (
    <motion.header
    id="top" className="header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h1>Thomas Cooper</h1>
      <p>Quantitative Research | Machine Learning | Financial Modeling</p>
      <nav>
        <Scrollspy
          items={['about', 'projects', 'blog', 'prep', 'contact']}
          currentClassName="active"
          componentTag="ul"
          offset={-100}
        >
          <li><a href="#about">About</a></li>
          <li><a href="#projects">Projects</a></li>
          <li><a href="#blog">Blog</a></li>
          <li><a href="#prep">Interview Prep</a></li>
          <li><a href="#contact">Contact</a></li>
        </Scrollspy>
      </nav>
    </motion.header>
  );
}

export default Header;
