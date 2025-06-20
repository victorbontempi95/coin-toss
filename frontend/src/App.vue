<template>
  <div class="app">
    <!-- Introduction Page -->
    <div v-if="currentPage === 'intro'" class="intro-page">
      <div class="intro-content">
        <div class="intro-header">
          <h1 class="intro-title">
            Coin Toss <span class="text-primary">Volatility Simulator</span>
          </h1>
          <p class="intro-subtitle">
            See how volatility can destroy your results, even when you have the edge
          </p>
        </div>

        <!-- Full-width parameter section at the top -->
        <div class="parameter-setup-top">
          <h3>Set Your Parameters</h3>
          <div class="parameter-grid">
            <!-- Keep the same parameter inputs as before -->
            <div class="parameter-group">
              <label class="parameter-label">Win Return (%)</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model.number="winReturn" 
                  class="parameter-input"
                  step="1"
                  min="0"
                  max="200"
                >
                <span class="input-suffix">%</span>
              </div>
              <p class="parameter-help">How much you gain when you win (e.g., 50 = +50%)</p>
            </div>

            <div class="parameter-group">
              <label class="parameter-label">Loss Return (%)</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model.number="loseReturn" 
                  class="parameter-input"
                  step="1"
                  min="-100"
                  max="0"
                >
                <span class="input-suffix">%</span>
              </div>
              <p class="parameter-help">How much you lose when you lose (e.g., -40 = -40%)</p>
            </div>

            <div class="parameter-group">
              <label class="parameter-label">Simulation Rounds</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model.number="simulationRounds" 
                  class="parameter-input"
                  step="10"
                  min="1"
                  max="10000"
                >
                <span class="input-suffix">tosses</span>
              </div>
              <p class="parameter-help">Number of coin tosses for auto simulation (e.g., 100)</p>
            </div>
          </div>

          <div class="expected-value-preview">
            <span class="ev-label">Expected Value per Round:</span>
            <span class="ev-value" :class="expectedValue >= 1 ? 'text-success' : 'text-danger'">
              {{ ((0.5 * (1 + winReturn/100) + 0.5 * (1 + loseReturn/100)) * 100 - 100).toFixed(2) }}%
            </span>
          </div>
          <div class="button-container">
            <button class="start-btn" @click="startSimulator">
              Start Simulation
            </button>
          </div>
        </div>

        <!-- Explanation cards in 3-column grid below -->
        <div class="intro-explanation">
          <div class="explanation-card">
            <h3>What is this simulator?</h3>
            <p>This tool demonstrates how seemingly profitable strategies can lead to ruin due to volatility drag.</p>
            <br>
            <p>Even with positive expected returns, the compounding effect of gains and losses can dramatically impact your final results.</p>
          </div>

          <div class="explanation-card">
            <h3>How it works</h3>
            <ul>
              <li>Start with $100</li>
              <li>Toss a coin</li>
              <li>Win: Your balance increases by the win percentage</li>
              <li>Lose: Your balance decreases by the loss percentage</li>
              <li>Watch how volatility affects your results over time</li>
            </ul>
          </div>

          <div class="explanation-card">
            <h3>Key Insight</h3>
            <p>A strategy that wins 50% when right but loses 40% when wrong has a positive expected value (+5%).</p>
            <br>
            <p>However, due to volatility drag, you'll likely lose money over many rounds.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Simulator Page (your existing content) -->
    <main v-if="currentPage === 'simulator'" class="main">
      <div class="hero-section">
        <h1 class="hero-title">
          Coin Toss <span class="text-primary">Volatility Simulator</span>
        </h1>
        <p class="hero-subtitle">
          Experience the power of compounding returns with variable risk parameters
        </p>
        <button class="back-btn" @click="currentPage = 'intro'">← Back</button>
      </div>

      <div class="simulation-section-mobile">
        <h4 class="section-title">Quick Simulation</h4>
        
        <div class="simulation-controls">
          <div class="input-group">
            <label class="setting-label">Number of Tosses</label>
            <input 
              type="number" 
              v-model.number="simulationRounds" 
              class="setting-input"
              min="1"
              max="1000"
            >
          </div>
        </div>

        <button 
          class="sim-btn"
          @click="runSimulation('random')"
          :disabled="loading"
        >
          {{ loading ? 'Processing...' : 'Run Simulation' }}
        </button>
      </div>

      <!-- Rest of your existing simulator interface... -->
      <div class="trading-interface">
        <!-- Stats Panel - UPDATED to fix win/loss tracking -->
        <div class="panel stats-panel">
          <div class="panel-header">
            <h3>Simulation Overview</h3>
            <div class="status-indicator" :class="getStatusClass()">
              <span class="status-dot"></span>
              Round {{ roundNumber }}
            </div>
          </div>
          
          <div class="wealth-display">
            <div class="wealth-main">
              <span class="wealth-label">Current Balance</span>
              <span class="wealth-value" :class="getWealthClass()">
                ${{ currentWealth.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
              </span>
            </div>
            <div class="wealth-stats">
              <div class="stat-item">
                <span class="stat-label">Wins</span>
                <span class="stat-value text-success">{{ totalWins }}</span>
              </div>
              <div class="stat-separator">|</div>
              <div class="stat-item">
                <span class="stat-label">Losses</span>
                <span class="stat-value text-danger">{{ totalLosses }}</span>
              </div>
            </div>
          </div>

          <div class="expected-value">
            <span class="ev-label">Expected Value per Round:</span>
            <span class="ev-value" :class="expectedValue >= 1 ? 'text-success' : 'text-danger'">
              {{ (expectedValue * 100 - 100).toFixed(2) }}%
            </span>
          </div>
        </div>

        <!-- Chart Panel -->
        <div class="panel chart-panel">
          <div class="panel-header">
            <h3>PnL Over Time</h3>
          </div>
          
          <div class="chart-container">
            <canvas ref="chartCanvas" class="chart-canvas"></canvas>
          </div>

          <div class="chart-stats">
            <div class="chart-stat">
              <span class="chart-stat-label">Starting Balance</span>
              <span class="chart-stat-value">$100.00</span>
            </div>
            <div class="chart-stat">
              <span class="chart-stat-label">Peak Balance</span>
              <span class="chart-stat-value text-success">${{ Math.max(...wealthHistory).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}</span>
            </div>
            <div class="chart-stat">
              <span class="chart-stat-label">Current Balance</span>
              <span class="chart-stat-value" :class="getWealthClass()">
                ${{ currentWealth.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
              </span>
            </div>
            <div class="chart-stat">
              <span class="chart-stat-label">Total Return</span>
              <span class="chart-stat-value" :class="getTotalReturnClass()">
                {{ ((currentWealth / 100 - 1) * 100).toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Controls Panel - UPDATED for percentage inputs -->
        <div class="panel controls-panel">
          <div class="panel-header">
            <h3>Parameters</h3>
          </div>

          <div class="settings-grid">
            <div class="setting-group">
              <label class="setting-label">Win Return (%)</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model.number="winReturn" 
                  class="setting-input"
                  step="1"
                  min="0"
                  max="200"
                  :disabled="roundNumber > 0"
                >
                <span class="input-suffix">%</span>
              </div>
            </div>

            <div class="setting-group">
              <label class="setting-label">Loss Return (%)</label>
              <div class="input-group">
                <input 
                  type="number" 
                  v-model.number="loseReturn" 
                  class="setting-input"
                  step="1"
                  min="-100"
                  max="0"
                  :disabled="roundNumber > 0"
                >
                <span class="input-suffix">%</span>
              </div>
            </div>
          </div>

          <!-- Rest of your existing controls... -->
          <div class="trading-section">
            <h4 class="section-title">Manual Toss</h4>
            <div class="choice-buttons">
              <button 
                class="choice-btn heads-btn" 
                :class="{ active: selectedChoice === 'heads' }"
                @click="selectedChoice = 'heads'"
                :disabled="loading"
              >
                HEADS
              </button>
              <button 
                class="choice-btn tails-btn" 
                :class="{ active: selectedChoice === 'tails' }"
                @click="selectedChoice = 'tails'"
                :disabled="loading"
              >
                TAILS
              </button>
            </div>
            
            <button 
              class="trade-btn"
              @click="makeChoice(selectedChoice)"
              :disabled="!selectedChoice || loading"
            >
              {{ loading ? 'Processing...' : 'Toss Coin' }}
            </button>
          </div>

          <div class="simulation-section">
            <h4 class="section-title">Simulate Again</h4>
            
            <div class="simulation-controls">
              <div class="input-group">
                <label class="setting-label">Number of Tosses</label>
                <input 
                  type="number" 
                  v-model.number="simulationRounds" 
                  class="setting-input"
                  min="1"
                  max="1000"
                >
              </div>
            </div>

            <button 
              class="sim-btn"
              @click="runSimulation('random')"
              :disabled="loading"
            >
              {{ loading ? 'Processing...' : 'Toss Coins' }}
            </button>
          </div>

          <button class="reset-btn" @click="resetGame" :disabled="loading">
            Reset Portfolio
          </button>
        </div>
      </div>

      <!-- Last Trade Result -->
      <div v-if="lastResult" class="trade-result" :class="lastResult.player_won ? 'result-win' : 'result-loss'">
        <div class="result-content">
          <div class="result-icon">
            {{ lastResult.player_won ? '🎉' : '💸' }}
          </div>
          <div class="result-details">
            <div class="result-main">
              <span class="result-text">
                {{ lastResult.player_won ? 'Coin Toss Won!' : 'Coin Toss Lost' }}
              </span>
              <span class="result-outcome">
                Coin: {{ lastResult.coin_result.toUpperCase() }} | 
                Your Choice: {{ lastResult.player_choice.toUpperCase() }}
              </span>
            </div>
            <div class="result-change">
              <span class="change-label">Balance Change:</span>
              <span class="change-value" :class="lastResult.player_won ? 'text-success' : 'text-danger'">
                {{ lastResult.player_won ? '+' : '' }}${{ (lastResult.new_wealth - lastResult.previous_wealth).toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, nextTick, toRefs } from 'vue'

export default {
  name: 'CoinTossApp',
  setup() {
    const playerId = 'player_' + Math.random().toString(36).substr(2, 9)
    const loading = ref(false)
    const selectedChoice = ref('')
    const winReturn = ref(50)
    const loseReturn = ref(-40)
    const simulationRounds = ref(100)
    const chartView = ref('area')
    const chartCanvas = ref(null)
    const lastResult = ref(null)
    const currentPage = ref('intro')
    
    const gameState = reactive({
      currentWealth: 100,
      roundNumber: 0,
      totalWins: 0,
      totalLosses: 0,
      wealthHistory: [100]
    })

    const { roundNumber, totalWins, totalLosses, wealthHistory } = toRefs(gameState)

    const currentWealth = ref(100)
    const expectedValue = ref(0.9)

    let chart = null

    const formatNumber = (num) => {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(num)
    }

    const getStatusClass = () => {
      if (currentWealth.value > 100) return 'status-profit'
      if (currentWealth.value < 100) return 'status-loss'
      return 'status-neutral'
    }

    const getWealthClass = () => {
      if (currentWealth.value > 100) return 'wealth-profit'
      if (currentWealth.value < 100) return 'wealth-loss'
      return 'wealth-neutral'
    }

    const getTotalReturnClass = () => {
      const returnPct = ((currentWealth.value - 100) / 100) * 100
      return returnPct >= 0 ? 'text-success' : 'text-danger'
    }

    const createChart = () => {
      if (!chartCanvas.value) return

      const ctx = chartCanvas.value.getContext('2d')
      const data = gameState.wealthHistory
      const width = chartCanvas.value.width = chartCanvas.value.offsetWidth * 2
      const height = chartCanvas.value.height = 300 * 2
      
      ctx.scale(2, 2)
      ctx.clearRect(0, 0, width/2, height/2)

      if (data.length < 2) return

      const padding = 40
      const chartWidth = width/2 - padding * 2
      const chartHeight = height/2 - padding * 2

      const minValue = Math.min(...data, 100) * 0.9
      const maxValue = Math.max(...data, 100) * 1.1

      // Grid and axes
      ctx.strokeStyle = '#2a2d3a'
      ctx.lineWidth = 1
      
      // Horizontal grid lines
      for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i
        ctx.beginPath()
        ctx.moveTo(padding, y)
        ctx.lineTo(padding + chartWidth, y)
        ctx.stroke()
      }

      // Vertical grid lines
      for (let i = 0; i <= 10; i++) {
        const x = padding + (chartWidth / 10) * i
        ctx.beginPath()
        ctx.moveTo(x, padding)
        ctx.lineTo(x, padding + chartHeight)
        ctx.stroke()
      }

      // Baseline at $100
      const baselineY = padding + chartHeight - ((100 - minValue) / (maxValue - minValue)) * chartHeight
      ctx.strokeStyle = '#4a9eff'
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.beginPath()
      ctx.moveTo(padding, baselineY)
      ctx.lineTo(padding + chartWidth, baselineY)
      ctx.stroke()
      ctx.setLineDash([])

      // Data line/area
      ctx.beginPath()
      data.forEach((value, index) => {
        const x = padding + (index / (data.length - 1)) * chartWidth
        const y = padding + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })

      if (chartView.value === 'area') {
        // Fill area
        const lastX = padding + chartWidth
        const lastY = padding + chartHeight - ((data[data.length - 1] - minValue) / (maxValue - minValue)) * chartHeight
        ctx.lineTo(lastX, padding + chartHeight)
        ctx.lineTo(padding, padding + chartHeight)
        ctx.closePath()
        
        const gradient = ctx.createLinearGradient(0, padding, 0, padding + chartHeight)
        gradient.addColorStop(0, currentWealth.value >= 100 ? 'rgba(74, 158, 255, 0.3)' : 'rgba(255, 82, 82, 0.3)')
        gradient.addColorStop(1, 'rgba(74, 158, 255, 0.05)')
        ctx.fillStyle = gradient
        ctx.fill()
      }

      // Redraw the line path for stroking
      ctx.beginPath()
      data.forEach((value, index) => {
        const x = padding + (index / (data.length - 1)) * chartWidth
        const y = padding + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })

      // Stroke the line
      ctx.strokeStyle = '#4a9eff'
      ctx.lineWidth = 4
      ctx.stroke()

      // Win-Loss dots on the graph
      if (data.length > 1) {
        data.forEach((value, index) => {
          if (index > 0) {
            const x = padding + (index / (data.length - 1)) * chartWidth
            const y = padding + chartHeight - ((value - minValue) / (maxValue - minValue)) * chartHeight
            
            const previousValue = data[index - 1]
            const isWin = value > previousValue
            
            ctx.beginPath()
            ctx.arc(x, y, 3, 0, 2 * Math.PI) // first number is the dot radius
            ctx.fillStyle = isWin ? '#00c851' : '#ff5252'
            ctx.fill()
            // Removed the white stroke outline
          }
        })
      }

      // Stroke the line (this will be on top of the area but behind the dots)
      ctx.strokeStyle = currentWealth.value >= 100 ? '#4a9eff' : '#ff5252'
      ctx.lineWidth = 3.5
      ctx.stroke()

      // Labels
      ctx.fillStyle = '#a0a3b1'
      ctx.font = '12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      ctx.textAlign = 'center'
      
      // Y-axis labels
      for (let i = 0; i <= 5; i++) {
        const value = minValue + (maxValue - minValue) * (1 - i / 5)
        const y = padding + (chartHeight / 5) * i + 4
        ctx.fillText('$' + value.toFixed(0), padding - 20, y)
      }
    }

    const startSimulator = async () => {
      currentPage.value = 'simulator'
      expectedValue.value = 0.5 * (1 + winReturn.value/100) + 0.5 * (1 + loseReturn.value/100)
      
      // Automatically run simulation when starting
      await runInitialSimulation()
    }

    const runInitialSimulation = async () => {
      loading.value = true
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/simulate/${playerId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            num_tosses: simulationRounds.value,
            win_return: winReturn.value / 100,
            lose_return: loseReturn.value / 100,
            simulation_type: 'random' // Always use random for initial simulation
          })
        })

        const result = await response.json()
        if (result.success) {
          const data = result.data
          gameState.roundNumber = data.total_rounds
          gameState.totalWins = data.total_wins
          gameState.totalLosses = data.total_losses
          gameState.wealthHistory = data.wealth_history
          currentWealth.value = data.final_wealth
          lastResult.value = null
          
          await nextTick()
          createChart()
        }
      } catch (error) {
        console.error('Initial simulation failed:', error)
      } finally {
        loading.value = false
      }
    }

    const makeChoice = async (choice) => {
      if (!choice || loading.value) return

      loading.value = true
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/coin-toss/${playerId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            choice: choice,
            win_return: winReturn.value / 100, // Convert percentage to decimal
            lose_return: loseReturn.value / 100, // Convert percentage to decimal
            current_wealth: currentWealth.value
          })
        })

        const result = await response.json()
        if (result.success) {
          const data = result.data
          // Update all game state properties
          gameState.roundNumber = data.round_number
          gameState.totalWins = data.total_wins
          gameState.totalLosses = data.total_losses
          gameState.wealthHistory = data.wealth_history
          currentWealth.value = data.new_wealth
          lastResult.value = data
          
          await nextTick()
          createChart()
        }
      } catch (error) {
        console.error('Trade failed:', error)
      } finally {
        loading.value = false
      }
    }

    const runSimulation = async (type) => {
      loading.value = true
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/simulate/${playerId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            num_tosses: simulationRounds.value,
            win_return: winReturn.value / 100,
            lose_return: loseReturn.value / 100,
            simulation_type: type
          })
        })

        const result = await response.json()
        if (result.success) {
          const data = result.data
          gameState.roundNumber = data.total_rounds
          gameState.totalWins = data.total_wins
          gameState.totalLosses = data.total_losses
          gameState.wealthHistory = data.wealth_history
          currentWealth.value = data.final_wealth
          lastResult.value = null
          
          await nextTick()
          createChart()
        }
      } catch (error) {
        console.error('Simulation failed:', error)
      } finally {
        loading.value = false
      }
    }
    const resetGame = async () => {
      loading.value = true
      try {
        await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/reset-game/${playerId}`, {
          method: 'POST'
        })
        
        Object.assign(gameState, {
          roundNumber: 0,
          totalWins: 0,
          totalLosses: 0,
          wealthHistory: [100]
        })
        currentWealth.value = 100
        lastResult.value = null
        selectedChoice.value = ''
        
        await nextTick()
        createChart()
      } catch (error) {
        console.error('Reset failed:', error)
      } finally {
        loading.value = false
      }
    }

    watch([winReturn, loseReturn], () => {
      expectedValue.value = 0.5 * (1 + winReturn.value/100) + 0.5 * (1 + loseReturn.value/100)
    })
    watch(() => gameState.totalWins, (newVal, oldVal) => {
      console.log('Wins changed from', oldVal, 'to', newVal)
    })
    watch(() => gameState.totalLosses, (newVal, oldVal) => {
      console.log('Losses changed from', oldVal, 'to', newVal)
    })

    onMounted(() => {
      expectedValue.value = 0.5 * (1 + winReturn.value/100) + 0.5 * (1 + loseReturn.value/100)
      nextTick(() => createChart())
    })

    return {
      playerId,
      loading,
      selectedChoice,
      winReturn,
      loseReturn,
      simulationRounds,
      chartCanvas,
      lastResult,
      roundNumber,
      totalWins,
      totalLosses,
      wealthHistory,
      currentPage,
      startSimulator,
      runInitialSimulation,
      currentWealth,
      expectedValue,
      formatNumber,
      getStatusClass,
      getWealthClass,
      getTotalReturnClass,
      makeChoice,
      runSimulation,
      resetGame
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1d29 0%, #2a2d3a 100%);
  color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Introduction Page Styles */
.intro-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.intro-content {
  max-width: 1000px;
  width: 100%;
}

.intro-header {
  text-align: center;
  margin-bottom: 48px;
}

.intro-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.intro-subtitle {
  font-size: 18px;
  color: #a0a3b1;
  margin-bottom: 0;
}

.intro-explanation {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.explanation-card {
  background: rgba(42, 45, 58, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid #363948;
  border-radius: 12px;
  padding: 24px;
}

.explanation-card h3 {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  color: #4a9eff;
}

.explanation-card p {
  margin: 0;
  color: #a0a3b1;
  line-height: 1.6;
}

.explanation-card ul {
  margin: 0;
  padding-left: 20px;
  color: #a0a3b1;
}

.explanation-card li {
  margin-bottom: 8px;
  line-height: 1.5;
}


.parameter-setup {
  background: rgba(42, 45, 58, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid #363948;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
}

.parameter-setup-top {
  background: rgba(42, 45, 58, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid #363948;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
}

.parameter-setup h3 {
  margin: 0 0 24px 0;
  font-size: 24px;
  font-weight: 600;
}

.parameter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.parameter-group {
  text-align: left;
}

.parameter-label {
  display: block;
  font-size: 16px;
  color: #ffffff;
  font-weight: 500;
  margin-bottom: 8px;
}

.parameter-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(26, 29, 41, 0.8);
  border: 1px solid #4a4d5a;
  border-radius: 6px;
  color: white;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
  font-size: 16px;
  transition: border-color 0.2s;
}

.parameter-input:focus {
  outline: none;
  border-color: #4a9eff;
}

.parameter-help {
  font-size: 14px;
  color: #a0a3b1;
  margin: 8px 0 0 0;
  font-style: italic;
}

.expected-value-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: rgba(74, 158, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(74, 158, 255, 0.2);
  margin-bottom: 32px;
}

.start-btn {
  padding: 16px 48px;
  background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.button-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin-top: 16px;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(74, 158, 255, 0.3);
}

.back-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #4a9eff;
  color: #4a9eff;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 16px;
  margin-top: 24px;
  font-size: 14px;
}

.back-btn:hover {
  background: rgba(74, 158, 255, 0.1);
}

/* Responsive for intro page */
@media (max-width: 768px) {
  .intro-title {
    font-size: 36px;
  }
  
  .intro-explanation {
    grid-template-columns: 1fr;
  }
  
  .parameter-grid {
    grid-template-columns: 1fr;
  }
  
  .parameter-setup {
    padding: 24px;
  }
}

/* Header */
.header {
  background: rgba(26, 29, 41, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #2a2d3a;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  display: flex;
  gap: 32px;
}

.nav-link {
  color: #a0a3b1;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #ffffff;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #4a9eff;
  color: #4a9eff;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(74, 158, 255, 0.1);
}

.btn-primary {
  padding: 8px 16px;
  background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
  border: none;
  color: white;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
}

/* Main Content */
.main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.hero-section {
  text-align: center;
  padding: 60px 0 40px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
}

.text-primary {
  background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  color: #a0a3b1;
  margin-bottom: 0;
}



/* Trading Interface */
.trading-interface {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.panel {
  background: rgba(42, 45, 58, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid #363948;
  border-radius: 12px;
  padding: 24px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

/* Stats Panel */
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4a9eff;
}

.status-profit .status-dot { background: #00c851; }
.status-loss .status-dot { background: #ff5252; }
.status-neutral .status-dot { background: #4a9eff; }

.wealth-display {
  margin-bottom: 20px;
}

.wealth-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.wealth-label {
  font-size: 14px;
  color: #a0a3b1;
}

.wealth-value {
  font-size: 32px;
  font-weight: 700;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
}

.wealth-profit { color: #00c851; }
.wealth-loss { color: #ff5252; }
.wealth-neutral { color: #4a9eff; }

.wealth-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 12px;
  color: #a0a3b1;
}

.stat-value {
  font-weight: 600;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
}

.stat-separator {
  color: #4a4d5a;
}

.expected-value {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(74, 158, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(74, 158, 255, 0.2);
}

.ev-label {
  font-size: 14px;
  color: #a0a3b1;
}

.ev-value {
  font-weight: 600;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
}


.chart-container {
  margin: 20px 0;
  height: 300px;
  position: relative;
}

.chart-canvas {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.chart-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-stat-label {
  font-size: 12px;
  color: #a0a3b1;
}

.chart-stat-value {
  font-weight: 600;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
}

/* Controls Panel */
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label {
  font-size: 14px;
  color: #a0a3b1;
  font-weight: 500;
}

.input-group {
  position: relative;
}

.setting-input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(26, 29, 41, 0.8);
  border: 1px solid #4a4d5a;
  border-radius: 6px;
  color: white;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
  transition: border-color 0.2s;
}

.setting-input:focus {
  outline: none;
  border-color: #4a9eff;
}

.input-suffix {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0a3b1;
  font-size: 14px;
  pointer-events: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 24px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #363948;
}

.choice-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.choice-btn {
  flex: 1;
  padding: 12px;
  background: rgba(26, 29, 41, 0.8);
  border: 2px solid #4a4d5a;
  border-radius: 8px;
  color: #a0a3b1;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.choice-btn:hover {
  border-color: #4a9eff;
  color: white;
}

.choice-btn.active {
  border-color: #4a9eff;
  background: rgba(74, 158, 255, 0.2);
  color: white;
}

.choice-icon {
  font-size: 16px;
}

.trade-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 24px;
}

.trade-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(74, 158, 255, 0.3);
}

.trade-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.simulation-controls {
  margin-bottom: 16px;
}


.sim-btn {
  padding: 10px 16px;
  background: rgba(26, 29, 41, 0.8);
  border: 1px solid #4a4d5a;
  border-radius: 6px;
  color: #a0a3b1;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.sim-btn:hover:not(:disabled) {
  border-color: #4a9eff;
  color: white;
  background: rgba(74, 158, 255, 0.1);
}

.sim-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reset-btn {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px solid #ff5252;
  border-radius: 6px;
  color: #ff5252;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover:not(:disabled) {
  background: rgba(255, 82, 82, 0.1);
}

.reset-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Trade Result */
.trade-result {
  margin: 24px 0;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid;
  animation: slideIn 0.3s ease-out;
}

.result-win {
  background: rgba(0, 200, 81, 0.1);
  border-color: rgba(0, 200, 81, 0.3);
}

.result-loss {
  background: rgba(255, 82, 82, 0.1);
  border-color: rgba(255, 82, 82, 0.3);
}

.result-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.result-icon {
  font-size: 32px;
}

.result-details {
  flex: 1;
}

.result-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.result-text {
  font-size: 18px;
  font-weight: 600;
}

.result-outcome {
  font-size: 14px;
  color: #a0a3b1;
}

.result-change {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sim-btn {
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #4a9eff 0%, #6c5ce7 100%);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
}

.sim-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(74, 158, 255, 0.3);
}

.sim-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.change-label {
  font-size: 14px;
  color: #a0a3b1;
}

.change-value {
  font-weight: 600;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
}

/* Utility Classes */
.text-success {
  color: #00c851;
}

.text-danger {
  color: #ff5252;
}

.text-warning {
  color: #ffbb33;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 1200px) {
  .trading-interface {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .chart-panel {
    order: -1;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .nav {
    display: none;
  }
  
  .main {
    padding: 0 16px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .panel {
    padding: 16px;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .choice-buttons {
    flex-direction: column;
  }
  
  .chart-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .wealth-stats {
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .header-actions {
    gap: 8px;
  }
  
  .btn-secondary,
  .btn-primary {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .hero-section {
    padding: 40px 0 20px;
  }
  
  .hero-title {
    font-size: 28px;
  }
  
  .wealth-value {
    font-size: 24px;
  }
}
</style>