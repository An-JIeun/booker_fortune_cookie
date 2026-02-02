<template>
  <div class="home-container">
    <!-- 첫 화면: 포춘쿠키 접시와 헤더 -->
    <div v-if="currentStep === 'home'" class="home-screen">
      <!-- 포춘쿠키 접시 -->
      <div class="plate-container">
        <div class="plate">
          <div 
            v-for="(cookie, index) in cookieBasket" 
            :key="index"
            class="cookie-on-plate"
            :style="getCookiePosition(index)"
            :data-index="index"
          >
            <div class="cookie-image-wrapper">
              <img 
                src="/fortune-cookie.png" 
                alt="포춘쿠키" 
                class="cookie-image"
                @error="handleImageError"
              />
              <div class="cookie-fallback" v-if="imageError"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 헤더 애니메이션 -->
      <h1 class="header-title" :class="{ 'show': showHeader }">
        활자중독자들 설날 이벤트<br>
        <span class="subtitle">🥠 독서 포춘쿠키 나누기 🥠</span>
      </h1>

      <!-- 안내 메시지 -->
      <p class="header-message" :class="{ 'show': showMessage }">
        쿠키를 구우면 다른 회원이 구운 쿠키를 받을 수 있습니다!<br>
        회원들에게 연초 인사와 책 추천 글을 작성해주세요!
      </p>

      <!-- 나도 쿠키 만들기 버튼 -->
      <button 
        v-if="showHeader" 
        class="create-cookie-btn" 
        :class="{ 'show': showButton }"
        @click="goToInput"
      >
        나도 쿠키 만들기
      </button>
    </div>

    <!-- 메시지 입력 섹션 -->
    <div v-if="currentStep === 'input'" class="input-section">
      <h2 class="input-title">포춘 쿠키 만들기</h2>
      
      <div class="input-group">
        <label class="input-label">🍀 쿠키를 열어볼 사람을 위한 설날 메시지</label>
        <textarea
          v-model="newYearMessage"
          placeholder="설날을 축하하는 따뜻한 메시지를 입력하세요..."
          class="message-input"
          rows="4"
        ></textarea>
      </div>

      <div class="input-group">
        <label class="input-label">📚 쿠키를 열어볼 사람을 위한 책 추천</label>
        <textarea
          v-model="bookRecommendation"
          placeholder="추천하고 싶은 책과 이유를 입력하세요..."
          class="message-input"
          rows="4"
        ></textarea>
      </div>

      <button 
        @click="createFortuneCookie" 
        class="create-btn" 
        :disabled="!newYearMessage.trim() || !bookRecommendation.trim() || isBaking"
      >
        {{ isBaking ? '구워지는 중...' : '포춘쿠키 만들기 🍪' }}
      </button>
      <button @click="goHome" class="back-btn">돌아가기</button>
    </div>

    <!-- 오븐 애니메이션 섹션 -->
    <div v-if="currentStep === 'baking'" class="baking-section">
      <div class="oven">
        <div class="oven-door">
          <div class="oven-window">
            <div class="flame flame1"></div>
            <div class="flame flame2"></div>
            <div class="flame flame3"></div>
            <div class="cookie-in-oven" :class="{ 'baking': true }">
              <div class="cookie-baking">
                <img 
                  src="/fortune-cookie.png" 
                  alt="포춘쿠키" 
                  class="cookie-baking-image"
                  @error="handleBakingImageError"
                />
                <div class="cookie-baking-fallback" v-if="bakingImageError"></div>
              </div>
            </div>
          </div>
        </div>
        <div class="oven-controls">
          <div class="oven-knob"></div>
        </div>
      </div>
      <p class="baking-text">🔥 포춘 쿠키를 굽는 중... 🔥</p>
    </div>

    <!-- 포춘 쿠키 열기 섹션 -->
    <div v-if="currentStep === 'opening'" class="fortune-section">
      <div class="fortune-cookie" :class="{ 'opened': isOpened, 'shaking': isShaking }" @click="shakeAndOpenCookie">
        <div v-if="!isOpened" class="cookie-image-container">
          <img 
            src="/fortune-cookie.png" 
            alt="포춘쿠키" 
            class="fortune-cookie-image"
            @error="handleFortuneImageError"
          />
          <div class="fortune-cookie-fallback" v-if="fortuneImageError"></div>
        </div>
        <div class="fortune-paper" v-if="isOpened">
          <button class="close-btn" @click.stop="closeFortune">×</button>
          <div class="fortune-content">
            <div v-if="currentMessageId === 0" class="default-message-header">
              <p class="default-header-text">첫 쿠키입니다🍀 운영자의 쿠키를 드리도록 하겠습니다🥠</p>
            </div>
            <div v-if="isLuckyMessage && currentMessageId !== 0" class="lucky-message-header">
              <p class="lucky-header-text">🎉 럭키 메시지! 🎉<br>모든 쿠키를 읽으셨네요! 랜덤으로 선택된 특별한 메시지입니다🥠</p>
            </div>
            <div class="fortune-section-item">
              <h3 class="fortune-label">설날 메시지</h3>
              <p class="fortune-text">{{ fortuneData.new_year_message }}</p>
            </div>
            <div class="fortune-section-item">
              <h3 class="fortune-label">📚추천하는 책</h3>
              <p class="fortune-text">{{ fortuneData.book_recommendation }}</p>
            </div>
          </div>
        </div>
      </div>
      <p v-if="!isOpened" class="click-hint"> 🍪 포춘 쿠키를 클릭하세요! 🍪</p>
      <button @click="goHome" class="reset-btn">다시 하기</button>
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
      currentStep: 'home', // 'home', 'input', 'baking', 'opening'
      showHeader: false,
      showMessage: false,
      showButton: false,
      cookieBasket: [],
      newYearMessage: '',
      bookRecommendation: '',
      isBaking: false,
      isOpened: false,
      fortuneData: {
        new_year_message: '',
        book_recommendation: ''
      },
      currentMessageId: null,
      loading: false,
      error: null,
      imageError: false,
      bakingImageError: false,
      fortuneImageError: false,
      isShaking: false,
      createdMessageId: null, // 방금 생성한 메시지 ID (자기 자신이 작성한 메시지 제외용)
      isLuckyMessage: false, // 모든 쿠키를 읽었을 때 나오는 럭키 메시지 여부
    }
  },
  mounted() {
    this.loadCookieCount()
    // 헤더 애니메이션 시작
    setTimeout(() => {
      this.showHeader = true
      setTimeout(() => {
        this.showMessage = true
        setTimeout(() => {
          this.showButton = true
        }, 500)
      }, 500)
    }, 500)
  },
  methods: {
    getCookiePosition(index) {
      const total = this.cookieBasket.length
      if (total === 0) return {}
      
      const angle = (index / total) * 2 * Math.PI
      // 접시 크기에 비례하여 radius 계산 (접시 반지름의 약 35%로 조정하여 안쪽으로 배치)
      // 기본 접시: 280px (반지름 140px) -> radius 49px
      // 태블릿 접시: 240px (반지름 120px) -> radius 42px  
      // 모바일 접시: 200px (반지름 100px) -> radius 35px
      let radius
      if (window.innerWidth <= 400) {
        radius = 35  // 모바일: 접시 반지름 100px의 35%
      } else if (window.innerWidth <= 768) {
        radius = 42  // 태블릿: 접시 반지름 120px의 35%
      } else {
        radius = 49  // 데스크톱: 접시 반지름 140px의 35%
      }
      const x = Math.cos(angle) * radius
      const y = Math.sin(angle) * radius
      const rotation = (angle * 180) / Math.PI
      
      // CSS 변수로 최종 위치 저장
      return {
        '--final-x': `${x}px`,
        '--final-y': `${y}px`,
        '--final-rotation': `${rotation}deg`,
        '--animation-delay': `${index * 0.1}s`,
        position: 'absolute',
        left: '50%',
        top: '50%',
        transform: `translate(var(--final-x, 0px), var(--final-y, 0px)) rotate(var(--final-rotation, 0deg))`
      }
    },
    async loadCookieCount() {
      try {
        // 데이터베이스에서 최신 개수를 가져오기 위해 캐시 방지
        const response = await axios.get(`${API_BASE_URL}/messages/count`, {
          params: { _t: Date.now() },
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        })
        const count = response.data.count
        console.log('데이터베이스에서 조회한 쿠키 개수:', count)
        
        // 데이터베이스에 있는 실제 개수만큼 쿠키 표시
        if (count > 0) {
          this.cookieBasket = Array(count).fill(null).map((_, i) => ({ id: i + 1 }))
        } else {
          this.cookieBasket = []
        }
      } catch (err) {
        console.error('쿠키 개수 로드 실패:', err)
        this.cookieBasket = []
      }
    },
    goToInput() {
      this.currentStep = 'input'
    },
    goHome() {
      this.currentStep = 'home'
      this.showHeader = false
      this.showMessage = false
      this.showButton = false
      this.isOpened = false
      this.fortuneData = { new_year_message: '', book_recommendation: '' }
      this.currentMessageId = null
      this.newYearMessage = ''
      this.bookRecommendation = ''
      this.createdMessageId = null // 초기화
      this.isLuckyMessage = false // 초기화
      
      setTimeout(() => {
        this.showHeader = true
        setTimeout(() => {
          this.showMessage = true
          setTimeout(() => {
            this.showButton = true
          }, 500)
        }, 500)
      }, 100)
      
      this.loadCookieCount()
    },
    async createFortuneCookie() {
      if (!this.newYearMessage.trim() || !this.bookRecommendation.trim() || this.isBaking) return
      
      this.isBaking = true
      this.error = null
      
      try {
        const response = await axios.post(`${API_BASE_URL}/messages`, {
          new_year_message: this.newYearMessage,
          book_recommendation: this.bookRecommendation
        })
        
        console.log('메시지 생성 응답:', response.data)
        console.log('생성된 메시지 ID:', response.data.id)
        
        // 방금 생성한 메시지 ID 저장 (자기 자신이 작성한 메시지 제외용)
        this.createdMessageId = response.data.id
        
        // 오븐 애니메이션 시작
        this.currentStep = 'baking'
        this.isBaking = true
        
        // 3초 후 랜덤 쿠키 열기 화면으로 이동
        setTimeout(async () => {
          this.isBaking = false
          await this.loadCookieCount()
          // 랜덤 쿠키 가져오기 (자기 자신이 작성한 메시지 제외)
          this.currentStep = 'opening'
          this.isOpened = false
          this.isShaking = false
          await this.fetchRandomCookie()
        }, 3000)
        
      } catch (err) {
        this.error = '포춘 쿠키 만들기에 실패했습니다.'
        console.error(err)
        this.isBaking = false
      }
    },
    handleImageError(event) {
      this.imageError = true
      if (event.target) {
        event.target.style.display = 'none'
      }
    },
    handleBakingImageError(event) {
      this.bakingImageError = true
      if (event.target) {
        event.target.style.display = 'none'
      }
    },
    handleFortuneImageError(event) {
      this.fortuneImageError = true
      if (event.target) {
        event.target.style.display = 'none'
      }
    },
    async shakeAndOpenCookie() {
      if (this.isOpened) return
      
      // 흔들림 애니메이션 시작
      this.isShaking = true
      
      // 흔들림 후 포춘 쿠키 열기
      setTimeout(() => {
        this.isShaking = false
        this.isOpened = true
      }, 600)
    },
    async fetchRandomCookie() {
      this.loading = true
      this.error = null
      
      try {
        // 자기 자신이 작성한 메시지 ID를 제외하기 위한 파라미터
        const params = {}
        if (this.createdMessageId) {
          params.exclude_ids = this.createdMessageId.toString()
          console.log('자기 자신이 작성한 메시지 제외:', this.createdMessageId)
        }
        
        // 데이터베이스에서 직접 랜덤 메시지 가져오기 (자기 자신이 작성한 메시지 제외)
        console.log('랜덤 쿠키 요청 (데이터베이스에서 직접 조회):', params)
        
        const response = await axios.get(`${API_BASE_URL}/messages/random`, { 
          params,
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        })
        console.log('랜덤 쿠키 응답:', response.data)
        console.log('받은 메시지 ID:', response.data.id)
        
        this.fortuneData = {
          new_year_message: response.data.new_year_message,
          book_recommendation: response.data.book_recommendation
        }
        this.currentMessageId = response.data.id
        this.isLuckyMessage = response.data.is_read || false // 이미 읽은 메시지면 럭키 메시지
        
        if (this.currentMessageId === 0) {
          console.warn('⚠️ 운영자 메시지가 반환되었습니다. 데이터베이스에 메시지가 없거나 모든 메시지가 제외되었을 수 있습니다.')
        } else if (this.isLuckyMessage) {
          console.log('🎉 럭키 메시지입니다! 모든 쿠키를 읽어서 랜덤으로 선택된 메시지입니다.')
        }
        
        // 운영자 메시지(id=0)가 아닌 경우에만 읽음 처리
        if (this.currentMessageId && this.currentMessageId !== 0) {
          try {
            await axios.patch(`${API_BASE_URL}/messages/${this.currentMessageId}/read`)
          } catch (err) {
            console.error('메시지 읽음 처리 실패:', err)
          }
        }
      } catch (err) {
        console.error('랜덤 쿠키 가져오기 실패:', err)
        this.error = '포춘 쿠키를 가져오는데 실패했습니다.'
        this.currentMessageId = null
        this.fortuneData = { new_year_message: '', book_recommendation: '' }
        this.currentStep = 'home'
      } finally {
        this.loading = false
      }
    },
    closeFortune() {
      this.goHome()
    }
  }
}
</script>

