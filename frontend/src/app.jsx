import { useRef, useState } from "react";
import { FileText, Send, UploadCloud } from "lucide-react";

import { askQuestion, textToSpeech, uploadDocument } from "./api/client";

function App() {
  const [file, setFile] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnswering, setIsAnswering] = useState(false);
  const [error, setError] = useState("");
  
  const [language, setLanguage] = useState("english");
  const [voiceOutput, setVoiceOutput] = useState(false);
  const audioRef = useRef(null);

  function stopSpeaking() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
  }

  async function speakAnswer(text) {
    if (!voiceOutput) {
      return;
    }

    try {
      stopSpeaking();

      const cleanText = text.split("Source:")[0].trim();
      const audioUrl = await textToSpeech(cleanText, language);
      const audio = new Audio(audioUrl);

      audioRef.current = audio;

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };

      await audio.play();
    } catch (err) {
      setError("Could not play voice output.");
    }
  }

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) {
      setError("Please choose a PDF or Word file first.");
      return;
    }

    setError("");
    setIsUploading(true);

    try {
      const result = await uploadDocument(file);
      setUploadInfo(result);
    } catch (err) {
      setError("Could not upload the document.");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleAsk(event) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      return;
    }

    setError("");
    setQuestion("");

    const userMessage = {
      role: "user",
      text: trimmedQuestion,
    };

    setMessages((current) => [...current, userMessage]);
    setIsAnswering(true);

    try {
      const result = await askQuestion(trimmedQuestion, false, language);

      const botMessage = {
        role: "bot",
        text: result.answer,
        sources: result.sources || [],
      };

      setMessages((current) => [...current, botMessage]);
      speakAnswer(result.answer);
    } catch (err) {
      setError(err.message || "Could not get an answer.");
    } finally {
      setIsAnswering(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="sidebar">
        <div>
          <h1>DocuRAG</h1>
          <p>Ask questions from your PDF or Word documents.</p>
        </div>

        <form className="upload-panel" onSubmit={handleUpload}>
          <label className="file-picker">
            <UploadCloud size={22} />
            <span>{file ? file.name : "Choose PDF or DOCX"}</span>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(event) => setFile(event.target.files[0])}
            />
          </label>

          <button type="submit" disabled={isUploading}>
            {isUploading ? "Processing..." : "Upload Document"}
          </button>
        </form>

        {uploadInfo && (
          <div className="document-info">
            <FileText size={20} />
            <div>
              <strong>{uploadInfo.filename}</strong>
              <span>
                {uploadInfo.pages_found} pages · {uploadInfo.chunks_found} chunks
              </span>
              <span>{uploadInfo.terms_found || 0} document terms</span>
            </div>
          </div>
        )}

        {error && <p className="error-text">{error}</p>}
      </section>

      <section className="chat-area">
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <h2>Upload a document and start asking.</h2>
              <p>Answers will include source pages from your document.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <article key={index} className={`message ${message.role}`}>
              <p>{message.text}</p>

              {message.sources?.length > 0 && (
                <div className="sources">
                  {message.sources.slice(0, 2).map((source, sourceIndex) => (
                    <span key={sourceIndex}>Page {source.page}</span>
                  ))}
                </div>
              )}
            </article>
          ))}

          {isAnswering && (
            <article className="message bot">
              <p>Thinking...</p>
            </article>
          )}
        </div>

        <div className="web-toggle">
          <div className="web-toggle-controls">
            
            <label>
              <input
                type="checkbox"
                checked={voiceOutput}
                onChange={(event) => setVoiceOutput(event.target.checked)}
              />
              Speak answers
            </label>

            <button type="button" className="stop-voice" onClick={stopSpeaking}>
              Stop voice
            </button>

            <select
  value={language}
  onChange={(event) => {
    setLanguage(event.target.value);
  }}
>
  <option value="english">English</option>
  <option value="hindi">Hindi</option>
  <option value="hinglish">Hinglish</option>
  <option value="punjabi">Punjabi</option>
  <option value="roman_punjabi">Roman Punjabi</option>
  <option value="french">French</option>
  <option value="spanish">Spanish</option>
</select>
          </div>
        </div>

        <form className="chat-input" onSubmit={handleAsk}>
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask something from the document..."
          />
          <button type="submit" disabled={isAnswering}>
            <Send size={18} />
          </button>
        </form>
      </section>
    </main>
  );
}

export default App;
