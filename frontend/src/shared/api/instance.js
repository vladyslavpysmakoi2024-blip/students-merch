import axios from "axios";

export const api = axios.create({
  withCredentials: true,
  baseURL: "http://localhost:8000",
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

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      originalRequest.url !== "/auth/login" &&
      originalRequest.url !== "/auth/refresh"
    ) {
      if (!isRefreshing) {
        isRefreshing = true;
        originalRequest._retry = true;

        try {
          await axios.post(
            "http://localhost:8000/auth/refresh",
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
