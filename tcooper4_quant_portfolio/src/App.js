import { useEffect, useState } from 'react';
import './styles.css';

import Header from './components/Header';
import Footer from './components/Footer';
import About from './components/About';
import Skills from './components/Skills';
import Projects from './components/Projects';
import Blog from './components/Blog';
import PDFViewer from './components/PDFViewer';
import InterviewPrep from './components/InterviewPrep';
import Contact from './components/Contact';
import DarkModeToggle from './components/DarkModeToggle';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });

  useEffect(() => {
    document.body.className = darkMode ? 'dark' : '';
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  return (
    <div className="container">
      <div style={{ textAlign: 'right', marginBottom: '1rem' }}>
        <button onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>

      <Header />
      <About />
      <Skills />
      <Projects />
      <Blog />
      <PDFViewer />
      <InterviewPrep />
      <Contact />
      <Footer />

      {/* Back to Top Button */}
      <a href="#top" className="back-to-top" aria-label="Back to Top">↑</a>
    </div>
  );
}

export default App;
