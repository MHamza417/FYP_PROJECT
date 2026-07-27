import React, { useEffect, useState } from 'react';
import { getServices } from '../../api/serviceApi';
import "./Services.css";

function Services() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
            <div className="service-icon"></div>
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