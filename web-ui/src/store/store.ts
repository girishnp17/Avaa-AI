import { configureStore } from '@reduxjs/toolkit';
import { apiSlice } from './apiSlice';
import themeSlice from './themeSlice';
import resumeSlice from './resumeSlice';

export const store = configureStore({
  reducer: {
    api: apiSlice.reducer,
    theme: themeSlice,
    resume: resumeSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(apiSlice.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
