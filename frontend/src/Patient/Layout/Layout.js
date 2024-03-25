import { useState, useEffect } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";
import "./layout.css";
import Dropdown from "./Dropdown";
import Footer from "../../components/footer/Footer";

const Layout = () => {
  const [showNavbar, setShowNavbar] = useState(false);
  const [LoggedinObj, setLoggedinObj] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const storedUserObj = localStorage.getItem("loggedin_obj");
    setLoggedinObj(storedUserObj ? storedUserObj : null);
  }, []);

  const handleShowNavbar = () => {
    setShowNavbar(!showNavbar);
  };

  return (
    <>
      <nav className="layout-navbar">
        <div className="layout-container">
          <div className="layout-logo">
            <b>
              Diagno<span>Care</span>
            </b>
          </div>
          <div className="layout-menu-icon" onClick={handleShowNavbar}>
            <MenuOpenIcon sx={{ fontSize: 45 }} />
          </div>
          <div className={`layout-nav-elements  ${showNavbar && "active"}`}>
            <ul>
              <li>
                <Link to="/p-layout">Home</Link>
              </li>
              <li>
                <Link to="/p-layout/services">Services</Link>
              </li>
              <li>
                <Link to="/p-layout/doctors">Find a Doctor</Link>
              </li>
              <li>
                <Link to="/p-layout/chatbot">ChatBot</Link>
              </li>
            </ul>
            <div
              className="layout-active-link"
              style={{ left: `${calculateLeftPosition(location.pathname)}%` }}
            ></div>
          </div>
        </div>
        <Dropdown obj1={LoggedinObj} />
      </nav>
      <Outlet />
      <Footer />
    </>
  );
};

const calculateLeftPosition = (pathname) => {
  switch (pathname) {
    case "/p-layout":
      return 1;
    case "/p-layout/services":
      return 23.9;
    case "/p-layout/doctors":
      return 53.2;
    case "/p-layout/doctors/:id":
      return 53.2;
    case "/p-layout/chatbot":
      return 82.9;
    case "/braintumor":
      return 85;
    default:
      return 0;
  }
};

export default Layout;
