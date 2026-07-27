import axios from "axios";

const API_URL = "http://13.53.169.32:8000/api/projects/";

export const getProjects = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};