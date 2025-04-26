import { useEffect, useState } from 'react';

function ScrollProgress() {
  const [scrollWidth, setScrollWidth] = useState(0);

  useEffect(() => {
    const updateScroll = () => {
      const scrollTop = window.scrollY;
      const winHeight = document.body.scrollHeight - window.innerHeight;
      const scrolled = (scrollTop / winHeight) * 100;
      setScrollWidth(scrolled);
    };

    window.addEventListener('scroll', updateScroll);
    return () => window.removeEventListener('scroll', updateScroll);
  }, []);

  return (
    <div className="scroll-progress-bar" style={{ width: `${scrollWidth}%` }} />
  );
}
export default ScrollProgress;
