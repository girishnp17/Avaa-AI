import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Divider,
  Paper
} from '@mui/material';
import { VolumeUp } from '@mui/icons-material';
import { useVoiceInterview } from '../../hooks/useVoiceInterview';
import { AudioRecorder } from './AudioRecorder';

interface VoiceInterviewSessionProps {
  jobDescription: string;
  resumePath?: string;
  onComplete?: (report: any) => void;
}

export const VoiceInterviewSession: React.FC<VoiceInterviewSessionProps> = ({
  jobDescription,
  resumePath = 'resume.pdf',
  onComplete
}) => {
  const {
    isConnected,
    isConnecting,
    connectionError,
    session,
    currentQuestion,
    sessionStatus,
    interviewReport,
    isCompleted,
    error,
    connect,
    createSession,
    getNextQuestion,
    endInterview,
    getSessionStatus,
    clearError,
    // Recording state and functions for AudioRecorder
    isRecording,
    isProcessingAudio,
    isTranscribing,
    currentTranscription,
    startRecording,
    stopRecording
  } = useVoiceInterview();

  const [isInitialized, setIsInitialized] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (!isInitialized && !isConnected && !isConnecting) {
      connect();
      setIsInitialized(true);
    }
  }, [isInitialized, isConnected, isConnecting, connect]);

  useEffect(() => {
    if (isConnected && !session) {
      createSession(jobDescription, resumePath);
    }
  }, [isConnected, session, jobDescription, resumePath, createSession]);

  useEffect(() => {
    if (session && !currentQuestion) {
      getNextQuestion();
    }
  }, [session, currentQuestion, getNextQuestion]);

  // Auto-play question audio when a new question is received
  useEffect(() => {
    if (currentQuestion) {
      // Small delay to ensure UI has updated
      const timer = setTimeout(() => {
        playQuestionAudio(); // This will try Gemini audio first, then Web Speech fallback
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [currentQuestion]);

  useEffect(() => {
    if (session?.session_id) {
      const interval = setInterval(() => {
        getSessionStatus();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [session?.session_id, getSessionStatus]);

  useEffect(() => {
    if (interviewReport && onComplete) {
      onComplete(interviewReport);
    }
  }, [interviewReport, onComplete]);

  const playQuestionAudio = () => {
    if (currentQuestion?.has_audio && currentQuestion.audio_data) {
      if (audioElement) {
        audioElement.pause();
      }

      // Try different audio formats that browsers can handle - MP3 first since backend converts to MP3
      const audioFormats = [
        `data:audio/mpeg;base64,${currentQuestion.audio_data}`,
        `data:audio/mp3;base64,${currentQuestion.audio_data}`,
        `data:audio/wav;base64,${currentQuestion.audio_data}`,
        `data:audio/ogg;base64,${currentQuestion.audio_data}`
      ];

      let formatIndex = 0;
      const tryNextFormat = () => {
        if (formatIndex < audioFormats.length) {
          const audio = new Audio(audioFormats[formatIndex]);
          setAudioElement(audio);

          audio.addEventListener('canplaythrough', () => {
            console.log(`✅ Audio format ${formatIndex} (${audioFormats[formatIndex].split(';')[0]}) is playable`);
            audio.play().catch(error => {
              console.error('Error playing audio:', error);
              // If all audio formats fail, try Web Speech API fallback
              tryWebSpeechFallback();
            });
          });

          audio.addEventListener('error', (error) => {
            console.log(`❌ Audio format ${formatIndex} failed, trying next...`);
            formatIndex++;
            tryNextFormat();
          });

          audio.load();
        } else {
          console.log('❌ All audio formats failed, trying Web Speech API fallback...');
          tryWebSpeechFallback();
        }
      };

      tryNextFormat();
    } else {
      // No audio data available, use Web Speech API fallback
      tryWebSpeechFallback();
    }
  };

  const tryWebSpeechFallback = () => {
    if (currentQuestion?.question_text && 'speechSynthesis' in window) {
      console.log('🗣️ Using Web Speech API fallback for question reading...');

      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(currentQuestion.question_text);
      utterance.rate = 0.9; // Slightly slower for clarity
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      // Try to use a professional-sounding voice
      const voices = window.speechSynthesis.getVoices();
      const preferredVoice = voices.find(voice =>
        voice.name.includes('Google') ||
        voice.name.includes('Microsoft') ||
        voice.name.includes('Natural') ||
        voice.lang.startsWith('en')
      );

      if (preferredVoice) {
        utterance.voice = preferredVoice;
        console.log(`🎤 Using voice: ${preferredVoice.name}`);
      }

      utterance.onstart = () => {
        console.log('🗣️ Web Speech synthesis started');
      };

      utterance.onend = () => {
        console.log('✅ Web Speech synthesis completed');
      };

      utterance.onerror = (event) => {
        console.error('❌ Web Speech synthesis error:', event.error);
      };

      window.speechSynthesis.speak(utterance);
    } else {
      console.log('⚠️ Web Speech API not available - question will be text-only');
    }
  };

  const handleRecordingComplete = (_transcription: string) => {
    // Don't automatically advance to next question
    // Let the user manually proceed after reviewing their transcription
    console.log('Recording completed and transcribed. User can now proceed to next question.');
  };

  const handleEndInterview = () => {
    if (session?.session_id) {
      endInterview();
    }
  };

  const getProgressPercentage = () => {
    if (sessionStatus) {
      return sessionStatus.progress_percent;
    }
    if (currentQuestion && session) {
      return Math.round((currentQuestion.question_number / session.total_questions) * 100);
    }
    return 0;
  };

  if (isConnecting) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Typography variant="h6">Connecting to interview server...</Typography>
      </Box>
    );
  }

  if (connectionError) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={() => window.location.reload()}>
          Retry
        </Button>
      }>
        Failed to connect to interview server: {connectionError}
      </Alert>
    );
  }

  if (isCompleted && interviewReport) {
    return (
      <Card sx={{ maxWidth: '800px', mx: 'auto', mt: 2 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom color="primary">
            🎉 Interview Completed!
          </Typography>

          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Overall Score: {interviewReport.final_report.overall_score}/100
            </Typography>
            <LinearProgress
              variant="determinate"
              value={interviewReport.final_report.overall_score}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>

          <Typography variant="h6" gutterBottom>
            Decision: {interviewReport.final_report.selected ? '✅ Selected' : '❌ Not Selected'}
          </Typography>

          <Typography variant="body1" paragraph>
            {interviewReport.final_report.selection_reason}
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Strengths:</Typography>
            {interviewReport.final_report.strengths.map((strength: string, index: number) => (
              <Chip key={index} label={strength} color="success" size="small" sx={{ mr: 1, mb: 1 }} />
            ))}
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>Areas for Improvement:</Typography>
            {interviewReport.final_report.improvement_areas.map((area: string, index: number) => (
              <Chip key={index} label={area} color="warning" size="small" sx={{ mr: 1, mb: 1 }} />
            ))}
          </Box>

          <Typography variant="body2" color="textSecondary">
            Total Questions Asked: {interviewReport.total_questions_asked}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ maxWidth: '800px', mx: 'auto', mt: 2 }}>
      {error && (
        <Alert severity="error" onClose={clearError} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" color="primary">
              Voice Interview Session
            </Typography>
            <Button
              variant="outlined"
              color="error"
              onClick={handleEndInterview}
              size="small"
            >
              End Interview
            </Button>
          </Box>

          {sessionStatus && (
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">
                  Question {sessionStatus.questions_asked + 1} of {sessionStatus.total_questions}
                </Typography>
                <Typography variant="body2">
                  {getProgressPercentage()}% Complete
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={getProgressPercentage()}
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
          )}

          {currentQuestion && (
            <Paper sx={{ p: 3, mb: 3, backgroundColor: 'background.default' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                <Typography variant="h6" color="primary">
                  Question #{currentQuestion.question_number}
                </Typography>
                {currentQuestion.has_audio && (
                  <Button
                    startIcon={<VolumeUp />}
                    onClick={playQuestionAudio}
                    size="small"
                    variant="outlined"
                  >
                    Play Audio
                  </Button>
                )}
              </Box>

              <Typography variant="body1" sx={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
                {currentQuestion.question_text}
              </Typography>

              <Chip
                label={currentQuestion.question_type}
                size="small"
                color="primary"
                variant="outlined"
                sx={{ mt: 2 }}
              />
            </Paper>
          )}

          {currentQuestion && !isCompleted && (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 3, gap: 2 }}>
              <AudioRecorder
                onRecordingComplete={handleRecordingComplete}
                disabled={!session}
                isRecording={isRecording}
                isProcessingAudio={isProcessingAudio}
                isTranscribing={isTranscribing}
                currentTranscription={currentTranscription}
                error={error}
                startRecording={startRecording}
                stopRecording={stopRecording}
                clearError={clearError}
              />

              {/* Show Next Question button when transcription is complete */}
              {currentTranscription && !isRecording && !isProcessingAudio && !isTranscribing && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={getNextQuestion}
                  size="large"
                  sx={{ mt: 2 }}
                >
                  Next Question
                </Button>
              )}
            </Box>
          )}

          {sessionStatus?.skills_discussed && sessionStatus.skills_discussed.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Skills Discussed:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {sessionStatus.skills_discussed.map((skill, index) => (
                  <Chip key={index} label={skill} size="small" color="info" />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};