import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
} from '@mui/material';
import {
  VoiceChat,
  PlayArrow,
} from '@mui/icons-material';
import { useStartVoiceInterviewMutation, useExecuteVoiceInterviewMutation } from '../store/apiSlice';

export default function InterviewBot() {
  const [showVoiceDialog, setShowVoiceDialog] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [voiceSession, setVoiceSession] = useState<any>(null);
  const [startVoiceInterview, { isLoading: isStartingVoice }] = useStartVoiceInterviewMutation();
  const [executeVoiceInterview, { isLoading: isExecutingVoice }] = useExecuteVoiceInterviewMutation();

  const handleStartVoiceInterview = async () => {
    if (!jobDescription.trim()) {
      alert('Please enter a job description first');
      return;
    }

    try {
      const result = await startVoiceInterview({
        jobDescription: jobDescription,
        resumeFile: 'resume.pdf'
      }).unwrap();

      setVoiceSession(result.data);
    } catch (error) {
      console.error('❌ Failed to start voice interview:', error);
      alert('Failed to prepare voice interview. Please try again.');
    }
  };

  const handleExecuteVoiceInterview = async () => {
    try {
      const result = await executeVoiceInterview({
        sessionId: voiceSession?.session_id
      }).unwrap();
      
      alert(`Voice Interview Instructions:\n\n${result.data.instructions.join('\n')}\n\n${result.data.note}`);
    } catch (error) {
      console.error('❌ Failed to execute voice interview:', error);
      alert('Failed to execute voice interview. Please try again.');
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 4 }}>
      <Typography variant="h3" sx={{ mb: 4, fontWeight: 700, textAlign: 'center' }}>
        AVA Voice Interview
      </Typography>

      <Card sx={{ border: '2px solid', borderColor: 'primary.main' }}>
        <CardContent sx={{ textAlign: 'center', p: 4 }}>
          <VoiceChat sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
            AI-Powered Voice Interview System
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
            Experience real-time voice interview with AI evaluation
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, mb: 3, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Chip label="15 Questions" color="primary" />
            <Chip label="Voice-to-Voice" color="secondary" />
            <Chip label="Real-time Analysis" color="info" />
          </Box>

          <Button
            variant="contained"
            size="large"
            startIcon={<VoiceChat />}
            onClick={() => setShowVoiceDialog(true)}
            sx={{ px: 4, py: 1.5 }}
          >
            Start Voice Interview
          </Button>
        </CardContent>
      </Card>

      {/* Voice Interview Dialog */}
      <Dialog 
        open={showVoiceDialog} 
        onClose={() => setShowVoiceDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          AVA Voice Interview Setup
        </DialogTitle>
        
        <DialogContent>
          {!voiceSession ? (
            <>
              <Alert severity="info" sx={{ mb: 2 }}>
                Requirements: Microphone, quiet environment, resume.pdf file
              </Alert>
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Job Description"
                placeholder="Paste job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                sx={{ mb: 2 }}
              />
              
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label="15 Questions" size="small" />
                <Chip label="AI Generated" size="small" />
                <Chip label="Voice Evaluation" size="small" />
              </Box>
            </>
          ) : (
            <>
              <Alert severity="success" sx={{ mb: 2 }}>
                Session ready: {voiceSession.session_id}
              </Alert>
              
              <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600 }}>
                Fixed Questions:
              </Typography>
              <Box sx={{ mb: 2 }}>
                {voiceSession.interview_structure?.fixed_questions?.map((question: string, index: number) => (
                  <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                    {index + 1}. {question}
                  </Typography>
                ))}
              </Box>
              
              <Alert severity="warning">
                Voice interview runs in terminal. Click Execute for instructions.
              </Alert>
            </>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setShowVoiceDialog(false)}>
            Cancel
          </Button>
          {!voiceSession ? (
            <Button
              variant="contained"
              onClick={handleStartVoiceInterview}
              disabled={!jobDescription.trim() || isStartingVoice}
            >
              {isStartingVoice ? 'Preparing...' : 'Prepare'}
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleExecuteVoiceInterview}
              disabled={isExecutingVoice}
              color="success"
              startIcon={<PlayArrow />}
            >
              {isExecutingVoice ? 'Starting...' : 'Execute'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
