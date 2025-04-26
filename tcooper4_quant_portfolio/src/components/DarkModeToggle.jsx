import { useState, useEffect } from 'react';

function DarkModeToggle() {
  const [darkMode, setDarkMode] = useState(() => {
    // Load preference from localStorage on first load
    return localStorage.getItem('darkMode') === 'true';
  });

  useEffect(() => {
    document.body.className = darkMode ? 'dark' : '';
    // Save preference to localStorage every time it changes
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  return (
    <div style={{ textAlign: 'right', marginBottom: '1rem' }}>
      <button onClick={() => setDarkMode(!darkMode)}>
        {darkMode ? 'Light Mode' : 'Dark Mode'}
      </button>
    </div>
  );
}

export default DarkModeToggle;
