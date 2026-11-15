
"use client";

import { useEffect, useState } from "react";

const API_URL = "https://sentioguard-gateway.gayassheik77.workers.dev";

const navigation = [
  { name: "Dashboard", icon: "▦" },
  { name: "Generate Video", icon: "＋" },
  { name: "Generation History", icon: "◷" },
  { name: "About Project", icon: "ⓘ" },
];

type GenerationRecord = {
  id: string;
  emotion: string;
  intensity: number;
  date: string;
  videoUrl: string;
  imageName: string;
  audioName: string;
};

export default function Home() {
  const [darkMode, setDarkMode] = useState(false);
  const [activePage, setActivePage] = useState("Dashboard");
  const [history, setHistory] = useState<GenerationRecord[]>([]);

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("sentioguard-history");
      if (saved) {
        setHistory(JSON.parse(saved));
      }
    } catch {
      console.error("Could not load generation history.");
    }
  }, []);

  function saveGeneration(record: GenerationRecord) {
    setHistory((previous) => {
      const updated = [record, ...previous];
      localStorage.setItem("sentioguard-history", JSON.stringify(updated));
      return updated;
    });
  }

  function removeGeneration(id: string) {
    setHistory((previous) => {
      const updated = previous.filter((record) => record.id !== id);
      localStorage.setItem("sentioguard-history", JSON.stringify(updated));
      return updated;
    });
  }

  function clearHistory() {
    setHistory([]);
    localStorage.setItem("sentioguard-history", JSON.stringify([]));
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <h2>SentioGaurdAI</h2>
            <p>RESEARCH PLATFORM</p>
          </div>
        </div>

        <div className="nav-section">
          <p className="nav-heading">WORKSPACE</p>

          {navigation.map((item) => (
            <button
              key={item.name}
              onClick={() => setActivePage(item.name)}
              className={`nav-item ${
                activePage === item.name ? "active" : ""
              }`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="project-status">
            <span className="status-dot" />
            <div>
              <strong>System status</strong>
              <p>Research environment</p>
            </div>
          </div>
          <p className="sidebar-version">SentioGaurdAI · v1.0</p>
        </div>
      </aside>

      <section className="main-area">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Workspace / {activePage}</p>
            <h1>{activePage}</h1>
          </div>

          <div className="topbar-actions">
            <span className="environment-label">
              <span className="status-dot" />
              Research Environment
            </span>

            <button
              className="theme-button"
              onClick={() => setDarkMode(!darkMode)}
              aria-label="Toggle theme"
              title="Toggle light and dark theme"
            >
              {darkMode ? "☀" : "☾"}
            </button>
          </div>
        </header>

        {activePage === "Dashboard" && (
          <Dashboard
            setActivePage={setActivePage}
            history={history}
          />
        )}

        {activePage === "Generate Video" && (
          <GenerationStudio onSave={saveGeneration} />
        )}

        {activePage === "Generation History" && (
          <GenerationHistory
            history={history}
            onRemove={removeGeneration}
            onClear={clearHistory}
          />
        )}

        {activePage === "About Project" && <AboutProject />}

        <footer className="footer">
          <span>SentioGaurdAI</span>
          <span>Academic Research Project · 2026</span>
        </footer>
      </section>
    </main>
  );
}

/* DASHBOARD */

function Dashboard({
  setActivePage,
  history,
}: {
  setActivePage: (page: string) => void;
  history: GenerationRecord[];
}) {
  return (
    <div className="content">
      <section className="welcome-section">
        <div>
          <p className="eyebrow">FINAL YEAR PROJECT</p>
          <h2>Multimodal Emotion-Controlled Talking Video</h2>
          <p className="welcome-description">
            An AI-based research platform for generating emotionally
            expressive talking-head videos using facial images, speech
            audio, and user-selected emotions.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => setActivePage("Generate Video")}
        >
          + New Generation
        </button>
      </section>

      <section className="stats-grid">
        <StatCard
          label="Total Generations"
          value={String(history.length)}
          detail="Generated video sessions"
          icon="▤"
        />
        <StatCard
          label="Available Emotions"
          value="8"
          detail="FLOAT emotion options"
          icon="◎"
        />
        <StatCard
          label="Processing Engine"
          value="FLOAT"
          detail="ComfyUI workflow"
          icon="◈"
        />
        <StatCard
          label="System Status"
          value="Ready"
          detail="Local research environment"
          icon="✓"
        />
      </section>

      <section className="dashboard-grid">
        <div className="panel project-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">PROJECT OVERVIEW</p>
              <h3>About the research</h3>
            </div>
            <span className="panel-icon">◈</span>
          </div>

          <p className="panel-description">
            SentioGaurdAI explores emotion-controlled talking-head
            generation through multimodal AI. The system combines visual
            identity, speech input, and emotion conditioning to produce
            an expressive video output.
          </p>

          <div className="workflow">
            {[
              ["01", "Facial Image", "Reference face input"],
              ["02", "Speech Audio", "Dialogue and voice input"],
              ["03", "Emotion Control", "Selected emotional expression"],
              ["04", "Video Generation", "Emotion-conditioned output"],
            ].map(([number, title, description]) => (
              <div className="workflow-step" key={number}>
                <span className="step-number">{number}</span>
                <div>
                  <strong>{title}</strong>
                  <p>{description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="right-column">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">QUICK ACCESS</p>
                <h3>Generation studio</h3>
              </div>
            </div>

            <p className="panel-description">
              Start a new emotion-controlled talking-head generation.
            </p>

            <button
              className="secondary-button"
              onClick={() => setActivePage("Generate Video")}
            >
              Open generation studio →
            </button>
          </div>

          <div className="panel info-panel">
            <p className="eyebrow">RESEARCH MODULE</p>
            <h3>Multimodal processing</h3>
            <p className="panel-description">
              Facial reference, audio conditioning, and emotional
              expression generation.
            </p>
            <span className="module-tag">AI · COMPUTER VISION</span>
          </div>
        </div>
      </section>

      <section className="panel activity-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">ACTIVITY</p>
            <h3>Recent generations</h3>
          </div>
          <button
            className="text-button"
            onClick={() => setActivePage("Generation History")}
          >
            View history →
          </button>
        </div>

        {history.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">▤</div>
            <strong>No generation history yet</strong>
            <p>Your generated videos will appear here.</p>
          </div>
        ) : (
          <div className="workflow">
            {history.slice(0, 3).map((record) => (
              <div className="workflow-step" key={record.id}>
                <span className="step-number">✓</span>
                <div>
                  <strong>{record.emotion} generation</strong>
                  <p>{new Date(record.date).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

/* GENERATION STUDIO */

function GenerationStudio({
  onSave,
}: {
  onSave: (record: GenerationRecord) => void;
}) {
  const [image, setImage] = useState<File | null>(null);
  const [audio, setAudio] = useState<File | null>(null);
  const [emotion, setEmotion] = useState("happy");
  const [intensity, setIntensity] = useState(7);
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("idle");
  const [jobId, setJobId] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [imagePreview, setImagePreview] = useState("");
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const busy =
    status === "submitting" ||
    status === "queued" ||
    status === "processing";

  useEffect(() => {
    if (!image) {
      setImagePreview("");
      return;
    }

    const url = URL.createObjectURL(image);
    setImagePreview(url);

    return () => URL.revokeObjectURL(url);
  }, [image]);

  useEffect(() => {
    let cancelled = false;

    async function checkBackend() {
      try {
        const response = await fetch(`${API_URL}/api/health`);
        const data = await response.json();

        if (!cancelled) {
          setBackendOnline(
            response.ok &&
            data.backend === "online" &&
            data.comfyui === "online" &&
            data.workflow === true
          );
        }
      } catch {
        if (!cancelled) setBackendOnline(false);
      }
    }

    checkBackend();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleGenerate() {
    if (!image || !audio) {
      setMessage("Please upload both a facial image and speech audio.");
      return;
    }

    setMessage("");
    setVideoUrl("");
    setJobId("");
    setStatus("submitting");

    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("audio", audio);
      formData.append("emotion", emotion);
      formData.append("intensity", String(intensity));

      const response = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Could not submit generation.");
      }

      const id = result.job_id;

      if (!id) {
        throw new Error("Backend did not return a generation ID.");
      }

      setJobId(id);
      setStatus("queued");
      setMessage("Your generation has been submitted to FLOAT.");

      // Poll the backend until FLOAT finishes or reports an error.
      const maximumAttempts = 1800;

      for (let attempt = 0; attempt < maximumAttempts; attempt++) {
        await new Promise((resolve) => setTimeout(resolve, 3000));

        const statusResponse = await fetch(
          `${API_URL}/api/generate/${id}`,
          { cache: "no-store" }
        );

        const statusResult = await statusResponse.json();

        if (!statusResponse.ok) {
          throw new Error(
            statusResult.detail || "Could not retrieve generation status."
          );
        }

        if (statusResult.status === "completed") {
          const completedVideoUrl = `${API_URL}${statusResult.video_url}`;

          setVideoUrl(completedVideoUrl);
          setStatus("completed");
          setMessage("Your talking-head video has been generated successfully.");

          onSave({
            id,
            emotion,
            intensity,
            date: new Date().toISOString(),
            videoUrl: completedVideoUrl,
            imageName: image.name,
            audioName: audio.name,
          });

          return;
        }

        if (statusResult.status === "failed") {
          throw new Error(
            statusResult.error || "FLOAT generation failed."
          );
        }

        if (
          statusResult.status === "processing" ||
          statusResult.status === "queued"
        ) {
          setStatus(statusResult.status);
          setMessage(
            statusResult.status === "processing"
              ? "FLOAT is generating your video. Please wait..."
              : "Your request is waiting in the ComfyUI queue..."
          );
        }
      }

      throw new Error(
        "Generation is taking longer than expected. Check ComfyUI before submitting another request."
      );
    } catch (error) {
      setStatus("failed");
      setMessage(
        error instanceof Error
          ? error.message
          : "An unexpected error occurred."
      );
    }
  }

  return (
    <div className="content">
      <div className="page-intro">
        <p className="eyebrow">GENERATION WORKSPACE</p>
        <h2>Emotion-controlled video generation</h2>
        <p>
          Configure your reference image, speech audio and desired emotion.
        </p>
      </div>

      <div className="studio-layout">
        <div className="studio-form">
          <section className="panel studio-panel">
            <div className="studio-section-heading">
              <span className="studio-step">01</span>
              <div>
                <h3>Reference facial image</h3>
                <p>Upload the face image used for video generation.</p>
              </div>
            </div>

            <label className="upload-area">
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                disabled={busy}
                onChange={(e) => {
                  setImage(e.target.files?.[0] ?? null);
                  setMessage("");
                }}
              />

              {imagePreview ? (
                <img
                  src={imagePreview}
                  alt="Selected facial reference"
                  className="image-preview"
                />
              ) : (
                <span className="upload-icon">▧</span>
              )}

              <strong>
                {image ? image.name : "Choose a facial image"}
              </strong>

              <span>
                {image
                  ? `${(image.size / 1024 / 1024).toFixed(2)} MB`
                  : "PNG, JPG or WEBP"}
              </span>

              <span className="upload-link">
                {image ? "Choose another image" : "Browse files"}
              </span>
            </label>
          </section>

          <section className="panel studio-panel">
            <div className="studio-section-heading">
              <span className="studio-step">02</span>
              <div>
                <h3>Speech audio</h3>
                <p>Upload the dialogue or speech audio.</p>
              </div>
            </div>

            <label className="upload-area">
              <input
                type="file"
                accept=".wav,.mp3,.m4a,.flac,.ogg,audio/*"
                disabled={busy}
                onChange={(e) => {
                  setAudio(e.target.files?.[0] ?? null);
                  setMessage("");
                }}
              />

              <span className="upload-icon">♫</span>
              <strong>
                {audio ? audio.name : "Choose speech audio"}
              </strong>
              <span>
                {audio
                  ? `${(audio.size / 1024 / 1024).toFixed(2)} MB`
                  : "WAV, MP3, M4A, FLAC or OGG"}
              </span>
              <span className="upload-link">
                {audio ? "Choose another audio file" : "Browse files"}
              </span>
            </label>
          </section>

          <section className="panel studio-panel">
            <div className="studio-section-heading">
              <span className="studio-step">03</span>
              <div>
                <h3>Emotion configuration</h3>
                <p>
                  Select the emotional expression for the generated video.
                </p>
              </div>
            </div>

            <label className="field-label" htmlFor="emotion">
              Desired emotion
            </label>

            <select
              id="emotion"
              className="studio-select"
              value={emotion}
              disabled={busy}
              onChange={(e) => setEmotion(e.target.value)}
            >
              <option value="none">None (Audio-driven)</option>
              <option value="angry">Angry</option>
              <option value="disgust">Disgust</option>
              <option value="fear">Fear</option>
              <option value="happy">Happy</option>
              <option value="neutral">Neutral</option>
              <option value="sad">Sad</option>
              <option value="surprise">Surprise</option>
            </select>

            <div className="intensity-heading">
              <label className="field-label" htmlFor="intensity">
                Emotion intensity
              </label>
              <strong>{intensity}/10</strong>
            </div>

            <input
              id="intensity"
              className="intensity-slider"
              type="range"
              min="1"
              max="10"
              value={intensity}
              disabled={busy || emotion === "none"}
              onChange={(e) => setIntensity(Number(e.target.value))}
            />

            <div className="slider-labels">
              <span>Subtle</span>
              <span>Strong</span>
            </div>
          </section>

          <section className="panel studio-panel">
            <div className="studio-section-heading">
              <span className="studio-step">04</span>
              <div>
                <h3>Generation settings</h3>
                <p>Default FLOAT workflow configuration.</p>
              </div>
            </div>

            <div className="settings-grid">
              <Setting label="Generation engine" value="FLOAT" />
              <Setting label="Processing framework" value="ComfyUI" />
              <Setting label="Output frame rate" value="25 FPS" />
              <Setting label="Audio guidance" value="2.0" />
              <Setting label="Reference guidance" value="1.0" />
              <Setting label="Reference crop" value="Enabled" />
            </div>
          </section>

          <button
            className="primary-button generate-button"
            disabled={!image || !audio || busy || backendOnline === false}
            onClick={handleGenerate}
          >
            {status === "submitting"
              ? "Submitting request..."
              : status === "queued"
                ? "Waiting in queue..."
                : status === "processing"
                  ? "Generating video..."
                  : status === "completed"
                    ? "Generate Another Video →"
                    : "Generate Talking-Head Video →"}
          </button>

          {backendOnline === false && (
            <p className="generation-message">
              Backend or ComfyUI is unavailable. Start both services and refresh this page.
            </p>
          )}

          {backendOnline === true && (
            <p className="form-hint">
              Backend and ComfyUI are connected.
            </p>
          )}

          {message && (
            <p className="generation-message" role="status">
              {message}
            </p>
          )}

          {jobId && (
            <p className="form-hint">
              Generation ID: {jobId}
            </p>
          )}

          {(!image || !audio) && (
            <p className="form-hint">
              Upload both a facial image and speech audio to continue.
            </p>
          )}
        </div>

        <aside className="studio-output">
          <section className="panel output-panel">
            <p className="eyebrow">GENERATION OUTPUT</p>
            <h3>Video preview</h3>

            {videoUrl ? (
              <div>
                <video
                  key={videoUrl}
                  controls
                  playsInline
                  preload="metadata"
                  style={{
                    width: "100%",
                    borderRadius: "12px",
                    background: "#000",
                    marginTop: "16px",
                  }}
                >
                  <source src={videoUrl} type="video/mp4" />
                  Your browser does not support video playback.
                </video>

                <a
                  href={videoUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="secondary-button"
                  style={{
                    display: "inline-block",
                    marginTop: "14px",
                    textDecoration: "none",
                  }}
                >
                  Open generated video →
                </a>
              </div>
            ) : (
              <div className="video-placeholder">
                <span className="video-placeholder-icon">
                  {busy ? "◌" : "▶"}
                </span>
                <strong>
                  {busy ? "Generation in progress" : "Preview will appear here"}
                </strong>
                <p>
                  {busy
                    ? "FLOAT is processing your inputs. Keep this page open."
                    : "Your generated video will be displayed in this area."}
                </p>
              </div>
            )}

            <div className="output-details">
              <div>
                <span>Selected emotion</span>
                <strong>{emotion}</strong>
              </div>
              <div>
                <span>Emotion intensity</span>
                <strong>{emotion === "none" ? "Not applicable" : `${intensity}/10`}</strong>
              </div>
              <div>
                <span>Generation status</span>
                <strong
                  className={
                    status === "completed"
                      ? "status-complete"
                      : status === "failed"
                        ? "status-pending"
                        : "status-pending"
                  }
                >
                  {status === "idle"
                    ? "Ready"
                    : status.charAt(0).toUpperCase() + status.slice(1)}
                </strong>
              </div>
            </div>
          </section>

          <section className="panel output-panel">
            <p className="eyebrow">INPUT SUMMARY</p>
            <h3>Uploaded files</h3>

            <div className="file-summary">
              <span>▧</span>
              <div>
                <strong>Facial image</strong>
                <p>{image ? image.name : "No image selected"}</p>
              </div>
            </div>

            <div className="file-summary">
              <span>♫</span>
              <div>
                <strong>Speech audio</strong>
                <p>{audio ? audio.name : "No audio selected"}</p>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

/* GENERATION HISTORY */

function GenerationHistory({
  history,
  onRemove,
  onClear,
}: {
  history: GenerationRecord[];
  onRemove: (id: string) => void;
  onClear: () => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [emotionFilter, setEmotionFilter] = useState("all");

  const filteredHistory = history.filter((record) => {
    const searchable = [
      record.emotion,
      record.imageName,
      record.audioName,
      new Date(record.date).toLocaleString(),
    ].join(" ").toLowerCase();

    return searchable.includes(searchTerm.toLowerCase()) &&
      (emotionFilter === "all" || record.emotion === emotionFilter);
  });

  const formatDate = (value: string) =>
    new Date(value).toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });

  return (
    <div className="content history-page">
      <div className="page-intro history-intro">
        <div>
          <p className="eyebrow">OUTPUT MANAGEMENT</p>
          <h2>Generation history</h2>
          <p>Browse, review and open videos generated in this browser.</p>
        </div>
        <div className="history-total">
          <span className="history-total-value">{history.length}</span>
          <span className="history-total-label">Saved outputs</span>
        </div>
      </div>

      <section className="history-summary-grid">
        <div className="history-summary-card">
          <span className="history-summary-icon">▣</span>
          <div><span className="history-summary-label">Total outputs</span><strong>{history.length}</strong></div>
        </div>
        <div className="history-summary-card">
          <span className="history-summary-icon">✓</span>
          <div><span className="history-summary-label">Completed</span><strong>{history.length}</strong></div>
        </div>
        <div className="history-summary-card">
          <span className="history-summary-icon">◎</span>
          <div><span className="history-summary-label">Emotion types used</span><strong>{new Set(history.map((item) => item.emotion)).size}</strong></div>
        </div>
      </section>

      <section className="panel history-panel">
        <div className="history-toolbar">
          <div>
            <p className="eyebrow">YOUR LIBRARY</p>
            <h3>Generated videos</h3>
            <p className="history-subtitle">{filteredHistory.length} of {history.length} records shown</p>
          </div>
          {history.length > 0 && (
            <button
              type="button"
              className="history-clear-button"
              onClick={() => {
                if (window.confirm("Clear all saved generation records from this browser?")) onClear();
              }}
            >
              Clear history
            </button>
          )}
        </div>

        {history.length > 0 && (
          <div className="history-filters">
            <label className="history-search">
              <span aria-hidden="true">⌕</span>
              <input
                type="search"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search by emotion or file name"
                aria-label="Search generation history"
              />
            </label>
            <select
              className="history-filter-select"
              value={emotionFilter}
              onChange={(event) => setEmotionFilter(event.target.value)}
              aria-label="Filter by emotion"
            >
              <option value="all">All emotions</option>
              {[...new Set(history.map((item) => item.emotion))].sort().map((emotion) => (
                <option key={emotion} value={emotion}>{emotion.charAt(0).toUpperCase() + emotion.slice(1)}</option>
              ))}
            </select>
          </div>
        )}

        {history.length === 0 ? (
          <div className="history-empty-state">
            <span className="history-empty-icon">◷</span>
            <h3>No generations yet</h3>
            <p>Videos you generate will appear here with their emotion, input files and creation date.</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="history-empty-state compact">
            <h3>No matching records</h3>
            <p>Try a different search term or emotion filter.</p>
            <button type="button" className="text-button" onClick={() => { setSearchTerm(""); setEmotionFilter("all"); }}>
              Reset filters
            </button>
          </div>
        ) : (
          <div className="history-list">
            {filteredHistory.map((record, index) => (
              <article className="history-record" key={record.id}>
                <div className="history-record-index">{String(index + 1).padStart(2, "0")}</div>
                <div className="history-record-main">
                  <div className="history-record-heading">
                    <div>
                      <h4>
                        {record.emotion.charAt(0).toUpperCase() + record.emotion.slice(1)}
                        <span className="history-intensity">Intensity {record.intensity}/10</span>
                      </h4>
                      <p className="history-date">{formatDate(record.date)}</p>
                    </div>
                    <span className="history-complete-badge"><span /> Completed</span>
                  </div>

                  <div className="history-file-grid">
                    <div className="history-file">
                      <span className="history-file-icon">▧</span>
                      <div><span>Reference image</span><strong title={record.imageName}>{record.imageName}</strong></div>
                    </div>
                    <div className="history-file">
                      <span className="history-file-icon">♫</span>
                      <div><span>Speech audio</span><strong title={record.audioName}>{record.audioName}</strong></div>
                    </div>
                  </div>

                  <div className="history-record-actions">
                    <a href={record.videoUrl} target="_blank" rel="noreferrer" className="history-open-button">
                      <span>▶</span> Open video
                    </a>
                    <button type="button" className="history-remove-button" onClick={() => onRemove(record.id)}>
                      Remove record
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}

        <p className="history-footnote">
          History records are stored in this browser, not the video files themselves.
          A video may become unavailable if its source file is no longer present on the backend.
        </p>
      </section>
    </div>
  );
}

/* ABOUT PROJECT */

function AboutProject() {
  return (
    <div className="content">
      <div className="page-intro">
        <p className="eyebrow">PROJECT INFORMATION</p>
        <h2>About SentioGaurdAI</h2>
        <p>Research overview and system information.</p>
      </div>

      <div className="panel">
        <h3>Research objective</h3>
        <p className="panel-description">
          To develop a multimodal AI system that generates talking-head
          videos from a reference facial image and speech audio,
          conditioned on a selected emotion.
        </p>

        <div className="about-details">
          <Detail label="Project domain" value="Image Analysis and Pattern Recognition" />
          <Detail label="Generation framework" value="ComfyUI + FLOAT" />
          <Detail label="Frontend" value="Next.js + React + TypeScript" />
          <Detail label="Backend" value="Python + FastAPI" />
        </div>
      </div>
    </div>
  );
}

/* REUSABLE COMPONENTS */

function StatCard({
  label,
  value,
  detail,
  icon,
}: {
  label: string;
  value: string;
  detail: string;
  icon: string;
}) {
  return (
    <div className="panel stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <span className="stat-icon">{icon}</span>
      </div>
      <h3>{value}</h3>
      <p>{detail}</p>
    </div>
  );
}

function Setting({ label, value }: { label: string; value: string }) {
  return (
    <div className="setting-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
