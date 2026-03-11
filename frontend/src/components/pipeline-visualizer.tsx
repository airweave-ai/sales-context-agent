import { useState, useEffect, useRef } from 'react'
import { StepCard } from './step-card'

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

interface PipelineVisualizerProps {
  state: PipelineState | null
}

export function PipelineVisualizer({ state }: PipelineVisualizerProps) {
  // Track which step should be expanded
  const [expandedStep, setExpandedStep] = useState<number | null>(null)
  const [pipelineComplete, setPipelineComplete] = useState(false)
  const prevRunId = useRef<string | null>(null)
  const stepRefs = useRef<(HTMLDivElement | null)[]>([])

  // Reset state when a new pipeline run starts
  useEffect(() => {
    if (state?.run_id && state.run_id !== prevRunId.current) {
      prevRunId.current = state.run_id
      setExpandedStep(null)
      setPipelineComplete(false)
    }
  }, [state?.run_id])

  // Auto-expand the current running step and scroll to it
  useEffect(() => {
    if (!state || state.status !== 'running') return

    const currentStep = state.current_step
    const step = state.steps[currentStep]

    // When a step starts running and has data, expand it
    if (step?.status === 'running' && step.data) {
      setExpandedStep(currentStep)

      // Scroll the step into view smoothly
      setTimeout(() => {
        stepRefs.current[currentStep]?.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        })
      }, 100)
    }
  }, [state?.current_step, state?.status, state?.steps])

  // When pipeline completes, keep the last step (brief output) open
  useEffect(() => {
    if (state?.status === 'completed' && !pipelineComplete) {
      setPipelineComplete(true)
      setExpandedStep(state.steps.length - 1)
    }
  }, [state?.status, state?.steps.length, pipelineComplete])

  if (!state) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="text-4xl mb-4">📋</div>
        <p className="text-lg font-medium text-foreground mb-2">Ready to generate a brief</p>
        <p className="text-sm text-muted-foreground max-w-md">
          The demo will generate a pre-meeting brief for Acme Analytics by searching across Notion, Google Drive, and GitHub.
        </p>
      </div>
    )
  }

  const totalDuration = state.steps.reduce((acc, step) => acc + (step.duration_ms || 0), 0)
  const isRunning = state.status === 'running'

  return (
    <div className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {state.steps.map((step, idx) => {
              const isCompleted = step.status === 'completed'
              const isStepRunning = step.status === 'running'
              const isPending = step.status === 'pending'

              return (
                <div key={step.id} className="flex items-center">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${
                      isCompleted
                        ? 'bg-primary w-8'
                        : isStepRunning
                        ? 'bg-primary w-12 animate-pulse'
                        : 'bg-muted w-6'
                    }`}
                  />
                  {idx < state.steps.length - 1 && (
                    <div className={`h-0.5 w-2 ${isPending ? 'bg-muted' : 'bg-primary/50'}`} />
                  )}
                </div>
              )
            })}
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>
              Step {Math.min(state.current_step + 1, state.steps.length)} of {state.steps.length}
            </span>
            {totalDuration > 0 && (
              <span>Total: {(totalDuration / 1000).toFixed(1)}s</span>
            )}
          </div>
        </div>

        <StatusBadge status={state.status} />
      </div>

      {/* Step cards */}
      <div className="space-y-4">
        {state.steps.map((step, idx) => {
          const isCurrentStep = idx === state.current_step && isRunning
          const isLastStep = idx === state.steps.length - 1
          const shouldAutoExpand = isRunning && idx === expandedStep
          const shouldForceOpen = pipelineComplete && isLastStep
          const shouldAutoCollapse = isRunning && !isLastStep

          return (
            <div
              key={step.id}
              ref={el => { stepRefs.current[idx] = el }}
            >
              <StepCard
                step={step}
                isActive={isCurrentStep}
                autoExpand={shouldAutoExpand}
                forceOpen={shouldForceOpen}
                autoCollapse={shouldAutoCollapse}
              />
            </div>
          )
        })}
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const statusStyles = {
    idle: 'bg-muted text-muted-foreground',
    running: 'bg-primary text-primary-foreground animate-pulse',
    completed: 'bg-green-500/20 text-green-500 border border-green-500/50',
    error: 'bg-destructive/20 text-destructive border border-destructive/50',
  }

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-mono uppercase ${statusStyles[status as keyof typeof statusStyles]}`}>
      {status}
    </span>
  )
}
