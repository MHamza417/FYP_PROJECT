import "./Projects.css";
import { useEffect, useState } from "react";
import { getProjects } from "../../projectApi";
import project1 from "../../assets/images/project1.jpg";
import project2 from "../../assets/images/project2.jpg";
import project3 from "../../assets/images/project3.jpg";
import project4 from "../../assets/images/project4.jpg";
import project5 from "../../assets/images/project5.jpg";
import project6 from "../../assets/images/project6.jpg";

const images = [
  project1,
  project2,
  project3,
  project4,
  project5,
  project6,
];

function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch (error) {
        console.error("Error loading projects:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  if (loading) {
    return <h2 style={{ textAlign: "center" }}>Loading Projects...</h2>;
  }

  return (
    <section className="projects" id="projects">

      <div className="project-heading">
        <span>OUR PROJECTS</span>

        <h2>Recent Work</h2>

        <p>Some of our latest professional projects.</p>
      </div>

      <div className="project-grid">
        {projects.map((project, index) => (
          <div className="project-card" key={project.id}>

            <img
              src={images[index % images.length]}
              alt={project.title}
            />

            <div className="overlay">
              <h3>{project.title}</h3>

              <p>{project.description}</p>

              <button>View Project</button>
            </div>

          </div>
        ))}
      </div>

    </section>
  );
}

export default Projects;