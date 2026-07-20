import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/projects/";

export const getProjects = async () => {
  const response = await axios.get(API_URL);
  return response.data;
};