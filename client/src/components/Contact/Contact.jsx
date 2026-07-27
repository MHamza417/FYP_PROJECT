import "./Contact.css";
import { useState } from "react";
import { sendContactMessage } from "../../api/contactApi"; // API call import ki
import {
  FaPhoneAlt,
  FaEnvelope,
  FaMapMarkerAlt,
  FaFacebookF,
  FaLinkedinIn,
  FaGithub,
} from "react-icons/fa";

function Contact() {
  const [formData, setFormData] = useState({ name: "", email: "", subject: "", message: "" });
  const [statusMsg, setStatusMsg] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Direct Gmail Web Link open karne ka function (100% Working on all devices)
  const handleEmailClick = () => {
    const email = "hamza.dev.pk@gmail.com";
    const subject = encodeURIComponent("Inquiry from Nexus Technologies");
    const body = encodeURIComponent("Hi Hamza,\n\n");
    
    // Yeh URL direct web-based Gmail composer open karega naye tab mein
    const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${email}&su=${subject}&body=${body}`;
    
    window.open(gmailUrl, "_blank"); // Naya tab khulega
  };

  // Direct Phone click action
  const handlePhoneClick = () => {
    window.location.href = "tel:+923001234567";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatusMsg("Sending...");
    setIsSuccess(false);

    const backendData = {
      name: formData.name,
      email: formData.email,
      message: `Subject: ${formData.subject}\n\nMessage:\n${formData.message}`
    };
    
    const result = await sendContactMessage(backendData);
    
    if (result && (result.status === "success" || result.message === "Message saved successfully!")) {
      setIsSuccess(true);
      setStatusMsg("Message Sent Successfully! 👍");
      setFormData({ name: "", email: "", subject: "", message: "" }); 
    } else {
      setIsSuccess(false);
      setStatusMsg(result?.message || "Something went wrong. Please try again.");
    }
  };

  return (
    <section className="contact" id="contact">

      <div className="contact-title">
        <span>CONTACT US</span>
        <h2>Let's Build Something Amazing</h2>
        <p>Have a project in mind? Contact our team today.</p>
      </div>

      <div className="contact-container">

        {/* Left Side (Dynamic Interaction) */}
        <div className="contact-info">

          {/* Phone Box */}
          <div className="info-box" onClick={handlePhoneClick} style={{ cursor: "pointer" }}>
            <FaPhoneAlt className="icon" />
            <div>
              <h3>Phone</h3>
              <p>+92 300 4371708</p>
            </div>
          </div>

          {/* Email Box (Direct Gmail Web Opener) */}
          <div className="info-box" onClick={handleEmailClick} style={{ cursor: "pointer" }}>
            <FaEnvelope className="icon" />
            <div>
              <h3>Email</h3>
              <p>hamza.dev.pk@gmail.com</p>
            </div>
          </div>

          <div className="info-box">
            <FaMapMarkerAlt className="icon" />
            <div>
              <h3>Address</h3>
              <p>Lahore, Pakistan</p>
            </div>
          </div>

          <div className="social-icons">
            <FaFacebookF />
            <FaLinkedinIn />
            <FaGithub />
          </div>

        </div>

        {/* Right Side (Form) */}
        <div className="contact-form">

          <form onSubmit={handleSubmit}>

            <input
              type="text"
              name="name"
              placeholder="Your Name"
              value={formData.name}
              onChange={handleChange}
              required
            />

            <input
              type="email"
              name="email"
              placeholder="Your Email"
              value={formData.email}
              onChange={handleChange}
              required
            />

            <input
              type="text"
              name="subject"
              placeholder="Subject"
              value={formData.subject}
              onChange={handleChange}
              required
            />

            <textarea
              name="message"
              rows="6"
              placeholder="Write your message..."
              value={formData.message}
              onChange={handleChange}
              required
            ></textarea>

            <button type="submit">
              Send Message
            </button>

          </form>

          {statusMsg && (
            <p 
              className="status-message" 
              style={{ 
                marginTop: "15px", 
                fontWeight: "bold", 
                color: isSuccess ? "#4caf50" : "#f44336"
              }}
            >
              {statusMsg}
            </p>
          )}

        </div>

      </div>

    </section>
  );
}

export default Contact;