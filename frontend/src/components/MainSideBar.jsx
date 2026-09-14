import { Link } from "react-router-dom";
import { FaPerson } from "react-icons/fa6";

function MainSideBar({ closeSidebar, isOpen, onAnimationEnd }) {
  const items = [
    { 
      title: "Головна", 
      link: "/", 
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
      )
    },
    { 
      title: "Збережене", 
      link: "/favorites", 
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
      )
    },
    { 
      title: "Корзина", 
      link: "/cart", 
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="9" cy="21" r="1"></circle>
          <circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
      )
    },
    {
      title: "3D Візуалізація",
      link: "/model",
      icon: (
        <FaPerson size={30} />
      )
    }
  ];

  return (
    <div className={`sidebar ${!isOpen ? 'closing' : ''}`} onAnimationEnd={onAnimationEnd}>
      {items.map(i => (
        <Link key={i.title} to={i.link} className="sidebar-link" onClick={closeSidebar} title={i.title}>
          <div className="sidebar-item">
            {i.icon}
          </div>
        </Link>
      ))}
    </div>
  );
}

export default MainSideBar;
