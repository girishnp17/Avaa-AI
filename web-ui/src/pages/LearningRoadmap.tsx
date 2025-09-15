import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Chip,
  LinearProgress,
  Alert,
  Badge,
  Rating,
} from '@mui/material';
import {
  School,
  PlayArrow,
  ArrowForward,
  Timeline,
  Language,
  AttachMoney,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useCreateRoadmapMutation } from '../store/apiSlice';
import { useNavigate } from 'react-router-dom';

interface RoadmapFormData {
  subject: string;
  currentSkills: string;
  goals: string;
}

interface CourseInterface {
  title: string;
  description: string;
  platform: string;
  rating: string;
  price: string;
  skills_gained: string[];
  url: string;
  duration: string;
  level: string;
}

interface RoadmapStep {
  step_number: number;
  title: string;
  description: string;
  duration: string;
  skills_to_learn: string[];
  key_topics: string[];
  learning_objectives: string[];
  difficulty_level: string;
}

interface RoadmapDataInterface {
  roadmap_title: string;
  steps: RoadmapStep[];
  prerequisites: string[];
  career_outcomes: string[];
  salary_range: string;
  total_duration: string;
}

export default function LearningRoadmap() {
  const [formData, setFormData] = useState<RoadmapFormData>({
    subject: '',
    currentSkills: '',
    goals: '',
  });
  const [showResults, setShowResults] = useState(false);
  const [preloadedRoadmap, setPreloadedRoadmap] = useState<any>(null);
  const [createRoadmap, { data: roadmapResult, isLoading, error }] = useCreateRoadmapMutation();
  const navigate = useNavigate();

  // Check for pre-generated roadmap and stored domain on component mount
  useEffect(() => {
    const selectedCareer = localStorage.getItem('selectedCareer');
    const storedDomain = localStorage.getItem('careerDomain');
    const preGeneratedRoadmap = localStorage.getItem('preGeneratedRoadmap');

    // PRIORITY: Use selected career recommendation first, then fallback to domain
    const subjectToUse = selectedCareer || storedDomain;
    
    if (subjectToUse) {
      setFormData({
        subject: subjectToUse,
        currentSkills: '',
        goals: `Master ${subjectToUse} skills and become a professional`
      });

      console.log('🎯 Using selected career for roadmap:', subjectToUse);

      // If we have pre-generated roadmap, use it
      if (preGeneratedRoadmap) {
        try {
          const parsedRoadmap = JSON.parse(preGeneratedRoadmap);
          setPreloadedRoadmap(parsedRoadmap);
          setShowResults(true);
          console.log('✅ Using pre-generated roadmap for:', subjectToUse);
        } catch (error) {
          console.log('⚠️ Failed to parse pre-generated roadmap, will generate new one');
          handleAutoGenerate(subjectToUse, '');
        }
      } else {
        // Auto-generate roadmap using SELECTED career
        handleAutoGenerate(subjectToUse, '');
      }
    }
  }, []);

  const handleAutoGenerate = async (subject: string, skills: string) => {
    try {
      console.log('🚀 Auto-generating roadmap for SELECTED career:', subject);
      await createRoadmap({
        subject: subject,  // This will be "Python Freelance" or "Backend Developer"
        currentSkills: skills,
        goals: `Master ${subject} skills and become a professional ${subject}`
      }).unwrap();
      console.log('✅ Roadmap auto-generated successfully for:', subject);
      setShowResults(true);
    } catch (error) {
      console.error('❌ Auto roadmap generation failed:', error);
    }
  };

  const handleProceedToJobSearch = () => {
    navigate('/jobs');
  };

  const renderCourseCard = (course: any, index: number) => (
    <Grid item xs={12} sm={6} lg={4} key={index}>
      <Card 
        sx={{ 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: 4
          }
        }}
      >
        <CardContent sx={{ flexGrow: 1 }}>
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600, lineHeight: 1.3 }}>
            {course.title}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.4 }}>
            {course.description}
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            {course.platform && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <School fontSize="small" color="primary" />
                <Typography variant="body2">{course.platform}</Typography>
              </Box>
            )}
            
            {course.rating && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Rating value={parseFloat(course.rating)} readOnly size="small" />
                <Typography variant="body2">({course.rating})</Typography>
              </Box>
            )}
            
            {course.price && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <AttachMoney fontSize="small" color="primary" />
                <Typography variant="body2">{course.price}</Typography>
              </Box>
            )}
          </Box>
          
          {course.skills_gained && course.skills_gained.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                Skills you'll gain:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {course.skills_gained.slice(0, 3).map((skill: string, idx: number) => (
                  <Chip
                    key={idx}
                    label={skill}
                    size="small"
                    variant="outlined"
                    color="primary"
                  />
                ))}
                {course.skills_gained.length > 3 && (
                  <Chip
                    label={`+${course.skills_gained.length - 3} more`}
                    size="small"
                    variant="outlined"
                    color="secondary"
                  />
                )}
              </Box>
            </Box>
          )}
        </CardContent>
        
        <Box sx={{ p: 2, pt: 0 }}>
          <Button 
            variant="contained" 
            fullWidth
            startIcon={<Language />}
            onClick={() => course.url && window.open(course.url, '_blank')}
            sx={{ borderRadius: 2 }}
          >
            View Course
          </Button>
        </Box>
      </Card>
    </Grid>
  );

  // Use preloaded roadmap or API result
  const currentRoadmap = preloadedRoadmap || roadmapResult;

  // Helper function to safely get roadmap data
  const getRoadmapData = () => {
    if (!currentRoadmap) return null;
    
    // Handle different response structures from the course recommender
    const data = currentRoadmap.data || currentRoadmap;
    
    // The course recommender returns roadmap data directly in data.roadmap
    return data.roadmap || data;
  };

  const parsedRoadmapData = getRoadmapData();

  // Get courses by step and all courses from the enhanced course recommender response
  const getCoursesData = () => {
    if (!currentRoadmap) return { coursesByStep: {}, allCourses: [], summary: {} };
    
    const data = currentRoadmap.data || currentRoadmap;
    
    return {
      coursesByStep: data.courses_by_step || {},
      allCourses: data.course_recommendations || [],
      summary: data.summary || {}
    };
  };

  const { coursesByStep, allCourses, summary } = getCoursesData();

  return (
    <Box>
      {/* Domain Display */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
          Learning Roadmap
        </Typography>
        {formData.subject && (
          <Typography variant="h5" sx={{ color: 'primary.main', fontWeight: 600 }}>
            {formData.subject} Career Path
          </Typography>
        )}
      </Box>

      {/* Auto-generation indicator */}
      {isLoading && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            🎯 AI is creating your personalized 8-step learning roadmap with real courses...
          </Typography>
          <LinearProgress sx={{ mt: 1 }} />
        </Alert>
      )}

      {/* Loading State */}
      {!showResults && !formData.subject && (
        <Paper sx={{ p: 4, textAlign: 'center', mb: 4 }}>
          <School sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
            Loading Your Learning Plan...
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Please wait while we generate your personalized roadmap
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Chip label="Personalized Roadmap" color="primary" />
            <Chip label="Course Recommendations" color="primary" />
            <Chip label="Career Guidance" color="primary" />
            <Chip label="AI-Powered" color="primary" />
          </Box>
        </Paper>
      )}

      {/* Results Display */}
      {parsedRoadmapData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {(() => {
            // Get course recommendations from the current roadmap response
            const responseData = currentRoadmap?.data || currentRoadmap;
            const courseRecommendations = responseData?.course_recommendations || [];
            
            return (
              <>
                {/* Roadmap Overview */}
                <Paper sx={{ p: 3, mb: 4 }}>
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Timeline color="primary" />
                    {parsedRoadmapData.roadmap_title || 'Learning Roadmap'}
                  </Typography>

                  {/* Enhanced Roadmap Summary */}
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h6" color="primary.main">{parsedRoadmapData.steps?.length || 8}</Typography>
                        <Typography variant="body2">Learning Steps</Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h6" color="success.main">{parsedRoadmapData.total_duration || '8-12 months'}</Typography>
                        <Typography variant="body2">Total Duration</Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h6" color="warning.main">{courseRecommendations.length}</Typography>
                        <Typography variant="body2">Courses Found</Typography>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h6" color="info.main">{parsedRoadmapData.salary_range || 'Competitive'}</Typography>
                        <Typography variant="body2">Salary Range</Typography>
                      </Card>
                    </Grid>
                  </Grid>

                  {/* Quality Metrics */}
                  {responseData?.summary && (
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} sm={4}>
                        <Card sx={{ p: 2, textAlign: 'center', bgcolor: 'success.50' }}>
                          <Typography variant="h6" color="success.main">
                            {responseData.summary.quality_verified_courses || 0}
                          </Typography>
                          <Typography variant="body2">Quality Verified</Typography>
                        </Card>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Card sx={{ p: 2, textAlign: 'center', bgcolor: 'info.50' }}>
                          <Typography variant="h6" color="info.main">
                            {responseData.summary.platform_breakdown?.university || 0}
                          </Typography>
                          <Typography variant="body2">University Courses</Typography>
                        </Card>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Card sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.50' }}>
                          <Typography variant="h6" color="warning.main">
                            {responseData.summary.platform_breakdown?.free || 0}
                          </Typography>
                          <Typography variant="body2">Free Courses</Typography>
                        </Card>
                      </Grid>
                    </Grid>
                  )}
                </Paper>

                {/* 8-Step Learning Roadmap */}
                <Paper sx={{ p: 3, mb: 4 }}>
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <School color="primary" />
                    8-Step Learning Path
                  </Typography>

                  {parsedRoadmapData?.steps && (
                    <Stepper orientation="vertical">
                      {parsedRoadmapData.steps.map((step, index) => (
                        <Step key={index} active={true}>
                          <StepLabel>
                            <Typography variant="h6" sx={{ fontWeight: 600 }}>
                              Step {step.step_number}: {step.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Duration: {step.duration} | Level: {step.difficulty_level}
                            </Typography>
                          </StepLabel>
                          <StepContent>
                            <Card sx={{ mt: 2, mb: 3 }}>
                              <CardContent>
                                <Typography variant="body1" sx={{ mb: 2 }}>
                                  {step.description}
                                </Typography>
                                
                                {/* Skills to Learn */}
                                {step.skills_to_learn && (
                                  <>
                                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                                      Skills to Learn:
                                    </Typography>
                                    <Box sx={{ mb: 3 }}>
                                      {step.skills_to_learn.map((skill, idx) => (
                                        <Chip
                                          key={idx}
                                          label={skill}
                                          color="primary"
                                          variant="outlined"
                                          sx={{ mr: 1, mb: 1 }}
                                        />
                                      ))}
                                    </Box>
                                  </>
                                )}

                                {/* Key Topics */}
                                {step.key_topics && (
                                  <>
                                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                                      Key Topics:
                                    </Typography>
                                    <Box sx={{ mb: 3 }}>
                                      {step.key_topics.map((topic, idx) => (
                                        <Chip
                                          key={idx}
                                          label={topic}
                                          color="secondary"
                                          variant="outlined"
                                          sx={{ mr: 1, mb: 1 }}
                                        />
                                      ))}
                                    </Box>
                                  </>
                                )}

                                {/* Learning Objectives */}
                                {step.learning_objectives && (
                                  <>
                                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                                      Learning Objectives:
                                    </Typography>
                                    <Box component="ul" sx={{ mb: 3, pl: 2 }}>
                                      {step.learning_objectives.map((objective, idx) => (
                                        <Typography key={idx} component="li" variant="body2" sx={{ mb: 1 }}>
                                          {objective}
                                        </Typography>
                                      ))}
                                    </Box>
                                  </>
                                )}

                                {/* Courses for this Step */}
                                {coursesByStep[`step_${step.step_number}`] && coursesByStep[`step_${step.step_number}`].length > 0 && (
                                  <>
                                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                                      Recommended Courses for this Step:
                                    </Typography>
                                    <Grid container spacing={2} sx={{ mb: 3 }}>
                                      {coursesByStep[`step_${step.step_number}`].slice(0, 3).map((course, courseIdx) => (
                                        <Grid item xs={12} md={4} key={courseIdx}>
                                          <Card sx={{ height: '100%', border: '1px solid', borderColor: 'primary.light' }}>
                                            <CardContent sx={{ p: 2 }}>
                                              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, fontSize: '0.9rem' }}>
                                                {course.title}
                                              </Typography>
                                              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                                                {course.platform} • {course.duration}
                                              </Typography>
                                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                                <Typography variant="caption" color="success.main">{course.price}</Typography>
                                                <Typography variant="caption">{course.rating}</Typography>
                                              </Box>
                                              <Button 
                                                size="small" 
                                                variant="outlined" 
                                                fullWidth
                                                onClick={() => course.url && window.open(course.url, '_blank')}
                                                sx={{ fontSize: '0.8rem' }}
                                              >
                                                View Course
                                              </Button>
                                            </CardContent>
                                          </Card>
                                        </Grid>
                                      ))}
                                    </Grid>
                                  </>
                                )}
                                
                                <Button
                                  variant="contained"
                                  startIcon={<PlayArrow />}
                                  sx={{ mt: 2 }}
                                >
                                  Start Step {step.step_number}
                                </Button>
                              </CardContent>
                            </Card>
                          </StepContent>
                        </Step>
                      ))}
                    </Stepper>
                  )}
                </Paper>

                {/* All Course Recommendations Section */}
                {courseRecommendations && courseRecommendations.length > 0 && (
                  <Paper sx={{ p: 3, mb: 4 }}>
                    <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <School color="primary" />
                      All Recommended Courses
                      <Badge badgeContent={courseRecommendations.length} color="primary" />
                    </Typography>

                    <Grid container spacing={3}>
                      {courseRecommendations.map((course, index) => 
                        renderCourseCard(course, index)
                      )}
                    </Grid>
                  </Paper>
                )}

                {/* Career Outcomes */}
                {parsedRoadmapData?.career_outcomes && parsedRoadmapData.career_outcomes.length > 0 && (
                  <Paper sx={{ p: 3, mb: 4 }}>
                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                      Career Outcomes
                    </Typography>
                    <Grid container spacing={1}>
                      {parsedRoadmapData.career_outcomes.map((outcome, index) => (
                        <Grid item key={index}>
                          <Chip
                            label={outcome}
                            color="success"
                            variant="outlined"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        </Grid>
                      ))}
                    </Grid>
                  </Paper>
                )}
              </>
            );
          })()}
        </motion.div>
      )}

      {/* Proceed Button */}
      {showResults && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button
            variant="contained"
            color="secondary"
            endIcon={<ArrowForward />}
            onClick={handleProceedToJobSearch}
            sx={{ px: 4, py: 1.5 }}
          >
            Proceed to Job Search
          </Button>
        </Box>
      )}
    </Box>
  );
}
