import { useEffect, useRef, useState } from 'react'

const API_URL = (import.meta.env.VITE_API_URL || 'https://sentioguard-gateway.gayassheik77.workers.dev').replace(/\/$/, '')
const EMOTIONS = ['none', 'angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
const INITIAL_TURNS = [
  { character: 'alice', dialogue: 'Hello Bob, how are you?', emotion: 'happy', strength: 1, duration: 3, audio: null, audioUrl: null },
  { character: 'bob', dialogue: "I'm fine, Alice. How are you?", emotion: 'neutral', strength: 1, duration: 3, audio: null, audioUrl: null },
  { character: 'alice', dialogue: "I'm doing great!", emotion: 'happy', strength: 1, duration: 2, audio: null, audioUrl: null },
]

function isSupportedImage(file) {
  return file && (['image/jpeg', 'image/png'].includes(file.type) || /\.(jpe?g|png)$/i.test(file.name))
}

function isSupportedAudio(file) {
  return file && (file.type.startsWith('audio/') || /\.(wav|mp3|flac|m4a|ogg)$/i.test(file.name))
}

function readableError(error) {
  return error instanceof Error ? error.message : 'An unexpected error occurred.'
}

function CharacterCard({ characterId, character, onNameChange, onImageChange }) {
  const input = useRef(null)
  const label = characterId === 'alice' ? 'Alice' : 'Bob'

  return (
    <section className="character-card">
      <div className="character-card-heading"><span>{characterId === 'alice' ? 'A' : 'B'}</span><h3>{label}</h3></div>
      <label className="name-field">Display name
        <input value={character.name} maxLength="80" onChange={(event) => onNameChange(event.target.value)} placeholder={label} />
      </label>
      <label className="visually-hidden" htmlFor={`${characterId}-image-input`}>{label} reference image</label>
      <input id={`${characterId}-image-input`} ref={input} className="visually-hidden" type="file" accept="image/jpeg,image/png,.jpg,.jpeg,.png" onChange={(event) => onImageChange(event.target.files?.[0])} />
      <button className="character-image-picker" type="button" onClick={() => input.current?.click()}>
        {character.imageUrl ? <img src={character.imageUrl} alt={`${character.name || label} reference`} /> : <><b>Upload portrait</b><small>JPG, JPEG, or PNG</small></>}
      </button>
      <p className="file-name">{character.image ? character.image.name : 'No image selected'}</p>
    </section>
  )
}

function TurnCard({ index, turn, characterNames, onChange, onAudioChange }) {
  const audioInput = useRef(null)
  const characterName = characterNames[turn.character] || turn.character

  return (
    <section className="turn-card">
      <div className="turn-heading"><span>TURN {index + 1}</span><strong>{characterName}</strong></div>
      <div className="turn-grid">
        <label>Speaker
          <select value={turn.character} onChange={(event) => onChange('character', event.target.value)}>
            <option value="alice">{characterNames.alice || 'Alice'}</option>
            <option value="bob">{characterNames.bob || 'Bob'}</option>
          </select>
        </label>
        <label>Duration <em>seconds</em>
          <input type="number" min="0.1" step="0.1" value={turn.duration} onChange={(event) => onChange('duration', event.target.value)} />
        </label>
        <label className="turn-dialogue">Dialogue
          <textarea value={turn.dialogue} maxLength="1000" rows="3" onChange={(event) => onChange('dialogue', event.target.value)} placeholder="Enter this turn's dialogue" />
        </label>
        <label>Emotion
          <select value={turn.emotion} onChange={(event) => onChange('emotion', event.target.value)}>
            {EMOTIONS.map((emotion) => <option key={emotion} value={emotion}>{emotion[0].toUpperCase() + emotion.slice(1)}</option>)}
          </select>
        </label>
        <label className="turn-strength">Emotion strength <strong>{Number(turn.strength).toFixed(1)}</strong>
          <input type="range" min="1" max="4" step="0.1" value={turn.strength} onChange={(event) => onChange('strength', Number(event.target.value))} />
        </label>
      </div>
      <div className="turn-audio">
        <input id={`turn-${index + 1}-audio-input`} ref={audioInput} className="visually-hidden" type="file" accept="audio/wav,audio/mpeg,audio/flac,audio/mp4,audio/ogg,.wav,.mp3,.flac,.m4a,.ogg" onChange={(event) => onAudioChange(event.target.files?.[0])} />
        <button className="compact-upload" type="button" onClick={() => audioInput.current?.click()}>{turn.audio ? 'Replace audio' : 'Upload turn audio'}</button>
        <span className="file-name">{turn.audio ? turn.audio.name : 'No audio selected'}</span>
        {turn.audioUrl && <audio controls src={turn.audioUrl}>Your browser does not support audio preview.</audio>}
      </div>
    </section>
  )
}

export default function ConversationGenerator({ backendOnline }) {
  const [characters, setCharacters] = useState({
    alice: { name: 'Alice', image: null, imageUrl: null },
    bob: { name: 'Bob', image: null, imageUrl: null },
  })
  const [turns, setTurns] = useState(INITIAL_TURNS)
  const [videoUrl, setVideoUrl] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const objectUrls = useRef(new Set())

  useEffect(() => () => objectUrls.current.forEach((url) => URL.revokeObjectURL(url)), [])

  const makeObjectUrl = (file) => {
    const url = URL.createObjectURL(file)
    objectUrls.current.add(url)
    return url
  }

  const releaseObjectUrl = (url) => {
    if (!url) return
    URL.revokeObjectURL(url)
    objectUrls.current.delete(url)
  }

  const chooseImage = (characterId, file) => {
    setError('')
    if (!file) return
    if (!isSupportedImage(file)) {
      setError('Character images must be JPG, JPEG, or PNG files.')
      return
    }
    setCharacters((previous) => {
      const current = previous[characterId]
      releaseObjectUrl(current.imageUrl)
      return { ...previous, [characterId]: { ...current, image: file, imageUrl: makeObjectUrl(file) } }
    })
  }

  const chooseAudio = (index, file) => {
    setError('')
    if (!file) return
    if (!isSupportedAudio(file)) {
      setError('Turn audio must be WAV, MP3, FLAC, M4A, or OGG.')
      return
    }
    setTurns((previous) => previous.map((turn, turnIndex) => {
      if (turnIndex !== index) return turn
      releaseObjectUrl(turn.audioUrl)
      return { ...turn, audio: file, audioUrl: makeObjectUrl(file) }
    }))
  }

  const updateTurn = (index, field, value) => setTurns((previous) => previous.map((turn, turnIndex) => turnIndex === index ? { ...turn, [field]: value } : turn))
  const totalDuration = turns.reduce((total, turn) => total + (Number(turn.duration) || 0), 0)

  const generateConversation = async (event) => {
    event.preventDefault()
    setError('')
    if (!backendOnline) return setError('Backend Offline. Start the FastAPI server and try again.')
    if (!characters.alice.name.trim() || !characters.bob.name.trim()) return setError('Enter names for both characters.')
    if (!characters.alice.image || !characters.bob.image) return setError('Upload one reference image for Alice and one for Bob.')
    for (const [index, turn] of turns.entries()) {
      if (!turn.dialogue.trim()) return setError(`Enter dialogue for turn ${index + 1}.`)
      if (!turn.audio) return setError(`Upload audio for turn ${index + 1}.`)
      if (!(Number(turn.duration) > 0)) return setError(`Turn ${index + 1} duration must be greater than zero.`)
    }

    setGenerating(true)
    if (videoUrl) {
      releaseObjectUrl(videoUrl)
      setVideoUrl(null)
    }
    try {
      const form = new FormData()
      form.append('image_alice', characters.alice.image)
      form.append('image_bob', characters.bob.image)
      form.append('alice_name', characters.alice.name.trim())
      form.append('bob_name', characters.bob.name.trim())
      turns.forEach((turn, index) => {
        const number = index + 1
        form.append(`audio_turn_${number}`, turn.audio)
        form.append(`turn_${number}_character`, turn.character)
        form.append(`turn_${number}_dialogue`, turn.dialogue.trim())
        form.append(`turn_${number}_emotion`, turn.emotion)
        form.append(`turn_${number}_emotion_strength`, String(turn.strength))
        form.append(`turn_${number}_duration`, String(turn.duration))
      })
      const response = await fetch(`${API_URL}/generate-conversation`, { method: 'POST', body: form })
      if (!response.ok) {
        let detail = `Conversation generation failed (${response.status}).`
        try { detail = (await response.json()).detail || detail } catch { /* non-JSON API error */ }
        throw new Error(detail)
      }
      const blob = await response.blob()
      if (!blob.size) throw new Error('The server returned an empty conversation video.')
      setVideoUrl(makeObjectUrl(blob))
    } catch (requestError) {
      setError(readableError(requestError))
    } finally {
      setGenerating(false)
    }
  }

  return (
    <form className="workspace conversation-workspace" onSubmit={generateConversation}>
      <section className="card">
        <div className="card-heading"><span>01</span><h2>Characters</h2></div>
        <p className="card-intro">Add one reference portrait for each person. They stay visible side-by-side in the final conversation.</p>
        <div className="character-grid">
          <CharacterCard characterId="alice" character={characters.alice} onNameChange={(name) => setCharacters((previous) => ({ ...previous, alice: { ...previous.alice, name } }))} onImageChange={(file) => chooseImage('alice', file)} />
          <CharacterCard characterId="bob" character={characters.bob} onNameChange={(name) => setCharacters((previous) => ({ ...previous, bob: { ...previous.bob, name } }))} onImageChange={(file) => chooseImage('bob', file)} />
        </div>
      </section>

      <section className="card">
        <div className="card-heading conversation-heading"><span>02</span><h2>Conversation timeline</h2><b>{totalDuration.toFixed(1)} seconds total</b></div>
        <p className="card-intro">Three turns are generated one after another. Only the active speaker's audio plays in each segment.</p>
        <div className="turn-list">
          {turns.map((turn, index) => <TurnCard key={index} index={index} turn={turn} characterNames={{ alice: characters.alice.name, bob: characters.bob.name }} onChange={(field, value) => updateTurn(index, field, value)} onAudioChange={(file) => chooseAudio(index, file)} />)}
        </div>
        <button className="generate-button" type="submit" disabled={generating || !backendOnline}>
          {generating ? <><span className="spinner" /> Generating conversation video...</> : 'Generate conversation video'}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
      </section>

      <section className="card output-card">
        <div className="card-heading"><span>03</span><h2>Conversation video</h2></div>
        {videoUrl ? <div className="video-result"><video src={videoUrl} controls playsInline /><a className="download-button" href={videoUrl} download="float-conversation.mp4">Download conversation video</a></div> : <div className="empty-output">Your two-person conversation video will appear here.</div>}
      </section>
    </form>
  )
}
