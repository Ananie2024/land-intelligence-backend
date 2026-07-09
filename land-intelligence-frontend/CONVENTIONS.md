# Project Conventions & Code Standards
## Land Intelligence Frontend Foundation

This document defines the conventions and coding standards established for the Land Intelligence System frontend application. All contributors must follow these standards to ensure project consistency, maintainability, and scalability.

---

## 1. Directory Structure

The project directory structure is standardized as follows under `src/`:

```text
src/
├── api/             # HTTP clients (Axios, QueryClient) and base request definitions
├── assets/          # Static assets (images, svg icons, global fonts)
├── components/      # Global shared UI components
│   ├── common/      # Generic helper components (ScrollToTop, SEO, etc.)
│   ├── layout/      # Layout components (Header, Sidebar, Footer, Navigation)
│   └── ui/          # Core reusable atomic UI components (Button, Input, Table)
├── features/        # Domain-driven features
│   ├── authentication/
│   ├── dashboard/
│   ├── land/
│   ├── projects/
│   ├── users/
│   └── reports/
├── hooks/           # Global custom React hooks
├── layouts/         # Page wrappers & layout shells (AdminLayout, AuthLayout)
├── pages/           # High-level route pages (aggregates features)
├── routes/          # Navigation routers (React Router configuration)
├── services/        # Business logic & API request wrappers
├── store/           # Global state management (Zustand stores)
├── types/           # Global TypeScript type definitions and schemas
├── utils/           # Helper scripts & validation utilities
├── App.tsx          # Application root wrapper
└── main.tsx         # React entry point mounting to index.html
```

---

## 2. File & Folder Naming Conventions

### Directory Naming
* All folder names under `src/` must be written in **lowercase** (alphanumeric, camelCase, or kebab-case if necessary for compound names).
  * *Correct:* `components/common`, `features/authentication`
  * *Incorrect:* `Components/Common`, `features/Authentication`

### File Naming
* **React Components**: Use **PascalCase** with `.tsx` extension.
  * *Correct:* `Button.tsx`, `ParcelCard.tsx`, `SidebarWrapper.tsx`
* **Custom Hooks**: Use **camelCase** prefixed with `use` with `.ts` or `.tsx` extension.
  * *Correct:* `useAuth.ts`, `useQueryParams.ts`
* **TypeScript Types**: Use **camelCase** or match domain names. Files containing type declarations should end with `.ts` or `.d.ts`.
  * *Correct:* `user.types.ts`, `gis.ts`
* **Utilities & Services**: Use **camelCase** with `.ts` extension.
  * *Correct:* `formatDate.ts`, `authService.ts`

---

## 3. TypeScript Standards

* **Strict Mode Enabled**: The compiler option `"strict": true` is enforced in `tsconfig.json`. Code must compile without implicit `any` definitions.
* **Avoid `any`**: Do not use `any` unless writing generic functions where the type is dynamic. Prefer `unknown` or specify partial structures.
* **Props Definition**: Define React component props using `interface` rather than `type`.
  ```typescript
  // Preferred
  interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger';
    isLoading?: boolean;
  }
  ```
* **Path Aliases**: Always use the path alias `@/` when importing modules from inside `src/` to prevent brittle relative directory lookups.
  * *Correct:* `import { api } from '@/api/axios';`
  * *Incorrect:* `import { api } from '../../../../api/axios';`

---

## 4. API & Query Conventions

### Axios Requests
* All requests must utilize the pre-configured [api](file:///C:/Users/User/Desktop/Ananie/Dev_Workspace/land-intelligence-backend/land-intelligence-frontend/src/api/axios.ts) Axios instance.
* Endpoints must be mapped inside [constants.ts](file:///C:/Users/User/Desktop/Ananie/Dev_Workspace/land-intelligence-backend/land-intelligence-frontend/src/utils/constants.ts).

### TanStack Query Keys
* Query keys must be formatted as arrays following a structured pattern: `[domain, scope, variables]`.
  ```typescript
  // Query key standard
  const parcelQueryKey = ['parcels', 'list', filters];
  const parcelDetailKey = ['parcels', 'detail', parcelId];
  ```

### API Error Handling
* Network and backend validation errors throw an instance of `ApiError`. You must inspect `error.errors` for form/field level validations, and fall back to `error.message` for toast notifications.
  ```typescript
  try {
    await loginMutation.mutateAsync(credentials);
  } catch (error) {
    if (error instanceof ApiError && error.errors) {
      error.errors.forEach(err => {
        if (err.field) {
          setError(err.field, { message: err.message });
        }
      });
    }
  }
  ```

---

## 5. CSS & Styling Conventions

* **Tailwind CSS v4** is the primary design engine. Avoid writing custom styling declarations inside CSS files. Instead, extend variables under the `@theme` directive in [index.css](file:///C:/Users/User/Desktop/Ananie/Dev_Workspace/land-intelligence-backend/land-intelligence-frontend/src/index.css).
* For complex layouts requiring backdrop blur or visual glass effects, utilize the pre-configured utility classes:
  * `.glass-panel` for standard card glass panels.
  * `.glass-panel-hover` for interactive glass cards.
