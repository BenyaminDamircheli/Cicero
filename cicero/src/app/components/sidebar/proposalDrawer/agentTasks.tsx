"use client";

import { useState, useEffect } from "react";
import { Loader2, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Task {
  id: number;
  type: string;
  name: string;
  completed: boolean;
  details?: string[];
}

interface AIAgentTaskProps {
  wsRef: React.MutableRefObject<WebSocket | null>;
  clientId: string;
}

export default function AIAgentTask({ wsRef, clientId }: AIAgentTaskProps) {
  const [tasks, setTasks] = useState<Task[]>([]);


    const ws = wsRef.current;
    if (!ws) {
      console.error("WebSocket is not connected");
      return;
    }

    const handleMessage = (event: MessageEvent) => {
      console.log("WebSocket message received:", event.data);
      const data = JSON.parse(event.data);
      const {type: taskType, action: taskName, status, details} = data;
      setTasks((prev) => {
        const existingTask = prev.find((t) => t.name === taskName);

        if (existingTask) {
          return prev.map((t) =>
            t.name === taskName && taskType === "update"
              ? { ...t, completed: status === "success", status, details }
              : t
          );
        } else {
          return [
            ...prev,
            {
              id: prev.length + 1,
              type: "pending",
              name: taskName,
              completed: status === "success",
              status,
              details: details
                ? Array.isArray(details)
                  ? details
                  : [details]
                : undefined,
            },
          ];
        }
      });
    };

    const handleError = (error: Event) => {
      console.error("WebSocket error:", error);
    };

    ws.addEventListener("message", handleMessage);
    ws.addEventListener("error", handleError);



  return (
    <div className="space-y-2 mb-5">
      <h3 className="text-lg font-semibold">Agent Tasks</h3>
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
              <span className="text-gray-600 text-sm">
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
                      {typeof detail === "string"
                        ? detail
                        : (detail as { name?: string; type?: string }).name ||
                          (detail as { name?: string; type?: string }).type}
                    </span>
                  </div>
                ))}
              </motion.div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