<style scoped>
.home-container {
  width: 100%;
  max-width: 600px;
  text-align: center;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
}

/* 첫 화면 */
.home-screen {
  width: 100%;
}

.plate-container {
  position: relative;
  width: 100%;
  height: 350px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: visible;
}

.plate {
  position: relative;
  width: 280px;
  height: 280px;
  background: 
    radial-gradient(circle at 50% 50%, rgba(0, 0, 0, 0.1) 0%, transparent 60%),
    linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
  border-radius: 50%;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.2),
    inset 0 5px 15px rgba(255, 255, 255, 0.8),
    inset 0 -10px 30px rgba(0, 0, 0, 0.15),
    inset 0 0 80px rgba(0, 0, 0, 0.08);
  border: 3px solid #d4d4d4;
  margin: 0 auto;
  overflow: visible;
}

.plate::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 60%;
  background: radial-gradient(circle, rgba(0, 0, 0, 0.12) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.plate::after {
  content: '';
  position: absolute;
  top: 20%;
  left: 20%;
  width: 60%;
  height: 60%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.cookie-on-plate {
  width: 50px;
  height: 50px;
  opacity: 0;
  transform-origin: center;
  animation: cookieDrop 1s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
  animation-delay: var(--animation-delay, 0s);
}

/* 애니메이션: 위에서 떨어지면서 회전하며 최종 위치로 이동 (자연스러운 중력 효과) */
@keyframes cookieDrop {
  0% {
    opacity: 0;
    transform: translate(var(--final-x, 0px), calc(var(--final-y, 0px) - 200px)) rotate(0deg) scale(0.5);
  }
  20% {
    opacity: 0.8;
    transform: translate(var(--final-x, 0px), calc(var(--final-y, 0px) - 120px)) rotate(90deg) scale(0.7);
  }
  40% {
    opacity: 1;
    transform: translate(var(--final-x, 0px), calc(var(--final-y, 0px) - 40px)) rotate(180deg) scale(0.9);
  }
  55% {
    opacity: 1;
    transform: translate(var(--final-x, 0px), calc(var(--final-y, 0px) + 8px)) rotate(270deg) scale(1.05);
  }
  70% {
    opacity: 1;
    transform: translate(var(--final-x, 0px), calc(var(--final-y, 0px) - 3px)) rotate(340deg) scale(0.98);
  }
  85% {
    opacity: 1;
    transform: translate(var(--final-x, 0px), calc(var(--final-y, 0px) + 1px)) rotate(var(--final-rotation, 0deg)) scale(1.01);
  }
  100% {
    opacity: 1;
    transform: translate(var(--final-x, 0px), var(--final-y, 0px)) rotate(var(--final-rotation, 0deg)) scale(1);
  }
}

.cookie-image-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.cookie-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.2));
}

