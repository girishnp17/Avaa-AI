import { Box, Typography, Grid, Card, CardContent, Button, Container } from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Description,
  Work,
  School,
  Search,
  Psychology,
  TrendingUp,
} from '@mui/icons-material';

const tools = [
  {
    title: 'Career Guidance',
    description: 'Get personalized career advice and market insights',
    icon: <Work sx={{ fontSize: 48 }} />,
    path: '/career',
    color: '#dc004e',
    gradient: 'linear-gradient(135deg, #dc004e 0%, #ff5983 100%)',
  },
  {
    title: 'Learning Roadmap',
    description: 'Create structured learning paths for skill development',
    icon: <School sx={{ fontSize: 48 }} />,
    path: '/roadmap',
    color: '#2e7d32',
    gradient: 'linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%)',
  },
  {
    title: 'Job Search',
    description: 'Find relevant jobs with AI-powered matching and analysis',
    icon: <Search sx={{ fontSize: 48 }} />,
    path: '/jobs',
    color: '#ed6c02',
    gradient: 'linear-gradient(135deg, #ed6c02 0%, #ffb74d 100%)',
  },
  {
    title: 'AI Resume Generator',
    description: 'Create ATS-optimized resumes with AI-powered content generation',
    icon: <Description sx={{ fontSize: 48 }} />,
    path: '/resume',
    color: '#1976d2',
    gradient: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
  },
  {
    title: 'Interview Bot',
    description: 'Practice interviews with AI-powered feedback and coaching',
    icon: <Psychology sx={{ fontSize: 48 }} />,
    path: '/interview',
    color: '#9c27b0',
    gradient: 'linear-gradient(135deg, #9c27b0 0%, #ce93d8 100%)',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 8,
          mb: 6,
          borderRadius: 4,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Container maxWidth="lg">
            <Typography
              variant="h1"
              component="h1"
              sx={{
                textAlign: 'center',
                mb: 3,
                fontSize: { xs: '2.5rem', md: '3.5rem' },
                fontWeight: 700,
                background: 'linear-gradient(45deg, #fff 30%, #e3f2fd 90%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              AI-Powered Career Tools
            </Typography>
            <Typography
              variant="h5"
              sx={{
                textAlign: 'center',
                mb: 4,
                opacity: 0.9,
                maxWidth: 800,
                mx: 'auto',
                lineHeight: 1.6,
              }}
            >
              Transform your career journey with cutting-edge AI technology. From resume generation
              to interview preparation, we've got you covered.
            </Typography>
            <Box sx={{ textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.2)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontSize: '1.1rem',
                  '&:hover': {
                    backgroundColor: 'rgba(255,255,255,0.3)',
                  },
                }}
                onClick={() => navigate('/resume')}
              >
                Get Started
              </Button>
            </Box>
          </Container>
        </motion.div>
      </Box>

      {/* Tools Grid */}
      <Container maxWidth="lg">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Typography
            variant="h2"
            component="h2"
            sx={{
              textAlign: 'center',
              mb: 6,
              fontSize: { xs: '2rem', md: '2.5rem' },
              fontWeight: 600,
              color: 'text.primary',
            }}
          >
            Choose Your AI Tool
          </Typography>

          <Grid container spacing={4}>
            {tools.map((tool, index) => (
              <Grid item xs={12} sm={6} lg={4} key={tool.title}>
                <motion.div variants={itemVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      cursor: 'pointer',
                      position: 'relative',
                      overflow: 'hidden',
                      '&:hover': {
                        '& .tool-icon': {
                          transform: 'scale(1.1) rotate(5deg)',
                        },
                        '& .gradient-overlay': {
                          opacity: 0.1,
                        },
                      },
                    }}
                    onClick={() => navigate(tool.path)}
                  >
                    <Box
                      className="gradient-overlay"
                      sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: tool.gradient,
                        opacity: 0,
                        transition: 'opacity 0.3s ease',
                      }}
                    />
                    <CardContent sx={{ p: 4, position: 'relative', zIndex: 1 }}>
                      <Box
                        className="tool-icon"
                        sx={{
                          color: tool.color,
                          mb: 3,
                          transition: 'transform 0.3s ease',
                          display: 'flex',
                          justifyContent: 'center',
                        }}
                      >
                        {tool.icon}
                      </Box>
                      <Typography
                        variant="h5"
                        component="h3"
                        sx={{
                          fontWeight: 600,
                          mb: 2,
                          textAlign: 'center',
                          color: 'text.primary',
                        }}
                      >
                        {tool.title}
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: 'text.secondary',
                          textAlign: 'center',
                          lineHeight: 1.6,
                        }}
                      >
                        {tool.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* Stats Section */}
      <Box sx={{ mt: 8, py: 6, backgroundColor: 'background.paper', borderRadius: 4 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} sx={{ textAlign: 'center' }}>
            <Grid item xs={12} sm={4}>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main', mb: 1 }}>
                10K+
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                Resumes Generated
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'secondary.main', mb: 1 }}>
                95%
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                Success Rate
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main', mb: 1 }}>
                24/7
              </Typography>
              <Typography variant="h6" sx={{ color: 'text.secondary' }}>
                AI Assistance
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
