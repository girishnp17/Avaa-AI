import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api',
  }),
  tagTypes: ['Resume', 'Career', 'Jobs', 'Courses', 'Roadmap', 'Interview'],
  endpoints: (builder) => ({
    generateResume: builder.mutation({
      query: (data) => ({
        url: '/resume/generate',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Resume'],
    }),
    analyzeCareer: builder.mutation({
      query: (data) => ({
        url: '/career/analyze',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Career'],
    }),
    searchJobs: builder.mutation({
      query: (data) => ({
        url: '/jobs/search',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Jobs'],
    }),
    recommendCourses: builder.mutation({
      query: (data) => ({
        url: '/courses/recommend',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Courses'],
    }),
    createRoadmap: builder.mutation({
      query: (data) => ({
        url: '/roadmap/create',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Roadmap'],
    }),
    startVoiceInterview: builder.mutation({
      query: (data) => ({
        url: '/interview/voice',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Interview'],
    }),
    executeVoiceInterview: builder.mutation({
      query: (data) => ({
        url: '/interview/voice/start',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['Interview'],
    }),
  }),
});

export const {
  useGenerateResumeMutation,
  useAnalyzeCareerMutation,
  useSearchJobsMutation,
  useRecommendCoursesMutation,
  useCreateRoadmapMutation,
  useStartVoiceInterviewMutation,
  useExecuteVoiceInterviewMutation,
} = apiSlice;
