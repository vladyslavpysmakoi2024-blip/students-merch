import { Link } from "react-router-dom";

function Hero() {
  return (
    <section className="hero">
      <img src="/cat.5.png" alt="" className="hero-cat hero-cat--top-left" />

      <div className="hero-inner">
        <img
          src="/doodle-1.svg"
          alt=""
          className="hero-doodles hero-doodles--1"
        />
        <img
          src="/doodle-2.svg"
          alt=""
          className="hero-doodles hero-doodles--2"
        />

        <img
          src="/cat.6.png"
          alt=""
          className="hero-cat hero-cat--bottom-left"
        />
        <img src="/cat.7.png" alt="" className="hero-cat hero-cat--top-right" />
        <img
          src="/cat.8.png"
          alt=""
          className="hero-cat hero-cat--bottom-right"
        />
      </div>

      <Link to="/model" className="hero-btn-3d">
        Твоя 3D-модель
      </Link>
    </section>
  );
}

export default Hero;
