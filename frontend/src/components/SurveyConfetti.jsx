import { useEffect, useRef } from "react";

const COLORS = ["#3d5690", "#eaf3b2", "#8ab1c7", "#f4a6c0", "#ff7f6b", "#ffffff"];

function SurveyConfetti({ active, duration = 3200 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!active) return undefined;

    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const context = canvas.getContext("2d");
    const particles = [];
    const startedAt = performance.now();
    let frameId = 0;
    let width = 0;
    let height = 0;

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };

    const spawn = (count) => {
      for (let i = 0; i < count; i += 1) {
        particles.push({
          x: Math.random() * width,
          y: -20 - Math.random() * 80,
          size: 6 + Math.random() * 8,
          speedY: 2.4 + Math.random() * 4.2,
          speedX: -2 + Math.random() * 4,
          rotation: Math.random() * Math.PI,
          rotationSpeed: -0.2 + Math.random() * 0.4,
          color: COLORS[i % COLORS.length],
        });
      }
    };

    const tick = (now) => {
      const elapsed = now - startedAt;
      context.clearRect(0, 0, width, height);

      if (elapsed < duration * 0.55) {
        spawn(6);
      }

      particles.forEach((particle) => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        particle.rotation += particle.rotationSpeed;
        context.save();
        context.translate(particle.x, particle.y);
        context.rotate(particle.rotation);
        context.fillStyle = particle.color;
        context.fillRect(-particle.size / 2, -particle.size / 4, particle.size, particle.size / 2);
        context.restore();
      });

      if (elapsed < duration) {
        frameId = requestAnimationFrame(tick);
      } else {
        context.clearRect(0, 0, width, height);
      }
    };

    resize();
    spawn(90);
    window.addEventListener("resize", resize);
    frameId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener("resize", resize);
      context.clearRect(0, 0, width, height);
    };
  }, [active, duration]);

  if (!active) return null;

  return <canvas ref={canvasRef} className="survey-confetti" aria-hidden="true" />;
}

export default SurveyConfetti;
