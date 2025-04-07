
document.addEventListener('DOMContentLoaded', function() {
  const recordButton = document.getElementById('recordButton');
  const timerDisplay = document.getElementById('timer');
  const answeredQuestions = document.getElementById('answeredQuestions');
  const questionDisplay = document.getElementById('question');
  const progressBar = document.getElementById('progressBar');
  
  let mediaRecorder;
  let audioChunks = [];
  let timerInterval;
  let seconds = 0;
  let isPaused = false;
  let requiredSeconds = 10; // Mínimo de 10 segundos
  
  const questions = [
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
  
  let currentQuestionIndex = 0;
  
  // Função para atualizar a pergunta atual
  function updateQuestion() {
    if (currentQuestionIndex < questions.length) {
      // Adiciona a pergunta ao chat
      const questionBubble = document.createElement('div');
      questionBubble.className = 'chat-bubble question-bubble';
      questionBubble.textContent = questions[currentQuestionIndex];
      answeredQuestions.appendChild(questionBubble);
      
      // Atualiza a pergunta atual
      questionDisplay.textContent = questions[currentQuestionIndex];
      
      // Rola para baixo para mostrar a nova pergunta
      answeredQuestions.scrollTop = answeredQuestions.scrollHeight;
      
      currentQuestionIndex++;
    } else {
      // Fim do questionário
      questionDisplay.textContent = "Obrigado por responder ao questionário!";
      recordButton.style.display = 'none';
      timerDisplay.style.display = 'none';
      document.querySelector('.progress-container').style.display = 'none';
    }
  }
  
  // Inicia com a primeira pergunta
  updateQuestion();
  
  // Função para formatar o tempo
  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
  
  // Função para atualizar a barra de progresso
  function updateProgressBar() {
    const progress = (seconds / requiredSeconds) * 100;
    progressBar.style.width = `${Math.min(progress, 100)}%`;
    
    // Quando atingir 10 segundos, envia automaticamente
    if (seconds >= requiredSeconds) {
      stopRecordingAndSend();
    }
  }
  
  // Função para parar a gravação e enviar
  function stopRecordingAndSend() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      clearInterval(timerInterval);
    }
  }
  
  // Iniciar/parar/pausar gravação
  recordButton.addEventListener('click', async function() {
    if (!mediaRecorder) {
      // Iniciar nova gravação
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Verifica se o navegador suporta MediaRecorder (ou o prefixado WebKitMediaRecorder)
        const Recorder = window.MediaRecorder || window.WebKitMediaRecorder;
        if (!Recorder) {
          alert('Seu navegador não suporta gravação de áudio.');
          return;
        }
        
        // Define mimeType compatível
        let options = { audioBitsPerSecond: 128000 };
        if (Recorder.isTypeSupported && Recorder.isTypeSupported('audio/webm;codecs=opus')) {
          options.mimeType = 'audio/webm;codecs=opus';
        } else if (Recorder.isTypeSupported && Recorder.isTypeSupported('audio/ogg;codecs=opus')) {
          options.mimeType = 'audio/ogg;codecs=opus';
        }
        
        mediaRecorder = new Recorder(stream, options);
        
        mediaRecorder.ondataavailable = function(e) {
          audioChunks.push(e.data);
        };
        
        mediaRecorder.onstop = function() {
          const audioBlob = new Blob(audioChunks, { type: options.mimeType || 'audio/webm' });
          const audioUrl = URL.createObjectURL(audioBlob);
          
          // Cria o elemento de áudio para a resposta
          const answerBubble = document.createElement('div');
          answerBubble.className = 'chat-bubble answer-bubble';
          
          const audioContainer = document.createElement('div');
          audioContainer.className = 'audio-answer';
          
          const audioPlayer = document.createElement('audio');
          audioPlayer.className = 'audio-player';
          audioPlayer.controls = true;
          audioPlayer.src = audioUrl;
          
          // Força o carregamento
          audioPlayer.load();
          
          // Cria o link para download do áudio
          const downloadLink = document.createElement('a');
          downloadLink.href = audioUrl;
          downloadLink.download = 'audio_gravado.' + (options.mimeType.includes('ogg') ? 'ogg' : 'webm');
          downloadLink.textContent = 'Baixar áudio';
          downloadLink.className = 'download-link';
          
          audioContainer.appendChild(audioPlayer);
          audioContainer.appendChild(downloadLink);
          answerBubble.appendChild(audioContainer);
          answeredQuestions.appendChild(answerBubble);
          
          // Rola para baixo para mostrar a nova resposta
          answeredQuestions.scrollTop = answeredQuestions.scrollHeight;
          
          // Limpa os chunks de áudio para a próxima gravação
          audioChunks = [];
          
          // Reseta o timer e progresso
          seconds = 0;
          timerDisplay.textContent = formatTime(seconds);
          progressBar.style.width = '0%';
          
          // Limpa o mediaRecorder
          mediaRecorder = null;
          recordButton.classList.remove('recording', 'paused');
          
          // Avança para a próxima pergunta
          setTimeout(updateQuestion, 500);
        };
        
        mediaRecorder.start(100); // Coleta dados a cada 100ms para melhor compatibilidade
        recordButton.classList.add('recording');
        recordButton.innerHTML = '<i class="fas fa-pause"></i>';
        
        // Inicia o timer
        timerInterval = setInterval(function() {
          if (!isPaused) {
            seconds++;
            timerDisplay.textContent = formatTime(seconds);
            updateProgressBar();
          }
        }, 1000);
        
      } catch (error) {
        console.error('Erro ao acessar o microfone:', error);
        alert('Não foi possível acessar o microfone. Por favor, verifique as permissões.');
      }
    } else {
      // Pausar/continuar gravação existente
      if (mediaRecorder.state === 'recording') {
        mediaRecorder.pause();
        recordButton.classList.remove('recording');
        recordButton.classList.add('paused');
        recordButton.innerHTML = '<i class="fas fa-microphone"></i>';
        isPaused = true;
      } else if (mediaRecorder.state === 'paused') {
        mediaRecorder.resume();
        recordButton.classList.add('recording');
        recordButton.classList.remove('paused');
        recordButton.innerHTML = '<i class="fas fa-pause"></i>';
        isPaused = false;
      }
    }
  });
});
