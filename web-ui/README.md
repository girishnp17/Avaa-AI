# 🎨 Unified AI Tools - Modern Web UI

A stunning, hackathon-winning React + TypeScript interface for the Unified AI Career Tools suite.

## ✨ Features

- **🎯 Modern Design**: Material-UI with custom theme and animations
- **📱 Responsive**: Mobile-first design that works on all devices
- **⚡ Fast**: Built with Vite for lightning-fast development
- **🔒 Type Safe**: Full TypeScript support
- **🎭 Animated**: Smooth Framer Motion animations
- **🌙 Dark Mode**: Toggle between light and dark themes
- **📊 Real-time**: Redux Toolkit for state management

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) v5
- **State Management**: Redux Toolkit + RTK Query
- **Routing**: React Router v6
- **Animations**: Framer Motion
- **Icons**: Material Icons + Lucide React

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   cd web-ui
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Open Browser**:
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
web-ui/
├── src/
│   ├── components/          # Reusable UI components
│   │   └── Layout/         # App layout and navigation
│   ├── pages/              # Page components
│   │   ├── HomePage.tsx    # Landing page with tool cards
│   │   ├── ResumeGenerator.tsx
│   │   ├── CareerGuidance.tsx
│   │   ├── LearningRoadmap.tsx
│   │   ├── JobSearch.tsx
│   │   └── InterviewBot.tsx
│   ├── store/              # Redux store and slices
│   │   ├── store.ts        # Main store configuration
│   │   ├── apiSlice.ts     # RTK Query API endpoints
│   │   ├── themeSlice.ts   # Theme management
│   │   └── resumeSlice.ts  # Resume form state
│   ├── theme/              # MUI theme configuration
│   │   └── theme.ts        # Light/dark theme setup
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
└── tsconfig.json           # TypeScript configuration
```

## 🎨 Design System

### Color Palette
- **Primary**: #1976d2 (Professional Blue)
- **Secondary**: #dc004e (Accent Pink)
- **Success**: #2e7d32 (Green)
- **Warning**: #ed6c02 (Orange)
- **Background**: #f8fafc (Light Gray)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: 700 weight for impact
- **Body**: 400 weight for readability

### Components
- **Cards**: Elevated with hover animations
- **Buttons**: Rounded corners, smooth transitions
- **Forms**: Clean, accessible inputs
- **Navigation**: Sticky sidebar with active states

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🌟 Key Features by Page

### 🏠 Home Page
- Hero section with gradient background
- Animated tool cards with hover effects
- Statistics section
- Responsive grid layout

### 📄 Resume Generator
- Multi-step form with progress indicator
- Real-time form validation
- Dynamic experience/education sections
- Live preview (planned)
- PDF generation

### 💼 Career Guidance
- Drag & drop file upload
- Comprehensive analysis dashboard
- Market insights with charts
- AI-powered recommendations
- Skills gap analysis

### 🗺️ Learning Roadmap
- Interactive timeline with 8 steps
- Expandable step details
- Progress tracking
- Resource recommendations
- Course integration

### 🔍 Job Search
- Advanced search with filters
- AI match scoring
- Job cards with detailed info
- Save/bookmark functionality
- Salary insights

### 🤖 Interview Bot
- Real-time chat interface
- Voice recording support
- Progress tracking
- Interview tips sidebar
- Common questions quick access

## 🎯 Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo for expensive components
- **Bundle Analysis**: Optimized bundle size
- **Image Optimization**: WebP format support

## 🔌 API Integration

The UI connects to the Flask backend at `http://localhost:8000/api/`:

- `POST /api/resume/generate` - Generate resume
- `POST /api/career/analyze` - Analyze career
- `POST /api/jobs/search` - Search jobs
- `POST /api/courses/recommend` - Recommend courses
- `POST /api/roadmap/create` - Create roadmap

## 🎨 Customization

### Theme Customization
Edit `src/theme/theme.ts` to customize colors, typography, and component styles.

### Adding New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Update navigation in `src/components/Layout/Layout.tsx`

### State Management
Use Redux Toolkit slices for complex state. Simple component state for UI-only data.

## 🚀 Deployment

1. **Build for Production**:
   ```bash
   npm run build
   ```

2. **Deploy to Vercel/Netlify**:
   ```bash
   # Connect your repo and deploy
   ```

## 🏆 Hackathon Features

This UI is designed to win hackathons with:

- **Visual Impact**: Stunning animations and modern design
- **User Experience**: Intuitive navigation and interactions
- **Technical Excellence**: TypeScript, best practices, performance
- **Innovation**: AI-powered features with real-time feedback
- **Completeness**: Full-featured application with all tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Built with ❤️ for hackathon success!**
