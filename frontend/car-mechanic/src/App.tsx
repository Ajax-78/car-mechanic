
import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import {
  CarFront,
  Wrench,
  Send,
  Paperclip,
  Mic,
  CalendarDays,
} from "lucide-react";

import {
  sendChatMessage,
  uploadMedia,
  getDiagnosis,
  createBooking,
} from "./services/api";

import "./index.css";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Diagnosis {
  severity?: string;
  title?: string;
  diagnosis?: string;
  summary?: string;
  description?: string;
  service?: string;
  confidence?: number;
}

interface BookingForm {
  name: string;
  phone: string;
  date: string;
  time: string;
  issue: string;
}

interface BookingModalProps {
  diagnosis: Diagnosis | null;
  onClose: () => void;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm AutoMate, your virtual mechanic. Tell me what is happening with your car.",
    },
  ]);

  const [input, setInput] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [bookingOpen, setBookingOpen] = useState<boolean>(false);

  const handleSend = async (): Promise<void> => {
    if (!input.trim() && !file) return;

    setLoading(true);

    try {
      let mediaId: string | null = null;

      // --------------------------------
      // 1. Upload media if attached
      // --------------------------------
      if (file) {
        const formData = new FormData();
        formData.append("file", file);

        const uploadResponse = await uploadMedia(formData);

        mediaId =
          uploadResponse.data.id ||
          uploadResponse.data.media_id ||
          uploadResponse.data.file?.id ||
          null;
      }

      // --------------------------------
      // 2. Add user's message
      // --------------------------------
      const userMessage: Message = {
        role: "user",
        content: input.trim() || `Uploaded ${file?.name}`,
      };

      setMessages((prev) => [...prev, userMessage]);

      // --------------------------------
      // 3. Send message to Django
      // --------------------------------
      const response = await sendChatMessage({
        message: input.trim(),
        media_id: mediaId,
        history: messages,
      });

      console.log("CHAT RESPONSE:", response.data);

      // --------------------------------
      // 4. Get AI reply
      // Django response:
      //
      // {
      //   success: true,
      //   data: {
      //      reply: "..."
      //   }
      // }
      // --------------------------------
      const assistantMessage: Message = {
        role: "assistant",
        content:
          response.data.data?.reply ||
          response.data.reply ||
          response.data.message ||
          "Please provide more details about the problem.",
      };

      setMessages((prev) => [...prev, assistantMessage]);

      setInput("");
      setFile(null);
    } catch (error: any) {
      console.error("CHAT ERROR:", error);
      console.error("STATUS:", error.response?.status);
      console.error("DATA:", error.response?.data);
      console.error("URL:", error.config?.url);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the mechanic service.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------
  // Generate Diagnosis
  // --------------------------------
  const handleDiagnosis = async (): Promise<void> => {
    setLoading(true);

    try {
      const response = await getDiagnosis({
        messages,
      });

      console.log("DIAGNOSIS RESPONSE:", response.data);

      // Django returns:
      // {
      //   success: true,
      //   diagnosis: {...}
      // }

      setDiagnosis(response.data.diagnosis);
    } catch (error: any) {
      console.error("DIAGNOSIS ERROR:", error);
      console.error("DATA:", error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">
        <div className="logo">
          <CarFront size={24} />

          <div>
            <h1>AutoMate</h1>
            <span>AI Car Mechanic</span>
          </div>
        </div>

        <div className="online">
          <span />
          Mechanic Online
        </div>
      </header>

      <div className="layout">

        {/* HISTORY */}

        <aside className="history">
          <h3>Diagnosis History</h3>

          <p>
            Your previous diagnoses will appear here.
          </p>
        </aside>

        {/* CHAT */}

        <main className="chat">

          <div className="chat-header">
            <div className="mechanic-icon">
              <Wrench size={20} />
            </div>

            <div>
              <strong>Virtual Mechanic</strong>
              <small>
                Ask about your car problem
              </small>
            </div>
          </div>

          <div className="messages">

            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-row ${message.role}`}
              >
                <div className="message">
                  {message.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row assistant">
                <div className="message">
                  Thinking...
                </div>
              </div>
            )}

          </div>

          {/* INPUT */}

          <div className="composer">

            {file && (
              <div className="file">
                📎 {file.name}
              </div>
            )}

            <div className="input-row">

              {/* FILE UPLOAD */}

              <label className="icon-button">

                <Paperclip size={20} />

                <input
                  type="file"
                  hidden
                  accept="image/*,audio/*,video/*"
                  onChange={(
                    e: ChangeEvent<HTMLInputElement>
                  ) => {
                    const selectedFile =
                      e.target.files?.[0] ?? null;

                    setFile(selectedFile);
                  }}
                />

              </label>

              {/* TEXT INPUT */}

              <input
                value={input}
                onChange={(
                  e: ChangeEvent<HTMLInputElement>
                ) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (
                    e.key === "Enter" &&
                    !e.shiftKey
                  ) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Describe what your car is doing..."
              />

              {/* MICROPHONE */}

              <button
                className="icon-button"
                type="button"
              >
                <Mic size={20} />
              </button>

              {/* SEND */}

              <button
                className="send-button"
                onClick={handleSend}
                disabled={loading}
                type="button"
              >
                <Send size={18} />
              </button>

            </div>

            <div className="upload-types">
              <span>📷 Images</span>
              <span>🎤 Audio</span>
              <span>🎥 Video</span>
            </div>

          </div>

        </main>

        {/* DIAGNOSIS */}

        <aside className="diagnosis">

          <h3>Diagnosis</h3>

          {!diagnosis ? (

            <div className="empty-diagnosis">

              <Wrench size={35} />

              <h4>No diagnosis yet</h4>

              <p>
                Chat with the mechanic first.
                Once enough information is
                collected, generate a diagnosis.
              </p>

              <button
                onClick={handleDiagnosis}
                disabled={
                  messages.length < 2 ||
                  loading
                }
                type="button"
              >
                Generate Diagnosis
              </button>

            </div>

          ) : (

            <div className="diagnosis-result">

              <span className="severity">
                {diagnosis.severity ||
                  "Medium"}{" "}
                Priority
              </span>

              <h4>
                {diagnosis.title ||
                  diagnosis.diagnosis ||
                  "Vehicle Issue"}
              </h4>

              <p>
                {diagnosis.summary ||
                  diagnosis.description ||
                  "No description available."}
              </p>

              <div className="service">

                <strong>
                  Recommended Service
                </strong>

                <span>
                  {diagnosis.service ||
                    "Professional inspection"}
                </span>

              </div>

              <button
                onClick={() =>
                  setBookingOpen(true)
                }
                type="button"
              >
                <CalendarDays size={18} />
                Book a Mechanic
              </button>

            </div>

          )}

        </aside>

      </div>

      {/* BOOKING MODAL */}

      {bookingOpen && (
        <BookingModal
          diagnosis={diagnosis}
          onClose={() =>
            setBookingOpen(false)
          }
        />
      )}

    </div>
  );
}

function BookingModal({
  diagnosis,
  onClose,
}: BookingModalProps) {

  const [form, setForm] =
    useState<BookingForm>({
      name: "",
      phone: "",
      date: "",
      time: "",
      issue:
        diagnosis?.summary ||
        diagnosis?.service ||
        "",
    });

  const [loading, setLoading] =
    useState<boolean>(false);

  const handleBooking = async (
    e: FormEvent<HTMLFormElement>
  ): Promise<void> => {

    e.preventDefault();

    setLoading(true);

    try {

      // Convert frontend field names
      // to Django backend field names.

      const response =
        await createBooking({

          customer_name:
            form.name,

          phone:
            form.phone,

          preferred_date:
            form.date,

          preferred_time:
            form.time,

          problem_description:
            form.issue,

          diagnosis:
            diagnosis?.summary || "",

        });

      console.log(
        "BOOKING RESPONSE:",
        response.data
      );

      alert(
        `Booking created: ${
          response.data.booking?.id ||
          response.data.id ||
          response.data.booking_id ||
          "success"
        }`
      );

      onClose();

    } catch (error: any) {

      console.error(
        "BOOKING ERROR:",
        error
      );

      console.error(
        "STATUS:",
        error.response?.status
      );

      console.error(
        "DATA:",
        error.response?.data
      );

      alert(
        error.response?.data?.message ||
        "Booking failed."
      );

    } finally {

      setLoading(false);

    }
  };

  return (
    <div className="modal-overlay">

      <div className="modal">

        <h2>
          Book a Mechanic
        </h2>

        <form
          onSubmit={handleBooking}
        >

          <input
            required
            placeholder="Your name"
            value={form.name}
            onChange={(
              e: ChangeEvent<HTMLInputElement>
            ) =>
              setForm({
                ...form,
                name: e.target.value,
              })
            }
          />

          <input
            required
            placeholder="Phone number"
            value={form.phone}
            onChange={(
              e: ChangeEvent<HTMLInputElement>
            ) =>
              setForm({
                ...form,
                phone: e.target.value,
              })
            }
          />

          <input
            required
            type="date"
            value={form.date}
            onChange={(
              e: ChangeEvent<HTMLInputElement>
            ) =>
              setForm({
                ...form,
                date: e.target.value,
              })
            }
          />

          <input
            required
            type="time"
            value={form.time}
            onChange={(
              e: ChangeEvent<HTMLInputElement>
            ) =>
              setForm({
                ...form,
                time: e.target.value,
              })
            }
          />

          <textarea
            required
            placeholder="Describe the problem"
            value={form.issue}
            onChange={(
              e: ChangeEvent<HTMLTextAreaElement>
            ) =>
              setForm({
                ...form,
                issue: e.target.value,
              })
            }
          />

          <button
            disabled={loading}
            type="submit"
          >
            {loading
              ? "Booking..."
              : "Confirm Booking"}
          </button>

          <button
            type="button"
            onClick={onClose}
          >
            Cancel
          </button>

        </form>

      </div>

    </div>
  );
}

export default App;

