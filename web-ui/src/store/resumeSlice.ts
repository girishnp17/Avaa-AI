import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ResumeData {
  personalInfo: {
    fullName: string;
    email: string;
    phone: string;
    location: string;
    summary: string;
  };
  experience: Array<{
    company: string;
    position: string;
    duration: string;
    description: string;
  }>;
  education: Array<{
    institution: string;
    degree: string;
    year: string;
  }>;
  skills: string[];
  jobDescription?: string;
}

interface ResumeState {
  currentStep: number;
  data: ResumeData;
  isGenerating: boolean;
}

const initialState: ResumeState = {
  currentStep: 0,
  data: {
    personalInfo: {
      fullName: '',
      email: '',
      phone: '',
      location: '',
      summary: '',
    },
    experience: [],
    education: [],
    skills: [],
    jobDescription: '',
  },
  isGenerating: false,
};

const resumeSlice = createSlice({
  name: 'resume',
  initialState,
  reducers: {
    setStep: (state, action: PayloadAction<number>) => {
      state.currentStep = action.payload;
    },
    updatePersonalInfo: (state, action) => {
      state.data.personalInfo = { ...state.data.personalInfo, ...action.payload };
    },
    addExperience: (state, action) => {
      state.data.experience.push(action.payload);
    },
    updateExperience: (state, action) => {
      const { index, data } = action.payload;
      state.data.experience[index] = data;
    },
    removeExperience: (state, action) => {
      state.data.experience.splice(action.payload, 1);
    },
    addEducation: (state, action) => {
      state.data.education.push(action.payload);
    },
    updateEducation: (state, action) => {
      const { index, data } = action.payload;
      state.data.education[index] = data;
    },
    removeEducation: (state, action) => {
      state.data.education.splice(action.payload, 1);
    },
    setSkills: (state, action) => {
      state.data.skills = action.payload;
    },
    setJobDescription: (state, action) => {
      state.data.jobDescription = action.payload;
    },
    setGenerating: (state, action) => {
      state.isGenerating = action.payload;
    },
    resetForm: (state) => {
      state.data = initialState.data;
      state.currentStep = 0;
    },
  },
});

export const {
  setStep,
  updatePersonalInfo,
  addExperience,
  updateExperience,
  removeExperience,
  addEducation,
  updateEducation,
  removeEducation,
  setSkills,
  setJobDescription,
  setGenerating,
  resetForm,
} = resumeSlice.actions;

export default resumeSlice.reducer;
