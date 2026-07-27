import "./Testimonials.css";
import { FaStar } from "react-icons/fa";

const reviews = [
  {
    name: "Ahmed Ali",
    company: "ABC Software House",
    review:
      "Nexus Technologies delivered our project on time with excellent quality."
  },
  {
    name: "Sarah Khan",
    company: "Digital Agency",
    review:
      "Professional team with outstanding web development and cloud services."
  },
  {
    name: "John Smith",
    company: "Global Tech",
    review:
      "Highly recommended for DevOps and enterprise software solutions."
  }
];

function Testimonials() {
  return (
    <section className="testimonials">
      <div className="testimonial-title">
        <span>TESTIMONIALS</span>
        <h2>What Our Clients Say</h2>
      </div>

      <div className="testimonial-grid">
        {reviews.map((item) => (
          <div className="testimonial-card" key={item.name}>
            <div className="stars">
              <FaStar />
              <FaStar />
              <FaStar />
              <FaStar />
              <FaStar />
            </div>
            <p>"{item.review}"</p>
            <h3>{item.name}</h3>
            <span>{item.company}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Testimonials;