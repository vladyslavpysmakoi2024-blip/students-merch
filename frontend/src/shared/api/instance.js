import axios from "axios";

export const API_BASE_URL = process.env.API_URL;


if (!API_BASE_URL) {
  throw new Error("REACT_APP_API_URL is not set");
}


export const api = axios.create({
  withCredentials: true,
  baseURL: API_BASE_URL,
});

let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = () => {
  refreshSubscribers.forEach((cb) => cb());
  refreshSubscribers = []; // Очищаємо чергу
};

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    const isAuthRoute =
      originalRequest?.url &&
      (originalRequest.url.includes("/auth/login") ||
        originalRequest.url.includes("/auth/register") ||
        originalRequest.url.includes("/auth/refresh"));

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthRoute
    ) {
      if (!isRefreshing) {
        isRefreshing = true;
        originalRequest._retry = true;

        try {
          await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            {},
            { withCredentials: true },
          );
          isRefreshing = false;
          onRefreshed();
          return api(originalRequest);
        } catch (refreshError) {
          isRefreshing = false;
          refreshSubscribers = [];

          // window.location.href = "/login";

          return Promise.reject(refreshError);
        }
      } else {
        // Якщо рефреш вже йде, ми ставимо цей запит у чергу (повертаємо Promise)
        // Promise вирішиться (resolve) тільки тоді, коли викличеться onRefreshed()
        return new Promise((resolve) => {
          subscribeTokenRefresh(() => {
            originalRequest._retry = true;
            resolve(api(originalRequest));
          });
        });
      }
    }

    return Promise.reject(error);
  },
);