.cookie-fallback {
  width: 100%;
  height: 100%;
  background: 
    /* 중앙 압착 부분의 어두운 그림자 (U자 구조) */
    radial-gradient(ellipse at 50% 70%, rgba(0, 0, 0, 0.25) 0%, rgba(0, 0, 0, 0.15) 15%, transparent 30%),
    /* 반 접힌 부분의 하이라이트 */
    radial-gradient(ellipse at 50% 45%, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.2) 20%, transparent 40%),
    /* 좌우 측면 명암 */
    linear-gradient(90deg, 
      rgba(0, 0, 0, 0.1) 0%,
      transparent 15%,
      transparent 85%,
      rgba(0, 0, 0, 0.1) 100%
    ),
    /* 기본 색상 그라데이션 */
    linear-gradient(135deg, #f4c88a 0%, #d4a574 30%, #c49460 70%, #b8864a 100%);
  /* 얇은 원형 → 반 접힘 형태 */
  border-radius: 50% 50% 50% 50% / 45% 45% 55% 55%;
  /* 원형에서 아래쪽 10도 부분 제외 (175도 ~ 185도), U자 모양을 더 깊게, 끝부분 보존 */
  clip-path: polygon(
    50% 0%,
    100% 0%,
    100% 50%,
    99.8% 55%,
    99.2% 58%,
    98% 60%,
    96% 61%,
    50% 62%,
    4% 61%,
    2% 60%,
    0.8% 58%,
    0.2% 55%,
    0% 50%,
    0% 0%
  );
  position: relative;
  box-shadow: 
    /* 외부 그림자 */
    0 3px 8px rgba(0, 0, 0, 0.3),
    /* 위쪽 반 접힌 부분의 하이라이트 */
    inset 0 3px 6px rgba(255, 255, 255, 0.4),
    /* 중앙 압착 부분의 그림자 */
    inset 0 6px 15px rgba(0, 0, 0, 0.3);
  overflow: visible;
}

