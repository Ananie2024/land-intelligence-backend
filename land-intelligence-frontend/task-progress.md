# Migration Task Progress

- [x] Analyze codebase structure
- [x] Add `unwrapPaginated` helper to `apiClient.ts`
- [x] Refactor `userService.ts` to return `PaginatedEnvelope<T>` (eliminated hand-rolled transform)
- [x] Refactor `landService.ts` - `getParishes` and `getParcels` to return `PaginatedEnvelope<T>`
- [x] Refactor `documentService.ts` - `getDocuments` to return `PaginatedEnvelope<T>`
- [x] Add `searchParcels` to `taxService.ts` (moved inline apiClient calls out of Tax.tsx)
- [x] Fix `useResourceMutation` to properly track loading/error state (was hardcoded `false`/`null`)
- [x] Deduplicate `PaginatedEnvelope` type - import from `apiClient.ts` instead of redefining in hooks
- [x] Migrate `Parishes.tsx` → `useResourceList` + `useResourceMutation`
- [x] Migrate `Parcels.tsx` → `useResourceList` + `useResourceMutation`
- [x] Migrate `Documents.tsx` → `useResourceList` + `useResourceMutation`
- [x] Migrate `Backups.tsx` → `useResourceQuery`
- [x] Migrate `Tax.tsx` → `useResourceQuery` + `taxService` (removed inline apiClient calls)
- [x] Fix missing `useState` import and `isSubmitting` in Users.tsx
- [x] TypeScript compiles with zero errors