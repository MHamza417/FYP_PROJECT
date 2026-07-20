import React, { useEffect, useState } from 'react';
import { getServices } from '../../api/serviceApi'; // Agar path thoda different hai to adjust kar lein
// Agar aap dynamic icons render kar rahe hain, to apne icons import yahan barkarar rakhein, jaise:
// import * as Icons from 'react-icons/fa'; 
// import { FaQuestionCircle } from 'react-icons/fa';
import "./Services.css";
function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Backend se data fetch karne ke liye useEffect
  useEffect(() => {
    const fetchServicesData = async () => {
      try {
        const data = await getServices();
        setServices(data);
      } catch (err) {
        setError("Failed to load services");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchServicesData();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px', color: '#fff' }}>Loading services...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', padding: '50px', color: 'red' }}>{error}</div>;
  }

  return (
    <section className="services" id="services">
      <div className="section-title">
        <span>OUR SERVICES</span>
        <h2>What We Offer</h2>
        <p>
          We deliver complete digital solutions to help your business grow.
        </p>
      </div>

      <div className="services-grid">
        {services.map((service) => (
          <div className="service-card" key={service.id}>
            <div className="service-icon">
              {/* Dynamic Icon Rendering Logic (Aapke purane code ke mutabiq) */}
              {/* Agar Icons object import kiya hai to ye chalega, warna fallback icon show hoga */}
              {/* {Icons[service.icon] ? React.createElement(Icons[service.icon]) : <FaQuestionCircle />} */}
            </div>

            <h3>{service.title}</h3>
            <p>{service.description}</p>

            <button>Learn More →</button>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Services;