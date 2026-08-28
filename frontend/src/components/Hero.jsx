function Hero() {
  return (
    <section className="hero">
      {/* Підстав правильні назви файлів замість cat.5.png і т.д. */}
      <img src="/cat.5.png" alt="" className="hero-cat hero-cat--top-left" />
      
      {/* Контейнер, який ідеально обрізає котиків по формі плашки */}
      <div className="hero-inner">
        {/* Каракулі (перекотиполе) */}
        <img src="/doodle-1.svg" alt="" className="hero-doodles hero-doodles--1" />
        <img src="/doodle-2.svg" alt="" className="hero-doodles hero-doodles--2" />

        <img src="/cat.6.png" alt="" className="hero-cat hero-cat--bottom-left" />
        <img src="/cat.7.png" alt="" className="hero-cat hero-cat--top-right" />
        <img src="/cat.8.png" alt="" className="hero-cat hero-cat--bottom-right" />
      </div>
    </section>
  );
}

export default Hero;