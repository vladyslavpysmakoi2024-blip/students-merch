import axios, { InternalAxiosRequestConfig } from "axios";

const rawApiUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";

export const API_BASE_URL =
  typeof window !== "undefined" &&
  window.location.hostname &&
  window.location.hostname !== "localhost" &&
  window.location.hostname !== "127.0.0.1"
    ? rawApiUrl.replace(
        /\/\/(localhost|127\.0\.0\.1)(?=[:/]|$)/,
        `//${window.location.hostname}`,
      )
    : rawApiUrl;

export const api = axios.create({
  withCredentials: true,
  baseURL: API_BASE_URL,
});

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

let isRefreshing = false;
// error is set when refresh failed: queued requests must reject, not hang forever
let refreshSubscribers: Array<(error?: unknown) => void> = [];

const subscribeTokenRefresh = (cb: (error?: unknown) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (error?: unknown) => {
  refreshSubscribers.forEach((cb) => cb(error));
  refreshSubscribers = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    const isSkipRefreshRoute =
      originalRequest?.url &&
      (originalRequest.url.includes("/auth/login") ||
        originalRequest.url.includes("/auth/register") ||
        originalRequest.url.includes("/auth/refresh") ||
        originalRequest.url.includes("/user/me"));

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isSkipRefreshRoute
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
          onRefreshed(refreshError ?? new Error("Token refresh failed"));
          return Promise.reject(refreshError);
        }
      } else {
        return new Promise((resolve, reject) => {
          subscribeTokenRefresh((refreshError) => {
            if (refreshError) {
              reject(refreshError);
              return;
            }
            originalRequest._retry = true;
            resolve(api(originalRequest));
          });
        });
      }
    }

    return Promise.reject(error);
  },
);
