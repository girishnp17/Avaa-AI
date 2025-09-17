import { useState, useCallback, useRef, useEffect } from 'react';
import {
  voiceInterviewSocket,
  InterviewSession,
  Question,
  TranscriptionResult,
  SessionStatus,
  InterviewReport,
  VoiceInterviewEventHandlers
} from '../services/voiceInterviewSocket';

export interface UseVoiceInterviewState {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;

  // Session state
  session: InterviewSession | null;
  sessionId: string | null;

  // Question state
  currentQuestion: Question | null;
  questionHistory: Question[];

  // Recording state
  isRecording: boolean;
  isProcessingAudio: boolean;

  // Transcription state
  currentTranscription: TranscriptionResult | null;
  transcriptionHistory: TranscriptionResult[];
  isTranscribing: boolean;

  // Progress state
  sessionStatus: SessionStatus | null;

  // Completion state
  interviewReport: InterviewReport | null;
  isCompleted: boolean;

  // Error state
  error: string | null;
}

export interface UseVoiceInterviewActions {
  // Connection actions
  connect: () => Promise<void>;
  disconnect: () => void;

  // Session actions
  createSession: (jobDescription: string, resumePath?: string) => void;
  endInterview: () => void;

  // Question actions
  getNextQuestion: () => void;

  // Recording actions
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  sendAudioChunk: (audioData: string) => void;

  // Transcription actions
  checkTranscription: () => void;

  // Status actions
  getSessionStatus: () => void;

  // Utility actions
  clearError: () => void;
  resetInterview: () => void;
}

const initialState: UseVoiceInterviewState = {
  isConnected: false,
  isConnecting: false,
  connectionError: null,
  session: null,
  sessionId: null,
  currentQuestion: null,
  questionHistory: [],
  isRecording: false,
  isProcessingAudio: false,
  currentTranscription: null,
  transcriptionHistory: [],
  isTranscribing: false,
  sessionStatus: null,
  interviewReport: null,
  isCompleted: false,
  error: null,
};

