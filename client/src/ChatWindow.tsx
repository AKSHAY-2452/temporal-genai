import { AnimatePresence, motion } from "framer-motion";
import type { Message } from "./App";

export function ChatWindow({
  chatOpen,
  setChatOpen,
  messages,
  prompt,
  sendPrompt,
  setPrompt,
}: {
  chatOpen: boolean;
  setChatOpen: (para: boolean) => void;
  messages: Message[];
  prompt: string;
  sendPrompt: () => Promise<void>;
  setPrompt: (para: string) => void;
}) {
  return (
    <AnimatePresence>
      {chatOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.25 }}
          className="absolute bottom-8 right-0 w-100 h-200 bg-gray-800 rounded-2xl shadow-lg flex flex-col overflow-hidden"
        >
          <div className="bg-gray-700 p-3 font-semibold text-gray-100 flex justify-between items-center">
            Workflow Assistant
            <button
              onClick={() => setChatOpen(false)}
              className="text-gray-200 hover:text-white font-bold text-xl"
            >
              ✖
            </button>
          </div>
          <div className="p-3 text-gray-300 text-sm  border-gray-700">
            <p className="leading-relaxed">
              Tell me the workflow you want to create.
              <br />
              <br />
              Please include:
            </p>
            <ul className="list-disc list-inside pl-1 mt-1 space-y-1">
              <li>Workflow name</li>
              <li>List of activities</li>
              <li>Activity names and their inputs</li>
              <li>Any retry policies, timers, or other configurations</li>
            </ul>
            <p className="mt-3 italic text-gray-400">
              Example: “Create a workflow named
              <strong> OrderProcessor</strong> with activities
              <strong> chargeCard(amount)</strong>,
              <strong> sendEmail(to)</strong>, and
              <strong> waitFor(1h)</strong>.”
            </p>
          </div>

          <div className="flex-1 p-3 space-y-2 max-h-96 overflow-y-auto">
            <AnimatePresence>
              <div
                className="space-y-4 p-4 overflow-y-auto max-h-80  scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800 
  hover:scrollbar-thumb-gray-500 rounded-lg"
              >
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex w-full ${
                      msg.sender === "user" ? "justify-start" : "justify-end"
                    }`}
                  >
                    <div
                      className={`max-w-[75%] p-3 rounded-xl shadow text-sm ${
                        msg.sender === "user"
                          ? "bg-gray-700 text-white rounded-bl-none"
                          : "bg-white text-gray-900 rounded-br-none"
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
              </div>
            </AnimatePresence>
          </div>

          <div className="flex p-3 border-t border-gray-700">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 rounded-lg p-2 bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-gray-500 transition"
              onKeyDown={(e) => e.key === "Enter" && sendPrompt()}
            />
            <button
              onClick={sendPrompt}
              className="ml-2 bg-white text-gray-900 px-3 rounded-lg font-semibold shadow hover:bg-gray-100 transition transform hover:scale-105"
            >
              Send
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
