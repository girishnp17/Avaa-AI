import React from 'react';
import { Box, Button, Typography, CircularProgress, Alert } from '@mui/material';
import { Mic, MicOff } from '@mui/icons-material';
import { TranscriptionResult } from '../../services/voiceInterviewSocket';

interface AudioRecorderProps {
  onRecordingComplete?: (transcription: string) => void;
  disabled?: boolean;
  // Recording state
  isRecording: boolean;
  isProcessingAudio: boolean;
  isTranscribing: boolean;
  currentTranscription: TranscriptionResult | null;
  error: string | null;
  // Recording functions
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  clearError: () => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  disabled = false,
  isRecording,
  isProcessingAudio,
  isTranscribing,
  currentTranscription,
  error,
  startRecording,
  stopRecording,
  clearError
}) => {

  const handleStartRecording = async () => {
    if (error) clearError();
    console.log('🎤 Starting recording...');
    try {
      await startRecording();
      console.log('✅ Recording started successfully');
    } catch (err) {
      console.error('❌ Recording failed:', err);
    }
  };

  const handleStopRecording = () => {
    stopRecording();
  };

  React.useEffect(() => {
    if (currentTranscription && onRecordingComplete) {
      onRecordingComplete(currentTranscription.transcription);
    }
  }, [currentTranscription, onRecordingComplete]);

  const getRecordingStatus = () => {
    if (isRecording) return 'Recording...';
    if (isProcessingAudio) return 'Processing audio...';
    if (isTranscribing) return 'Transcribing...';
    return 'Ready to record';
  };

  const isProcessing = isProcessingAudio || isTranscribing;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      {error && (
        <Alert severity="error" onClose={clearError} sx={{ width: '100%' }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {!isRecording ? (
          <Button
            variant="contained"
            color="primary"
            onClick={handleStartRecording}
            disabled={disabled || isProcessing}
            startIcon={<Mic />}
            size="large"
            sx={{
              borderRadius: '50px',
              minWidth: '140px',
              height: '50px'
            }}
          >
            Start Recording
          </Button>
        ) : (
          <Button
            variant="contained"
            color="error"
            onClick={handleStopRecording}
            startIcon={<MicOff />}
            size="large"
            sx={{
              borderRadius: '50px',
              minWidth: '140px',
              height: '50px',
              animation: 'pulse 1.5s infinite'
            }}
          >
            Stop Recording
          </Button>
        )}

        {isProcessing && (
          <CircularProgress size={24} />
        )}
      </Box>

      <Typography
        variant="body2"
        color="textSecondary"
        sx={{ textAlign: 'center' }}
      >
        {getRecordingStatus()}
      </Typography>

      {currentTranscription && (
        <Box
          sx={{
            p: 2,
            backgroundColor: 'background.paper',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
            maxWidth: '100%',
            width: '400px'
          }}
        >
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Your response:
          </Typography>
          <Typography variant="body1">
            "{currentTranscription.transcription}"
          </Typography>
        </Box>
      )}

      <style>{`
        @keyframes pulse {
          0% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.05);
          }
          100% {
            transform: scale(1);
          }
        }
      `}</style>
    </Box>
  );
};