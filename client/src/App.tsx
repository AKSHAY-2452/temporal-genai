import { useState } from "react";
import type { Workflow, Activity } from "./workflow";
import { v4 as uuidv4 } from "uuid";
import { AnimatePresence, motion } from "framer-motion";
import { ChatWindow } from "./ChatWindow";

export type Message = {
  id: string;
  sender: "user" | "bot";
  text: string;
};

export default function App() {
  const [workflow, setWorkflow] = useState<Workflow>({
    name: "",
    activities: [],
  });
  const [activityName, setActivityName] = useState("");
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);


  const addActivity = () => {
    if (!activityName) return;

    const newActivity: Activity = {
      id: uuidv4(),
      name: activityName,
      timeout_seconds: 10,
    };

    setWorkflow((prev) => ({
      ...prev,
      activities: [...prev.activities, newActivity],
    }));

    setActivityName("");
  };

  const submitWorkflow = async () => {
    if (!workflow.name || workflow.activities.length === 0) {
      alert("Please add workflow name and at least one activity");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/generate-workflow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(workflow),
      });

      const data = await response.json();
      console.log(data);
      
    } catch (err) {
    }
  };

const sendPrompt = async () => {
  if (!prompt || loading) return;

  const userMessage: Message = { id: uuidv4(), sender: "user", text: prompt };
  setMessages((prev) => [...prev, userMessage]);
  setPrompt("");

  setLoading(true);  

  try {
    const response = await fetch("http://localhost:8000/api/generate-workflow", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    if (response.status === 200) {
      const data = await response.json();
      const botMessage: Message = {
        id: uuidv4(),
        sender: "bot",
        text: data.message,
      };
      setMessages((prev) => [...prev, botMessage]);
    } 
    else {
      const botMessage: Message = {
        id: uuidv4(),
        sender: "bot",
        text: "❌ Failed to create workflow. Please try again.",
      };
      setMessages((prev) => [...prev, botMessage]);
    }
  } catch (err) {
    console.error(err);
    const botMessage: Message = {
      id: uuidv4(),
      sender: "bot",
      text: "⚠️ Server unreachable. Try again later.",
    };
    setMessages((prev) => [...prev, botMessage]);
  }

  setLoading(false); 
};


  return (
    <div className="bg-gray-900 min-h-screen flex items-center justify-center p-6 font-sans text-gray-100 relative">
      <div className={`w-full max-w-4xl p-10 bg-gray-800 rounded-2xl shadow-lg space-y-8 ${chatOpen?"opacity-30 pointer-events-none":"opacity-100"}  z-0`}>
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">
            Temporal Workflow Builder
          </h1>
          <p className="text-gray-400 text-base leading-relaxed">
            Design reliable <strong>workflows</strong> where each step (
            <strong>activity</strong>) can run independently and recover from
            failures. Add your workflow name, define activities, and generate it
            in your backend.
          </p>
        </div>

        <div className="space-y-2">
          <label className="text-gray-300 font-medium ">Workflow Name</label>
          <input
            type="text"
            value={workflow.name}
            onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
            placeholder="Enter workflow name..."
            className="w-full rounded-lg p-3 bg-gray-700 border border-gray-600 text-white focus:ring-2 focus:ring-gray-500 focus:outline-none transition"
          />
        </div>

        <div className="flex space-x-3 items-center">
          <input
            type="text"
            value={activityName}
            onChange={(e) => setActivityName(e.target.value)}
            placeholder="Enter activity name..."
            className="flex-1 rounded-lg p-3 bg-gray-700 border border-gray-600 text-white focus:ring-2 focus:ring-gray-500 focus:outline-none transition"
          />
          <button
            onClick={addActivity}
            className="bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold shadow hover:bg-gray-100 transition transform hover:scale-105"
          >
            Add Activity
          </button>
        </div>

        <div className="min-h-[20vh]">
          <h2 className="text-lg font-semibold mb-2">Activities</h2>
          {workflow.activities.length === 0 ? (
            <p className="text-gray-500 italic">
              No activities yet. Add one above.
            </p>
          ) : (
            <ul className="space-y-2">
              <AnimatePresence>
                {workflow.activities.map((act) => (
                  <motion.li
                    key={act.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.25 }}
                    className="bg-gray-700 border border-gray-600 rounded-lg p-3 flex justify-between items-center hover:bg-gray-600 transition cursor-pointer"
                  >
                    <span className="font-medium">{act.name}</span>
                    <span className="text-gray-400 text-sm">
                      Timeout: {act.timeout_seconds}s
                    </span>
                  </motion.li>
                ))}
              </AnimatePresence>
            </ul>
          )}
        </div>

        <button
          onClick={submitWorkflow}
          className="w-full bg-white text-gray-900 px-6 py-4 rounded-lg font-semibold shadow hover:bg-gray-100 transition transform hover:scale-105 text-lg"
        >
          Generate Workflow
        </button>

        <p className="text-gray-500 text-sm mt-4">
          Tip: Workflows define orchestration. Activities are individual tasks.
          This tool helps you quickly design and deploy workflows without
          writing code.
        </p>
      </div>

      <div className="fixed bottom-8 right-8 z-500">
        <ChatWindow
          messages={messages}
          sendPrompt={sendPrompt}
          setChatOpen={setChatOpen}
          setPrompt={setPrompt}
          chatOpen={chatOpen}
          prompt={prompt}
        />
        {!chatOpen && (
          <button
            onClick={() => setChatOpen(true)}
            className="w-16 h-16 rounded-full bg-white text-gray-900 font-bold text-xl shadow-lg hover:bg-gray-100 transition transform hover:scale-110 flex items-center justify-center"
          >
            💬
          </button>
        )}
      </div>
    </div>
  );
}
