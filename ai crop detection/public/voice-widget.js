(function() {
  // API Key should be handled securely. For development, we can try to get it from a global config or env.
  const GROQ_API_KEY = window.VITE_GROQ_API_KEY || ""; 

  // --- 1. INJECT CSS ---
  const style = document.createElement('style');
  style.innerHTML = `
    #va-trigger {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: #6c63ff;
      box-shadow: 0 4px 20px rgba(108,99,255,0.4);
      cursor: pointer;
      z-index: 9999;
      transition: transform 0.2s;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    #va-trigger:hover {
      transform: scale(1.1);
    }
    #va-trigger svg {
      fill: white;
      width: 24px;
      height: 24px;
    }

    #va-popup {
      position: fixed;
      bottom: 90px;
      right: 24px;
      width: 320px;
      height: 420px;
      background: #1a1a2e;
      border-radius: 20px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      display: flex;
      flex-direction: column;
      z-index: 9999;
      color: white;
      font-family: 'Segoe UI', sans-serif;
      overflow: hidden;
      opacity: 0;
      pointer-events: none;
      transform: translateY(20px);
      transition: opacity 0.3s, transform 0.3s;
    }
    #va-popup.active {
      opacity: 1;
      pointer-events: all;
      transform: translateY(0);
    }

    #va-header {
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255,255,255,0.05);
      border-bottom: 1px solid rgba(255,255,255,0.1);
      font-weight: bold;
    }
    #va-close {
      background: none;
      border: none;
      color: white;
      font-size: 1.2rem;
      cursor: pointer;
      transition: color 0.2s;
    }
    #va-close:hover { color: #ff6b6b; }

    #va-avatar-container {
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 24px 0 16px 0;
      height: 120px;
    }
    #va-avatar {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: radial-gradient(#6c63ff, #4a42cc);
      box-shadow: 0 0 20px rgba(108,99,255,0.5);
      transition: all 0.2s ease;
    }

    @keyframes va-pulse {
      0% { box-shadow: 0 0 0 0 rgba(108,99,255, 0.7); }
      70% { box-shadow: 0 0 0 20px rgba(108,99,255, 0); }
      100% { box-shadow: 0 0 0 0 rgba(108,99,255, 0); }
    }
    .va-listening #va-avatar {
      animation: va-pulse 1.5s infinite;
    }

    @keyframes va-bounce {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }
    .va-speaking #va-avatar {
      animation: va-bounce 1s infinite alternate;
    }

    #va-status {
      text-align: center;
      font-size: 0.9rem;
      color: #a0a0b0;
      margin-bottom: 12px;
      min-height: 20px;
    }

    #va-chat {
      flex: 1;
      padding: 0 20px 20px 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    #va-transcript {
      color: #b0b0c0;
      font-style: italic;
      font-size: 0.9rem;
      text-align: right;
    }

    #va-response {
      color: white;
      font-size: 1rem;
      line-height: 1.4;
      text-align: left;
    }

    /* Scrollbar styling */
    #va-chat::-webkit-scrollbar { width: 6px; }
    #va-chat::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 3px; }

    .hidden { display: none !important; }
  `;
  document.head.appendChild(style);

  // --- 2. INJECT HTML ---
  const container = document.createElement('div');
  container.innerHTML = `
    <div id="va-trigger" title="Voice Assistant">
      <svg viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
        <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
      </svg>
    </div>

    <div id="va-popup">
      <div id="va-header">
        <span>AgriSense Assistant</span>
        <button id="va-close">✕</button>
      </div>
      <div id="va-avatar-container">
        <div id="va-avatar"></div>
      </div>
      <div id="va-status">Initializing...</div>
      <div id="va-chat">
        <div id="va-transcript"></div>
        <div id="va-response">Hi, how can I help you today?</div>
      </div>
    </div>
  `;
  document.body.appendChild(container);

  // --- 3. LOGIC ---
  const trigger = document.getElementById('va-trigger');
  const popup = document.getElementById('va-popup');
  const closeBtn = document.getElementById('va-close');
  const avatar = document.getElementById('va-avatar-container');
  const statusEl = document.getElementById('va-status');
  const transcriptEl = document.getElementById('va-transcript');
  const responseEl = document.getElementById('va-response');

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let synth = window.speechSynthesis;
  let isPopupOpen = false;

  if (!SpeechRecognition) {
    statusEl.innerText = "Voice not supported in this browser. Use Chrome.";
    return; // Fast exit if not supported
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-IN'; // Defaults to Indian accent/English which handles Hinglish very well

  // --- UI Helpers ---
  function setStatus(text, mode = 'idle') {
    statusEl.innerText = text;
    avatar.className = '';
    if (mode === 'listening') avatar.classList.add('va-listening');
    if (mode === 'speaking') avatar.classList.add('va-speaking');
  }

  // --- Language Detection Helper ---
  function detectLang(text) {
    if (/[\u0900-\u097F]/.test(text)) return { code: 'hi-IN', name: 'Hindi/Devanagari' };
    if (/[\u0B80-\u0BFF]/.test(text)) return { code: 'ta-IN', name: 'Tamil' };
    if (/[\u0C00-\u0C7F]/.test(text)) return { code: 'te-IN', name: 'Telugu' };
    if (/[\u0980-\u09FF]/.test(text)) return { code: 'bn-IN', name: 'Bengali' };
    
    // Simple heuristic for Hinglish if Latin script but common Hindi words appear
    const lower = text.toLowerCase();
    if (lower.includes('kya') || lower.includes('hai') || lower.includes('kaise')) {
      return { code: 'hi-IN', name: 'Hinglish (Hindi in English script)' };
    }
    
    return { code: 'en-US', name: 'English' };
  }

  // --- Groq API Call ---
  async function askGroq(userText, langName) {
    try {
      const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${GROQ_API_KEY}`
        },
        body: JSON.stringify({
          model: "llama-3.3-70b-versatile",
          messages: [
            {
              role: "system",
              content: `You are an AI assistant for a smart agriculture app called AgriSense AI. 
                The user is speaking in the language/script: ${langName}.
                IMPORTANT RULES:
                1. You MUST reply in the EXACT SAME language and EXACT SAME script the user used.
                2. If the user speaks Hindi using the Devanagari script (e.g. "नमस्ते"), reply ONLY in Devanagari script Hindi.
                3. If the user speaks Hindi using the English alphabet (Hinglish, e.g. "kaise ho"), reply ONLY in Hinglish using the English alphabet.
                4. If the user speaks English, reply in English.
                5. Keep replies SHORT (1-3 sentences max) since this is a voice interface.
                6. Do NOT use markdown, asterisks, bullet points, or special characters — plain text only, so it can be spoken aloud seamlessly.
                7. Be conversational, natural, and helpful for a farmer or agriculture user.`
            },
            {
              role: "user",
              content: userText
            }
          ],
          max_tokens: 300,
          temperature: 0.7
        })
      });
      
      if (!response.ok) throw new Error("API request failed");
      
      const data = await response.json();
      return data.choices[0].message.content.trim();
    } catch (e) {
      console.error(e);
      return "Sorry, I could not connect to the AI service right now.";
    }
  }

  // --- TTS ---
  function speak(text, langCode) {
    if (!isPopupOpen) return;
    
    // Stop any existing speech
    synth.cancel();
    
    const utter = new SpeechSynthesisUtterance(text);
    
    // Default to matching langCode, fallback to Indian English to keep accent consistent
    utter.lang = langCode || 'en-IN';
    utter.rate = 1.0;
    utter.pitch = 1.0;

    // Pick a natural-sounding voice if available, preferring Female Indian English/Hindi
    const voices = synth.getVoices();
    let preferredVoice = 
      voices.find(v => v.lang === utter.lang && (v.name.includes('Female') || v.name.includes('Google'))) ||
      voices.find(v => v.lang === utter.lang) ||
      voices.find(v => v.lang.includes('IN')) || 
      voices.find(v => v.lang.includes('GB')); // Fallback to British if no Indian accent available
      
    if (preferredVoice) {
      utter.voice = preferredVoice;
    }

    utter.onstart = () => {
      setStatus("Speaking...", 'speaking');
    };

    utter.onend = () => {
      setStatus("Listening...", 'listening');
      if (isPopupOpen) {
        try { recognition.start(); } catch(e) {}
      }
    };

    utter.onerror = () => {
      // In case TTS fails, try to fallback to listening immediately
      setStatus("Listening...", 'listening');
      if (isPopupOpen) {
        try { recognition.start(); } catch(e) {}
      }
    }

    synth.speak(utter);
  }

  // --- Speech Recognition Events ---
  recognition.onstart = () => {
    setStatus("Listening...", 'listening');
  };

  recognition.onresult = (event) => {
    let finalTranscript = '';
    let interimTranscript = '';
    
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }
    
    transcriptEl.innerText = finalTranscript || interimTranscript;
    
    if (finalTranscript) {
      recognition.stop();
      processInput(finalTranscript);
    }
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error", event.error);
    if (event.error === 'not-allowed') {
      setStatus("Please allow microphone access.", 'idle');
    } else if (event.error === 'no-speech') {
      // Just restart listening if still open
      if (isPopupOpen) {
        try { recognition.start(); } catch(e) {}
      }
    } else {
      setStatus("Network error or mic off.", 'idle');
    }
  };

  recognition.onend = () => {
    // If popup is open, and we aren't currently "thinking" or "speaking", try to listen again
    // We already handle restart in utter.onend and processInput
  };

  // --- Main Processing Flow ---
  async function processInput(text) {
    setStatus("Thinking...", 'idle');
    responseEl.innerText = "...";
    
    const detected = detectLang(text);
    const botReply = await askGroq(text, detected.name);
    
    if (!isPopupOpen) return;
    
    transcriptEl.innerText = text;
    responseEl.innerText = botReply;
    
    speak(botReply, detected.code);
  }

  // --- Interactions ---
  trigger.addEventListener('click', () => {
    isPopupOpen = true;
    popup.classList.add('active');
    trigger.style.transform = 'scale(0)';
    transcriptEl.innerText = "";
    responseEl.innerText = "Hi, how can I help you today?";
    
    // Announce the greeting and start listening
    speak(responseEl.innerText, 'en-US');
  });

  closeBtn.addEventListener('click', () => {
    isPopupOpen = false;
    popup.classList.remove('active');
    trigger.style.transform = 'scale(1)';
    synth.cancel();
    try { recognition.stop(); } catch(e) {}
    setStatus("Tap mic to speak...", 'idle');
  });

})();
