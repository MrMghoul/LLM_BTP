import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './global.css';

const ChatPage = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Fetch conversations from MongoDB
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
      console.log("Sending query:", query); // Log the query being sent
      const res = await axios.post('http://127.0.0.1:8000/api/chat/', { query });
      console.log("Response received:", res.data); // Log the response received
      setResponse(res.data.response);
  
      const newMessage = { type: 'question', text: query };
      const newResponse = { type: 'response', text: res.data.response };
  
      if (selectedConversation && selectedConversation.id) {
        // Mettre à jour la conversation existante
        const updatedMessages = [...selectedConversation.messages, newMessage, newResponse];
        const updatedConversation = { ...selectedConversation, messages: updatedMessages, response: res.data.response };
  
        await axios.put(`http://127.0.0.1:8000/api/conversations/${selectedConversation.id}`, updatedConversation);
        setConversations(conversations.map(conv => conv.id === selectedConversation.id ? updatedConversation : conv));
        setSelectedConversation(updatedConversation);
      } else {
        // Créer une nouvelle conversation
        const newConversation = { query, response: res.data.response, messages: [newMessage, newResponse] };
        const response = await axios.post('http://127.0.0.1:8000/api/conversations/', newConversation);
        newConversation.id = response.data.id;
        setConversations([...conversations, newConversation]);
        setSelectedConversation(newConversation);
      }
  
      // Mettre à jour les messages
      setMessages([...messages, newMessage, newResponse]);
      setQuery(''); // Réinitialiser le champ de saisie
    } catch (error) {
      console.error('Error fetching response:', error);
      if (error.response) {
        console.error('Server response:', error.response.data); // Log the server response
      }
    }
  };

  const handleAddConversation = () => {
    setSelectedConversation({ query: '', response: '', messages: [] });
    setMessages([]);
  };

  const handleDeleteConversation = async (index) => {
    try {
      const conversationToDelete = conversations[index];
      await axios.delete(`http://127.0.0.1:8000/api/conversations/${conversationToDelete.id}`);
      setConversations(conversations.filter((_, i) => i !== index));
      if (selectedConversation === conversationToDelete) {
        setSelectedConversation(null); // Clear selected conversation if it was deleted
        setMessages([]); // Clear messages
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleSelectConversation = (conv) => {
    setSelectedConversation(conv);
    setMessages(conv.messages); // Charger tous les messages de la conversation sélectionnée
  };

  return (
    <div className="container">
      <div className="sidebar">
        <button className="add-conversation-button" onClick={handleAddConversation}>Add Conversation</button>
        <h2>Conversations</h2>
        <ul className="list-none p-0">
          {conversations.map((conv, index) => (
            <li key={index} className="flex justify-between items-center py-2 cursor-pointer text-blue-500 hover:underline" onClick={() => handleSelectConversation(conv)}>
              {`Conversation N°${index + 1}`}
              <button className="text-red-500 hover:text-red-700" onClick={(e) => { e.stopPropagation(); handleDeleteConversation(index); }}>❌</button>
            </li>
          ))}
        </ul>
      </div>
      <div className="chat-container">
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
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;