/** Exercises the React conversation form against the local FastAPI pipeline. */
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { chromium } from 'playwright-core'

const projectRoot = resolve(import.meta.dirname, '..', '..')
const imagePath = resolve(projectRoot, 'backend/test_data/download.jpg')
const audioPath = resolve(projectRoot, 'backend/test_data/03-01-02-02-02-01-01.wav')
const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'

if (!existsSync(imagePath) || !existsSync(audioPath)) throw new Error('Test media is missing from backend/test_data.')
if (!existsSync(edgePath)) throw new Error(`Microsoft Edge was not found at ${edgePath}`)

const browser = await chromium.launch({ executablePath: edgePath, headless: true })
try {
  const page = await browser.newPage()
  await page.goto('http://127.0.0.1:5173', { waitUntil: 'networkidle' })
  await page.getByRole('button', { name: 'Two-person conversation' }).click()
  await page.setInputFiles('#alice-image-input', imagePath)
  await page.setInputFiles('#bob-image-input', imagePath)
  await page.setInputFiles('#turn-1-audio-input', audioPath)
  await page.setInputFiles('#turn-2-audio-input', audioPath)
  await page.setInputFiles('#turn-3-audio-input', audioPath)
  await page.getByRole('button', { name: 'Generate conversation video' }).click()
  const video = page.locator('video')
  await video.waitFor({ state: 'attached', timeout: 900_000 })
  await page.waitForFunction(() => {
    const result = document.querySelector('video')
    return result && result.readyState >= 2 && result.currentSrc.startsWith('blob:') && result.duration > 0
  }, { timeout: 900_000 })
  const duration = await video.evaluate((element) => element.duration)
  console.log(`Conversation browser UI test succeeded: a playable MP4 Blob is displayed (${duration.toFixed(2)} seconds).`)
} finally {
  await browser.close()
}
