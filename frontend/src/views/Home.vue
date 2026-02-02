<template>
  <div class="home-container">
    <h1 class="title">🍪 포춘 쿠키</h1>
    
    <div v-if="!showFortune" class="input-section">
      <textarea
        v-model="message"
        placeholder="메시지를 입력하세요..."
        class="message-input"
        rows="4"
      ></textarea>
      <button @click="submitMessage" class="submit-btn" :disabled="!message.trim()">
        메시지 보내기
      </button>
      <button @click="getFortune" class="fortune-btn">
        포춘 쿠키 열기 🍪
      </button>
    </div>

    <div v-if="showFortune" class="fortune-section">
      <div class="fortune-cookie" :class="{ 'opened': isOpened }" @click="openCookie">
        <div class="cookie-top" v-if="!isOpened"></div>
        <div class="cookie-bottom" v-if="!isOpened"></div>
        <div class="fortune-paper" v-if="isOpened">
          <p class="fortune-text">{{ fortuneMessage }}</p>
        </div>
      </div>
      <button @click="reset" class="reset-btn">다시 하기</button>
    </div>

    <div v-if="loading" class="loading">로딩 중...</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default {
  name: 'Home',
  data() {
    return {
      message: '',
      showFortune: false,
      isOpened: false,
      fortuneMessage: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async submitMessage() {
      if (!this.message.trim()) return
      
      this.loading = true
      this.error = null
      
      try {
        await axios.post(`${API_BASE_URL}/messages`, {
          message: this.message
        })
        this.message = ''
        alert('메시지가 저장되었습니다!')
      } catch (err) {
        this.error = '메시지 전송에 실패했습니다.'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async getFortune() {
      this.loading = true
      this.error = null
      this.showFortune = true
      this.isOpened = false
      
      try {
        const response = await axios.get(`${API_BASE_URL}/messages/random`)
        this.fortuneMessage = response.data.message
        this.currentMessageId = response.data.id
      } catch (err) {
        this.error = '포춘 쿠키를 가져오는데 실패했습니다.'
        console.error(err)
        this.showFortune = false
      } finally {
        this.loading = false
      }
    },
    async openCookie() {
      if (this.isOpened) return
      
      this.isOpened = true
      
      // 메시지를 읽음으로 표시
      if (this.currentMessageId) {
        try {
          await axios.patch(`${API_BASE_URL}/messages/${this.currentMessageId}/read`)
        } catch (err) {
          console.error('메시지 읽음 처리 실패:', err)
        }
      }
    },
    reset() {
      this.showFortune = false
      this.isOpened = false
      this.fortuneMessage = ''
      this.currentMessageId = null
    }
  }
}
</script>

<style scoped>
.home-container {
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.title {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.input-section {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.message-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  margin-bottom: 1rem;
  transition: border-color 0.3s;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
}

.submit-btn, .fortune-btn {
  width: 100%;
  padding: 1rem;
  margin: 0.5rem 0;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  touch-action: manipulation;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.fortune-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.submit-btn:active, .fortune-btn:active {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fortune-section {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.fortune-cookie {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 2rem auto;
  cursor: pointer;
  touch-action: manipulation;
}

.cookie-top, .cookie-bottom {
  position: absolute;
  width: 100%;
  height: 50%;
  background: linear-gradient(135deg, #d4a574 0%, #c49460 100%);
  border-radius: 50%;
  transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.cookie-top {
  top: 0;
  z-index: 2;
  transform-origin: bottom center;
}

.cookie-bottom {
  bottom: 0;
  z-index: 1;
}

.fortune-cookie.opened .cookie-top {
  transform: rotateX(180deg) translateY(-20px);
  opacity: 0;
}

.fortune-paper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  width: 180px;
  min-height: 120px;
  background: #fff8e1;
  border: 2px solid #ffd54f;
  border-radius: 10px;
  padding: 1.5rem;
  z-index: 3;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  animation: unfold 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
}

.fortune-cookie.opened .fortune-paper {
  transform: translate(-50%, -50%) scale(1);
}

@keyframes unfold {
  0% {
    transform: translate(-50%, -50%) scale(0) rotate(0deg);
    opacity: 0;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1) rotate(5deg);
  }
  100% {
    transform: translate(-50%, -50%) scale(1) rotate(0deg);
    opacity: 1;
  }
}

.fortune-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  font-weight: 500;
  word-break: keep-all;
}

.reset-btn {
  margin-top: 1.5rem;
  padding: 0.8rem 2rem;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  touch-action: manipulation;
}

.reset-btn:active {
  background: #667eea;
  color: white;
  transform: scale(0.95);
}

.loading, .error {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 10px;
  font-weight: bold;
}

.loading {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
}

.error {
  background: #ffebee;
  color: #c62828;
}

/* 모바일 반응형 */
@media (max-width: 600px) {
  .title {
    font-size: 2rem;
    margin-bottom: 1.5rem;
  }

  .input-section, .fortune-section {
    padding: 1.5rem;
  }

  .fortune-cookie {
    width: 180px;
    height: 180px;
  }

  .fortune-paper {
    width: 160px;
    padding: 1rem;
  }

  .fortune-text {
    font-size: 1rem;
  }
}

@media (max-width: 400px) {
  .title {
    font-size: 1.5rem;
  }

  .fortune-cookie {
    width: 150px;
    height: 150px;
  }

  .fortune-paper {
    width: 140px;
    padding: 0.8rem;
  }
}
</style>

