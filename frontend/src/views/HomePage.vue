<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="highlight">VISoR</span> Platform
          </h1>
          <h2 class="hero-subtitle">
            Volumetric Imaging with Synchronized on-the-fly-scan and Readout
          </h2>
          <p class="hero-description">
            Explore high-throughput, high-quality brain mapping from mouse brain to monkey brain 
            and human brain at micro-meter resolution. Interactive visualization of multi-channel 
            fluorescence imaging with precise brain region analysis.
          </p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="scrollToSpecimens">
              <el-icon><View /></el-icon>
              Explore Specimens
            </el-button>
            <el-button size="large" @click="learnMore">
              <el-icon><InfoFilled /></el-icon>
              Learn More
            </el-button>
          </div>
        </div>
        <div class="hero-visual">
          <div class="brain-visualization">
            <el-icon class="brain-icon" size="200">
              <View />
            </el-icon>
            <div class="visual-stats">
              <div class="stat-item">
                <span class="stat-number">{{ totalSpecimens }}</span>
                <span class="stat-label">Specimens</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">241</span>
                <span class="stat-label">Brain Regions</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">8</span>
                <span class="stat-label">Resolution Levels</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">4</span>
                <span class="stat-label">Channels</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-content">
        <h2 class="section-title">Advanced Imaging Technology</h2>
        <div class="features-grid">
          <div class="feature-card">
            <el-icon class="feature-icon" size="48">
              <Camera />
            </el-icon>
            <h3>High-Resolution Imaging</h3>
            <p>Micrometer-scale resolution with volumetric scanning capabilities for detailed brain structure analysis.</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon" size="48">
              <PictureRounded />
            </el-icon>
            <h3>Multi-Channel Fluorescence</h3>
            <p>4-channel imaging (405nm, 488nm, 561nm, 640nm) for comprehensive visualization of neural structures.</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon" size="48">
              <DataAnalysis />
            </el-icon>
            <h3>3D Reconstruction</h3>
            <p>Real-time 3D visualization and navigation through complex brain structures and regions.</p>
          </div>
          <div class="feature-card">
            <el-icon class="feature-icon" size="48">
              <Connection />
            </el-icon>
            <h3>Interactive Analysis</h3>
            <p>Click-to-explore region identification with synchronized multi-view navigation.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Specimens Section -->
    <section class="specimens-section" ref="specimensSection">
      <div class="section-content">
        <h2 class="section-title">Available Specimens</h2>
        <p class="section-description">
          Explore our collection of high-resolution brain imaging datasets from different species
        </p>
        
        <div v-if="visorStore.loading" class="loading-container">
          <el-loading text="Loading specimens..." />
        </div>
        
        <div v-else-if="visorStore.error" class="error-container">
          <el-alert
            title="Error loading specimens"
            :description="visorStore.error"
            type="error"
            show-icon
            @close="visorStore.clearError"
          />
        </div>
        
        <div v-else class="specimens-grid">
          <SpecimenCard
            v-for="specimen in visorStore.specimens"
            :key="specimen.id"
            :specimen="specimen"
            @click="openSpecimen(specimen.id)"
          />
          
          <!-- Placeholder cards for future specimens -->
          <div class="specimen-placeholder">
            <el-icon class="placeholder-icon" size="48">
              <Plus />
            </el-icon>
            <h3>Mouse Brain</h3>
            <p>Coming soon</p>
          </div>
          
          <div class="specimen-placeholder">
            <el-icon class="placeholder-icon" size="48">
              <Plus />
            </el-icon>
            <h3>Human Brain</h3>
            <p>Coming soon</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Technology Section -->
    <section class="technology-section">
      <div class="section-content">
        <h2 class="section-title">VISoR Technology Overview</h2>
        <div class="technology-content">
          <div class="tech-description">
            <h3>Synchronized Scanning & Readout</h3>
            <p>
              VISoR employs synchronized on-the-fly scanning and readout technology to achieve 
              high-throughput volumetric imaging. This approach enables rapid acquisition of 
              large-scale datasets while maintaining exceptional spatial resolution.
            </p>
            
            <h3>Multi-Scale Analysis</h3>
            <p>
              From cellular structures to whole-brain connectivity, VISoR supports multi-scale 
              analysis through its hierarchical resolution pyramid system. Navigate seamlessly 
              from overview to detailed inspection.
            </p>
            
            <h3>Real-Time Visualization</h3>
            <p>
              Interactive exploration of massive datasets through optimized tile-based rendering 
              and progressive loading. Experience smooth navigation through gigabyte-scale brain images.
            </p>
          </div>
          
          <div class="tech-specs">
            <h3>Technical Specifications</h3>
            <ul class="specs-list">
              <li><strong>Resolution:</strong> 10μm pixel size</li>
              <li><strong>Channels:</strong> 4 fluorescence channels</li>
              <li><strong>Data Size:</strong> Up to 275GB per specimen</li>
              <li><strong>Pyramid Levels:</strong> 8 resolution levels</li>
              <li><strong>3D Reconstruction:</strong> Real-time rendering</li>
              <li><strong>Region Analysis:</strong> 241 anatomical regions</li>
              <li><strong>Coordinate System:</strong> Right-handed 3D</li>
              <li><strong>File Format:</strong> HDF5 (.ims)</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </div>
  <Footer />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVISoRStore } from '@/stores/visor'
