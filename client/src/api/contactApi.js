const API_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/contact/` 
  : 'http://localhost:5000/api/contact/';

export const sendContactMessage = async (formData) => {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return { status: "error", message: errorData.message || "Server Error" };
    }

    return await response.json();
  } catch (error) {
    console.error("EXACT FETCH ERROR:", error);
    return { status: "error", message: "Failed to send message" };
  }
};