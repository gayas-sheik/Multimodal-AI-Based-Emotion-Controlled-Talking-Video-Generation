import { useEffect, useRef, useState } from 'react'
import ConversationGenerator from './ConversationGenerator.jsx'

const API_URL = (import.meta.env.VITE_API_URL || 'https://sentioguard-gateway.gayassheik77.workers.dev').replace(/\/$/, '')
const EMOTIONS = ['none', 'angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

function readableError(error) {
  return error instanceof Error ? error.message : 'An unexpected error occurred.'
}

export default function App() {
  const [image, setImage] = useState(null)
  const [audio, setAudio] = useState(null)
  const [imageUrl, setImageUrl] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [emotion, setEmotion] = useState('none')
  const [strength, setStrength] = useState(1)
  const [backendOnline, setBackendOnline] = useState(false)
  const [checkingHealth, setCheckingHealth] = useState(true)
  const [mode, setMode] = useState('single')
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const imageInput = useRef(null)
  const audioInput = useRef(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`)
        setBackendOnline(response.ok)
      } catch {
        setBackendOnline(false)
      } finally {
        setCheckingHealth(false)
      }
    }
    checkHealth()
  }, [])

  useEffect(() => () => {
    if (imageUrl) URL.revokeObjectURL(imageUrl)
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    if (videoUrl) URL.revokeObjectURL(videoUrl)
  }, [imageUrl, audioUrl, videoUrl])

  const chooseImage = (file) => {
    setError('')
    if (!file) return
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setError('Please choose a JPG, JPEG, or PNG image.')
      return
    }
    if (imageUrl) URL.revokeObjectURL(imageUrl)
    setImage(file)
    setImageUrl(URL.createObjectURL(file))
  }

  const chooseAudio = (file) => {
    setError('')
    if (!file) return
    if (!file.type.startsWith('audio/') && !/\.(wav|mp3|flac|m4a|ogg)$/i.test(file.name)) {
      setError('Please choose a supported audio file: WAV, MP3, FLAC, M4A, or OGG.')
      return
    }
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    setAudio(file)
    setAudioUrl(URL.createObjectURL(file))
  }

  const generate = async (event) => {
    event.preventDefault()
    setError('')
    if (!image || !audio || !emotion) {
      setError('Select a reference image, an audio file, and an emotion before generating.')
      return
    }
    if (!backendOnline) {
      setError('Backend Offline. Start the FastAPI server and try again.')
      return
    }

    setGenerating(true)
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl)
      setVideoUrl(null)
    }
    try {
      const form = new FormData()
      form.append('image', image)
      form.append('audio', audio)
      form.append('emotion', emotion)
      form.append('emotion_strength', String(strength))
      const response = await fetch(`${API_URL}/generate`, { method: 'POST', body: form })
      if (!response.ok) {
        let detail = `Generation failed (${response.status}).`
        try { detail = (await response.json()).detail || detail } catch { /* non-JSON API error */ }
        throw new Error(detail)
      }
      const blob = await response.blob()
      if (!blob.size) throw new Error('The server returned an empty video file.')
      setVideoUrl(URL.createObjectURL(blob))
    } catch (requestError) {
      setError(readableError(requestError))
    } finally {
      setGenerating(false)
    }
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">F</div>
        <div>
          <p className="eyebrow">DIRECT FLOAT INFERENCE</p>
          <h1>FLOAT AI Talking Video Generator</h1>
        </div>
        <div className={`status ${backendOnline ? 'online' : 'offline'}`}>
          <span className="status-dot" />
          {checkingHealth ? 'Checking Backend...' : backendOnline ? 'Backend Connected' : 'Backend Offline'}
        </div>
      </header>

      <section className="intro">
        <p>{mode === 'single' ? 'Create a talking video from one portrait and one voice recording. FLOAT runs locally on your GPU.' : 'Create a two-person, three-turn talking conversation. FLOAT generates each turn locally, then composes one final scene.'}</p>
      </section>

      <nav className="mode-switcher" aria-label="Generator mode">
        <button className={mode === 'single' ? 'active' : ''} type="button" onClick={() => setMode('single')}>Single person</button>
        <button className={mode === 'conversation' ? 'active' : ''} type="button" onClick={() => setMode('conversation')}>Two-person conversation</button>
      </nav>

      {mode === 'single' ? <form className="workspace" onSubmit={generate}>
        <section className="card inputs-card">
          <div className="card-heading"><span>01</span><h2>Source files</h2></div>
          <div className="upload-grid">
            <div className="field-block">
              <label htmlFor="image-input">Reference image <em>JPG, JPEG, PNG</em></label>
              <input id="image-input" ref={imageInput} className="visually-hidden" type="file" accept="image/jpeg,image/png" onChange={(e) => chooseImage(e.target.files?.[0])} />
              <button className="upload-box image-box" type="button" onClick={() => imageInput.current?.click()}>
                {imageUrl ? <img src={imageUrl} alt="Selected reference" /> : <><b>Upload portrait</b><small>One clearly visible face</small></>}
              </button>
              <p className="file-name">{image ? image.name : 'No image selected'}</p>
            </div>
            <div className="field-block">
              <label htmlFor="audio-input">Driving audio <em>WAV, MP3, FLAC, M4A, OGG</em></label>
              <input id="audio-input" ref={audioInput} className="visually-hidden" type="file" accept="audio/wav,audio/mpeg,audio/flac,audio/mp4,audio/ogg,.wav,.mp3,.flac,.m4a,.ogg" onChange={(e) => chooseAudio(e.target.files?.[0])} />
              <button className="upload-box audio-box" type="button" onClick={() => audioInput.current?.click()}>
                <b>{audio ? 'Replace audio' : 'Upload audio'}</b><small>Speech drives lip movement and timing</small>
              </button>
              <p className="file-name">{audio ? audio.name : 'No audio selected'}</p>
              {audioUrl && <audio controls src={audioUrl} className="audio-preview">Your browser does not support audio preview.</audio>}
            </div>
          </div>
        </section>

        <section className="card controls-card">
          <div className="card-heading"><span>02</span><h2>Expression</h2></div>
          <div className="control-grid">
            <label className="select-field">Emotion
              <select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
                {EMOTIONS.map((item) => <option value={item} key={item}>{item[0].toUpperCase() + item.slice(1)}</option>)}
              </select>
            </label>
            <label className="range-field">Emotion strength <strong>{strength.toFixed(1)}</strong>
              <input type="range" min="1" max="4" step="0.1" value={strength} onChange={(e) => setStrength(Number(e.target.value))} />
              <span>1.0 subtle <i /> 4.0 strong</span>
            </label>
          </div>
          <button className="generate-button" type="submit" disabled={generating || !backendOnline}>
            {generating ? <><span className="spinner" /> Generating talking video...</> : 'Generate video'}
          </button>
          {error && <p className="error-message" role="alert">{error}</p>}
        </section>

        <section className="card output-card">
          <div className="card-heading"><span>03</span><h2>Generated video</h2></div>
          {videoUrl ? <div className="video-result"><video src={videoUrl} controls playsInline /><a className="download-button" href={videoUrl} download="float-talking-video.mp4">Download video</a></div> : <div className="empty-output">Your generated talking video will appear here.</div>}
        </section>
      </form> : <ConversationGenerator backendOnline={backendOnline} />}
    </main>
  )
}
