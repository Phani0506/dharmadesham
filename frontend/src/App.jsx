import React, { useState, useRef, useEffect } from 'react';
import { ArrowRight, Send, ChevronLeft, Loader2 } from 'lucide-react';
import './App.css';

const API_URL = '/api/chat'; // Proxied to backend via Vite

function App() {
  const [currentView, setCurrentView] = useState('LANDING'); // LANDING, SUBMENU, CHAT
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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

  const handleCategoryClick = (category) => {
    if (category.disabled) return;
    if (category.id === 'smritis') {
      setCurrentView('SUBMENU');
    }
  };

  const handleGitaClick = () => {
    setCurrentView('CHAT');
    // Add initial greeting
    if (messages.length === 0) {
      setMessages([
        {
          role: 'bot',
          content: 'O seeker of Truth, I am here to share the profound wisdom of the Bhagavad Gita. What queries burden your mind today?'
        }
      ]);
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
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response from the Oracle.');
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'bot', content: data.answer }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'bot', content: 'An error occurred while consulting the ancient texts: ' + error.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="overlay"></div>

      <header onClick={() => setCurrentView('LANDING')}>
        <h1>Dharmadesham</h1>
      </header>

      <div className="content-wrapper">
        {currentView === 'LANDING' && (
          <>
            <div className="hero">
              <h2>Ancient Wisdom, Modern Quest</h2>
              <p>Explore the vast repository of Vedic texts. Select a category to begin your journey.</p>
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
            <div className="category-card" onClick={handleGitaClick}>
              <h3>Bhagavad Gita</h3>
              <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                The Song of God
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
              <h2>Bhagavad Gita Oracle</h2>
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
