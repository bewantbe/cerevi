<template>
  <div class="about-page">
    <div class="about-content">
      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-container">
          <h1 class="page-title">About VISoR Platform</h1>
          <p class="page-subtitle">
            Advancing neuroscience through high-resolution volumetric brain imaging
          </p>
        </div>
      </section>

      <!-- Technology Overview -->
      <section class="technology-section">
        <div class="section-container">
          <h2 class="section-title">What is VISoR?</h2>
          <div class="content-grid">
            <div class="text-content">
              <p>
                <strong>VISoR (Volumetric Imaging with Synchronized on-the-fly-scan and Readout)</strong> 
                is a cutting-edge imaging technology designed for high-throughput, high-quality brain mapping. 
                This innovative approach enables researchers to capture detailed three-dimensional images of 
                brain tissue at unprecedented scale and resolution.
              </p>
              
              <h3>Key Advantages</h3>
              <ul class="advantage-list">
                <li><strong>High Throughput:</strong> Rapid acquisition of large-scale datasets</li>
                <li><strong>Exceptional Quality:</strong> Micrometer-scale resolution for detailed analysis</li>
                <li><strong>Multi-Scale Mapping:</strong> From cellular to whole-brain connectivity</li>
                <li><strong>Multi-Species Support:</strong> Mouse, monkey, and human brain imaging</li>
              </ul>
            </div>
            
            <div class="stats-panel">
              <h3>Technical Specifications</h3>
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-number">10μm</span>
                  <span class="stat-label">Pixel Resolution</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">275GB</span>
                  <span class="stat-label">Max Dataset Size</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">8</span>
                  <span class="stat-label">Resolution Levels</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">4</span>
                  <span class="stat-label">Fluorescence Channels</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">241</span>
                  <span class="stat-label">Brain Regions</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">3D</span>
                  <span class="stat-label">Reconstruction</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Platform Features -->
      <section class="features-section">
        <div class="section-container">
          <h2 class="section-title">Platform Features</h2>
          <div class="features-grid">
            <div class="feature-item">
              <el-icon class="feature-icon" size="40">
                <View />
              </el-icon>
              <h4>Interactive Visualization</h4>
              <p>
                Multi-view brain exploration with synchronized sagittal, coronal, and horizontal views. 
                Real-time navigation through massive datasets with smooth zooming and panning.
              </p>
            </div>
            
            <div class="feature-item">
              <el-icon class="feature-icon" size="40">
                <PictureRounded />
              </el-icon>
              <h4>Multi-Channel Imaging</h4>
              <p>
                Support for 4 fluorescence channels (405nm, 488nm, 561nm, 640nm) enabling 
                comprehensive visualization of different neural structures and markers.
              </p>
            </div>
            
            <div class="feature-item">
              <el-icon class="feature-icon" size="40">
                <DataAnalysis />
              </el-icon>
              <h4>Brain Region Analysis</h4>
              <p>
                Hierarchical brain region browser with 241 anatomical regions. Click-to-identify 
                functionality for rapid region exploration and analysis.
              </p>
            </div>
            
            <div class="feature-item">
              <el-icon class="feature-icon" size="40">
                <Connection />
              </el-icon>
              <h4>3D Reconstruction</h4>
              <p>
                Real-time 3D brain shell visualization with coordinate mapping between 
                2D views and 3D models for comprehensive spatial understanding.
              </p>
            </div>
            
            <div class="feature-item">
              <el-icon class="feature-icon" size="40">
                <ZoomIn />
              </el-icon>
              <h4>Multi-Resolution Pyramid</h4>
              <p>
                Efficient tile-based rendering with 8 resolution levels enables smooth 
                navigation from overview to detailed cellular inspection.
              </p>
            </div>
            
            <div class="feature-item">
              <el-icon class="feature-icon" size="40">
                <Monitor />
              </el-icon>
              <h4>Web-Based Access</h4>
              <p>
                No software installation required. Access powerful brain imaging tools 
                directly through your web browser with responsive design.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Technology Stack -->
      <section class="tech-stack-section">
        <div class="section-container">
          <h2 class="section-title">Technology Stack</h2>
          <div class="tech-grid">
            <div class="tech-category">
              <h3>Frontend</h3>
              <ul class="tech-list">
                <li>Vue.js 3 + TypeScript</li>
                <li>OpenSeadragon (Image Viewer)</li>
                <li>Three.js (3D Visualization)</li>
                <li>Element Plus (UI Components)</li>
                <li>Pinia (State Management)</li>
              </ul>
            </div>
            
            <div class="tech-category">
              <h3>Backend</h3>
              <ul class="tech-list">
                <li>Python FastAPI</li>
                <li>HDF5 (.ims) File Processing</li>
                <li>Redis Caching</li>
                <li>Tile-based Image Serving</li>
                <li>REST API Architecture</li>
              </ul>
            </div>
            
            <div class="tech-category">
              <h3>Infrastructure</h3>
              <ul class="tech-list">
                <li>Docker Containerization</li>
                <li>Nginx Reverse Proxy</li>
                <li>Multi-container Orchestration</li>
                <li>Health Monitoring</li>
                <li>Performance Optimization</li>
              </ul>
            </div>
            
            <div class="tech-category">
              <h3>Data Formats</h3>
              <ul class="tech-list">
                <li>Imaris (.ims) HDF5 Images</li>
                <li>OBJ 3D Models</li>
                <li>JSON Region Hierarchies</li>
                <li>Multi-resolution Pyramids</li>
                <li>Lossless Atlas Masks</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- Research Applications -->
      <section class="applications-section">
        <div class="section-container">
          <h2 class="section-title">Research Applications</h2>
          <div class="applications-grid">
            <div class="application-card">
              <h4>Connectome Mapping</h4>
              <p>
                Trace neural connections across brain regions to understand 
                connectivity patterns and network organization.
              </p>
            </div>
            
            <div class="application-card">
              <h4>Disease Research</h4>
              <p>
                Compare healthy and diseased brain tissue to identify 
                pathological changes and potential therapeutic targets.
              </p>
            </div>
            
            <div class="application-card">
              <h4>Developmental Biology</h4>
              <p>
                Study brain development across different stages and species 
                to understand evolutionary and developmental processes.
              </p>
            </div>
            
            <div class="application-card">
              <h4>Comparative Neuroscience</h4>
              <p>
                Cross-species comparisons to understand brain evolution 
                and species-specific neural adaptations.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Contact Section -->
      <section class="contact-section">
        <div class="section-container">
          <h2 class="section-title">Get Involved</h2>
          <div class="contact-content">
            <div class="contact-info">
              <h3>Collaborate with Us</h3>
              <p>
                The VISoR Platform is an ongoing research initiative. We welcome 
                collaborations with researchers, institutions, and technology partners 
                interested in advancing brain imaging and analysis capabilities.
              </p>
              
              <div class="contact-methods">
                <div class="contact-item">
                  <el-icon><Message /></el-icon>
                  <span>Contact us for research collaborations</span>
                </div>
                <div class="contact-item">
                  <el-icon><Document /></el-icon>
                  <span>Access technical documentation</span>
                </div>
                <div class="contact-item">
                  <el-icon><Share /></el-icon>
                  <span>Share your research datasets</span>
                </div>
              </div>
            </div>
            
            <div class="version-info">
              <h3>Platform Version</h3>
              <div class="version-details">
                <div class="version-item">
                  <span class="version-label">Current Version:</span>
                  <span class="version-value">1.0.0</span>
                </div>
                <div class="version-item">
                  <span class="version-label">Last Updated:</span>
                  <span class="version-value">{{ currentDate }}</span>
                </div>
                <div class="version-item">
                  <span class="version-label">License:</span>
                  <span class="version-value">Research Use</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  View,
  PictureRounded,
  DataAnalysis,
  Connection,
  ZoomIn,
  Monitor,
  Message,
  Document,
  Share
} from '@element-plus/icons-vue'

