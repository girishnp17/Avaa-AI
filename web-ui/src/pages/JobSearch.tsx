import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Alert,
  Button,
  Divider,
  Badge,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Business,
  LocationOn,
  AttachMoney,
  Work,
  Schedule,
  TrendingUp,
  Star,
  Language,
  Search,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useSearchJobsMutation } from '../store/apiSlice';

interface JobSearchData {
  query: string;
  location: string;
}

export default function JobSearch() {
  const [searchData, setSearchData] = useState<JobSearchData>({
    query: '',
    location: '',
  });
  const [searchJobs, { data: jobResults, isLoading }] = useSearchJobsMutation();

  const handleSearch = async () => {
    if (searchData.query.trim() && searchData.location.trim()) {
      console.log('🔍 Searching jobs for:', searchData.query, 'in', searchData.location);
      try {
        await searchJobs({
          query: searchData.query.trim(),
          location: searchData.location.trim()
        }).unwrap();
        console.log('✅ Job search completed');
      } catch (error) {
        console.error('❌ Job search failed:', error);
      }
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const renderJobCard = (job: any, index: number) => (
    <Grid item xs={12} md={6} lg={4} key={index}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.1 }}
      >
        <Card 
          sx={{ 
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            border: '1px solid',
            borderColor: 'primary.light',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: 4,
              borderColor: 'primary.main'
            }
          }}
        >
          <CardContent sx={{ flexGrow: 1, p: 3 }}>
            {/* Job Header */}
            <Box sx={{ mb: 2 }}>
              <Typography 
                variant="h6" 
                sx={{ 
                  fontWeight: 700, 
                  mb: 1, 
                  color: 'primary.main',
                  lineHeight: 1.3,
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                {job.title}
              </Typography>

              {/* AI Score Badge */}
              {job.aiScore && (
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Badge 
                    badgeContent={`${Math.round(job.aiScore)}%`} 
                    color={job.aiScore >= 80 ? 'success' : job.aiScore >= 60 ? 'warning' : 'error'}
                    sx={{ '& .MuiBadge-badge': { fontSize: '0.7rem', fontWeight: 600 } }}
                  >
                    <Chip 
                      label="AI Match" 
                      size="small" 
                      color={job.aiScore >= 80 ? 'success' : job.aiScore >= 60 ? 'warning' : 'error'}
                      icon={<Star />}
                    />
                  </Badge>
                  
                  {job.source && (
                    <Chip 
                      label={job.source} 
                      size="small" 
                      variant="outlined"
                      color="primary"
                    />
                  )}
                </Box>
              )}
            </Box>

            {/* Company */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Business fontSize="small" color="action" />
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {job.company}
              </Typography>
            </Box>

            {/* Location */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <LocationOn fontSize="small" color="primary" />
              <Typography variant="body2" color="text.secondary">
                {job.location}
              </Typography>
            </Box>

            {/* Salary */}
            {job.salary && job.salary !== 'Not specified' && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <AttachMoney fontSize="small" color="success" />
                <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                  {job.salary}
                </Typography>
              </Box>
            )}

            {/* Job Type & Posted Date */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              {job.jobType && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Work fontSize="small" color="primary" />
                  <Typography variant="body2" color="primary.main" sx={{ fontWeight: 500 }}>
                    {job.jobType}
                  </Typography>
                </Box>
              )}
              
              {job.postedDate && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Schedule fontSize="small" color="action" />
                  <Typography variant="caption" color="text.secondary">
                    {job.postedDate}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Job Description */}
            {job.description && (
              <Box sx={{ mb: 2 }}>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    lineHeight: 1.5,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}
                >
                  {job.description}
                </Typography>
              </Box>
            )}

            {/* Match Analysis */}
            {job.matchAnalysis && (
              <Box sx={{ mb: 2 }}>
                <Alert severity="info" sx={{ p: 1 }}>
                  <Typography variant="caption">
                    <strong>AI Analysis:</strong> {job.matchAnalysis}
                  </Typography>
                </Alert>
              </Box>
            )}

            <Divider sx={{ my: 2 }} />

            {/* Apply Button */}
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="contained"
                fullWidth
                startIcon={<Language />}
                onClick={() => job.url && window.open(job.url, '_blank')}
                sx={{ 
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                View Job Details
              </Button>
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    </Grid>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
          Job Search
        </Typography>
        <Typography variant="h6" sx={{ color: 'text.secondary', mb: 4 }}>
          Find your perfect job opportunity
        </Typography>
        
        {/* Search Form */}
        <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="Job Title / Role"
                value={searchData.query}
                onChange={(e) => setSearchData(prev => ({ ...prev, query: e.target.value }))}
                placeholder="e.g., Software Engineer, Data Scientist, Marketing Manager"
                fullWidth
                required
                onKeyPress={handleKeyPress}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Work color="primary" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Location"
                value={searchData.location}
                onChange={(e) => setSearchData(prev => ({ ...prev, location: e.target.value }))}
                placeholder="e.g., New York, London, Remote, San Francisco"
                fullWidth
                required
                onKeyPress={handleKeyPress}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LocationOn color="primary" />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                size="large"
                onClick={handleSearch}
                disabled={isLoading || !searchData.query.trim() || !searchData.location.trim()}
                startIcon={<Search />}
                fullWidth
                sx={{ 
                  py: 1.5,
                  fontSize: '1.1rem',
                  fontWeight: 600
                }}
              >
                {isLoading ? 'Searching...' : 'Search Jobs'}
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Paper sx={{ p: 4, textAlign: 'center', mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            🔍 Searching for {searchData.query} jobs in {searchData.location}...
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            AI is analyzing job listings from multiple sources
          </Typography>
          <LinearProgress />
        </Paper>
      )}

      {/* Job Results */}
      {jobResults && !isLoading && (
        <Box>
          {/* Results Header */}
          <Paper sx={{ p: 3, mb: 4, bgcolor: 'primary.50', borderLeft: '4px solid', borderColor: 'primary.main' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <Typography variant="h5" sx={{ fontWeight: 600, color: 'primary.main' }}>
                  🎯 {jobResults.data?.total_found || jobResults.data?.jobs?.length || 0} Jobs Found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {searchData.query} positions in {searchData.location}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}>
                  <Chip 
                    label={`📍 ${searchData.location}`} 
                    color="primary" 
                    variant="outlined" 
                    size="small" 
                  />
                  <Chip 
                    label="🤖 AI Ranked" 
                    color="success" 
                    variant="outlined" 
                    size="small" 
                  />
                  <Chip 
                    label="🔥 Fresh Results" 
                    color="warning" 
                    variant="outlined" 
                    size="small" 
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Job Cards Grid */}
          <Grid container spacing={3}>
            {(() => {
              const jobs = jobResults.data?.jobs || [];
              
              // Sort jobs by AI score and relevance
              const sortedJobs = jobs.sort((a: any, b: any) => {
                const aScore = (a.aiScore || 0) + 
                              (a.salary && a.salary !== 'Not specified' ? 10 : 0) + 
                              (a.title.toLowerCase().includes(searchData.query.toLowerCase()) ? 15 : 0);
                const bScore = (b.aiScore || 0) + 
                              (b.salary && b.salary !== 'Not specified' ? 10 : 0) + 
                              (b.title.toLowerCase().includes(searchData.query.toLowerCase()) ? 15 : 0);
                return bScore - aScore;
              });

              return sortedJobs.map((job: any, index: number) => renderJobCard(job, index));
            })()}
          </Grid>

          {/* AI Analysis Section */}
          {jobResults.data?.ai_analysis && (
            <Paper sx={{ p: 3, mt: 4, bgcolor: 'background.default', border: '1px solid', borderColor: 'primary.light' }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp color="primary" />
                AI Market Analysis
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                {jobResults.data.ai_analysis}
              </Typography>
            </Paper>
          )}
        </Box>
      )}

      {/* No Results State */}
      {!isLoading && !jobResults && (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <Work sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
            Ready to Find Your Dream Job
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Enter a job title and location to start searching
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Chip label="Multi-Source Search" color="primary" />
            <Chip label="AI-Powered Matching" color="primary" />
            <Chip label="Real-Time Results" color="primary" />
            <Chip label="Salary Insights" color="primary" />
          </Box>
        </Paper>
      )}
    </Box>
  );
}