import SpecimenCard from '@/components/home/SpecimenCard.vue'
import {
  View,
  InfoFilled,
  Camera,
  PictureRounded,
  DataAnalysis,
  Connection,
  Plus
} from '@element-plus/icons-vue'

const router = useRouter()
const visorStore = useVISoRStore()

// Refs
const specimensSection = ref<HTMLElement>()

// Computed
const totalSpecimens = computed(() => visorStore.specimens.length)

// Methods
function scrollToSpecimens() {
  if (specimensSection.value) {
    specimensSection.value.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    })
  }
}

function learnMore() {
  router.push('/about')
}

function openSpecimen(specimenId: string) {
  router.push(`/viewer/${specimenId}`)
}

// Lifecycle
onMounted(() => {
  // Ensure specimens are loaded
  if (visorStore.specimens.length === 0) {
    visorStore.loadSpecimens()
  }
})
import Footer from '@/components/layout/Footer.vue'
</script>

<style scoped>
.home-page {
  min-height: 100%;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  min-height: 70vh;
  display: flex;
  align-items: center;
}

.hero-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.1;
}

.highlight {
  color: #ffd700;
}

.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 400;
  margin: 0 0 24px 0;
  opacity: 0.9;
  line-height: 1.3;
}

.hero-description {
  font-size: 1.1rem;
  line-height: 1.6;
  margin: 0 0 40px 0;
  opacity: 0.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.hero-visual {
  display: flex;
  justify-content: center;
}

.brain-visualization {
  text-align: center;
}

.brain-icon {
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 30px;
}

.visual-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #ffd700;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Sections */
.features-section,
.specimens-section,
.technology-section {
  padding: 80px 0;
}

.features-section {
  background: #f8f9fa;
}

.technology-section {
  background: #f8f9fa;
}

.section-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 600;
  text-align: center;
  margin: 0 0 20px 0;
  color: #303133;
}

.section-description {
  text-align: center;
  font-size: 1.1rem;
  color: #606266;
  margin: 0 0 60px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #303133;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

/* Specimens Grid */
.specimens-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.specimen-placeholder {
  background: white;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  transition: all 0.3s;
}

.specimen-placeholder:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.placeholder-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.specimen-placeholder h3 {
  color: #909399;
  margin: 0 0 8px 0;
}

.specimen-placeholder p {
  color: #c0c4cc;
  margin: 0;
}

/* Technology Section */
.technology-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 60px;
  align-items: start;
}

.tech-description h3 {
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 1.25rem;
}

.tech-description p {
  color: #606266;
  line-height: 1.6;
  margin: 0 0 30px 0;
}

.tech-specs {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tech-specs h3 {
  color: #303133;
  margin: 0 0 20px 0;
  font-size: 1.25rem;
}

.specs-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.specs-list li {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  color: #606266;
}

.specs-list li:last-child {
  border-bottom: none;
}

.specs-list strong {
  color: #303133;
}

/* Loading and Error States */
.loading-container,
.error-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .technology-content {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 60px 0;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.25rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features-grid,
  .specimens-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .section-content {
    padding: 0 16px;
  }
  
  .features-section,
  .specimens-section,
  .technology-section {
    padding: 60px 0;
  }
}
</style>
