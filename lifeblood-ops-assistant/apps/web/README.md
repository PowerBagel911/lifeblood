# Lifeblood Operations Assistant - Web Frontend

Modern React + TypeScript frontend for the Lifeblood Operations RAG system.

## Features

- 🩸 **Medical AI Chat Interface** - Ask questions about blood donation procedures
- 📝 **Multiple Response Modes** - General, Checklist, and Plain English formats
- 📚 **Source Citations** - View document sources with relevance scores  
- 🎨 **Modern UI** - Clean, responsive design with Tailwind CSS
- ⚡ **Fast Development** - Vite for instant hot reloading

## Components

- **ChatPage** - Main application layout and state management
- **ChatBox** - Input area with mode selection and send functionality
- **SourcesPanel** - Display citations with snippets and relevance scores
- **ModeSelect** - Dropdown for response mode selection

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## Available Scripts

- `npm run dev` - Start development server on http://localhost:3000
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons

## TODO - Backend Integration

Currently uses mock data. Next steps:
1. Add API service layer
2. Connect to FastAPI backend (/ask endpoint)
3. Add error handling and loading states
4. Implement real-time features

## Medical Disclaimer

This application provides information for reference only. Always consult qualified medical professionals for medical decisions.
