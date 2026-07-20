import "./Hero.css";
import hero from "../../assets/images/hero.png";
import { FaArrowRight } from "react-icons/fa";

function Hero() {
  return (
    <section className="hero" id="home">

      <div className="hero-left">

        <span className="tag">
          🚀 Trusted IT Solutions Company
        </span>

        <h1>
          Transform Your Business With
          <span> Nexus Technologies</span>
        </h1>

        <p>
          We design modern websites, mobile applications,
          cloud infrastructure, DevOps solutions and secure
          networking systems for businesses worldwide.
        </p>

        <div className="hero-buttons">

          <button className="primary-btn">
            Get Started
            <FaArrowRight />
          </button>

          <button className="secondary-btn">
            Our Services
          </button>

        </div>

        <div className="hero-stats">

          <div>
            <h2>50+</h2>
            <p>Projects</p>
          </div>

          <div>
            <h2>30+</h2>
            <p>Clients</p>
          </div>

          <div>
            <h2>5+</h2>
            <p>Years</p>
          </div>

        </div>

      </div>

      <div className="hero-right">

        <img src={hero} alt="Hero"/>

      </div>

    </section>
  );
}

export default Hero;