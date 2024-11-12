"use client"

import { useState, useEffect } from "react"
import { Loader2, CheckCircle2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface Task {
  id: number
  name: string
  completed: boolean
  details?: string[]
}

interface AIAgentTaskProps {
  wsRef: React.MutableRefObject<WebSocket | null>;
  clientId: string;
}

export default function AIAgentTask({ wsRef, clientId }: AIAgentTaskProps) {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    const ws = wsRef.current
    if (!ws) {
      console.error("WebSocket is not connected")
      return
    }

    console.log("WebSocket connected")

    ws.onmessage = (event) => {
      console.log("WebSocket message received:", event.data)
      const data = JSON.parse(event.data)
      
      setTasks(prev => {
        const taskName = data.type
        const existingTask = prev.find(t => t.name === taskName)
        
        if (existingTask) {
          return prev.map(t => 
            t.name === taskName 
              ? { 
                  ...t, 
                  completed: true,
                  details: data.data ? (Array.isArray(data.data) ? data.data : [data.data]) : undefined
                }
              : t
          )
        }
        
        return [...prev, {
          id: prev.length + 1,
          name: taskName,
          completed: false,
          details: data.data ? (Array.isArray(data.data) ? data.data : [data.data]) : undefined
        }]
      })
    }

    ws.onerror = (error) => {
      console.error("WebSocket error:", error)
    }

    return () => {
      ws.onmessage = null
      ws.onerror = null
    }
  }, [])

  return (
    <div className="space-y-2">
      <AnimatePresence>
        {tasks.map((task) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-1"
          >
            <div className="flex items-center space-x-2">
              {task.completed ? (
                <CheckCircle2 className="w-4 h-4 text-green-500" />
              ) : (
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
              )}
              <span className={task.completed ? 'text-gray-600' : 'text-blue-600'}>
                {task.name}
              </span>
            </div>
            
            {task.details && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="ml-6 text-sm text-gray-500 space-y-1"
              >
                {task.details.map((detail, i) => (
                  <div key={i} className="flex items-center space-x-2">
                    <div className="w-1 h-1 rounded-full bg-gray-400" />
                    <span>
                      {typeof detail === 'string' 
                        ? detail 
                        : (detail as {name?: string; type?: string}).name || 
                          (detail as {name?: string; type?: string}).type}
                    </span>
                  </div>
                ))}
              </motion.div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}