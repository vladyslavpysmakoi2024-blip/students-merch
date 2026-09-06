import { FaTelegram, FaInstagram, FaTiktok, FaThreads, FaFacebook } from "react-icons/fa6";

function Footer() {
  const currentYear = new Date().getFullYear();

return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <img src="/footer-logo.png" alt="Логотип Колегії та Профкому студентів" className="footer-logo" />
          <h3 className="footer-brand-name">
            Колегія та профком<br />
            студентів і аспірантів
          </h3>
        </div>

        <div className="footer-columns">
          <div className="footer-column">
            <h4 className="footer-column-title">Соціальні мережі</h4>
            <div className="footer-socials">
              <a href="https://t.me/students_nulp" target="_blank" rel="noopener noreferrer" aria-label="Telegram">
                <FaTelegram />
              </a>
              <a href="https://www.instagram.com/students_nulp" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
                <FaInstagram />
              </a>
              <a href="https://www.tiktok.com/@students_nulp" target="_blank" rel="noopener noreferrer" aria-label="TikTok">
                <FaTiktok />
              </a>
              <a href="https://www.threads.com/@students_nulp" target="_blank" rel="noopener noreferrer" aria-label="Threads">
                <FaThreads />
              </a>
              <a href="https://www.facebook.com/share/17y7LmX2HC/?mibextid=wwXIfr" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                <FaFacebook />
              </a>
            </div>
          </div>

          <div className="footer-column">
            <h4 className="footer-column-title">Наші сервіси</h4>
            <ul className="footer-links">
              <li>
                <a href="https://t.me/students_nulp_official_bot" target="_blank" rel="noopener noreferrer">
                  Students NULP Bot
                </a>
              </li>
              <li>
                <a href="https://t.me/Students_nulp_support_bot" target="_blank" rel="noopener noreferrer">
                  Students NULP Support Bot
                </a>
              </li>
              <li>
                <span className="footer-link-pending">Leocard Bot (скоро)</span>
              </li>
            </ul>
          </div>

          <div className="footer-column">
            <h4 className="footer-column-title">Де нас знайти</h4>
            <p className="footer-text">вул. Степана Бандери, 12, Львів<br />Кабінет 235</p>
            <p className="footer-text">Пн–Пт: 10:00–16:00</p>
          </div>

          <div className="footer-column">
            <h4 className="footer-column-title">Контакти</h4>
            <p className="footer-text">
              Телефон: <a href="tel:+380322582415">032 258 24 15</a>
            </p>
            <p className="footer-text">
              <a href="mailto:students.profcom@lpnu.ua">students.profcom@lpnu.ua</a>
            </p>
            <p className="footer-text">
              Тех підтримка (Telegram): <a href="https://t.me/ajg473" target="_blank" rel="noopener noreferrer">@ajg473</a>
            </p>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {currentYear} Колегія та Профком студентів і аспірантів</p>
      </div>
    </footer>
  );
}

export default Footer;
