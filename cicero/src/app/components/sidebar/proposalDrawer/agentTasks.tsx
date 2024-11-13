"use client";

import { useState, useEffect } from "react";
import { Loader2, CheckCircle2, Search } from "lucide-react";
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
    const { type: taskType, action: taskName, status, data: taskData } = data;
    setTasks((prev) => {
      const existingTask = prev.find((t) => t.name === taskName);

      if (existingTask) {
        return prev.map((t) =>
          t.name === taskName && taskType === "update"
            ? {
                ...t,
                completed: status === "success",
                status,
                details:
                  taskData && taskName === "Finding POIs"
                    ? taskData.map((poi: any) => poi.address)
                    : taskName === "Creating Research Plan" &&
                      taskData?.search_queries
                    ? taskData.search_queries
                    : taskData,
              }
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
            details:
              taskData && taskName === "Finding POIs"
                ? taskData.map((poi: any) => poi.address)
                : taskName === "Creating Research Plan" &&
                  taskData?.search_queries
                ? taskData.search_queries
                : taskData,
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
      <div className="flex items-center gap-2">
        <Search className="w-3 h-3" />
        <h3 className="text-base font-semibold">Research</h3>
      </div>

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
              <span className="text-gray-600 text-sm">{task.name}</span>
            </div>

            {task.details && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="ml-6 text-sm text-gray-500 space-y-1"
              >
                {Array.isArray(task.details) &&
                  task.details.map((detail, i) => (
                    <div key={i} className="flex items-center space-x-2">
                      <div className="w-1 h-1 rounded-full bg-gray-400" />
                      <span>
                        {typeof detail === "string"
                          ? detail
                          : `${(detail as any).name || ""} ${
                              (detail as any).type
                                ? `(${(detail as any).type})`
                                : ""
                            } ${
                              (detail as any).address
                                ? `- ${(detail as any).address}`
                                : ""
                            }`}
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
