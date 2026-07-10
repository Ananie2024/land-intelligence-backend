// Type declarations for react-router v7
// Re-export all types from react-router-dom for compatibility

declare module 'react-router' {
  // Re-export everything from react-router-dom which exports from react-router internally
  export * from 'react-router-dom';
}

// Type augmentation for react-router-dom to include all v7 exports
declare module 'react-router-dom' {
  // Hooks
  export function useNavigate(): NavigateFunction;
  export function useLocation(): Location;
  export function useParams<T extends Record<string, string | undefined> = Record<string, string | undefined>>(): T;
  export function useSearchParams(): [URLSearchParams, SetURLSearchParams];

  // Components
  export function Navigate(props: NavigateProps): null;
  export function Outlet(props?: OutletProps): React.ReactElement | null;
  export function NavLink(props: NavLinkProps): React.ReactElement;
  export function RouterProvider(props: RouterProviderProps): React.ReactElement;

  // Router
  export function createBrowserRouter(routes: RouteObject[], opts?: unknown): unknown;
  export function createHashRouter(routes: RouteObject[], opts?: unknown): unknown;

  // Types
  export interface NavigateProps {
    to: string;
    replace?: boolean;
    state?: unknown;
  }
  export interface OutletProps {
    context?: unknown;
  }
  export interface NavLinkProps {
    to: string;
    className?: string | ((props: { isActive: boolean; isPending: boolean }) => string | undefined);
    children?: React.ReactNode | ((props: { isActive: boolean; isPending: boolean }) => React.ReactNode);
    onClick?: (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => void;
    [key: string]: unknown;
  }
  export interface RouteObject {
    path?: string;
    element?: React.ReactNode;
    children?: RouteObject[];
    [key: string]: unknown;
  }
  export interface Location {
    pathname: string;
    search: string;
    hash: string;
    state: unknown;
    key: string;
  }
  export interface RouterProviderProps {
    router: unknown;
  }
  export type NavigateFunction = (to: string | -1, options?: { replace?: boolean; state?: unknown }) => void;
  export type SetURLSearchParams = (nextInit?: URLSearchParams | ((prev: URLSearchParams) => URLSearchParams), navigateOpts?: { replace?: boolean; state?: unknown }) => void;
}
