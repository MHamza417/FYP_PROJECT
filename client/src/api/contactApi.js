// 127.0.0.1 standard IP use karein aakhir mein trailing slash ke sath
const API_URL = 'http://127.0.0.1:8000/api/contact/';

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
    console.error("EXACT FETCH ERROR:", error); // Yeh browser console mein error print karega
    return { status: "error", message: "Failed to send message" };
  }
};