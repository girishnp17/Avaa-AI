import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  Radio,
  FormControlLabel,
  RadioGroup,
} from '@mui/material';
import {
  CloudUpload,
  TrendingUp,
  AttachMoney,
  CheckCircle,
  Info,
  School,
  ArrowForward,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAnalyzeCareerMutation } from '../store/apiSlice';
import { useNavigate } from 'react-router-dom';

interface CareerData {
  domainInterest: string;
  resumeFile?: File;
}

export default function CareerGuidance() {
  const [careerData, setCareerData] = useState<CareerData>({
    domainInterest: '',
  });
  const [dragActive, setDragActive] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<string>('');
  const [analyzeCareer, { data: analysisResult, isLoading }] = useAnalyzeCareerMutation();
  const navigate = useNavigate();
  const [isAutoProcessing, setIsAutoProcessing] = useState(false);

  const handleInputChange = (field: keyof CareerData, value: string | File) => {
    setCareerData(prev => ({ ...prev, [field]: value }));
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.type.includes('document')) {
        handleInputChange('resumeFile', file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleInputChange('resumeFile', e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    try {
      // Create FormData to send both text and file
      const formData = new FormData();
      formData.append('domainInterest', careerData.domainInterest);
      if (careerData.resumeFile) {
        formData.append('resumeFile', careerData.resumeFile);
      }

      const result = await analyzeCareer({
        domainInterest: careerData.domainInterest,
        resumeFile: careerData.resumeFile,
      }).unwrap();
      
      console.log('✅ Career analysis completed:', result);
      setShowResults(true);
      localStorage.setItem('careerDomain', careerData.domainInterest);
      setIsAutoProcessing(true);
      
    } catch (error: any) {
      console.error('❌ Analysis failed:', error);
      alert('Career analysis failed: ' + (error?.data?.error || error?.message || 'Unknown error'));
    }
  };

  const handleStartNewAnalysis = () => {
    setShowResults(false);
    setCareerData({
      domainInterest: '',
    });
    setSelectedRecommendation('');
  };

  const handleProceedToRoadmap = () => {
    if (selectedRecommendation) {
      localStorage.setItem('selectedCareer', selectedRecommendation);
      localStorage.setItem('careerDomain', selectedRecommendation);
      localStorage.setItem('userResume', careerData.resumeFile?.name || '');
      localStorage.removeItem('preGeneratedRoadmap');
      
      console.log('🎯 Proceeding with selected career:', selectedRecommendation);
      navigate('/roadmap');
    }
  };

  // Auto-trigger background processes when user selects a recommendation
  useEffect(() => {
    if (selectedRecommendation && showResults) {
      console.log('🚀 Starting background processes for selected career:', selectedRecommendation);
      
      localStorage.setItem('selectedCareer', selectedRecommendation);
      localStorage.setItem('careerDomain', selectedRecommendation);
      setIsAutoProcessing(true);
      
      const triggerBackgroundProcesses = async () => {
        try {
          // Trigger learning roadmap generation
          const roadmapResponse = await fetch('/api/roadmap/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              subject: selectedRecommendation,
              currentSkills: '',
              goals: `Master ${selectedRecommendation} skills for career advancement`
            })
          });
          const roadmapResult = await roadmapResponse.json();
          localStorage.setItem('preGeneratedRoadmap', JSON.stringify(roadmapResult));
          console.log('✅ Roadmap pre-generated for:', selectedRecommendation);

          // Trigger job search
          const jobResponse = await fetch('/api/jobs/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query: selectedRecommendation,
              location: 'Remote',
              userSkills: ''
            })
          });
          const jobResults = await jobResponse.json();
          localStorage.setItem('preSearchedJobs', JSON.stringify(jobResults));
          console.log('✅ Jobs pre-searched for:', selectedRecommendation);
        } catch (error) {
          console.log('⚠️ Background processes failed:', error);
        } finally {
          setIsAutoProcessing(false);
          console.log('🎉 Background processes completed for:', selectedRecommendation);
        }
      };

      triggerBackgroundProcesses();
    }
  }, [selectedRecommendation, showResults]);

  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, textAlign: 'center' }}>
        AI Career Guidance
      </Typography>

      {!showResults ? (
        // Simplified Input Form - Only Domain and Resume
        <Grid container justifyContent="center">
          <Grid item xs={12} md={8} lg={6}>
            <Paper sx={{ p: 4 }}>
              <Typography variant="h5" sx={{ mb: 4, fontWeight: 600, textAlign: 'center' }}>
                Get AI-Powered Career Recommendations
              </Typography>

              <Grid container spacing={4}>
                {/* Domain of Interest - Required */}
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Domain of Interest *"
                    value={careerData.domainInterest}
                    onChange={(e) => handleInputChange('domainInterest', e.target.value)}
                    placeholder="e.g., Data Science, Software Development, AI/ML, Web Development"
                    helperText="What career field are you interested in?"
                    variant="outlined"
                    size="medium"
                    sx={{ mb: 2 }}
                  />
                </Grid>

                {/* Resume Upload - Optional */}
                <Grid item xs={12}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Upload Resume (Optional)
                  </Typography>
                  <Box
                    sx={{
                      border: '2px dashed',
                      borderColor: dragActive ? 'primary.main' : 'grey.300',
                      borderRadius: 2,
                      p: 4,
                      textAlign: 'center',
                      backgroundColor: dragActive ? 'primary.50' : 'background.paper',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'primary.50',
                      }
                    }}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('resume-upload')?.click()}
                  >
                    <input
                      id="resume-upload"
                      type="file"
                      accept=".pdf,.doc,.docx"
                      style={{ display: 'none' }}
                      onChange={handleFileSelect}
                    />
                    <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {careerData.resumeFile ? careerData.resumeFile.name : 'Drop your resume here or click to browse'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Supported formats: PDF, DOC, DOCX (Optional - helps provide better recommendations)
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              <Button
                fullWidth
                variant="contained"
                size="large"
                sx={{ mt: 4, py: 1.5, fontSize: '1.1rem' }}
                onClick={handleAnalyze}
                disabled={isLoading || !careerData.domainInterest.trim()}
                startIcon={isLoading ? undefined : <TrendingUp />}
              >
                {isLoading ? 'Analyzing Your Career Path...' : 'Get AI Career Recommendations'}
              </Button>

              {/* Help Text */}
              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="body2">
                  💡 Just enter your domain of interest to get started. The AI will analyze job markets, 
                  identify opportunities, and provide personalized career recommendations.
                </Typography>
              </Alert>
            </Paper>
          </Grid>
        </Grid>
      ) : (
        // Results Section - Full width when showing results
        <Box>
          {/* Back to Input Button */}
          <Box sx={{ mb: 3, textAlign: 'center' }}>
            <Button
              variant="outlined"
              onClick={handleStartNewAnalysis}
              sx={{ mb: 2 }}
            >
              Start New Analysis
            </Button>
          </Box>

          {analysisResult && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              {(() => {
                const data = analysisResult.data;
                const profile = data?.user_profile || {};
                const recommendationsData = data?.recommendations || {};

                // Handle different possible structures for recommendations
                let recommendations = [];
                if (Array.isArray(recommendationsData)) {
                  recommendations = recommendationsData;
                } else if (recommendationsData.recommendations && Array.isArray(recommendationsData.recommendations)) {
                  recommendations = recommendationsData.recommendations;
                }

                return (
                  <Grid container spacing={3}>
                    {/* Domain Name Display - Top Center */}
                    <Grid item xs={12}>
                      <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Typography 
                          variant="h4" 
                          sx={{ 
                            fontWeight: 700, 
                            color: 'primary.main',
                            textTransform: 'capitalize'
                          }}
                        >
                          {profile.domain_interest || 'Domain Analysis'}
                        </Typography>
                      </Box>
                    </Grid>

                    {/* AI Career Recommendations - Multiple Boxes */}
                    <Grid item xs={12}>
                      <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                        <School color="primary" />
                        AI Career Recommendations
                      </Typography>
                      
                      {recommendations.length > 0 ? (
                        <Box>
                          <RadioGroup 
                            value={selectedRecommendation} 
                            onChange={(e) => setSelectedRecommendation(e.target.value)}
                          >
                            <Grid container spacing={3}>
                              {recommendations.map((recommendation: any, index: number) => (
                                <Grid item xs={12} md={6} key={index}>
                                  <Card sx={{ 
                                    height: '100%', 
                                    border: '2px solid', 
                                    borderColor: selectedRecommendation === recommendation.job_title ? 'primary.main' : 'primary.light',
                                    backgroundColor: selectedRecommendation === recommendation.job_title ? 'primary.50' : 'background.paper',
                                    cursor: 'pointer',
                                    transition: 'all 0.3s ease'
                                  }}>
                                    <CardContent onClick={() => setSelectedRecommendation(recommendation.job_title || `Recommendation ${index + 1}`)}>
                                      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                                        <FormControlLabel
                                          value={recommendation.job_title || `Recommendation ${index + 1}`}
                                          control={<Radio />}
                                          label=""
                                          sx={{ mr: 1 }}
                                        />
                                        <CheckCircle color="success" sx={{ mr: 1, mt: 0.5 }} />
                                        <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                                          {recommendation.job_title || recommendation.title || `Recommendation ${index + 1}`}
                                        </Typography>
                                      </Box>
                                      
                                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.6 }}>
                                        {recommendation.description || recommendation}
                                      </Typography>
                                      
                                      {recommendation.required_skills && (
                                        <Box sx={{ mb: 2 }}>
                                          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>Required Skills:</Typography>
                                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                            {recommendation.required_skills.map((skill: string, idx: number) => (
                                              <Chip key={idx} label={skill} size="small" variant="outlined" color="primary" />
                                            ))}
                                          </Box>
                                        </Box>
                                      )}
                                      
                                      {recommendation.salary_range && (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                          <AttachMoney fontSize="small" color="primary" />
                                          <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                                            {recommendation.salary_range}
                                          </Typography>
                                        </Box>
                                      )}
                                      
                                      {recommendation.market_demand && (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                          <TrendingUp fontSize="small" color="primary" />
                                          <Typography variant="body2" color="text.secondary">
                                            {recommendation.market_demand}
                                          </Typography>
                                        </Box>
                                      )}
                                    </CardContent>
                                  </Card>
                                </Grid>
                              ))}
                            </Grid>
                          </RadioGroup>
                          
                          {/* Next Button */}
                          <Box sx={{ textAlign: 'center', mt: 4 }}>
                            <Button
                              variant="contained"
                              size="large"
                              endIcon={<ArrowForward />}
                              onClick={handleProceedToRoadmap}
                              disabled={!selectedRecommendation}
                              sx={{ px: 4, py: 1.5 }}
                            >
                              Proceed to Learning Roadmap
                            </Button>
                          </Box>
                        </Box>
                      ) : (
                        <Alert severity="info" icon={<Info />}>
                          AI recommendations are being generated. This may take a moment based on your profile and market data.
                        </Alert>
                      )}
                    </Grid>
                  </Grid>
                );
              })()}
            </motion.div>
          )}
        </Box>
      )}

      {/* Loading State */}
      {isLoading && (
        <Paper sx={{ p: 4, textAlign: 'center', mt: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            🔍 Analyzing your career profile...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            AI is processing your information and searching job markets
          </Typography>
          <LinearProgress />
        </Paper>
      )}

      {/* Background Processing Indicator */}
      {showResults && isAutoProcessing && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            🚀 AI is preparing your learning roadmap and job opportunities in the background...
          </Typography>
          <LinearProgress sx={{ mt: 1 }} />
        </Alert>
      )}
    </Box>
  );
}
