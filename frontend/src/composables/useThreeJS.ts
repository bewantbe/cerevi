import { ref, onMounted, onUnmounted, type Ref } from 'vue'
import * as THREE from 'three'

// Define OrbitControls type (Three.js addon)
interface OrbitControls {
  enabled: boolean
  enableDamping: boolean
  dampingFactor: number
  enableZoom: boolean
  enableRotate: boolean
  enablePan: boolean
  target: THREE.Vector3
  update(): void
  reset(): void
  dispose(): void
}

// Import OrbitControls dynamically
let OrbitControls: any

export interface ThreeJSOptions {
  specimenId: string
  enableControls?: boolean
  showGrid?: boolean
  backgroundColor?: number
}

export interface CoordinatePosition {
  x: number
  y: number
  z: number
}

export function useThreeJS(container: Ref<HTMLElement | undefined>) {
  // Core Three.js objects
  const scene = ref<THREE.Scene>()
  const camera = ref<THREE.PerspectiveCamera>()
  const renderer = ref<THREE.WebGLRenderer>()
  const controls = ref<OrbitControls>()
  const brainMesh = ref<THREE.Mesh>()
  
  // Loading and error states
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Camera information
  const cameraPosition = ref('0, 0, 500')
  const cameraTarget = ref('0, 0, 0')
  
  // Model properties
  const wireframeMode = ref(false)
  const modelLoaded = ref(false)
  
  // Crosshair for coordinate synchronization
  const crosshairPosition = ref<CoordinatePosition | null>(null)
  const crosshairMesh = ref<THREE.Object3D>()
  
  // Animation frame ID for cleanup
  let animationId: number | null = null

  /**
   * Initialize Three.js scene, camera, and renderer
   */
  const initThreeJS = async (options: ThreeJSOptions) => {
    if (!container.value) {
      error.value = 'Container element not available'
      return false
    }

    try {
      // Import OrbitControls dynamically
      const { OrbitControls: OrbitControlsClass } = await import('three/examples/jsm/controls/OrbitControls.js')
      OrbitControls = OrbitControlsClass

      // Create scene
      scene.value = new THREE.Scene()
      scene.value.background = new THREE.Color(options.backgroundColor || 0x1a1a1a)

      // Create camera
      const containerRect = container.value.getBoundingClientRect()
      camera.value = new THREE.PerspectiveCamera(
        60, // Field of view
        containerRect.width / containerRect.height, // Aspect ratio
        0.1, // Near plane
        10000 // Far plane
      )
      
      // Position camera for anatomical view (looking at brain from front-right-above)
      camera.value.position.set(300, 200, 400)
      camera.value.lookAt(0, 0, 0)

      // Create renderer
      renderer.value = new THREE.WebGLRenderer({ 
        antialias: true, 
        alpha: true,
        powerPreference: 'high-performance'
      })
      renderer.value.setSize(containerRect.width, containerRect.height)
      renderer.value.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      renderer.value.shadowMap.enabled = true
      renderer.value.shadowMap.type = THREE.PCFSoftShadowMap

      // Add renderer to container
      container.value.innerHTML = ''
      container.value.appendChild(renderer.value.domElement)

      // Create orbit controls
      if (options.enableControls !== false) {
        controls.value = new OrbitControls(camera.value, renderer.value.domElement)
        if (controls.value) {
          controls.value.enableDamping = true
          controls.value.dampingFactor = 0.05
          controls.value.enableZoom = true
          controls.value.enableRotate = true
          controls.value.enablePan = true
          controls.value.target.set(0, 0, 0)
        }
      }

      // Add lighting
      setupLighting()

      // Add coordinate grid if requested
      if (options.showGrid) {
        addCoordinateGrid()
      }

      // Start render loop
      startRenderLoop()

      // Update camera info
      updateCameraInfo()

      return true
    } catch (err) {
      error.value = `Failed to initialize Three.js: ${err}`
      console.error('Three.js initialization error:', err)
      return false
    }
  }

  /**
   * Setup scene lighting for brain visualization
   */
  const setupLighting = () => {
    if (!scene.value) return

    // Ambient light for overall illumination
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
    scene.value.add(ambientLight)

    // Main directional light (key light)
    const mainLight = new THREE.DirectionalLight(0xffffff, 0.8)
    mainLight.position.set(100, 100, 100)
    mainLight.castShadow = true
    mainLight.shadow.mapSize.width = 2048
    mainLight.shadow.mapSize.height = 2048
    mainLight.shadow.camera.near = 0.1
    mainLight.shadow.camera.far = 1000
    mainLight.shadow.camera.left = -200
    mainLight.shadow.camera.right = 200
    mainLight.shadow.camera.top = 200
    mainLight.shadow.camera.bottom = -200
    scene.value.add(mainLight)

    // Fill light from opposite side
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3)
    fillLight.position.set(-100, -50, -100)
    scene.value.add(fillLight)

    // Top light for better depth perception
    const topLight = new THREE.DirectionalLight(0xffffff, 0.2)
    topLight.position.set(0, 200, 0)
    scene.value.add(topLight)
  }

  /**
   * Add coordinate reference grid
   */
  const addCoordinateGrid = () => {
    if (!scene.value) return

    // XY plane grid (horizontal)
    const gridXY = new THREE.GridHelper(200, 20, 0x404040, 0x202020)
    gridXY.position.y = 0
    scene.value.add(gridXY)

    // Add axis labels
    const axisHelper = new THREE.AxesHelper(100)
    scene.value.add(axisHelper)
  }

  /**
   * Load brain shell model from backend
   */
  const loadBrainModel = async (specimenId: string) => {
    isLoading.value = true
    error.value = null

    try {
      // Import OBJ loader
      const { OBJLoader } = await import('three/examples/jsm/loaders/OBJLoader.js')
      const loader = new OBJLoader()

      // Construct model URL
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const modelUrl = `${baseUrl}/api/specimens/${specimenId}/model`

      // Load the OBJ model
      const object = await new Promise<THREE.Group>((resolve, reject) => {
        loader.load(
          modelUrl,
          (obj) => resolve(obj),
          (progress) => {
            console.log('Loading progress:', (progress.loaded / progress.total * 100) + '%')
          },
          (err) => reject(err)
        )
      })

      // Process the loaded model
      if (object && scene.value) {
        // Remove previous model if exists
        if (brainMesh.value) {
          scene.value.remove(brainMesh.value)
        }

        // Create material for brain mesh
        const material = new THREE.MeshPhongMaterial({
          color: 0xffc0cb, // Light pink brain color
          shininess: 30,
          transparent: true,
          opacity: 0.9,
          side: THREE.DoubleSide
        })

        // Apply material to all meshes in the object
        object.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.material = material
            child.castShadow = true
            child.receiveShadow = true
            
            // Store reference to the main mesh
            if (!brainMesh.value) {
              brainMesh.value = child
            }
          }
        })

        // Center and scale the model appropriately
        const box = new THREE.Box3().setFromObject(object)
        const center = box.getCenter(new THREE.Vector3())
        const size = box.getSize(new THREE.Vector3())
        
        // Center the model
        object.position.sub(center)
        
        // Scale to reasonable size (about 200 units)
        const maxDimension = Math.max(size.x, size.y, size.z)
        const scale = 200 / maxDimension
        object.scale.setScalar(scale)

        // Add to scene
        scene.value.add(object)
        brainMesh.value = object as any
        modelLoaded.value = true

        console.log('Brain model loaded successfully')
      }

    } catch (err) {
      error.value = `Failed to load brain model: ${err}`
      console.error('Model loading error:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update crosshair position to show current slice location
   */
  const updateCrosshair = (coordinates: CoordinatePosition) => {
    crosshairPosition.value = coordinates

    if (!scene.value || !brainMesh.value) return

    // Remove existing crosshair
    if (crosshairMesh.value) {
      scene.value.remove(crosshairMesh.value)
    }

    // Create crosshair visualization
    const crosshairGroup = new THREE.Group()

    // Convert image coordinates to 3D model space
    // This will need to be calibrated based on the actual coordinate system
    const modelX = (coordinates.x - 3008) * 0.02 // Center around 0
    const modelY = (coordinates.y - 3648) * 0.02
    const modelZ = (coordinates.z - 3520) * 0.02

    // Create crosshair lines
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00, linewidth: 2 })
    
    // X-axis line
    const xGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(modelX - 20, modelY, modelZ),
      new THREE.Vector3(modelX + 20, modelY, modelZ)
    ])
    const xLine = new THREE.Line(xGeometry, lineMaterial)
    crosshairGroup.add(xLine)

    // Y-axis line
    const yGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(modelX, modelY - 20, modelZ),
      new THREE.Vector3(modelX, modelY + 20, modelZ)
    ])
    const yLine = new THREE.Line(yGeometry, lineMaterial)
    crosshairGroup.add(yLine)

    // Z-axis line
    const zGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(modelX, modelY, modelZ - 20),
      new THREE.Vector3(modelX, modelY, modelZ + 20)
    ])
    const zLine = new THREE.Line(zGeometry, lineMaterial)
    crosshairGroup.add(zLine)

    // Add center point
    const pointGeometry = new THREE.SphereGeometry(2, 8, 8)
    const pointMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 })
    const centerPoint = new THREE.Mesh(pointGeometry, pointMaterial)
    centerPoint.position.set(modelX, modelY, modelZ)
    crosshairGroup.add(centerPoint)

    crosshairMesh.value = crosshairGroup
    scene.value.add(crosshairGroup)
  }

  /**
   * Toggle wireframe mode
   */
  const toggleWireframe = () => {
    wireframeMode.value = !wireframeMode.value
    
    if (brainMesh.value) {
      brainMesh.value.traverse((child) => {
        if (child instanceof THREE.Mesh && child.material instanceof THREE.Material) {
          ;(child.material as any).wireframe = wireframeMode.value
        }
      })
    }
  }

  /**
   * Reset camera to default position
   */
  const resetCamera = () => {
    if (!camera.value || !controls.value) return

    camera.value.position.set(300, 200, 400)
    camera.value.lookAt(0, 0, 0)
    controls.value.target.set(0, 0, 0)
    controls.value.reset()
    updateCameraInfo()
  }

  /**
   * Update camera position information
   */
  const updateCameraInfo = () => {
    if (!camera.value || !controls.value) return

    const pos = camera.value.position
    const target = controls.value.target
    
    cameraPosition.value = `${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)}`
    cameraTarget.value = `${target.x.toFixed(1)}, ${target.y.toFixed(1)}, ${target.z.toFixed(1)}`
  }

  /**
   * Start the render loop
   */
  const startRenderLoop = () => {
    const animate = () => {
      animationId = requestAnimationFrame(animate)

      // Update controls
      if (controls.value) {
        controls.value.update()
        updateCameraInfo()
      }

      // Render the scene
      if (renderer.value && scene.value && camera.value) {
        renderer.value.render(scene.value, camera.value)
      }
    }

    animate()
  }

  /**
   * Handle window resize
   */
  const handleResize = () => {
    if (!container.value || !camera.value || !renderer.value) return

    const containerRect = container.value.getBoundingClientRect()
    
    camera.value.aspect = containerRect.width / containerRect.height
    camera.value.updateProjectionMatrix()
    
    renderer.value.setSize(containerRect.width, containerRect.height)
  }

  /**
   * Cleanup Three.js resources
   */
  const cleanup = () => {
    // Stop animation loop
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }

    // Dispose controls
    if (controls.value) {
      controls.value.dispose()
    }

    // Dispose renderer
    if (renderer.value) {
      renderer.value.dispose()
    }

    // Clear scene
    if (scene.value) {
      scene.value.clear()
    }
  }

  // Setup resize listener
  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  // Cleanup on unmount
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
    cleanup()
  })

  return {
    // State
    scene,
    camera,
    renderer,
    controls,
    brainMesh,
    isLoading,
    error,
    cameraPosition,
    cameraTarget,
    wireframeMode,
    modelLoaded,
    crosshairPosition,

    // Methods
    initThreeJS,
    loadBrainModel,
    updateCrosshair,
    toggleWireframe,
    resetCamera,
    handleResize,
    cleanup
  }
}
