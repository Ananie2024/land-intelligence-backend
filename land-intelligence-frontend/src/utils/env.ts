import { z } from 'zod';

const envSchema = z.object({
  // Backend API URL
  VITE_API_URL: z.string().url().default('http://localhost:8000'),

  // Application config
  VITE_APP_NAME: z.string().default('Land Intelligence'),

  // Feature flags / Debugging
  VITE_ENABLE_DEBUG: z
    .union([z.string(), z.boolean()])
    .transform((val) => val === 'true' || val === true)
    .default(false),

  // Vite environment variables
  MODE: z.enum(['development', 'production', 'test']).default('development'),
  DEV: z.boolean().default(true),
  PROD: z.boolean().default(false),
});

// Validate import.meta.env properties
const parsedEnv = envSchema.safeParse({
  VITE_API_URL: import.meta.env.VITE_API_URL,
  VITE_APP_NAME: import.meta.env.VITE_APP_NAME,
  VITE_ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG,
  MODE: import.meta.env.MODE,
  DEV: import.meta.env.DEV,
  PROD: import.meta.env.PROD,
});

if (!parsedEnv.success) {
  console.error('❌ Frontend environment validation failed:', parsedEnv.error.format());
  
  if (import.meta.env.DEV) {
    throw new Error(
      `Invalid environment configuration: ${JSON.stringify(parsedEnv.error.format(), null, 2)}`
    );
  }
}

export const env = parsedEnv.success
  ? parsedEnv.data
  : envSchema.parse({
      VITE_API_URL: 'http://localhost:8000',
      VITE_APP_NAME: 'Land Intelligence',
      VITE_ENABLE_DEBUG: false,
      MODE: 'production',
      DEV: false,
      PROD: true,
    });
