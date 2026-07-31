import axios from 'axios';

const API_URL = 'http://localhost:5000/api/projects/';

export const getProjects = async () => {
  try {
    const response = await axios.get(API_URL);
    return response.data;
  } catch (error) {
    console.error("Error loading projects:", error);
    throw error;
  }
};