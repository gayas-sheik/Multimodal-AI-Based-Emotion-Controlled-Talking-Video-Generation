/** Runs the actual React form in local Microsoft Edge against FastAPI/FLOAT. */
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
  await page.setInputFiles('#image-input', imagePath)
  await page.setInputFiles('#audio-input', audioPath)
  await page.selectOption('select', 'happy')
  await page.locator('input[type=range]').fill('1')
  await page.getByRole('button', { name: 'Generate video' }).click()
  const video = page.locator('video')
  await video.waitFor({ state: 'attached', timeout: 480_000 })
  await page.waitForFunction(() => {
    const result = document.querySelector('video')
    return result && result.readyState >= 2 && result.currentSrc.startsWith('blob:') && result.duration > 0
  }, { timeout: 480_000 })
  const duration = await video.evaluate((element) => element.duration)
  console.log(`Browser UI test succeeded: a playable FLOAT video Blob is displayed (${duration.toFixed(2)} seconds).`)
} finally {
  await browser.close()
}
