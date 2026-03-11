import { useState, useCallback, useEffect } from 'react'
import { Play, RefreshCw, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PipelineVisualizer } from '@/components/pipeline-visualizer'
import { useWebSocket } from '@/hooks/useWebSocket'

interface PipelineStep {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'error'
  data?: Record<string, unknown>
  reasoning?: string
  duration_ms?: number
}

interface PipelineState {
  run_id: string
  status: 'idle' | 'running' | 'completed' | 'error'
  current_step: number
  steps: PipelineStep[]
  started_at?: string
  completed_at?: string
}

interface Config {
  airweave_configured: boolean
  openai_configured: boolean
  anthropic_configured: boolean
  llm_provider: string | null
  integrations?: {
    slack: { enabled: boolean; configured: boolean; mode: string }
  }
}

function App() {
  const [pipelineState, setPipelineState] = useState<PipelineState | null>(null)
  const [config, setConfig] = useState<Config | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // WebSocket connection
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/pipeline`

  const { isConnected, send } = useWebSocket(wsUrl, {
    onMessage: (message) => {
      if (message.state) {
        setPipelineState(message.state as PipelineState)
      }
      if (message.type === 'pipeline_completed' || message.type === 'pipeline_error') {
        setIsLoading(false)
      }
    },
    onOpen: () => {
      console.log('WebSocket connected')
    },
    onClose: () => {
      console.log('WebSocket disconnected')
    },
  })

  // Fetch config on mount
  useEffect(() => {
    fetch('/api/config')
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch((err) => console.error('Failed to fetch config:', err))
  }, [])

  const runPipeline = useCallback(() => {
    setIsLoading(true)
    setPipelineState(null)
    send({
      type: 'run',
      config: {
        use_sample_data: true,
      },
    })
  }, [send])

  const resetPipeline = useCallback(() => {
    setPipelineState(null)
    setIsLoading(false)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Airweave Logo */}
              <a href="https://airweave.ai" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <svg className="h-8 w-auto" viewBox="0 0 143 143" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M89.3854 128.578C79.4165 123.044 66.2502 114.852 60.0707 107.348L59.5432 106.724C58.2836 105.206 56.981 103.72 55.6676 102.299C51.4152 97.6699 46.8614 93.5036 42.146 89.9079C40.2405 88.4546 38.2704 87.055 36.3111 85.7847C35.2991 85.128 34.3302 84.5251 33.4151 83.9761C31.1221 82.6088 28.3338 82.2321 25.7716 82.9534C23.3385 83.6424 21.39 85.2464 20.2596 87.4534C18.0634 91.7381 19.5814 97.0347 23.7046 99.5108C27.0204 101.492 30.2608 103.817 33.3398 106.422C33.7381 106.756 33.8996 107.284 33.7596 107.768C32.6292 111.891 31.4989 118.663 31.0682 121.376C30.1424 127.135 32.9737 132.787 38.0982 135.457L38.2812 135.554C40.5204 136.706 43.1472 136.652 45.3219 135.403C47.4858 134.165 48.853 131.937 48.9822 129.439C49.036 128.363 49.1006 127.286 49.176 126.296C49.219 125.768 49.542 125.337 50.0264 125.165C50.1772 125.111 50.3494 125.079 50.5001 125.079C50.8554 125.079 51.1784 125.219 51.4475 125.488C55.743 129.891 60.3829 133.875 65.2167 137.33C69.8674 140.657 75.3686 142.412 81.139 142.412C83.2383 142.412 85.3376 142.175 87.3938 141.701L87.6199 141.647C90.4943 140.98 92.529 138.73 92.9488 135.791C93.3687 132.852 91.9476 130.02 89.3747 128.589H89.3639L89.3854 128.578Z" fill="currentColor" className="text-primary"/>
                  <path d="M142.051 57.8805L142.029 57.7621C141.545 55.2968 139.618 53.4128 137.098 52.9606C134.612 52.5192 132.254 53.5635 130.984 55.6951L130.908 55.8135C126.204 63.8662 119.561 71.3159 111.153 78.0014C108.946 79.7562 106.793 81.6078 104.726 83.5134C103.144 84.9775 100.765 85.2359 98.9452 84.127C97.1474 83.0397 95.3495 81.8447 93.6055 80.5744C89.8268 77.8291 86.1772 74.6533 82.7753 71.1329C80.9989 69.3028 79.298 67.3973 77.6939 65.438C75.5408 62.8219 73.2477 60.2597 70.8685 57.8374C65.8195 52.6915 56.1089 45.6185 53.2453 43.5838C52.8792 43.3362 52.6639 42.9486 52.5993 42.5073C52.5455 42.0659 52.6639 41.6567 52.9546 41.3122C54.774 39.1376 56.4965 36.8876 58.0683 34.6268C59.7369 32.2369 60.286 29.3086 59.5862 26.5957C58.908 23.9581 57.1424 21.8158 54.634 20.5885C50.4139 18.5 45.3972 19.8026 42.7273 23.6351C40.3373 27.0694 37.5167 30.439 34.3732 33.6364C34.0718 33.9378 33.6304 34.0455 33.2213 33.8948C30.0239 32.8505 26.7296 32 23.4461 31.3648C23.2093 31.3218 22.854 31.2572 22.4126 31.2034C15.9102 30.2345 9.61233 33.4857 6.71639 39.2775L6.6195 39.4606C5.68289 41.3338 5.76902 43.5407 6.82405 45.3709C7.90061 47.2226 9.82765 48.4068 11.9592 48.5252C12.9604 48.579 13.9401 48.6436 14.8659 48.7082C15.2966 48.7405 15.6411 48.9881 15.8025 49.3972C15.9533 49.8171 15.8671 50.2477 15.5657 50.5599C11.647 54.5862 8.10515 58.9032 5.0262 63.3925C0.644601 69.7872 -0.981008 77.9153 0.580002 85.688L0.601538 85.8064C1.20441 88.7777 3.55131 90.9093 6.57644 91.2323C9.48315 91.5445 12.1099 90.0266 13.2619 87.3782L13.3265 87.2167C18.1925 75.5683 26.2559 65.2226 37.2907 56.4594C37.8182 56.0503 38.5072 55.9858 39.067 56.298C44.8373 59.4738 50.3601 63.6078 55.4738 68.5923C56.0982 69.1951 56.1089 70.2071 55.5168 70.8315C52.9761 73.5122 50.5862 76.3112 48.4115 79.1749C46.7106 81.4141 47.0335 84.6007 49.1221 86.4416L52.8254 89.7036L52.7824 89.7467C53.3637 90.2634 53.945 90.7802 54.5264 91.2969L55.3123 91.8998C56.4319 92.8902 57.8529 93.3423 59.3386 93.1916C60.8027 93.0409 62.17 92.2658 63.0635 91.0816C64.6353 88.9931 66.3578 86.9584 68.1556 85.0098C68.457 84.676 68.8661 84.5038 69.3075 84.4931C69.7705 84.4931 70.1257 84.6437 70.4164 84.9344C75.3147 89.7682 80.6114 94.0744 86.1772 97.7024C88.3626 99.1234 88.9978 101.966 87.6306 104.183C86.4248 106.153 85.2729 108.199 84.2179 110.244C83.0014 112.624 82.7968 115.444 83.6688 117.963C84.4978 120.385 86.2095 122.291 88.481 123.346C89.7514 123.938 91.0971 124.24 92.4859 124.24C96.0062 124.24 99.182 122.302 100.786 119.158C102.229 116.316 103.919 113.506 105.781 110.836C106.869 109.265 108.86 108.543 110.755 109.028C114.76 110.061 120.143 111.127 123.954 111.848C127.808 112.57 131.619 110.729 133.46 107.284L133.643 106.939C135.021 104.334 135.031 101.212 133.664 98.5959C132.286 95.9584 129.681 94.1713 126.71 93.8268C125.978 93.7407 125.278 93.6546 124.61 93.5684C124.47 93.5469 124.352 93.5254 124.244 93.5038L122.856 93.1809L123.857 92.1581C123.932 92.0828 124.029 91.9859 124.158 91.8998C128.271 88.5086 132.071 84.9021 135.462 81.1772C141.168 74.9009 143.622 66.2023 142.018 57.8805H142.029H142.051Z" fill="currentColor" className="text-primary"/>
                  <path d="M56.1506 14.0429C65.0861 19.3396 76.9067 27.0801 82.4833 33.8732C83.14 34.659 83.7967 35.4449 84.4534 36.1985C85.6591 37.5873 85.7991 39.5789 84.7979 41.1292C82.9892 43.9174 80.9115 46.6627 78.6399 49.3003C76.9713 51.2165 76.9067 54.0156 78.4785 55.9534L78.5431 56.0288C78.7261 56.2656 78.9306 56.5132 79.1136 56.75C80.7931 58.8816 82.5801 60.9271 84.4211 62.8433C85.4007 63.8661 86.7249 64.4367 88.1352 64.4367L88.2644 65.2333L88.2429 64.4367C89.707 64.4044 91.1173 63.7584 92.0969 62.6388C94.3362 60.1089 96.4247 57.4498 98.3302 54.7691C99.6329 52.9282 102.13 52.5084 104.025 53.8111C105.963 55.146 107.965 56.4163 109.957 57.5897C112.293 58.957 115.114 59.2153 117.665 58.268C120.249 57.3098 122.262 55.2752 123.156 52.6591C124.555 48.6113 122.757 43.9605 118.882 41.6136C116.255 40.0203 113.65 38.2224 111.174 36.2846C109.882 35.2619 109.333 33.5825 109.796 32C110.937 28.0059 111.981 22.8276 112.648 19.1889C113.337 15.4317 111.647 11.5884 108.439 9.65058L108.062 9.43525C105.371 7.83118 102.087 7.71277 99.2668 9.1123C96.4247 10.5226 94.53 13.2463 94.1855 16.3791L94.1639 16.5728C94.1209 16.9604 93.884 17.2511 93.518 17.3695C93.152 17.4879 92.7859 17.3911 92.5168 17.1327C88.5012 12.848 84.238 8.96157 79.8134 5.57041C73.8708 1.01656 66.2811 -0.878188 58.9928 0.381386L58.6805 0.435234C55.6124 0.973513 53.2547 3.30965 52.6949 6.3886C52.1351 9.43527 53.4915 12.4281 56.1722 14.0106H56.1614L56.1506 14.0429Z" fill="currentColor" className="text-primary"/>
                </svg>
                <div>
                  <h1 className="text-lg font-semibold">Sales Context Agent</h1>
                  <p className="text-xs text-muted-foreground">Powered by Airweave</p>
                </div>
              </a>
            </div>

            <div className="flex items-center gap-4">
              {/* Connection status */}
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-muted-foreground">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Config status */}
              {config && (
                <div className="flex items-center gap-2">
                  <Badge variant={config.airweave_configured ? 'default' : 'outline'}>
                    Airweave {config.airweave_configured ? '✓' : '✗'}
                  </Badge>
                  {config.integrations?.slack && (
                    <Badge
                      variant={config.integrations.slack.mode === 'live' ? 'default' : 'outline'}
                      className={config.integrations.slack.mode === 'preview' ? 'text-amber-600 border-amber-600' : ''}
                    >
                      Slack {config.integrations.slack.mode === 'live' ? '✓' : '(preview)'}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-6 py-8">
        {/* Controls */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-semibold mb-1">Pipeline Visualization</h2>
            <p className="text-muted-foreground">
              Generate pre-meeting briefs from your CRM, docs, and codebase
            </p>
          </div>

          <div className="flex items-center gap-3">
            {pipelineState && (
              <Button variant="outline" onClick={resetPipeline} disabled={isLoading}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset
              </Button>
            )}
            <Button onClick={runPipeline} disabled={isLoading || !isConnected}>
              {isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Run Demo
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Pipeline visualizer */}
        <PipelineVisualizer state={pipelineState} />

        {/* Info section */}
        {!pipelineState && (
          <div className="mt-12 grid md:grid-cols-3 gap-6">
            <InfoCard
              title="Pre-Meeting Prep"
              description="Generate comprehensive account briefs with context from Notion, Google Drive, and GitHub in seconds."
              icon="📋"
            />
            <InfoCard
              title="Cross-Source Context"
              description="Airweave searches across your CRM, docs, and codebase to surface everything relevant to your meeting."
              icon="🔍"
            />
            <InfoCard
              title="Actionable Insights"
              description="AI-synthesized talking points, concern areas, and product updates so you walk into every call prepared."
              icon="💡"
            />
          </div>
        )}

        {/* Preview mode notice */}
        {!pipelineState && config?.integrations?.slack?.mode === 'preview' && (
          <div className="mt-6 p-4 rounded-lg border border-border bg-muted/50">
            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">Demo Mode:</strong> Running with sample data for Acme Analytics.
              Configure Airweave and Slack API keys to search your own data and post briefs to channels.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-auto">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Built with Airweave</span>
            <a
              href="https://airweave.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 hover:text-foreground transition-colors"
            >
              airweave.ai
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}

function InfoCard({ title, description, icon }: { title: string; description: string; icon: string }) {
  return (
    <div className="p-6 rounded-xl border border-border bg-card">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="font-mono text-sm font-semibold uppercase tracking-wide mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}

export default App
