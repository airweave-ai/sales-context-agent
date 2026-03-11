import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight, Check, Loader2, Clock, AlertCircle, Copy, CheckCheck } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { cn } from '@/lib/utils'

interface StepCardProps {
  step: {
    id: string
    name: string
    status: 'pending' | 'running' | 'completed' | 'error'
    data?: Record<string, unknown>
    reasoning?: string
    duration_ms?: number
  }
  isActive: boolean
  autoExpand?: boolean
  forceOpen?: boolean
  autoCollapse?: boolean
}

export function StepCard({ step, isActive, autoExpand = false, forceOpen = false, autoCollapse = false }: StepCardProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [wasAutoExpanded, setWasAutoExpanded] = useState(false)

  useEffect(() => {
    if (autoExpand && step.status === 'running' && step.data && !wasAutoExpanded) {
      setIsOpen(true)
      setWasAutoExpanded(true)
    }
  }, [autoExpand, step.status, step.data, wasAutoExpanded])

  useEffect(() => {
    if (autoCollapse && step.status === 'completed' && wasAutoExpanded && !forceOpen) {
      setIsOpen(false)
    }
  }, [autoCollapse, step.status, wasAutoExpanded, forceOpen])

  useEffect(() => {
    if (forceOpen && step.data) {
      setIsOpen(true)
    }
  }, [forceOpen, step.data])

  useEffect(() => {
    if (step.status === 'pending') {
      setWasAutoExpanded(false)
      setIsOpen(false)
    }
  }, [step.status])

  const statusIcon = {
    pending: <Clock className="h-4 w-4 text-muted-foreground" />,
    running: <Loader2 className="h-4 w-4 text-primary animate-spin" />,
    completed: <Check className="h-4 w-4 text-green-500" />,
    error: <AlertCircle className="h-4 w-4 text-destructive" />,
  }

  const statusBadge = {
    pending: <Badge variant="outline">Pending</Badge>,
    running: <Badge variant="default">Running</Badge>,
    completed: <Badge variant="secondary">Completed</Badge>,
    error: <Badge variant="destructive">Error</Badge>,
  }

  return (
    <Card className={cn(
      "transition-all duration-300",
      isActive && "ring-2 ring-primary",
      step.status === 'running' && "animate-step-pulse"
    )}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {statusIcon[step.status]}
              <CardTitle className="text-base">{step.name}</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              {step.duration_ms !== undefined && (
                <span className="text-xs text-muted-foreground">
                  {step.duration_ms}ms
                </span>
              )}
              {statusBadge[step.status]}
              {step.data && (
                <CollapsibleTrigger asChild>
                  <button className="p-1 hover:bg-accent rounded">
                    {isOpen ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>
                </CollapsibleTrigger>
              )}
            </div>
          </div>
        </CardHeader>

        <CollapsibleContent>
          <CardContent className="p-0">
            <div className="max-h-[60vh] overflow-y-auto p-6 pt-0">
              {step.data && (
                <div className="space-y-4">
                  <StepDataRenderer stepId={step.id} data={step.data} />

                  {step.reasoning && (
                    <div className="mt-4 pt-4 border-t border-border">
                      <div className="rounded-lg border border-indigo-500/20 bg-gradient-to-br from-indigo-500/5 to-blue-500/5 overflow-hidden">
                        <div className="flex items-center gap-2 px-3 py-2 bg-indigo-500/10 border-b border-indigo-500/20">
                          <SparklesIcon className="h-4 w-4 text-indigo-400" />
                          <span className="text-xs font-medium text-indigo-300">AI Reasoning</span>
                        </div>
                        <div className="p-3">
                          <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                            {step.reasoning}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  )
}

interface StepDataRendererProps {
  stepId: string
  data: Record<string, unknown>
}

function StepDataRenderer({ stepId, data }: StepDataRendererProps) {
  switch (stepId) {
    case 'briefing-request':
      return <BriefingRequestData data={data} />
    case 'decomposition':
      return <DecompositionData data={data} />
    case 'source-search':
      return <SourceSearchData data={data} />
    case 'synthesis':
      return <SynthesisData data={data} />
    case 'brief-output':
      return <BriefOutputData data={data} />
    default:
      return <pre className="code-block text-xs">{JSON.stringify(data, null, 2)}</pre>
  }
}

// ============================================================================
// Step 1: Briefing Request
// ============================================================================

function BriefingRequestData({ data }: { data: Record<string, unknown> }) {
  const request = data.briefing_request as {
    account: string
    topic: string
    attendees?: string[]
  }

  if (!request) return null

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="p-5 bg-gradient-to-br from-indigo-500/10 to-slate-500/10 rounded-lg border border-indigo-500/20">
        <div className="flex items-center gap-2 mb-4">
          <BriefcaseIcon className="h-5 w-5 text-indigo-400" />
          <span className="font-medium text-indigo-300">Briefing Request</span>
        </div>

        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide w-20 pt-0.5">Account</span>
            <span className="text-lg font-semibold">{request.account}</span>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide w-20 pt-0.5">Topic</span>
            <span className="text-sm">{request.topic}</span>
          </div>

          {request.attendees && request.attendees.length > 0 && (
            <div className="flex items-start gap-3">
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide w-20 pt-1">Attendees</span>
              <div className="flex flex-wrap gap-2">
                {request.attendees.map((attendee, idx) => (
                  <span
                    key={idx}
                    className="text-sm px-3 py-1 bg-background/50 rounded-full border border-border"
                  >
                    {attendee}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Step 2: Query Decomposition
// ============================================================================

function DecompositionData({ data }: { data: Record<string, unknown> }) {
  const queries = (data.queries || []) as Array<{
    query: string
    source_name: string
    rationale: string
  }>

  const getStaggerClass = (idx: number) => `stagger-${Math.min(idx + 1, 10)}`

  const sourceConfig: Record<string, { bg: string; border: string; text: string; icon: string; label: string }> = {
    notion: { bg: 'bg-slate-500/10', border: 'border-slate-500/30', text: 'text-slate-400', icon: '📝', label: 'Notion' },
    google_drive: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', icon: '📄', label: 'Google Drive' },
    github: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400', icon: '💻', label: 'GitHub' },
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="p-4 bg-gradient-to-r from-indigo-500/10 to-slate-500/10 rounded-lg border border-indigo-500/20 animate-fade-in">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SearchIcon className="h-5 w-5 text-indigo-400" />
            <span className="font-medium">Query Decomposition</span>
          </div>
          <span className="text-sm text-muted-foreground">{queries.length} queries generated</span>
        </div>
      </div>

      {/* Queries list */}
      <div className="space-y-3">
        {queries.map((query, idx) => {
          const config = sourceConfig[query.source_name] || sourceConfig.notion

          return (
            <div
              key={idx}
              className={cn(
                "rounded-lg border overflow-hidden animate-fade-in",
                getStaggerClass(idx + 1),
                config.border,
                config.bg
              )}
            >
              <div className="p-4">
                <div className="flex items-start gap-3">
                  {/* Source badge */}
                  <div className={cn(
                    "px-2.5 py-1 rounded-full text-xs font-medium flex items-center gap-1.5 flex-shrink-0",
                    config.bg, config.border, config.text, "border"
                  )}>
                    <span>{config.icon}</span>
                    <span>{config.label}</span>
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium mb-1">{query.query}</p>
                    <p className="text-xs text-muted-foreground">{query.rationale}</p>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ============================================================================
// Step 3: Source Search
// ============================================================================

function SourceSearchData({ data }: { data: Record<string, unknown> }) {
  const resultsBySource = data.results_by_source as Record<string, Array<{
    query: string
    source_name: string
    title: string
    content: string
    url?: string
    score: number
  }>> | undefined

  const results = (data.results || []) as Array<{
    source_name: string
    title: string
    content: string
    url?: string
    score: number
  }>

  const sourcesSearched = (data.sources_searched || []) as string[]
  const resultCount = data.result_count as number || results.length

  const sourceConfig: Record<string, { bg: string; border: string; text: string; icon: string; label: string }> = {
    notion: { bg: 'bg-slate-500/10', border: 'border-slate-500/30', text: 'text-slate-400', icon: '📝', label: 'Notion' },
    google_drive: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400', icon: '📄', label: 'Google Drive' },
    github: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400', icon: '💻', label: 'GitHub' },
  }

  const getStaggerClass = (idx: number) => `stagger-${Math.min(idx + 1, 10)}`

  return (
    <div className="space-y-4">
      {/* Search summary header */}
      <div className="p-4 bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 rounded-lg border border-cyan-500/20 animate-fade-in">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <SearchIcon className="h-5 w-5 text-cyan-400" />
            <span className="font-medium">Source Search via</span>
            <div className="flex items-center gap-1.5 px-2 py-0.5 bg-background/50 rounded-md border border-cyan-500/30">
              <AirweaveIcon className="h-4 w-4 text-cyan-400" />
              <span className="font-medium text-cyan-400">Airweave</span>
            </div>
          </div>
          <span className="text-xs px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded-full border border-indigo-500/30">
            {resultCount} results
          </span>
        </div>

        {/* Sources searched */}
        <div className="flex flex-wrap gap-3">
          {sourcesSearched.map((source, idx) => {
            const config = sourceConfig[source] || sourceConfig.notion
            const count = resultsBySource?.[source]?.length || 0

            return (
              <div key={source} className={cn(
                "flex items-center gap-2 px-3 py-1.5 bg-background/50 rounded-md border border-border animate-fade-in",
                getStaggerClass(idx + 1)
              )}>
                <span>{config.icon}</span>
                <span className="text-sm">{config.label}</span>
                <span className={cn("text-xs px-1.5 py-0.5 rounded", config.bg, config.text)}>
                  {count} found
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Results grouped by source */}
      {sourcesSearched.map((source, sourceIdx) => {
        const sourceResults = resultsBySource?.[source] || []
        const config = sourceConfig[source] || sourceConfig.notion

        if (sourceResults.length === 0) return null

        return (
          <div key={source} className={cn("border border-border rounded-lg overflow-hidden animate-fade-in", getStaggerClass(sourceIdx + 4))}>
            {/* Source header */}
            <div className="px-4 py-3 bg-muted/30 border-b border-border">
              <div className="flex items-center gap-2">
                <span className="text-lg">{config.icon}</span>
                <h4 className="text-sm font-medium">{config.label}</h4>
                <span className="text-xs text-muted-foreground">({sourceResults.length} results)</span>
              </div>
            </div>

            <div className="divide-y divide-border/50">
              {sourceResults.map((result, rIdx) => (
                <div key={rIdx} className="p-4 hover:bg-muted/20 transition-colors">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <h5 className="text-sm font-medium flex-1">{result.title}</h5>
                    <span className={cn(
                      "text-xs px-1.5 py-0.5 rounded flex-shrink-0",
                      result.score >= 0.9 ? "bg-green-500/20 text-green-400" :
                      result.score >= 0.8 ? "bg-blue-500/20 text-blue-400" :
                      "bg-muted text-muted-foreground"
                    )}>
                      {(result.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed whitespace-pre-wrap">
                    {result.content.slice(0, 300)}
                    {result.content.length > 300 && '...'}
                  </p>
                  {result.url && (
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary/70 hover:text-primary mt-2 inline-block truncate max-w-full"
                    >
                      {result.url}
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ============================================================================
// Step 4: Context Synthesis
// ============================================================================

function SynthesisData({ data }: { data: Record<string, unknown> }) {
  const brief = data.brief as {
    account: string
    topic: string
    generated_at: string
    sections: Array<{ heading: string; content: string }>
  }

  const sectionCount = data.section_count as number || 0

  if (!brief) return null

  const getStaggerClass = (idx: number) => `stagger-${Math.min(idx + 1, 10)}`

  return (
    <div className="space-y-4">
      {/* Synthesis header */}
      <div className="p-4 bg-gradient-to-r from-amber-500/10 to-indigo-500/10 rounded-lg border border-amber-500/20 animate-fade-in">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-amber-400" />
            <span className="font-medium">Context Synthesis</span>
          </div>
          <span className="text-sm text-muted-foreground">{sectionCount} sections generated</span>
        </div>
      </div>

      {/* Section previews */}
      <div className="space-y-3">
        {brief.sections.map((section, idx) => (
          <div
            key={idx}
            className={cn(
              "rounded-lg border border-border overflow-hidden animate-fade-in",
              getStaggerClass(idx + 1)
            )}
          >
            <div className="px-4 py-3 bg-muted/30 border-b border-border">
              <div className="flex items-center gap-2">
                <span className="text-sm">{getSectionIcon(section.heading)}</span>
                <h4 className="text-sm font-medium">{section.heading}</h4>
              </div>
            </div>
            <div className="p-4">
              <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap line-clamp-4">
                {section.content.slice(0, 200)}
                {section.content.length > 200 && '...'}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function getSectionIcon(heading: string): string {
  const lower = heading.toLowerCase()
  if (lower.includes('snapshot') || lower.includes('account')) return '📊'
  if (lower.includes('relationship') || lower.includes('history')) return '🤝'
  if (lower.includes('concern') || lower.includes('risk')) return '⚠️'
  if (lower.includes('product') || lower.includes('update')) return '🚀'
  if (lower.includes('talking') || lower.includes('point')) return '💬'
  return '📋'
}

// ============================================================================
// Step 5: Brief Output
// ============================================================================

function BriefOutputData({ data }: { data: Record<string, unknown> }) {
  const markdown = data.markdown as string || ''
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback
      const textArea = document.createElement('textarea')
      textArea.value = markdown
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (!markdown) return null

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Actions bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <DocumentIcon className="h-5 w-5 text-indigo-400" />
          <span className="font-medium">Generated Brief</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-3 py-1.5 text-xs bg-muted hover:bg-accent rounded-md border border-border transition-colors"
        >
          {copied ? (
            <>
              <CheckCheck className="h-3.5 w-3.5 text-green-500" />
              <span className="text-green-500">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              <span>Copy Brief</span>
            </>
          )}
        </button>
      </div>

      {/* Rendered brief */}
      <div className="rounded-lg border border-border bg-card/50 overflow-hidden">
        <div className="p-6 brief-markdown">
          <SimpleMarkdownRenderer markdown={markdown} />
        </div>
      </div>
    </div>
  )
}

// Simple markdown renderer (no dependencies)
function SimpleMarkdownRenderer({ markdown }: { markdown: string }) {
  const lines = markdown.split('\n')
  const elements: JSX.Element[] = []
  let inTable = false
  let tableRows: string[][] = []
  let tableHeaders: string[] = []
  let listItems: { text: string; ordered: boolean }[] = []
  let inList = false
  let listOrdered = false

  const flushList = () => {
    if (listItems.length > 0) {
      const Tag = listOrdered ? 'ol' : 'ul'
      elements.push(
        <Tag key={`list-${elements.length}`}>
          {listItems.map((item, i) => (
            <li key={i} dangerouslySetInnerHTML={{ __html: formatInline(item.text) }} />
          ))}
        </Tag>
      )
      listItems = []
      inList = false
    }
  }

  const flushTable = () => {
    if (tableHeaders.length > 0) {
      elements.push(
        <table key={`table-${elements.length}`}>
          <thead>
            <tr>
              {tableHeaders.map((h, i) => (
                <th key={i} dangerouslySetInnerHTML={{ __html: formatInline(h) }} />
              ))}
            </tr>
          </thead>
          <tbody>
            {tableRows.map((row, rIdx) => (
              <tr key={rIdx}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} dangerouslySetInnerHTML={{ __html: formatInline(cell) }} />
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )
      tableHeaders = []
      tableRows = []
      inTable = false
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()

    // Table rows
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushList()
      const cells = trimmed.slice(1, -1).split('|').map(c => c.trim())

      // Check if next line is separator
      if (!inTable) {
        const nextLine = lines[i + 1]?.trim() || ''
        if (nextLine.match(/^\|[\s-:|]+\|$/)) {
          tableHeaders = cells
          inTable = true
          i++ // Skip separator line
          continue
        }
      }

      if (inTable) {
        tableRows.push(cells)
        continue
      }
    } else if (inTable) {
      flushTable()
    }

    // Headings
    if (trimmed.startsWith('# ')) {
      flushList()
      elements.push(<h1 key={i} dangerouslySetInnerHTML={{ __html: formatInline(trimmed.slice(2)) }} />)
      continue
    }
    if (trimmed.startsWith('## ')) {
      flushList()
      elements.push(<h2 key={i} dangerouslySetInnerHTML={{ __html: formatInline(trimmed.slice(3)) }} />)
      continue
    }
    if (trimmed.startsWith('### ')) {
      flushList()
      elements.push(<h3 key={i} dangerouslySetInnerHTML={{ __html: formatInline(trimmed.slice(4)) }} />)
      continue
    }

    // Horizontal rule
    if (trimmed === '---' || trimmed === '***') {
      flushList()
      elements.push(<hr key={i} />)
      continue
    }

    // Unordered list
    if (trimmed.match(/^[-*]\s/)) {
      if (!inList || listOrdered) {
        flushList()
        inList = true
        listOrdered = false
      }
      listItems.push({ text: trimmed.slice(2), ordered: false })
      continue
    }

    // Ordered list
    if (trimmed.match(/^\d+\.\s/)) {
      if (!inList || !listOrdered) {
        flushList()
        inList = true
        listOrdered = true
      }
      listItems.push({ text: trimmed.replace(/^\d+\.\s/, ''), ordered: true })
      continue
    }

    // Empty line
    if (trimmed === '') {
      flushList()
      continue
    }

    // Regular paragraph
    flushList()
    elements.push(<p key={i} dangerouslySetInnerHTML={{ __html: formatInline(trimmed) }} />)
  }

  flushList()
  flushTable()

  return <>{elements}</>
}

function formatInline(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="text-xs px-1 py-0.5 bg-muted rounded">$1</code>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-primary hover:underline">$1</a>')
}

// ============================================================================
// Icon Components
// ============================================================================

function SparklesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l1.912 5.813a2 2 0 001.275 1.275L21 12l-5.813 1.912a2 2 0 00-1.275 1.275L12 21l-1.912-5.813a2 2 0 00-1.275-1.275L3 12l5.813-1.912a2 2 0 001.275-1.275L12 3z" />
      <path d="M5 3v4" />
      <path d="M3 5h4" />
      <path d="M19 17v4" />
      <path d="M17 19h4" />
    </svg>
  )
}

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  )
}

function BriefcaseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  )
}

function DocumentIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <line x1="10" y1="9" x2="8" y2="9" />
    </svg>
  )
}

function AirweaveIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 143 143" fill="currentColor">
      <path d="M89.3854 128.578C79.4165 123.044 66.2502 114.852 60.0707 107.348L59.5432 106.724C58.2836 105.206 56.981 103.72 55.6676 102.299C51.4152 97.6699 46.8614 93.5036 42.146 89.9079C40.2405 88.4546 38.2704 87.055 36.3111 85.7847C35.2991 85.128 34.3302 84.5251 33.4151 83.9761C31.1221 82.6088 28.3338 82.2321 25.7716 82.9534C23.3385 83.6424 21.39 85.2464 20.2596 87.4534C18.0634 91.7381 19.5814 97.0347 23.7046 99.5108C27.0204 101.492 30.2608 103.817 33.3398 106.422C33.7381 106.756 33.8996 107.284 33.7596 107.768C32.6292 111.891 31.4989 118.663 31.0682 121.376C30.1424 127.135 32.9737 132.787 38.0982 135.457L38.2812 135.554C40.5204 136.706 43.1472 136.652 45.3219 135.403C47.4858 134.165 48.853 131.937 48.9822 129.439C49.036 128.363 49.1006 127.286 49.176 126.296C49.219 125.768 49.542 125.337 50.0264 125.165C50.1772 125.111 50.3494 125.079 50.5001 125.079C50.8554 125.079 51.1784 125.219 51.4475 125.488C55.743 129.891 60.3829 133.875 65.2167 137.33C69.8674 140.657 75.3686 142.412 81.139 142.412C83.2383 142.412 85.3376 142.175 87.3938 141.701L87.6199 141.647C90.4943 140.98 92.529 138.73 92.9488 135.791C93.3687 132.852 91.9476 130.02 89.3747 128.589H89.3639L89.3854 128.578Z"/>
      <path d="M142.051 57.8805L142.029 57.7621C141.545 55.2968 139.618 53.4128 137.098 52.9606C134.612 52.5192 132.254 53.5635 130.984 55.6951L130.908 55.8135C126.204 63.8662 119.561 71.3159 111.153 78.0014C108.946 79.7562 106.793 81.6078 104.726 83.5134C103.144 84.9775 100.765 85.2359 98.9452 84.127C97.1474 83.0397 95.3495 81.8447 93.6055 80.5744C89.8268 77.8291 86.1772 74.6533 82.7753 71.1329C80.9989 69.3028 79.298 67.3973 77.6939 65.438C75.5408 62.8219 73.2477 60.2597 70.8685 57.8374C65.8195 52.6915 56.1089 45.6185 53.2453 43.5838C52.8792 43.3362 52.6639 42.9486 52.5993 42.5073C52.5455 42.0659 52.6639 41.6567 52.9546 41.3122C54.774 39.1376 56.4965 36.8876 58.0683 34.6268C59.7369 32.2369 60.286 29.3086 59.5862 26.5957C58.908 23.9581 57.1424 21.8158 54.634 20.5885C50.4139 18.5 45.3972 19.8026 42.7273 23.6351C40.3373 27.0694 37.5167 30.439 34.3732 33.6364C34.0718 33.9378 33.6304 34.0455 33.2213 33.8948C30.0239 32.8505 26.7296 32 23.4461 31.3648C23.2093 31.3218 22.854 31.2572 22.4126 31.2034C15.9102 30.2345 9.61233 33.4857 6.71639 39.2775L6.6195 39.4606C5.68289 41.3338 5.76902 43.5407 6.82405 45.3709C7.90061 47.2226 9.82765 48.4068 11.9592 48.5252C12.9604 48.579 13.9401 48.6436 14.8659 48.7082C15.2966 48.7405 15.6411 48.9881 15.8025 49.3972C15.9533 49.8171 15.8671 50.2477 15.5657 50.5599C11.647 54.5862 8.10515 58.9032 5.0262 63.3925C0.644601 69.7872 -0.981008 77.9153 0.580002 85.688L0.601538 85.8064C1.20441 88.7777 3.55131 90.9093 6.57644 91.2323C9.48315 91.5445 12.1099 90.0266 13.2619 87.3782L13.3265 87.2167C18.1925 75.5683 26.2559 65.2226 37.2907 56.4594C37.8182 56.0503 38.5072 55.9858 39.067 56.298C44.8373 59.4738 50.3601 63.6078 55.4738 68.5923C56.0982 69.1951 56.1089 70.2071 55.5168 70.8315C52.9761 73.5122 50.5862 76.3112 48.4115 79.1749C46.7106 81.4141 47.0335 84.6007 49.1221 86.4416L52.8254 89.7036L52.7824 89.7467C53.3637 90.2634 53.945 90.7802 54.5264 91.2969L55.3123 91.8998C56.4319 92.8902 57.8529 93.3423 59.3386 93.1916C60.8027 93.0409 62.17 92.2658 63.0635 91.0816C64.6353 88.9931 66.3578 86.9584 68.1556 85.0098C68.457 84.676 68.8661 84.5038 69.3075 84.4931C69.7705 84.4931 70.1257 84.6437 70.4164 84.9344C75.3147 89.7682 80.6114 94.0744 86.1772 97.7024C88.3626 99.1234 88.9978 101.966 87.6306 104.183C86.4248 106.153 85.2729 108.199 84.2179 110.244C83.0014 112.624 82.7968 115.444 83.6688 117.963C84.4978 120.385 86.2095 122.291 88.481 123.346C89.7514 123.938 91.0971 124.24 92.4859 124.24C96.0062 124.24 99.182 122.302 100.786 119.158C102.229 116.316 103.919 113.506 105.781 110.836C106.869 109.265 108.86 108.543 110.755 109.028C114.76 110.061 120.143 111.127 123.954 111.848C127.808 112.57 131.619 110.729 133.46 107.284L133.643 106.939C135.021 104.334 135.031 101.212 133.664 98.5959C132.286 95.9584 129.681 94.1713 126.71 93.8268C125.978 93.7407 125.278 93.6546 124.61 93.5684C124.47 93.5469 124.352 93.5254 124.244 93.5038L122.856 93.1809L123.857 92.1581C123.932 92.0828 124.029 91.9859 124.158 91.8998C128.271 88.5086 132.071 84.9021 135.462 81.1772C141.168 74.9009 143.622 66.2023 142.018 57.8805H142.029H142.051Z"/>
      <path d="M56.1506 14.0429C65.0861 19.3396 76.9067 27.0801 82.4833 33.8732C83.14 34.659 83.7967 35.4449 84.4534 36.1985C85.6591 37.5873 85.7991 39.5789 84.7979 41.1292C82.9892 43.9174 80.9115 46.6627 78.6399 49.3003C76.9713 51.2165 76.9067 54.0156 78.4785 55.9534L78.5431 56.0288C78.7261 56.2656 78.9306 56.5132 79.1136 56.75C80.7931 58.8816 82.5801 60.9271 84.4211 62.8433C85.4007 63.8661 86.7249 64.4367 88.1352 64.4367L88.2644 65.2333L88.2429 64.4367C89.707 64.4044 91.1173 63.7584 92.0969 62.6388C94.3362 60.1089 96.4247 57.4498 98.3302 54.7691C99.6329 52.9282 102.13 52.5084 104.025 53.8111C105.963 55.146 107.965 56.4163 109.957 57.5897C112.293 58.957 115.114 59.2153 117.665 58.268C120.249 57.3098 122.262 55.2752 123.156 52.6591C124.555 48.6113 122.757 43.9605 118.882 41.6136C116.255 40.0203 113.65 38.2224 111.174 36.2846C109.882 35.2619 109.333 33.5825 109.796 32C110.937 28.0059 111.981 22.8276 112.648 19.1889C113.337 15.4317 111.647 11.5884 108.439 9.65058L108.062 9.43525C105.371 7.83118 102.087 7.71277 99.2668 9.1123C96.4247 10.5226 94.53 13.2463 94.1855 16.3791L94.1639 16.5728C94.1209 16.9604 93.884 17.2511 93.518 17.3695C93.152 17.4879 92.7859 17.3911 92.5168 17.1327C88.5012 12.848 84.238 8.96157 79.8134 5.57041C73.8708 1.01656 66.2811 -0.878188 58.9928 0.381386L58.6805 0.435234C55.6124 0.973513 53.2547 3.30965 52.6949 6.3886C52.1351 9.43527 53.4915 12.4281 56.1722 14.0106H56.1614L56.1506 14.0429Z"/>
    </svg>
  )
}
