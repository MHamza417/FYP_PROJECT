import "./Team.css";

import team1 from "../../assets/images/team1.jpg";
import team2 from "../../assets/images/team2.jpg";
import team3 from "../../assets/images/team3.jpg";

import {
  FaFacebookF,
  FaLinkedinIn,
  FaGithub,
} from "react-icons/fa";

const members = [
  {
    image: team1,
    name: "Haseeb&mehk",
    role: "Founder & Full Stack Developer"
  },
  {
    image: team2,
    name: "Sana Khan",
    role: "Cloud & DevOps Engineer"
  },
  {
    image: team3,
    name: "Ayesha & Fareeha",
    role: "UI / UX Designer"
  }
];

function Team() {
  return (
    <section className="team" id="team">
      <div className="team-title">
        <span>OUR TEAM</span>
        <h2>Meet Our Experts</h2>
        <p>
          Our experienced professionals build innovative
          digital solutions for modern businesses.
        </p>
      </div>

      <div className="team-grid">
        {members.map((member) => (
          <div className="team-card" key={member.name}>
            <img src={member.image} alt={member.name} />
            <div className="team-info">
              <h3>{member.name}</h3>
              <p>{member.role}</p>
              <div className="social">
                <FaFacebookF />
                <FaLinkedinIn />
                <FaGithub />
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Team;