export const useVoiceInterview = (): UseVoiceInterviewState & UseVoiceInterviewActions => {
  const [state, setState] = useState<UseVoiceInterviewState>(initialState);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const transcriptionPollingRef = useRef<number | null>(null);
  const sessionIdRef = useRef<string | null>(null); // Ref to store current session ID
  const audioMimeTypeRef = useRef<string>('audio/webm'); // Ref to store audio MIME type

  // Setup event handlers immediately (not in useEffect to avoid race conditions)
  const setupEventHandlers = () => {
    const handlers: VoiceInterviewEventHandlers = {
      onConnected: () => {
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          connectionError: null
        }));
      },

      onSessionCreated: (session) => {
        console.log('🎉 onSessionCreated called with:', session);
        console.log('🔑 Setting session ID:', session.session_id);

        // Store in both state and ref for immediate access
        sessionIdRef.current = session.session_id;
        console.log('🔑 Session ID ref updated to:', sessionIdRef.current);

        setState(prev => ({
          ...prev,
          session,
          sessionId: session.session_id,
          error: null
        }));
      },

      onNextQuestion: (question) => {
        setState(prev => ({
          ...prev,
          currentQuestion: question,
          questionHistory: [...prev.questionHistory, question],
          error: null
        }));
      },

      onAudioReceived: () => {
        // Handle audio received event
      },

      onRecordingProcessed: (_result) => {
        setState(prev => ({
          ...prev,
          isProcessingAudio: false,
          isTranscribing: true
        }));
      },

      onTranscriptionStarted: () => {
        setState(prev => ({ ...prev, isTranscribing: true }));
      },

      onTranscriptionReady: (result) => {
        setState(prev => ({
          ...prev,
          currentTranscription: result,
          transcriptionHistory: [...prev.transcriptionHistory, result],
          isTranscribing: false
        }));

        // Clear polling
        if (transcriptionPollingRef.current) {
          clearInterval(transcriptionPollingRef.current);
          transcriptionPollingRef.current = null;
        }
      },

      onTranscriptionPending: () => {
        // Continue waiting for transcription
      },

      onSessionStatus: (status) => {
        setState(prev => ({ ...prev, sessionStatus: status }));
      },

      onInterviewCompleted: (report) => {
        setState(prev => ({
          ...prev,
          interviewReport: report,
          isCompleted: true
        }));
      },

      onError: (error) => {
        setState(prev => ({
          ...prev,
          error: error.message,
          isCompleted: error.completed || false
        }));
      },
    };

    voiceInterviewSocket.setEventHandlers(handlers);
  };

  // Setup event handlers on hook initialization
  useEffect(() => {
    setupEventHandlers();

    return () => {
      if (transcriptionPollingRef.current) {
        clearInterval(transcriptionPollingRef.current);
      }
    };
  }, []);

  // Connection actions
  const connect = useCallback(async () => {
    setState(prev => ({ ...prev, isConnecting: true, connectionError: null }));

    try {
      // Ensure event handlers are set up before connecting
      setupEventHandlers();
      await voiceInterviewSocket.connect();
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        connectionError: error instanceof Error ? error.message : 'Connection failed'
      }));
    }
  }, []);

  const disconnect = useCallback(() => {
    voiceInterviewSocket.disconnect();
    setState(prev => ({ ...prev, isConnected: false }));
  }, []);

  // Session actions
  const createSession = useCallback((jobDescription: string, resumePath = 'resume.pdf') => {
    voiceInterviewSocket.createSession(jobDescription, resumePath);
  }, []);

  const endInterview = useCallback(() => {
    const currentSessionId = sessionIdRef.current;
    if (currentSessionId) {
      voiceInterviewSocket.endInterview(currentSessionId);
    }
  }, []);

  // Question actions
  const getNextQuestion = useCallback(() => {
    const currentSessionId = sessionIdRef.current;
    if (currentSessionId) {
      voiceInterviewSocket.getNextQuestion(currentSessionId);
    }
  }, []);

  // Recording actions
  const startRecording = useCallback(async () => {
    console.log('🎤 Requesting microphone access...');
    console.log('🔑 Current session ID (state):', state.sessionId);
    console.log('🔑 Current session ID (ref):', sessionIdRef.current);

    // Validate session exists before recording
    if (!sessionIdRef.current) {
      setState(prev => ({ ...prev, error: 'No interview session found. Please restart the interview.' }));
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('✅ Microphone access granted');

      audioChunksRef.current = [];
      const mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4';
      audioMimeTypeRef.current = mimeType; // Store MIME type for later use
      console.log('🎧 Using MIME type:', mimeType);

      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        console.log('🛑 Recording stopped, processing audio...');
        console.log('📊 Audio chunks collected:', audioChunksRef.current.length);

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        console.log('📦 Audio blob size:', audioBlob.size, 'bytes');

        if (audioBlob.size === 0) {
          console.error('❌ Audio blob is empty!');
          setState(prev => ({ ...prev, error: 'No audio recorded. Please try again.' }));
          return;
        }

        const arrayBuffer = await audioBlob.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        const base64String = btoa(String.fromCharCode(...uint8Array));
        console.log('🔐 Base64 string length:', base64String.length);

        // Use the ref value for immediate access (no closure issues)
        const currentSessionId = sessionIdRef.current;
        console.log('🔑 Session ID at processing time (ref):', currentSessionId);

        if (currentSessionId) {
          console.log('📡 Sending audio to server...');
          console.log('🎧 Audio MIME type:', audioMimeTypeRef.current);
          voiceInterviewSocket.sendAudioChunk(currentSessionId, base64String, audioMimeTypeRef.current);
          voiceInterviewSocket.finishRecording(currentSessionId);

          // Start polling for transcription
          transcriptionPollingRef.current = setInterval(() => {
            voiceInterviewSocket.getTranscription(currentSessionId);
          }, 2000);

          setState(prev => ({ ...prev, isProcessingAudio: true }));
        } else {
          console.error('❌ No session ID available for audio processing!');
          setState(prev => ({ ...prev, error: 'Session not found. Please restart the interview.' }));
        }

        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
        console.log('🔌 Audio stream cleaned up');
      };

      mediaRecorderRef.current.start();
      setState(prev => ({ ...prev, isRecording: true, error: null }));

    } catch (error) {
      setState(prev => ({
        ...prev,
        error: `Failed to start recording: ${error instanceof Error ? error.message : 'Unknown error'}`
      }));
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      setState(prev => ({ ...prev, isRecording: false }));
    }
  }, [state.isRecording]);

  const sendAudioChunk = useCallback((audioData: string) => {
    const currentSessionId = sessionIdRef.current;
    if (currentSessionId) {
      voiceInterviewSocket.sendAudioChunk(currentSessionId, audioData, audioMimeTypeRef.current);
    }
  }, []);

  // Transcription actions
  const checkTranscription = useCallback(() => {
    const currentSessionId = sessionIdRef.current;
    if (currentSessionId) {
      voiceInterviewSocket.getTranscription(currentSessionId);
    }
  }, []);

  // Status actions
  const getSessionStatus = useCallback(() => {
    const currentSessionId = sessionIdRef.current;
    if (currentSessionId) {
      voiceInterviewSocket.getSessionStatus(currentSessionId);
    }
  }, []);

  // Utility actions
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const resetInterview = useCallback(() => {
    setState(initialState);
    if (transcriptionPollingRef.current) {
      clearInterval(transcriptionPollingRef.current);
      transcriptionPollingRef.current = null;
    }
  }, []);

  return {
    // State
    ...state,

    // Actions
    connect,
    disconnect,
    createSession,
    endInterview,
    getNextQuestion,
    startRecording,
    stopRecording,
    sendAudioChunk,
    checkTranscription,
    getSessionStatus,
    clearError,
    resetInterview,
  };
};