.cookie-fallback::before {
  content: '';
  position: absolute;
  top: 78%;
  left: 10%;
  width: 80%;
  height: 3px;
  /* 아래쪽 열린 부분의 가장자리 (투명한 공간의 경계) */
  background: linear-gradient(to right, 
    transparent 0%,
    rgba(0, 0, 0, 0.3) 5%,
    rgba(0, 0, 0, 0.4) 15%,
    rgba(0, 0, 0, 0.5) 25%,
    rgba(0, 0, 0, 0.55) 50%,
    rgba(0, 0, 0, 0.5) 75%,
    rgba(0, 0, 0, 0.4) 85%,
    rgba(0, 0, 0, 0.3) 95%,
    transparent 100%
  );
  border-radius: 2px;
  transform: translateY(-50%);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.cookie-fallback::after {
  content: '';
  position: absolute;
  top: 45%;
  left: 20%;
  width: 60%;
  height: 2px;
  /* 반 접힌 부분의 하이라이트 */
  background: linear-gradient(to right, 
    transparent 0%,
    rgba(255, 255, 255, 0.5) 20%,
    rgba(255, 255, 255, 0.6) 50%,
    rgba(255, 255, 255, 0.5) 80%,
    transparent 100%
  );
  border-radius: 1px;
  transform: translateY(-50%);
  box-shadow: 0 1px 2px rgba(255, 255, 255, 0.3);
}

.header-title {
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 2rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  opacity: 0;
  transform: translateY(-20px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.header-title.show {
  opacity: 1;
  transform: translateY(0);
}

.subtitle {
  font-size: 2rem;
  display: block;
  margin-top: 0.5rem;
  font-weight: bold;
}

.header-message {
  color: white;
  font-size: 1rem;
  line-height: 1.6;
  margin: 1.5rem auto 2rem;
  max-width: 500px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.header-message.show {
  opacity: 1;
  transform: translateY(0);
}

.create-cookie-btn {
  padding: 1.2rem 2.5rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 30px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  touch-action: manipulation;
  background: linear-gradient(135deg, #ff4500 0%, #ff6b35 50%, #ff8c42 100%);
  color: white;
  box-shadow: 
    0 8px 25px rgba(255, 69, 0, 0.6),
    0 0 20px rgba(255, 140, 66, 0.4),
    inset 0 2px 5px rgba(255, 255, 255, 0.2);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s ease, transform 0.8s ease, background 0.3s ease, box-shadow 0.3s ease;
}

.create-cookie-btn.show {
  opacity: 1;
  transform: translateY(0);
}

.create-cookie-btn:hover {
  background: linear-gradient(135deg, #ff5500 0%, #ff7b45 50%, #ff9c52 100%);
  box-shadow: 
    0 10px 30px rgba(255, 69, 0, 0.7),
    0 0 25px rgba(255, 140, 66, 0.5),
    inset 0 2px 5px rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.create-cookie-btn:active {
  background: linear-gradient(135deg, #ff3500 0%, #ff5b25 50%, #ff7c32 100%);
  transform: translateY(0) scale(0.98);
  box-shadow: 
    0 4px 15px rgba(255, 69, 0, 0.5),
    0 0 15px rgba(255, 140, 66, 0.3),
    inset 0 2px 5px rgba(0, 0, 0, 0.2);
}

/* 입력 섹션 */
.input-section {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 100%;
}

.input-title {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 2rem;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.input-label {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.5rem;
}

.message-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  transition: border-color 0.3s;
}

.message-input:focus {
  outline: none;
  border-color: #ff8c42;
}

.create-btn {
  width: 100%;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  touch-action: manipulation;
  background: linear-gradient(135deg, #ff4500 0%, #ff6b35 50%, #ff8c42 100%);
  color: white;
  box-shadow: 
    0 6px 20px rgba(255, 69, 0, 0.5),
    0 0 15px rgba(255, 140, 66, 0.3),
    inset 0 2px 4px rgba(255, 255, 255, 0.2);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.create-btn:hover {
  background: linear-gradient(135deg, #ff5500 0%, #ff7b45 50%, #ff9c52 100%);
  box-shadow: 
    0 8px 25px rgba(255, 69, 0, 0.6),
    0 0 20px rgba(255, 140, 66, 0.4),
    inset 0 2px 4px rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.create-btn:active {
  background: linear-gradient(135deg, #ff3500 0%, #ff5b25 50%, #ff7c32 100%);
  transform: scale(0.98);
  box-shadow: 
    0 3px 10px rgba(255, 69, 0, 0.4),
    0 0 10px rgba(255, 140, 66, 0.2),
    inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.create-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-btn {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #ff8c42;
  background: white;
  color: #ff8c42;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  touch-action: manipulation;
}

.back-btn:active {
  background: #ff8c42;
  color: white;
  transform: scale(0.95);
}

/* 오븐 애니메이션 */
.baking-section {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.oven {
  width: 300px;
  height: 250px;
  background: linear-gradient(135deg, #8b7355 0%, #6b5d4f 100%);
  border-radius: 15px;
  position: relative;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  margin-bottom: 2rem;
}

.oven-door {
  width: 100%;
  height: 80%;
  background: linear-gradient(135deg, #9d8b6f 0%, #7a6a56 100%);
  border-radius: 15px 15px 0 0;
  position: relative;
  overflow: hidden;
}

.oven-window {
  width: 200px;
  height: 150px;
  background: rgba(0, 0, 0, 0.8);
  border: 8px solid #5a4a3a;
  border-radius: 10px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.flame {
  position: absolute;
  width: 25px;
  height: 40px;
  background: linear-gradient(to top, 
    #ff0000 0%, 
    #ff6b00 20%, 
    #ffaa00 40%, 
    #ffff00 60%, 
    #ffaa00 80%, 
    #ff6b00 100%
  );
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  animation: flicker 0.4s infinite alternate;
  box-shadow: 
    0 0 10px rgba(255, 107, 0, 0.8),
    0 0 20px rgba(255, 170, 0, 0.6),
    inset 0 -5px 10px rgba(255, 0, 0, 0.3);
  filter: blur(0.5px);
}

.flame::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 15px;
  height: 20px;
  background: linear-gradient(to top, #ffff00 0%, #ffaa00 100%);
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  opacity: 0.8;
  animation: flickerInner 0.3s infinite alternate;
}

.flame::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 8px;
  background: radial-gradient(ellipse, rgba(255, 170, 0, 0.6) 0%, transparent 70%);
  border-radius: 50%;
}

.flame1 {
  bottom: 15px;
  left: 25%;
  animation-delay: 0s;
}

.flame2 {
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 45px;
  animation-delay: 0.15s;
}

.flame3 {
  bottom: 15px;
  right: 25%;
  animation-delay: 0.3s;
}

@keyframes flicker {
  0% {
    transform: scaleY(1) scaleX(1) translateY(0);
    opacity: 1;
  }
  50% {
    transform: scaleY(1.15) scaleX(0.95) translateY(-2px);
    opacity: 0.9;
  }
  100% {
    transform: scaleY(1.3) scaleX(0.9) translateY(-4px);
    opacity: 0.85;
  }
}

@keyframes flickerInner {
  0% {
    transform: translateX(-50%) scaleY(1) scaleX(1);
    opacity: 0.8;
  }
  100% {
    transform: translateX(-50%) scaleY(1.2) scaleX(0.9);
    opacity: 1;
  }
}

.cookie-in-oven {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.cookie-baking {
  width: 70px;
  height: 70px;
  position: relative;
  animation: baking 1.2s infinite;
}

.cookie-baking-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 15px rgba(255, 170, 0, 0.8)) brightness(1.1);
  animation: bakingRotate 1.2s infinite;
}

.cookie-baking-fallback {
  width: 100%;
  height: 100%;
  background: 
    /* 중앙 압착 부분의 어두운 그림자 (U자 구조) */
    radial-gradient(ellipse at 50% 70%, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.2) 15%, transparent 30%),
    /* 반 접힌 부분의 하이라이트 */
    radial-gradient(ellipse at 50% 45%, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.3) 20%, transparent 40%),
    /* 좌우 측면 명암 */
    linear-gradient(90deg, 
      rgba(0, 0, 0, 0.12) 0%,
      transparent 15%,
      transparent 85%,
      rgba(0, 0, 0, 0.12) 100%
    ),
    /* 기본 색상 그라데이션 */
    linear-gradient(135deg, #f4c88a 0%, #d4a574 30%, #c49460 70%, #b8864a 100%);
  /* 얇은 원형 → 반 접힘 형태 */
  border-radius: 50% 50% 50% 50% / 45% 45% 55% 55%;
  /* 원형에서 아래쪽 10도 부분 제외 (175도 ~ 185도), U자 모양을 더 깊게, 끝부분 보존 */
  clip-path: polygon(
    50% 0%,
    100% 0%,
    100% 50%,
    99.8% 55%,
    99.2% 58%,
    98% 60%,
    96% 61%,
    50% 62%,
    4% 61%,
    2% 60%,
    0.8% 58%,
    0.2% 55%,
    0% 50%,
    0% 0%
  );
  position: relative;
  box-shadow: 
    /* 오븐 빛 효과 */
    0 0 20px rgba(255, 170, 0, 0.6),
    0 0 40px rgba(255, 107, 0, 0.4),
    /* 외부 그림자 */
    0 3px 8px rgba(0, 0, 0, 0.3),
    /* 위쪽 반 접힌 부분의 하이라이트 */
    inset 0 3px 6px rgba(255, 255, 255, 0.4),
    /* 중앙 압착 부분의 그림자 */
    inset 0 6px 15px rgba(0, 0, 0, 0.3);
  animation: bakingRotate 1.2s infinite;
  overflow: visible;
}

.cookie-baking-fallback::before {
  content: '';
  position: absolute;
  top: 78%;
  left: 10%;
  width: 80%;
  height: 4px;
  /* 아래쪽 열린 부분의 가장자리 (투명한 공간의 경계) */
  background: linear-gradient(to right, 
    transparent 0%,
    rgba(0, 0, 0, 0.35) 5%,
    rgba(0, 0, 0, 0.45) 15%,
    rgba(0, 0, 0, 0.55) 25%,
    rgba(0, 0, 0, 0.6) 50%,
    rgba(0, 0, 0, 0.55) 75%,
    rgba(0, 0, 0, 0.45) 85%,
    rgba(0, 0, 0, 0.35) 95%,
    transparent 100%
  );
  border-radius: 2px;
  transform: translateY(-50%);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
}

@keyframes baking {
  0%, 100% {
    transform: scale(1) translateY(0);
  }
  25% {
    transform: scale(1.05) translateY(-3px);
  }
  50% {
    transform: scale(1.1) translateY(-5px);
  }
  75% {
    transform: scale(1.05) translateY(-3px);
  }
}

@keyframes bakingRotate {
  0%, 100% {
    transform: rotate(0deg);
    filter: drop-shadow(0 0 15px rgba(255, 170, 0, 0.8)) brightness(1.1);
  }
  25% {
    transform: rotate(5deg);
    filter: drop-shadow(0 0 20px rgba(255, 170, 0, 1)) brightness(1.15);
  }
  50% {
    transform: rotate(0deg);
    filter: drop-shadow(0 0 25px rgba(255, 107, 0, 0.9)) brightness(1.2);
  }
  75% {
    transform: rotate(-5deg);
    filter: drop-shadow(0 0 20px rgba(255, 170, 0, 1)) brightness(1.15);
  }
}

.oven-controls {
  height: 20%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.oven-knob {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #c0c0c0 0%, #808080 100%);
  border-radius: 50%;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.3);
}

.baking-text {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  margin-top: 1rem;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

/* 포춘 쿠키 열기 섹션 */
.fortune-section {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 100%;
}

.fortune-cookie {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 2rem auto;
  cursor: pointer;
  touch-action: manipulation;
  transition: transform 0.3s ease;
}

.fortune-cookie:hover {
  transform: scale(1.05);
}

.fortune-cookie.shaking {
  animation: shake 0.6s ease-in-out;
}

.cookie-image-container {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.fortune-cookie.opened .cookie-image-container {
  transform: scale(0) rotate(360deg);
  opacity: 0;
}

.fortune-cookie-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 5px 15px rgba(0, 0, 0, 0.3));
  transition: transform 0.3s ease;
}

.fortune-cookie-fallback {
  width: 100%;
  height: 100%;
  background: 
    /* 중앙 압착 부분의 어두운 그림자 (U자 구조) */
    radial-gradient(ellipse at 50% 75%, rgba(0, 0, 0, 0.28) 0%, rgba(0, 0, 0, 0.18) 15%, transparent 30%),
    /* 반 접힌 부분의 하이라이트 */
    radial-gradient(ellipse at 50% 45%, rgba(255, 255, 255, 0.45) 0%, rgba(255, 255, 255, 0.25) 20%, transparent 40%),
    /* 좌우 측면 명암 */
    linear-gradient(90deg, 
      rgba(0, 0, 0, 0.12) 0%,
      transparent 15%,
      transparent 85%,
      rgba(0, 0, 0, 0.12) 100%
    ),
    /* 기본 색상 그라데이션 */
    linear-gradient(135deg, #f4c88a 0%, #d4a574 30%, #c49460 70%, #b8864a 100%);
  /* 얇은 원형 → 반 접힘 형태 */
  border-radius: 50% 50% 50% 50% / 45% 45% 55% 55%;
  /* 원형에서 아래쪽 10도 부분 제외 (175도 ~ 185도), U자 모양을 더 깊게, 끝부분 보존 */
  clip-path: polygon(
    50% 0%,
    100% 0%,
    100% 50%,
    99.8% 55%,
    99.2% 58%,
    98% 60%,
    96% 61%,
    50% 62%,
    4% 61%,
    2% 60%,
    0.8% 58%,
    0.2% 55%,
    0% 50%,
    0% 0%
  );
  position: relative;
  box-shadow: 
    /* 외부 그림자 */
    0 5px 15px rgba(0, 0, 0, 0.3),
    /* 위쪽 반 접힌 부분의 하이라이트 */
    inset 0 3px 6px rgba(255, 255, 255, 0.4),
    /* 중앙 압착 부분의 그림자 */
    inset 0 6px 15px rgba(0, 0, 0, 0.3);
  overflow: visible;
}

.fortune-cookie-fallback::before {
  content: '';
  position: absolute;
  top: 78%;
  left: 10%;
  width: 80%;
  height: 4px;
  /* 아래쪽 열린 부분의 가장자리 (투명한 공간의 경계) */
  background: linear-gradient(to right, 
    transparent 0%,
    rgba(0, 0, 0, 0.35) 5%,
    rgba(0, 0, 0, 0.45) 15%,
    rgba(0, 0, 0, 0.55) 25%,
    rgba(0, 0, 0, 0.6) 50%,
    rgba(0, 0, 0, 0.55) 75%,
    rgba(0, 0, 0, 0.45) 85%,
    rgba(0, 0, 0, 0.35) 95%,
    transparent 100%
  );
  border-radius: 2px;
  transform: translateY(-50%);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
}

.fortune-cookie-fallback::after {
  content: '';
  position: absolute;
  top: 45%;
  left: 20%;
  width: 60%;
  height: 3px;
  /* 반 접힌 부분의 하이라이트 */
  background: linear-gradient(to right, 
    transparent 0%,
    rgba(255, 255, 255, 0.55) 20%,
    rgba(255, 255, 255, 0.65) 50%,
    rgba(255, 255, 255, 0.55) 80%,
    transparent 100%
  );
  border-radius: 1px;
  transform: translateY(-50%);
  box-shadow: 0 1px 3px rgba(255, 255, 255, 0.4);
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0) rotate(0deg);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-8px) rotate(-5deg);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(8px) rotate(5deg);
  }
}

.fortune-paper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  width: 280px;
  min-height: 200px;
  background: #fff8e1;
  border: 2px solid #ffd54f;
  border-radius: 10px;
  padding: 1.5rem;
  z-index: 3;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  animation: unfold 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
}

/* fortune-paper 내부 요소들의 위치 기준을 위해 relative 추가 */
.fortune-paper {
  position: relative;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 140, 66, 0.2);
  border-radius: 50%;
  font-size: 24px;
  font-weight: bold;
  color: #ff8c42;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  z-index: 10;
  line-height: 1;
  padding: 0;
  touch-action: manipulation;
}

.close-btn:hover {
  background: rgba(255, 140, 66, 0.4);
  transform: scale(1.1);
  color: #ff6b35;
}

.close-btn:active {
  transform: scale(0.95);
  background: rgba(255, 140, 66, 0.6);
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

.fortune-content {
  text-align: left;
}

.default-message-header {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%);
  border-radius: 10px;
  border: 2px solid #ffd54f;
  text-align: center;
}

.default-header-text {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ff8c42;
  margin: 0;
  line-height: 1.6;
}

.lucky-message-header {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%);
  border-radius: 10px;
  border: 2px solid #ffd54f;
  text-align: center;
  animation: luckyPulse 2s ease-in-out infinite;
}

.lucky-header-text {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ff6b35;
  margin: 0;
  line-height: 1.6;
}

@keyframes luckyPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 140, 66, 0.7);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 0 0 10px rgba(255, 140, 66, 0);
  }
}

.fortune-section-item {
  margin-bottom: 1.5rem;
}

.fortune-section-item:last-child {
  margin-bottom: 0;
}

.fortune-label {
  font-size: 1rem;
  font-weight: bold;
  color: #d4a574;
  margin-bottom: 0.5rem;
  border-bottom: 2px solid #ffd54f;
  padding-bottom: 0.3rem;
}

.fortune-text {
  font-size: 1rem;
  line-height: 1.8;
  color: #333;
  word-break: keep-all;
}

.click-hint {
  margin-top: 1rem;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
  animation: fadeInOut 2s infinite;
}

@keyframes fadeInOut {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

.reset-btn {
  margin-top: 1.5rem;
  padding: 0.8rem 2rem;
  border: 2px solid #ff8c42;
  background: white;
  color: #ff8c42;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  touch-action: manipulation;
}

.reset-btn:active {
  background: #ff8c42;
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
  color: #ff8c42;
}

.error {
  background: #ffebee;
  color: #c62828;
}

/* 모바일 반응형 */
@media (max-width: 600px) {
  .header-title {
    font-size: 1.2rem;
  }

  .subtitle {
    font-size: 1.6rem;
  }

  .header-message {
    font-size: 0.9rem;
    margin: 1rem auto 1.5rem;
    padding: 0 1rem;
  }

  .plate {
    width: 240px;
    height: 240px;
  }

  .cookie-on-plate {
    width: 45px;
    height: 45px;
  }

  .input-section, .baking-section, .fortune-section {
    padding: 1.5rem;
  }

  .oven {
    width: 250px;
    height: 200px;
  }

  .oven-window {
    width: 160px;
    height: 120px;
  }

  .fortune-paper {
    width: 240px;
    padding: 1rem;
  }
}

@media (max-width: 400px) {
  .header-title {
    font-size: 1rem;
  }

  .subtitle {
    font-size: 1.4rem;
  }

  .plate {
    width: 200px;
    height: 200px;
  }

  .cookie-on-plate {
    width: 35px;
    height: 35px;
  }

  .fortune-paper {
    width: 200px;
    padding: 0.8rem;
  }
}
</style>
