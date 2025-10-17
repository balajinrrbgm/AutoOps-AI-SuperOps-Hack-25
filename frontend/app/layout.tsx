import React from 'react'
import './globals.css'

export const metadata = {
  title: 'AutoOps AI - Agentic AI-Powered IT Operations',
  description: 'Intelligent IT operations automation platform powered by AI agents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}