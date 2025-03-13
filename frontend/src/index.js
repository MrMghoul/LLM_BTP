import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import axios from 'axios';
import './ChatPage.css';

const ChatPage = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [file, setFile] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/conversations/');
        setConversations(res.data.conversations);
      } catch (error) {
        console.error('Error fetching conversations:', error);
      }
    };
    fetchConversations();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('query', query);
      formData.append('history', JSON.stringify(messages));
      if (file) {
        formData.append('file', file);
      }
  
      console.log('Sending query to API:', query);
      console.log('Sending history to API:', messages);
      if (file) {
        console.log('Sending file to API:', file.name);
      }
  
      const res = await axios.post('http://127.0.0.1:8000/api/chat/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      console.log('Received response from API:', res.data.response);
  
      const newMessages = [...messages, { type: 'user', text: query }, { type: 'bot', text: res.data.response }];
      setResponse(res.data.response);
      setMessages(newMessages);
      setQuery('');
      setFile(null);
  
      if (selectedConversation) {
        // Mettre à jour la conversation existante
        const updatedConversation = { ...selectedConversation, query, response: res.data.response, messages: newMessages };
        console.log('Updating conversation in MongoDB:', updatedConversation);
        console.log('Selected conversation ID:', selectedConversation.id);
        await axios.put(`http://127.0.0.1:8000/api/conversations/${selectedConversation.id}`, updatedConversation);
      } else {
        // Ajouter une nouvelle conversation
        const newConversation = { query, response: res.data.response, messages: newMessages };
        console.log('Saving conversation to MongoDB:', newConversation);
        const response = await axios.post('http://127.0.0.1:8000/api/conversations/', newConversation);
        setSelectedConversation({ ...newConversation, id: response.data.id });
        setConversations([...conversations, { ...newConversation, id: response.data.id }]); // Ajouter la nouvelle conversation à la liste
      }
  
    } catch (error) {
      console.error('Error sending query:', error);
    }
  };
  
  const handleAddConversation = () => {
    setSelectedConversation(null); // Réinitialiser la conversation sélectionnée
    setMessages([]);
  };

  const handleDeleteConversation = async (index) => {
    try {
      const conversationToDelete = conversations[index];
      await axios.delete(`http://127.0.0.1:8000/api/conversations/${conversationToDelete.id}`);
      setConversations(conversations.filter((_, i) => i !== index));
      if (selectedConversation === conversationToDelete) {
        setSelectedConversation(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleSelectConversation = (conv) => {
    setSelectedConversation(conv);
    setMessages(conv.messages);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`app-container ${darkMode ? 'dark-mode' : ''}`}>
      <div className={darkMode ? 'logo-dark' : 'logo-light'}></div>
      <button className="dark-mode-toggle-outside" onClick={toggleDarkMode}>
        {darkMode ? 'Mode Clair' : 'Mode Sombre'}
      </button>
      <div className={`chat-container ${darkMode ? 'dark-mode' : ''}`}>
        <div className="sidebar">
          <button className="add-conversation-button" onClick={handleAddConversation}>Add Conversation</button>
          <h2>Conversations</h2>
          <ul className="conversation-list">
            {conversations.map((conv, index) => (
              <li key={index} className="conversation-item" onClick={() => handleSelectConversation(conv)}>
                {`Conversation N°${index + 1}`}
                <button className="delete-button" onClick={(e) => { e.stopPropagation(); handleDeleteConversation(index); }}>❌</button>
              </li>
            ))}
          </ul>
        </div>
        <div className="chat-content">
          <div className="chat-header">
            <h1>Chat with LLM</h1>
          </div>
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                <p>{msg.text}</p>
              </div>
            ))}
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask something..."
            />
            <input
              type="file"
              id="file-upload"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <label htmlFor="file-upload">📎</label>
            <button type="submit">Send</button>
          </form>
        </div>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ChatPage />
  </React.StrictMode>
);