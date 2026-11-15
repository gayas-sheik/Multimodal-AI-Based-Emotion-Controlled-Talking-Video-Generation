import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "SentioGaurdAI | Emotion-Controlled Talking-Head Generation",
    template: "%s | SentioGaurdAI",
  },
  description:
    "An academic research platform for multimodal, emotion-controlled talking-head video generation using facial images, speech audio, and FLOAT.",
  applicationName: "SentioGaurdAI",
  keywords: [
    "SentioGaurdAI",
    "emotion-controlled talking-head generation",
    "multimodal AI",
    "FLOAT",
    "ComfyUI",
  ],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f5f7fb",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