// Computed
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})
</script>

<style scoped>
.about-page {
  min-height: 100%;
  background: #ffffff;
}

.about-content {
  width: 100%;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 20px 0;
  line-height: 1.1;
}

.page-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  margin: 0;
  line-height: 1.4;
}

/* Common Section Styles */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 600;
  text-align: center;
  margin: 0 0 60px 0;
  color: #303133;
}

/* Technology Section */
.technology-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 60px;
  align-items: start;
}

.text-content h3 {
  color: #303133;
  margin: 30px 0 16px 0;
  font-size: 1.25rem;
}

.text-content p {
  color: #606266;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.advantage-list {
  color: #606266;
  line-height: 1.8;
  padding-left: 20px;
}

.advantage-list li {
  margin-bottom: 8px;
}

.advantage-list strong {
  color: #303133;
}

.stats-panel {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stats-panel h3 {
  color: #303133;
  margin: 0 0 20px 0;
  font-size: 1.25rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: #606266;
}

/* Features Section */
.features-section {
  padding: 80px 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.feature-item {
  text-align: center;
  padding: 30px 20px;
}

.feature-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.feature-item h4 {
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 1.25rem;
}

.feature-item p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

/* Tech Stack Section */
.tech-stack-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.tech-category {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tech-category h3 {
  color: #303133;
  margin: 0 0 20px 0;
  font-size: 1.25rem;
  text-align: center;
}

.tech-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tech-list li {
  color: #606266;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.9rem;
}

.tech-list li:last-child {
  border-bottom: none;
}

/* Applications Section */
.applications-section {
  padding: 80px 0;
}

.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
}

.application-card {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.application-card h4 {
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 1.1rem;
}

.application-card p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

/* Contact Section */
.contact-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.contact-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 60px;
  align-items: start;
}

.contact-info h3 {
  color: #303133;
  margin: 0 0 16px 0;
  font-size: 1.25rem;
}

.contact-info p {
  color: #606266;
  line-height: 1.6;
  margin: 0 0 30px 0;
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #606266;
}

.contact-item .el-icon {
  color: #409eff;
}

.version-info {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.version-info h3 {
  color: #303133;
  margin: 0 0 20px 0;
  font-size: 1.25rem;
}

.version-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.version-item:last-child {
  border-bottom: none;
}

.version-label {
  color: #606266;
  font-size: 0.9rem;
}

.version-value {
  color: #303133;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .content-grid,
  .contact-content {
    grid-template-columns: 1fr;
    gap: 40px;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2.5rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .hero-section {
    padding: 60px 0;
  }
  
  .features-section,
  .technology-section,
  .tech-stack-section,
  .applications-section,
  .contact-section {
    padding: 60px 0;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .tech-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 2rem;
  }
  
  .section-container {
    padding: 0 16px;
  }
  
  .hero-container {
    padding: 0 16px;
  }
}
</style>
