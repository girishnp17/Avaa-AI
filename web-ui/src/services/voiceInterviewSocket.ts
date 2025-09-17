import { io, Socket } from 'socket.io-client';

export interface InterviewSession {
  session_id: string;
  resume_data: any;
  total_questions: number;
  fixed_questions: string[];
}

export interface Question {
  question_number: number;
  question_text: string;
  question_type: string;
  has_audio: boolean;
  audio_data?: string;
  total_questions: number;
}

export interface TranscriptionResult {
  transcription: string;
  question_number: number;
  timestamp: string;
}

export interface SessionStatus {
  session_id: string;
  questions_asked: number;
  total_questions: number;
  progress_percent: number;
  skills_discussed: string[];
  projects_discussed: string[];
  is_complete: boolean;
}

export interface InterviewReport {
  final_report: {
    overall_score: number;
    selected: boolean;
    selection_reason: string;
    strengths: string[];
    improvement_areas: string[];
    recommendations: string[];
    technical_competency: string;
    communication_skills: string;
    problem_solving: string;
    cultural_fit: string;
    summary: string;
  };
  saved_file: string;
  qa_history: any[];
  total_questions_asked: number;
}

export type VoiceInterviewEventHandlers = {
  onConnected: () => void;
  onSessionCreated: (session: InterviewSession) => void;
  onNextQuestion: (question: Question) => void;
  onAudioReceived: () => void;
  onRecordingProcessed: (result: { question_number: number }) => void;
  onTranscriptionStarted: (data: { question_number: number }) => void;
  onTranscriptionReady: (result: TranscriptionResult) => void;
  onTranscriptionPending: () => void;
  onSessionStatus: (status: SessionStatus) => void;
  onInterviewCompleted: (report: InterviewReport) => void;
  onError: (error: { message: string; completed?: boolean }) => void;
};

class VoiceInterviewSocketService {
  private socket: Socket | null = null;
  private handlers: Partial<VoiceInterviewEventHandlers> = {};

  connect(serverUrl?: string): Promise<void> {
    // Auto-detect server URL based on current host
    if (!serverUrl) {
      const currentHost = window.location.hostname;
      if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
        serverUrl = 'http://localhost:8001';
      } else {
        serverUrl = `http://${currentHost}:8001`;
      }
      console.log(`🔗 Connecting to backend at: ${serverUrl}`);
    }
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(serverUrl, {
          transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
          console.log('✅ Connected to voice interview server');
          this.handlers.onConnected?.();
          resolve();
        });

        this.socket.on('connect_error', (error) => {
          console.error('❌ Connection error:', error);
          reject(error);
        });

        this.socket.on('connected', (data) => {
          console.log('📡 Server confirmed connection:', data);
        });

        this.socket.on('session_created', (session: InterviewSession) => {
          console.log('🎙️ Interview session created:', session.session_id);
          this.handlers.onSessionCreated?.(session);
        });

        this.socket.on('next_question', (question: Question) => {
          console.log(`📝 Next question received: #${question.question_number}`);
          this.handlers.onNextQuestion?.(question);
        });

        this.socket.on('audio_received', () => {
          this.handlers.onAudioReceived?.();
        });

        this.socket.on('recording_processed', (result) => {
          console.log(`🎤 Recording processed for question ${result.question_number}`);
          this.handlers.onRecordingProcessed?.(result);
        });

        this.socket.on('transcription_started', (data) => {
          console.log(`🔄 Transcription started for question ${data.question_number}`);
          this.handlers.onTranscriptionStarted?.(data);
        });

        this.socket.on('transcription_ready', (result: TranscriptionResult) => {
          console.log(`✅ Transcription ready: "${result.transcription.substring(0, 50)}..."`);
          this.handlers.onTranscriptionReady?.(result);
        });

        this.socket.on('transcription_pending', () => {
          this.handlers.onTranscriptionPending?.();
        });

        this.socket.on('session_status', (status: SessionStatus) => {
          this.handlers.onSessionStatus?.(status);
        });

        this.socket.on('interview_completed', (report: InterviewReport) => {
          console.log('🏁 Interview completed!');
          this.handlers.onInterviewCompleted?.(report);
        });

        this.socket.on('error', (error: { message: string; completed?: boolean }) => {
          console.error('❌ Server error:', error.message);
          this.handlers.onError?.(error);
        });

        this.socket.on('disconnect', () => {
          console.log('❌ Disconnected from voice interview server');
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  setEventHandlers(handlers: Partial<VoiceInterviewEventHandlers>) {
    this.handlers = { ...this.handlers, ...handlers };
  }

  createSession(jobDescription: string, resumePath: string = 'resume.pdf'): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('create_interview_session', {
      jobDescription,
      resumePath
    });
  }

  getNextQuestion(sessionId: string): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('get_next_question', { session_id: sessionId });
  }

  sendAudioChunk(sessionId: string, audioData: string, mimeType?: string): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('audio_chunk', {
      session_id: sessionId,
      audio_data: audioData,
      mime_type: mimeType || 'audio/webm'
    });
  }

  finishRecording(sessionId: string): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('finish_recording', { session_id: sessionId });
  }

  getTranscription(sessionId: string): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('get_transcription', { session_id: sessionId });
  }

  getSessionStatus(sessionId: string): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('get_session_status', { session_id: sessionId });
  }

  endInterview(sessionId: string): void {
    if (!this.socket) throw new Error('Socket not connected');

    this.socket.emit('end_interview', { session_id: sessionId });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }
}

export const voiceInterviewSocket = new VoiceInterviewSocketService();