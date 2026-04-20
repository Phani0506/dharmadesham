import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, Send, ChevronLeft, Loader2, Menu, X, MessageSquare } from 'lucide-react';
import './App.css';

const API_URL = '/api/chat'; // Proxied to backend via Vite

function App() {
  const [currentView, setCurrentView] = useState('LANDING'); // LANDING, SUBMENU, CHAT
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [currentTextType, setCurrentTextType] = useState('GITA');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const categories = [
    { id: 'vedas', name: 'Vedas', disabled: true },
    { id: 'smritis', name: 'Smritis', disabled: false },
    { id: 'puranas', name: 'Puranas', disabled: true },
    { id: 'rishis', name: 'Rishis', disabled: true },
    { id: 'shastrams', name: 'Shastrams', disabled: true },
    { id: 'bhagavadpadas', name: 'Bhagavadpadas', disabled: true },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    fetchChats();
  }, []);

  const fetchChats = async () => {
    try {
      const res = await fetch('/api/chats');
      if (res.ok) {
        const data = await res.json();
        setChatHistory(data);
      }
    } catch (e) {
      console.error('Failed to load chats', e);
    }
  };

  const handleLoadChat = async (chatId) => {
    try {
      const res = await fetch(`/api/chats/${chatId}`);
      if (res.ok) {
        const data = await res.json();
        const chatInfo = chatHistory.find(c => c.id === chatId);
        if (chatInfo && chatInfo.text_type) {
          setCurrentTextType(chatInfo.text_type);
        }
        setCurrentChatId(chatId);
        setMessages(data);
        setCurrentView('CHAT');
        setIsSidebarOpen(false);
      }
    } catch (e) {
      console.error('Failed to load chat history', e);
    }
  };

  const handleCategoryClick = (category) => {
    if (category.disabled) return;
    if (category.id === 'smritis') {
      setCurrentView('SUBMENU');
    }
  };

  const handleTextClick = async (textType) => {
    setIsSidebarOpen(false);
    setCurrentTextType(textType);
    try {
      const res = await fetch('/api/chats', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text_type: textType }),
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentChatId(data.chat_id);
        const greeting = textType === 'RAMAYANA' 
          ? 'Welcome, seeker. I am an oracle of the Ramayana. How may its boundless wisdom guide you today?'
          : textType === 'MAHABHARATA'
          ? 'Jai Shri Krishna. I am here to illuminate the eternal wisdom of the Mahabharata. What seeks your heart today?'
          : 'O seeker of Truth, I am here to share the profound wisdom of the Bhagavad Gita. What queries burden your mind today?';
        setMessages([{ role: 'bot', content: greeting }]);
        setCurrentView('CHAT');
        fetchChats();
      }
    } catch (e) {
      console.error('Failed to start a new chat', e);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const query = inputValue.trim();
    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, chat_id: currentChatId, text_type: currentTextType }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response from the Oracle.');
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'bot', content: data.answer }]);
      
      // Refresh history to update title
      if (messages.length <= 2) {
        fetchChats();
      }
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'bot', content: 'An error occurred while consulting the ancient texts: ' + error.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  let bgImage = '/bg.jpg';
  if (currentView === 'CHAT') {
    if (currentTextType === 'RAMAYANA') bgImage = '/1.jpg';
    else if (currentTextType === 'MAHABHARATA') bgImage = '/2.jpg';
    else if (currentTextType === 'GITA') bgImage = '/3.jpg';
  }

  return (
    <div className="app-container" style={{ backgroundImage: `url(${bgImage})` }}>
      <div className="overlay"></div>

      <header>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button className="menu-btn" onClick={() => setIsSidebarOpen(true)}>
            <Menu size={24} color="#e2e8f0" />
          </button>
          <h1 onClick={() => setCurrentView('LANDING')}>Dharmadesham</h1>
        </div>
      </header>

      <div className={`history-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Chat History</h2>
          <button className="close-btn" onClick={() => setIsSidebarOpen(false)}>
            <X size={24} />
          </button>
        </div>
        <div className="sidebar-content">
          <button className="new-chat-btn" onClick={() => handleTextClick('GITA')}>
            + New Gita Chat
          </button>
          <button className="new-chat-btn" onClick={() => handleTextClick('RAMAYANA')} style={{marginTop: '10px'}}>
            + New Ramayana Chat
          </button>
          <button className="new-chat-btn" onClick={() => handleTextClick('MAHABHARATA')} style={{marginTop: '10px'}}>
            + New Mahabharata Chat
          </button>
          <div className="history-list" style={{marginTop: '20px'}}>
            {chatHistory.map((chat) => (
              <div 
                key={chat.id} 
                className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
                onClick={() => handleLoadChat(chat.id)}
              >
                <div style={{minWidth: '20px'}}><MessageSquare size={16} /></div>
                <div className="history-title">[{chat.text_type === 'RAMAYANA' ? 'Ramayana' : chat.text_type === 'MAHABHARATA' ? 'Mahabharata' : 'Gita'}] {chat.title || 'New Chat'}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      {isSidebarOpen && <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)}></div>}

      <div className="content-wrapper">
        {currentView === 'LANDING' && (
          <>
            <div className="hero">
              <h2>Ancient Wisdom, Modern Quest</h2>
              <p>Explore the vast repository of Vedic texts.<br />Select a category to begin your journey.</p>
            </div>
            <div className="category-grid">
              {categories.map((cat) => (
                <div
                  key={cat.id}
                  className={`category-card ${cat.disabled ? 'disabled' : ''}`}
                  onClick={() => handleCategoryClick(cat)}
                >
                  <h3>{cat.name}</h3>
                </div>
              ))}
            </div>
          </>
        )}

        {currentView === 'SUBMENU' && (
          <div className="category-grid" style={{ maxWidth: '400px' }}>
            <div className="category-card" onClick={() => handleTextClick('GITA')}>
              <h3>Bhagavad Gita</h3>
              <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                The Song of God
              </p>
            </div>
            <div className="category-card" onClick={() => handleTextClick('RAMAYANA')}>
              <h3>Ramayana</h3>
              <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                The Epic of Rama
              </p>
            </div>
            <div className="category-card" onClick={() => handleTextClick('MAHABHARATA')}>
              <h3>Mahabharata</h3>
              <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                The Great Battle of Dharma
              </p>
            </div>
          </div>
        )}

        {currentView === 'CHAT' && (
          <div className="chat-container">
            <div className="chat-header">
              <button className="back-btn" onClick={() => setCurrentView('SUBMENU')}>
                <ChevronLeft size={20} />
                <span>Back to Smritis</span>
              </button>
              <h2>{currentTextType === 'RAMAYANA' ? 'Ramayana' : currentTextType === 'MAHABHARATA' ? 'Mahabharata' : 'Bhagavad Gita'}</h2>
              <div style={{ width: 40 }}></div> {/* Spacer */}
            </div>

            <div className="chat-messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <div className="message-bubble">
                    <div className="bot-response">{msg.content}</div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message bot">
                  <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Loader2 size={18} className="animate-spin" />
                    <span>Consulting the texts...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input" onSubmit={handleSendMessage}>
              <div className="input-wrapper">
                <input
                  type="text"
                  placeholder="Ask a question..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  disabled={isLoading}
                />
                <button type="submit" className="send-btn" disabled={!inputValue.trim() || isLoading}>
                  <Send size={20} />
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
