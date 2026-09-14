import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaCircleUser } from "react-icons/fa6";
import { CiLogin } from "react-icons/ci";
import { IoMenu } from "react-icons/io5";

import SideBar from "./MainSideBar";
import { useCurrentUser } from "../features/auth/useAuth";
import { useLiveSearch } from "../features/clothing/useClothing";
import { useDebounce } from "../shared/hooks/useDebounce";

function Header() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [renderSidebar, setRenderSidebar] = useState(false);

  const { isLoggedIn } = useCurrentUser();

  const searchRef = useRef(null);
  const searchBtnRef = useRef(null);
  const sidebarBtnRef = useRef(null);
  const navigate = useNavigate();

  // Живий пошук з дебаунсом 300мс та кешуванням
  const debouncedQuery = useDebounce(searchQuery, 300);
  const { searchResults } = useLiveSearch(debouncedQuery);

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target) &&
        searchBtnRef.current &&
        !searchBtnRef.current.contains(event.target)
      ) {
        setIsSearchOpen(false);
      }
      if (
        sidebarBtnRef.current &&
        !sidebarBtnRef.current.contains(event.target) &&
        !event.target.closest(".sidebar")
      ) {
        setIsSidebarOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!isSearchOpen) {
      setSearchQuery("");
    }
  }, [isSearchOpen]);

  useEffect(() => {
    if (isSidebarOpen) {
      setRenderSidebar(true);
    }
  }, [isSidebarOpen]);

  const handleSidebarAnimationEnd = () => {
    if (!isSidebarOpen) {
      setRenderSidebar(false);
    }
  };

  function toggleSidebar() {
    setIsSidebarOpen((state) => !state);
  }

  function toggleSearch() {
    setIsSearchOpen((state) => !state);
  }

  function handleSearchSubmit() {
    if (searchQuery.trim() !== "") {
      setIsSearchOpen(false);
      navigate(`/search?q=${searchQuery}`);
    }
  }

  return (
    <>
      <div className="header">
        <div className="logo-at-header">
          <Link to="/">
            <img
              className="logo-at-header-icon"
              src="logo-at-header.png"
              alt="header"
            />
          </Link>
        </div>

        <div className="title">#ТВОЯ_ПОЛІТЕХНІКА</div>

        <div className="header-icons">
          <button
            ref={searchBtnRef}
            onClick={toggleSearch}
            className={!isLoggedIn ? "search-btn-closer" : ""}
          >
            <svg
              width="35"
              height="35"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#eaf3b2"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ width: "40px", height: "40px", marginRight: "5px" }}
            >
              <circle cx="10" cy="10" r="6.5"></circle>
              <line x1="21" y1="21" x2="15" y2="15"></line>
            </svg>
          </button>

          <button>
            {isLoggedIn ? (
              <Link to="/me">
                <FaCircleUser size="60px" color="var(--secondary-yellow)" />
              </Link>
            ) : (
              <Link to="/login" className="login-icon-bold">
                <CiLogin size="60px" color="var(--secondary-yellow)" strokeWidth={1} />
              </Link>
            )}
          </button>

          <button ref={sidebarBtnRef} onClick={toggleSidebar}>
            <IoMenu size="60px" color="var(--secondary-yellow)" />
          </button>
        </div>
      </div>

      <div
        ref={searchRef}
        className={`search-dropdown ${isSearchOpen ? "open" : ""}`}
      >
        <input
          type="text"
          placeholder="Шукати круті товари..."
          autoFocus={isSearchOpen}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearchSubmit();
          }}
        />

        {searchQuery.length > 0 && (
          <div className="search-results-preview">
            <div className="search-suggestions">
              <div className="suggestion-item">
                <span className="icon">🔍</span> {searchQuery}
              </div>
            </div>

            <div className="search-products">
              <h4 className="search-section-title">Товари</h4>
              {searchResults.length > 0 ? (
                searchResults.map((product) => {
                  const photoSrc = product.photos?.[0];
                  return (
                    <div
                      className="search-product-item"
                      key={product.id}
                      onClick={() => {
                        setIsSearchOpen(false);
                        navigate(`/product?id=${product.id}`);
                      }}
                    >
                      <div
                        className="search-product-image"
                        style={
                          photoSrc
                            ? { backgroundImage: `url(${photoSrc})` }
                            : {}
                        }
                      >
                        {!photoSrc && (
                          <span style={{ fontSize: "12px" }}>📷</span>
                        )}
                      </div>
                      <div className="search-product-info">
                        <div className="search-product-name">
                          {product.name}
                        </div>
                        <div className="search-product-price">
                          {product.price ? `${product.price} ₴` : "??? ₴"}
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div
                  style={{
                    fontSize: "13px",
                    color: "rgba(61, 86, 144, 0.6)",
                    padding: "10px",
                  }}
                >
                  Нічого не знайдено...
                </div>
              )}
            </div>

            <button className="search-all-btn" onClick={handleSearchSubmit}>
              Всі результати ({searchQuery})
            </button>
          </div>
        )}
      </div>

      {renderSidebar && (
        <SideBar
          isOpen={isSidebarOpen}
          closeSidebar={() => setIsSidebarOpen(false)}
          onAnimationEnd={handleSidebarAnimationEnd}
        />
      )}
    </>
  );
}

export default Header;
