import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from "axios";

// Extend AxiosRequestConfig to include custom _retry property
declare module "axios" {
  export interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

import { env } from "@/utils/env";
import { LOCAL_STORAGE_KEYS } from "@/utils/constants";

import { APIResponse, ErrorDetail } from "@/types/api";
import { PaginationMeta } from "@/types/common";
import { ENDPOINTS } from "./endpoints";


// ==========================================
// Custom API Error
// ==========================================

export class ApiError extends Error {
  success: boolean;
  errors: ErrorDetail[] | null;
  meta: PaginationMeta | null;
  timestamp: string;
  status: number;

  constructor(response: Partial<APIResponse>, status: number) {
    super(response.message || "An error occurred during the API request");

    this.name = "ApiError";

    this.success = response.success ?? false;
    this.errors = response.errors ?? null;
    this.meta = response.meta ?? null;
    this.timestamp = response.timestamp ?? new Date().toISOString();
    this.status = status;
  }
}


// ==========================================
// Axios Client Configuration
// ==========================================
//
// Development:
// Browser → Vite Proxy → Python Backend
//
// localhost:5173/api/v1
//          ↓
// localhost:8000/api/v1
//
// Production:
// Browser → API URL (VITE_API_URL)
//
// https://api.your-domain.com/api/v1
//
// Note: VITE_API_URL should be the full backend URL (e.g., https://api.domain.com)
// and will be combined with /api/v1 for the API path.

const getBaseURL = (): string => {
  // In development, use relative URL for Vite proxy
  if (env.DEV) {
    return "/api/v1";
  }
  // In production, use VITE_API_URL + /api/v1
  // VITE_API_URL already has /api/v1 appended in .env.prod if needed
  // Or we append it here if the env var is just the base URL
  const apiUrl = env.VITE_API_URL;
  // If VITE_API_URL already ends with /api/v1, use it as-is
  if (apiUrl.endsWith("/api/v1")) {
    return apiUrl;
  }
  // Otherwise append /api/v1 to the base URL
  return `${apiUrl.replace(/\/$/, "")}/api/v1`;
};

export const api: AxiosInstance = axios.create({
  baseURL: getBaseURL(),

  timeout: 30000,

  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});


// ==========================================
// Token Refresh Queue
// ==========================================

interface FailedRequest {
  resolve: (value: unknown) => void;
  reject: (error: unknown) => void;
}


let isRefreshing = false;

let failedQueue: FailedRequest[] = [];


const processQueue = (
  error: Error | null,
  token: string | null = null
) => {
  failedQueue.forEach((request) => {
    if (error) {
      request.reject(error);
    } else {
      request.resolve(token);
    }
  });

  failedQueue = [];
};


// ==========================================
// Request Interceptor
// ==========================================

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {

    const token = localStorage.getItem(
      LOCAL_STORAGE_KEYS.ACCESS_TOKEN
    );


    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }


    // Let browser set multipart boundary automatically
    if (config.data instanceof FormData) {
      delete config.headers?.["Content-Type"];
    }


    if (env.VITE_ENABLE_DEBUG) {
      console.log(
        `[API Request] ${config.method?.toUpperCase()} ${config.url}`,
        config.data || ""
      );
    }


    return config;
  },


  (error) => {
    return Promise.reject(error);
  }
);



// ==========================================
// Response Interceptor
// ==========================================

api.interceptors.response.use(

  (response) => {

    if (env.VITE_ENABLE_DEBUG) {
      console.log(
        `[API Response] ${response.status} ${response.config.url}`,
        response.data
      );
    }


    return response;
  },


  async (
    error: AxiosError<APIResponse>
  ) => {


    const originalRequest = error.config;

    const status = error.response?.status;

    const errorData = error.response?.data;



    if (env.VITE_ENABLE_DEBUG) {

      console.error(
        `[API Error] ${
          status || "Network"
        } ${originalRequest?.url}`,
        errorData || error.message
      );

    }


    // ======================================
    // Handle Token Refresh
    // ======================================

    if (

      status === 401 &&

      originalRequest &&

      !originalRequest._retry &&

      !originalRequest.url?.includes(
        ENDPOINTS.AUTH.REFRESH
      )

    ) {

      originalRequest._retry = true;


      if (isRefreshing) {


        return new Promise(
          (resolve, reject) => {

            failedQueue.push({
              resolve,
              reject
            });

          }

        )
        .then((token) => {

          if (originalRequest.headers) {
            originalRequest.headers.Authorization =
              `Bearer ${token}`;
          }

          return api(originalRequest);

        })

        .catch((err) => {

          return Promise.reject(err);

        });

      }



      const refreshToken =
        localStorage.getItem(
          LOCAL_STORAGE_KEYS.REFRESH_TOKEN
        );



      if (refreshToken) {


        isRefreshing = true;



        try {

          /*
            IMPORTANT:
            Uses Vite proxy.
            No direct localhost:8000 call.
            
            We use the api instance directly (not axios.post) to ensure
            the request goes through the proxy and doesn't bypass interceptors.
          */

          const refreshResponse =
            await api.post(
              ENDPOINTS.AUTH.REFRESH,
              {
                refresh_token: refreshToken,
              }
            );


          const {
            access_token,
            refresh_token,
          } =
            refreshResponse.data.data ||
            refreshResponse.data;


          localStorage.setItem(
            LOCAL_STORAGE_KEYS.ACCESS_TOKEN,
            access_token
          );


          localStorage.setItem(
            LOCAL_STORAGE_KEYS.REFRESH_TOKEN,
            refresh_token
          );


          if (originalRequest.headers) {
            originalRequest.headers.Authorization =
              `Bearer ${access_token}`;
          }


          processQueue(null, access_token);


          isRefreshing = false;


          return api(originalRequest);


        } catch (refreshError) {

          processQueue(
            refreshError as Error,
            null
          );


          isRefreshing = false;


          localStorage.removeItem(
            LOCAL_STORAGE_KEYS.ACCESS_TOKEN
          );


          localStorage.removeItem(
            LOCAL_STORAGE_KEYS.REFRESH_TOKEN
          );


          localStorage.removeItem(
            LOCAL_STORAGE_KEYS.USER_PROFILE
          );


          // Dispatch event for auth store to handle logout
          window.dispatchEvent(
            new Event("auth:unauthorized")
          );


          return Promise.reject(

            new ApiError(

              {
                success: false,
                message:
                  "Session expired. Please log in again.",
              },

              401

            )

          );

        }

      }

    }



    // ======================================
    // Backend Structured Errors
    // ======================================

    if (

      errorData &&

      typeof errorData === "object" &&

      "success" in errorData

    ) {


      return Promise.reject(

        new ApiError(
          errorData,
          status || 500
        )

      );

    }



    // ======================================
    // Network Errors
    // ======================================

    return Promise.reject(

      new ApiError(

        {
          success: false,

          message:
            error.message ||
            "Network connection error. Please try again.",

          errors: [
            {
              message:
                error.message ||
                "Request failed",
            },
          ],
        },


        status || 0

      )

    );

  }

);