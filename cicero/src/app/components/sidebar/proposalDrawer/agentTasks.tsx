"use client"

import { useState, useEffect } from "react"
import { Loader2, CheckCircle2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface Task {
  id: number
  name: string
  completed: boolean
}

export default function AIAgentTask() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [currentTaskId, setCurrentTaskId] = useState(1)

  useEffect(() => {
    const interval = setInterval(() => {
      if (currentTaskId <= 5) {
        setTasks(prevTasks => [
          ...prevTasks,
          { id: currentTaskId, name: `Task ${currentTaskId}`, completed: false }
        ])
        setCurrentTaskId(prevId => prevId + 1)
      } else {
        clearInterval(interval)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [currentTaskId])

  useEffect(() => {
    const timeout = setTimeout(() => {
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === currentTaskId - 1 ? { ...task, completed: true } : task
        )
      )
    }, 2000)

    return () => clearTimeout(timeout)
  }, [tasks, currentTaskId])

  return (
    <div className="max-w-md mx-autofont-sans">
      <ul className="space-y-1">
        <AnimatePresence>
          {tasks.map(task => (
            <motion.li
              key={task.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="flex items-center space-x-2 py-2 last:border-b-0"
            >
              {task.completed ? (
                <CheckCircle2 className="w-4 h-4 text-green-500" />
              ) : (
                <Loader2 className="w-4 h-4 text-xs text-gray-400 animate-spin" />
              )}
              <span className={`text-sm ${task.completed ? 'text-gray-600' : 'text-gray-500'}`}>
                {task.name}
              </span>
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </div>
  )
}