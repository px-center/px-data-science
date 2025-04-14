// Função para validar CPF
function validateCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cpf[i]) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf[9])) return false;
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cpf[i]) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf[10])) return false;
    return true;
  }
  
  // Perguntas de texto
  const textQuestions = [
    "Qual é o seu nome completo?",
    "Qual é o seu CPF?"
  ];
  
  // Perguntas de áudio
  const audioQuestions = [
    "Lembre-se de algum episódio passado: aconteceu alguma emergência e você teve que tomar uma decisão rápida. Como você agiu e quais foram os resultados?",
    "Agora vamos pensar no seu trabalho. Nos conte sobre alguma situação em que você já precisou lidar com algum imprevisto...como você resolveu o problema?",
    "E sobre o seu estilo de trabalho: você se considera mais detalhista/racional ou mais espontâneo/intuitivo? Pode nos dar um exemplo prático disso?",
    "Parceiro, quais são os seus valores pessoais? Pode nos contar aqueles que você considera fundamentais na sua vida!",
    "Sabemos que trabalhar em equipe pode gerar muitos conflitos. Como você lida com eles?",
    "E em situações de pressão e estresse, como você se comunica com as pessoas nessas horas?",
    "Boa, parceiro! Já estamos na metade da nossa jornada. Agora queremos saber: o que te motiva a buscar a excelência no seu trabalho?",
    "Como você equilibra suas necessidades pessoais com as demandas profissionais?",
    "Agora nos conte uma situação em que você teve que lidar com um grande risco no trabalho. Como você lidou com isso?",
    "Diga pra gente: você se sente confortável em ambientes com pouca previsibilidade? Isso é, com poucas certezas e constância. Pode nos dizer o porquê?",
    "Você prefere analisar detalhadamente todas as informações antes de tomar uma decisão, ou confia mais na sua intuição/instinto?",
    "Pra gente terminar: como você lida com problemas difíceis, que exigem uma visão geral da situação versus um pensamento detalhista? Como você equilibra essas coisas?"
  ];
  
  let currentMode = "text";  // "text" ou "audio"
  let currentTextIndex = 0;
  let currentAudioIndex = 0;
  let fullName = "";
  let cpf = "";
  
  // Variável para armazenar a transcrição
  let transcript = "";
  
  // Configuração do reconhecimento de fala (Web Speech API)
  let recognition = null;
  if (window.SpeechRecognition || window.webkitSpeechRecognition) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "pt-BR";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onresult = (event) => {
      transcript = event.results[0][0].transcript;
    };
    recognition.onerror = (event) => {
      console.error("Erro na transcrição:", event.error);
    };
  }
  
  // Seletores
  const answeredQuestionsContainer = document.getElementById('answeredQuestions');
  const textInputWrapper = document.getElementById('textInputWrapper'); // wrapper do input
  const textAnswerInput = document.getElementById('textAnswerInput');
  const sendTextButton = document.getElementById('sendTextButton');
  const recordButton = document.getElementById('recordButton');
  const timerDisplay = document.getElementById('timer');
  const progressBar = document.getElementById('progressBar');
  const progressContainer = document.getElementById('progressContainer');
  
  // Adiciona mensagem no chat
  function addBubble(text, bubbleClass) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${bubbleClass}`;
    bubble.innerHTML = text;
    answeredQuestionsContainer.appendChild(bubble);
    answeredQuestionsContainer.scrollTop = answeredQuestionsContainer.scrollHeight;
  }
  
  // Mostra a próxima pergunta
  function showNextQuestion() {
    if (currentMode === "text") {
      if (currentTextIndex < textQuestions.length) {
        addBubble(textQuestions[currentTextIndex], "question-bubble");
        textInputWrapper.style.display = "flex";
        recordButton.style.display = "none";
        timerDisplay.style.display = "none";
        progressContainer.style.display = "none";
      } else {
        currentMode = "audio";
        showNextQuestion();
      }
    } else {
      if (currentAudioIndex < audioQuestions.length) {
        addBubble(`Pergunta ${currentAudioIndex + 1}: ${audioQuestions[currentAudioIndex]}`, "question-bubble");
        textInputWrapper.style.display = "none";
        recordButton.style.display = "block";
        timerDisplay.style.display = "block";
        progressContainer.style.display = "block";
      } else {
        addBubble("Questionário concluído!", "question-bubble");
        recordButton.style.display = "none";
        timerDisplay.style.display = "none";
        progressContainer.style.display = "none";
      }
    }
  }
  
  // Inicializa mostrando a primeira pergunta de texto
  showNextQuestion();
  
  // Envio de respostas de texto
  sendTextButton.addEventListener("click", () => {
    const answer = textAnswerInput.value.trim();
    if (!answer) {
      alert("Por favor, digite sua resposta.");
      return;
    }
    
    if (currentTextIndex === 1) {
      const onlyDigits = answer.replace(/\D/g, '');
      if (!validateCPF(onlyDigits)) {
        alert("CPF inválido. Por favor, insira um CPF válido contendo apenas números.");
        return;
      }
    }
    
    addBubble(`<strong>${textQuestions[currentTextIndex]}</strong><br>${answer}`, "answer-bubble");
    
    if (currentTextIndex === 0) {
      fullName = answer;
    } else if (currentTextIndex === 1) {
      cpf = answer.replace(/\D/g, '');
    }
    
    textAnswerInput.value = "";
    currentTextIndex++;
    showNextQuestion();
  });
  
  // Gravação de áudio e transcrição
  recordButton.addEventListener("click", async () => {
    if (!fullName || !cpf) {
      alert("Erro: Nome e CPF não foram informados.");
      return;
    }
    
    transcript = ""; // zera a transcrição antes de iniciar
    
    try {
      // Inicia o reconhecimento de fala se suportado
      if (recognition) recognition.start();
      
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      let chunks = [];
      let countdown = 10;
      
      recordButton.disabled = true;
      recordButton.classList.add("recording");
      timerDisplay.textContent = `0:${countdown < 10 ? "0" + countdown : countdown}`;
      progressBar.style.width = "0%";
      
      const intervalId = setInterval(() => {
        countdown--;
        timerDisplay.textContent = `0:${countdown < 10 ? "0" + countdown : countdown}`;
        progressBar.style.width = `${((10 - countdown) / 10) * 100}%`;
        if (countdown <= 0) {
          clearInterval(intervalId);
        }
      }, 1000);
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        recordButton.classList.remove("recording");
        recordButton.disabled = false;
        timerDisplay.textContent = "0:00";
        progressBar.style.width = "100%";
        
        // Para o reconhecimento de fala
        if (recognition) recognition.stop();
        
        const audioBlob = new Blob(chunks, { type: "audio/webm" });
        chunks = [];
        
        // Envia o áudio para a API
        const formData = new FormData();
        formData.append("file", audioBlob, `audio_resposta_${currentAudioIndex + 1}.webm`);
        formData.append("fullName", fullName);
        formData.append("cpf", cpf);
        formData.append("question", audioQuestions[currentAudioIndex]);
        formData.append("questionIndex", currentAudioIndex + 1);
        
        fetch("https://ds-drivers-interviews-data-acquisition-336884965866.us-east1.run.app", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.text())
          .then((apiResponse) => {
            // Exibe a transcrição obtida (se houver) em vez da resposta da API
            const displayText = transcript ? transcript : apiResponse;
            addBubble(`<strong>Resposta ${currentAudioIndex + 1}:</strong><br>${displayText}`, "answer-bubble");
            progressBar.style.width = "0%";
            currentAudioIndex++;
            showNextQuestion();
          })
          .catch((err) => {
            alert("Erro: " + err);
          });
      };
      
      mediaRecorder.start();
      setTimeout(() => {
        mediaRecorder.stop();
      }, 10000);
      
    } catch (error) {
      alert("Erro ao acessar o microfone: " + error);
      recordButton.disabled = false;
    }
  });
  