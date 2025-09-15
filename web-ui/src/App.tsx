import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Provider } from 'react-redux';
import { useSelector } from 'react-redux';
import { store, RootState } from './store/store';
import { theme, darkTheme } from './theme/theme';
import Layout from './components/Layout/Layout';
import HomePage from './pages/HomePage';
import ResumeGenerator from './pages/ResumeGenerator';
import CareerGuidance from './pages/CareerGuidance';
import LearningRoadmap from './pages/LearningRoadmap';
import JobSearch from './pages/JobSearch';
import InterviewBot from './pages/InterviewBot';

function AppContent() {
  const themeMode = useSelector((state: RootState) => state.theme.mode);
  const currentTheme = themeMode === 'dark' ? darkTheme : theme;

  return (
    <ThemeProvider theme={currentTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/resume" element={<ResumeGenerator />} />
            <Route path="/career" element={<CareerGuidance />} />
            <Route path="/roadmap" element={<LearningRoadmap />} />
            <Route path="/jobs" element={<JobSearch />} />
            <Route path="/interview" element={<InterviewBot />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;
