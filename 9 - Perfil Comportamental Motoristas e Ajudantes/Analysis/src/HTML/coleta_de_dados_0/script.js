// Definição das perguntas de texto (inicialmente)
const textQuestions = [
    "Qual é o seu nome completo?",
    "Qual é o seu CPF?"
  ];
  
  // Definição das perguntas por áudio (após as respostas de texto)
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
  
  let currentMode = "text"; // 'text' ou 'audio'
  let currentTextQuestionIndex = 0;
  let currentAudioQuestionIndex = 0;
  let fullName = "";
  let cpf = "";
  
  // Seleciona os elementos do DOM
  const textQuestionContainer = document.getElementById('textQuestionContainer');
  const textQuestionDisplay = document.getElementById('textQuestion');
  const textAnswerInput = document.getElementById('textAnswerInput');
  const sendTextButton = document.getElementById('sendTextButton');
  
  const audioQuestionContainer = document.getElementById('audioQuestionContainer');
  const audioQuestionDisplay = document.getElementById('audioQuestion');
  const recordButton = document.getElementById('recordButton');
  const timerDisplay = document.getElementById('timer');
  const progressBar = document.getElementById('progressBar');
  
  const answeredQuestionsContainer = document.getElementById('answeredQuestions');
  
  // Exibe a pergunta de texto atual
  function displayTextQuestion() {
    if (currentTextQuestionIndex < textQuestions.length) {
      textQuestionDisplay.textContent = textQuestions[currentTextQuestionIndex];
    } else {
      // Ao terminar as perguntas de texto, passa para o modo áudio
      currentMode = "audio";
      textQuestionContainer.style.display = "none";
      audioQuestionContainer.style.display = "flex";
      displayAudioQuestion();
    }
  }
  
  // Exibe a pergunta de áudio atual
  function displayAudioQuestion() {
    if (currentAudioQuestionIndex < audioQuestions.length) {
      audioQuestionDisplay.textContent = `Pergunta ${currentAudioQuestionIndex + 1}: ${audioQuestions[currentAudioQuestionIndex]}`;
    } else {
      audioQuestionDisplay.textContent = 'Questionário concluído!';
      recordButton.disabled = true;
    }
  }
  
  // Inicializa exibindo a primeira pergunta de texto
  displayTextQuestion();
  
  // Evento para envio das respostas de texto
  sendTextButton.addEventListener('click', () => {
    const answer = textAnswerInput.value.trim();
    if (!answer) {
      alert('Por favor, digite sua resposta.');
      return;
    }
    
    // Cria uma chat bubble com a resposta
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble answer-bubble';
    bubble.innerHTML = `<strong>${textQuestions[currentTextQuestionIndex]}</strong><br>${answer}`;
    answeredQuestionsContainer.appendChild(bubble);
    
    // Armazena as respostas para as duas primeiras perguntas
    if (currentTextQuestionIndex === 0) {
      fullName = answer;
    } else if (currentTextQuestionIndex === 1) {
      cpf = answer;
    }
    
    textAnswerInput.value = "";
    currentTextQuestionIndex++;
    displayTextQuestion();
  });
  
  // Evento para gravação das respostas de áudio
  recordButton.addEventListener('click', async () => {
    if (!fullName || !cpf) {
      alert('Erro: Nome e CPF não foram informados.');
      return;
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      let chunks = [];
      let countdown = 10;
      
      // Inicializa timer e barra de progresso
      timerDisplay.textContent = `0:${countdown < 10 ? '0' + countdown : countdown}`;
      progressBar.style.width = '0%';
      recordButton.disabled = true;
      recordButton.classList.add('recording');
      
      const intervalId = setInterval(() => {
        countdown--;
        timerDisplay.textContent = `0:${countdown < 10 ? '0' + countdown : countdown}`;
        progressBar.style.width = `${((10 - countdown) / 10) * 100}%`;
        if (countdown <= 0) {
          clearInterval(intervalId);
        }
      }, 1000);
      
      mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        recordButton.classList.remove('recording');
        timerDisplay.textContent = '0:00';
        progressBar.style.width = '100%';
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        chunks = [];
        
        // Prepara os dados a serem enviados para a API
        const formData = new FormData();
        formData.append('file', audioBlob, `audio_resposta_${currentAudioQuestionIndex + 1}.webm`);
        formData.append('fullName', fullName);
        formData.append('cpf', cpf);
        formData.append('question', audioQuestions[currentAudioQuestionIndex]);
        formData.append('questionIndex', currentAudioQuestionIndex + 1);
        
        // Chamada para a API (mantendo a integração definida)
        fetch('https://ds-drivers-interviews-data-acquisition-336884965866.us-east1.run.app', {
          method: 'POST',
          body: formData
        })
        .then(response => response.text())
        .then(data => {
          const bubble = document.createElement('div');
          bubble.className = 'chat-bubble answer-bubble';
          bubble.innerHTML = `<strong>Resposta ${currentAudioQuestionIndex + 1}:</strong><br>${data}`;
          answeredQuestionsContainer.appendChild(bubble);
          progressBar.style.width = '0%';
          currentAudioQuestionIndex++;
          displayAudioQuestion();
        })
        .catch(error => {
          alert('Erro: ' + error);
        })
        .finally(() => {
          recordButton.disabled = false;
        });
      };
      
      mediaRecorder.start();
      setTimeout(() => {
        mediaRecorder.stop();
      }, 10000);
      
    } catch (error) {
      alert('Erro ao acessar o microfone: ' + error);
      recordButton.disabled = false;
    }
  });
  