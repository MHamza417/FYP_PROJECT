const API_URL = 'http://13.53.169.32:5000/api/services/';

export const getServices = async () => {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching services:", error);
    return [];
  }
};