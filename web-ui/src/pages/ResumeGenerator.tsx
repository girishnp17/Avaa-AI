import { useState } from 'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Paper,
  Grid,
  TextField,
  Chip,
  IconButton,
  Card,
  CardContent,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import { Add, Delete, Download, Preview } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store/store';
import {
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
} from '../store/resumeSlice';
import { useGenerateResumeMutation } from '../store/apiSlice';

const steps = ['Personal Info', 'Experience', 'Education', 'Skills', 'Generate'];

const stepVariants = {
  hidden: { opacity: 0, x: 50 },
  visible: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -50 },
};

export default function ResumeGenerator() {
  const dispatch = useDispatch();
  const { currentStep, data } = useSelector((state: RootState) => state.resume);
  const [generateResume, { isLoading, data: resumeResult }] = useGenerateResumeMutation();
  const [skillInput, setSkillInput] = useState('');

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      dispatch(setStep(currentStep + 1));
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      dispatch(setStep(currentStep - 1));
    }
  };

  const handleAddSkill = () => {
    if (skillInput.trim()) {
      dispatch(setSkills([...data.skills, skillInput.trim()]));
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (index: number) => {
    const newSkills = data.skills.filter((_, i) => i !== index);
    dispatch(setSkills(newSkills));
  };

  const handleGenerateResume = async () => {
    try {
      const result = await generateResume({
        personalInfo: data.personalInfo,
        experience: data.experience,
        education: data.education,
        skills: data.skills,
        jobDescription: data.jobDescription
      }).unwrap();
      console.log('✅ Resume generated successfully:', result);
      alert('Resume generated successfully! Check console for details.');
    } catch (error: any) {
      console.error('❌ Error generating resume:', error);
      alert('Resume generation failed: ' + (error?.data?.error || error?.message || 'Unknown error'));
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <motion.div
            key="personal"
            variants={stepVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Personal Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={data.personalInfo.fullName}
                  onChange={(e) =>
                    dispatch(updatePersonalInfo({ fullName: e.target.value }))
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={data.personalInfo.email}
                  onChange={(e) =>
                    dispatch(updatePersonalInfo({ email: e.target.value }))
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Phone"
                  value={data.personalInfo.phone}
                  onChange={(e) =>
                    dispatch(updatePersonalInfo({ phone: e.target.value }))
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Location"
                  value={data.personalInfo.location}
                  onChange={(e) =>
                    dispatch(updatePersonalInfo({ location: e.target.value }))
                  }
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Professional Summary"
                  multiline
                  rows={4}
                  value={data.personalInfo.summary}
                  onChange={(e) =>
                    dispatch(updatePersonalInfo({ summary: e.target.value }))
                  }
                />
              </Grid>
            </Grid>
          </motion.div>
        );

      case 1:
        return (
          <motion.div
            key="experience"
            variants={stepVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Work Experience
              </Typography>
              <Button
                startIcon={<Add />}
                onClick={() =>
                  dispatch(
                    addExperience({
                      company: '',
                      position: '',
                      duration: '',
                      description: '',
                    })
                  )
                }
              >
                Add Experience
              </Button>
            </Box>
            {data.experience.map((exp, index) => (
              <Card key={index} sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">Experience {index + 1}</Typography>
                    <IconButton
                      color="error"
                      onClick={() => dispatch(removeExperience(index))}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Company"
                        value={exp.company}
                        onChange={(e) =>
                          dispatch(
                            updateExperience({
                              index,
                              data: { ...exp, company: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Position"
                        value={exp.position}
                        onChange={(e) =>
                          dispatch(
                            updateExperience({
                              index,
                              data: { ...exp, position: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Duration"
                        value={exp.duration}
                        onChange={(e) =>
                          dispatch(
                            updateExperience({
                              index,
                              data: { ...exp, duration: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Description"
                        multiline
                        rows={3}
                        value={exp.description}
                        onChange={(e) =>
                          dispatch(
                            updateExperience({
                              index,
                              data: { ...exp, description: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            key="education"
            variants={stepVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Education
              </Typography>
              <Button
                startIcon={<Add />}
                onClick={() =>
                  dispatch(
                    addEducation({
                      institution: '',
                      degree: '',
                      year: '',
                    })
                  )
                }
              >
                Add Education
              </Button>
            </Box>
            {data.education.map((edu, index) => (
              <Card key={index} sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="h6">Education {index + 1}</Typography>
                    <IconButton
                      color="error"
                      onClick={() => dispatch(removeEducation(index))}
                    >
                      <Delete />
                    </IconButton>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Institution"
                        value={edu.institution}
                        onChange={(e) =>
                          dispatch(
                            updateEducation({
                              index,
                              data: { ...edu, institution: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Degree"
                        value={edu.degree}
                        onChange={(e) =>
                          dispatch(
                            updateEducation({
                              index,
                              data: { ...edu, degree: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Year"
                        value={edu.year}
                        onChange={(e) =>
                          dispatch(
                            updateEducation({
                              index,
                              data: { ...edu, year: e.target.value },
                            })
                          )
                        }
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            key="skills"
            variants={stepVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Skills & Job Target
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField
                    fullWidth
                    label="Add Skill"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                  />
                  <Button variant="contained" onClick={handleAddSkill}>
                    Add
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                  {data.skills.map((skill, index) => (
                    <Chip
                      key={index}
                      label={skill}
                      onDelete={() => handleRemoveSkill(index)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target Job Description (Optional)"
                  multiline
                  rows={6}
                  value={data.jobDescription}
                  onChange={(e) => dispatch(setJobDescription(e.target.value))}
                  helperText="Paste a job description to optimize your resume for ATS"
                />
              </Grid>
            </Grid>
          </motion.div>
        );

      case 4:
        return (
          <motion.div
            key="generate"
            variants={stepVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                Generate Your Resume
              </Typography>
              <Typography variant="body1" sx={{ mb: 4, color: 'text.secondary' }}>
                Review your information and generate your AI-optimized resume
              </Typography>
              
              {isLoading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                  <CircularProgress size={60} />
                  <Typography>Generating your resume...</Typography>
                </Box>
              ) : (
                <Box>
                  <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 3 }}>
                    <Button
                      variant="outlined"
                      startIcon={<Preview />}
                      size="large"
                    >
                      Preview
                    </Button>
                    <Button
                      variant="contained"
                      startIcon={<Download />}
                      size="large"
                      onClick={handleGenerateResume}
                      disabled={isLoading}
                    >
                      {isLoading ? 'Generating Resume...' : 'Generate PDF'}
                    </Button>
                  </Box>

                  {resumeResult && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6 }}
                    >
                      <Card sx={{ mt: 3, p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                          Resume Generation Result
                        </Typography>
                        
                        {resumeResult.success ? (
                          <Box>
                            <Typography variant="body1" color="success.main" sx={{ mb: 2 }}>
                              ✅ {resumeResult.data?.message || 'Resume generated successfully!'}
                            </Typography>
                            
                            {resumeResult.data?.pdf_path && (
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                📄 PDF saved to: {resumeResult.data.pdf_path}
                              </Typography>
                            )}
                            
                            <Button
                              variant="outlined"
                              startIcon={<Download />}
                              onClick={() => alert('Resume download feature coming soon!')}
                            >
                              Download Resume
                            </Button>
                          </Box>
                        ) : (
                          <Typography variant="body1" color="error.main">
                            ❌ {resumeResult.error || 'Resume generation failed'}
                          </Typography>
                        )}
                      </Card>
                    </motion.div>
                  )}

                  {isLoading && (
                    <Card sx={{ mt: 3, p: 3, textAlign: 'center' }}>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        🤖 AI is generating your resume...
                      </Typography>
                      <LinearProgress />
                    </Card>
                  )}
                </Box>
              )}
            </Box>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, textAlign: 'center' }}>
        AI Resume Generator
      </Typography>

      <Paper sx={{ p: 4, mb: 4 }}>
        <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <AnimatePresence mode="wait">
          {renderStepContent()}
        </AnimatePresence>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={currentStep === 0}
            onClick={handleBack}
            variant="outlined"
          >
            Back
          </Button>
          <Button
            disabled={currentStep === steps.length - 1}
            onClick={handleNext}
            variant="contained"
          >
            Next
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
