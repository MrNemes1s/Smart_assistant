# Smart Assist Frontend

React + TypeScript frontend for the Smart Assist financial insights chat interface.

## Features

- Modern React 18 with TypeScript
- Real-time chat interface
- Session management
- Message history
- Responsive design (mobile-friendly)
- Beautiful gradient UI
- Typing indicators
- Suggestion prompts

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Setup

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies:**

```bash
cd frontend
npm install
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env if needed (default points to localhost:8000)
```

3. **Run development server:**

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx          # Main application component
│   ├── App.css          # Application styles
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── package.json         # Dependencies
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── README.md           # This file
```

## Features Overview

### Chat Interface

- Send messages to the financial insights agent
- View conversation history
- Real-time responses
- Typing indicators

### Session Management

- Create new chat sessions
- View all sessions in sidebar
- Switch between sessions
- Delete sessions

### Responsive Design

- Desktop-optimized layout
- Mobile-friendly with collapsible sidebar
- Touch-friendly controls

### Suggestions

Pre-built question templates:
- "What is my portfolio's total return?"
- "Show me my risk exposure by sector"
- "Calculate Sharpe ratio for my holdings"

## API Integration

The frontend communicates with the backend through:

- **REST API**: `POST /api/chat` for messages
- **Session API**: `GET /api/sessions` for session list
- **History API**: `GET /api/sessions/{id}` for message history

API calls are configured in `vite.config.ts` proxy settings.

## Customization

### Styling

Edit `src/App.css` to customize:
- Colors and gradients
- Layout and spacing
- Component styles
- Animations

### API URL

Change backend URL in `.env`:
```
VITE_API_URL=https://your-backend-url.com
```

### Branding

- Update title in `index.html`
- Modify header text in `App.tsx`
- Change color scheme in CSS

## Development

### Running Locally

```bash
npm run dev
```

### Type Checking

```bash
npm run build  # Runs tsc before build
```

### Linting

```bash
npm run lint
```

## Deployment

See the `/docs` folder for detailed Azure deployment instructions.

### Quick Deploy to Azure Static Web Apps

```bash
# Build the app
npm run build

# Deploy dist/ folder to Azure Static Web Apps
# (See Azure documentation for detailed steps)
```

## Troubleshooting

### CORS Issues

Ensure backend has CORS enabled for your frontend URL.

### API Connection Failed

1. Check backend is running on `http://localhost:8000`
2. Verify `VITE_API_URL` in `.env`
3. Check browser console for errors

### Build Errors

1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf dist
   npm run build
   ```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Next Steps

1. Add authentication (login/logout)
2. Implement WebSocket for streaming responses
3. Add file upload capability
4. Add chart visualization
5. Implement dark mode
6. Add user preferences
