/// <reference types="vite/client" />

declare module "*.css";

declare const process: {
  env: {
    REACT_APP_API_URL?: string;
    [key: string]: string | undefined;
  };
};
