"use client"

import { useEffect, useRef, useState } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "")

export default function LiveCamera() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [error, setError] = useState("")
  const requestInFlight = useRef(false)

  useEffect(() => {
    let stream: MediaStream | null = null
    async function setupCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (videoRef.current) videoRef.current.srcObject = stream
      } catch (err) {
        console.error("Camera access error:", err)
        setError("Camera access was denied or is unavailable.")
      }
    }
    setupCamera()
    return () => stream?.getTracks().forEach((track) => track.stop())
  }, [])

  useEffect(() => {
    if (!API_URL) {
      setError("The analysis service is not configured yet.")
      return
    }

    const interval = setInterval(() => {
      if (!videoRef.current || !canvasRef.current || requestInFlight.current) return
      if (videoRef.current.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return

      const canvas = canvasRef.current
      const ctx = canvas.getContext("2d")
      if (!ctx) return

      canvas.width = 640
      canvas.height = 480
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)

      canvas.toBlob(async (blob) => {
        if (!blob) return
        requestInFlight.current = true
        const formData = new FormData()
        formData.append("file", blob, "frame.jpg")

        try {
          const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            body: formData,
          })
          const data = await response.json()
          if (!response.ok) throw new Error(data.detail || "Analysis request failed.")
          setAnalysis(data)
          setError("")
        } catch (err) {
          console.error("Backend error:", err)
          setError("Unable to reach the analysis service.")
        } finally {
          requestInFlight.current = false
        }
      }, "image/jpeg", 0.8)
    }, 2500)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-white/10 bg-black">
      <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
      <canvas ref={canvasRef} className="hidden" />
      {error && <div role="status" className="absolute top-3 left-3 z-10 rounded-lg bg-black/70 px-3 py-2 text-sm text-amber-300">{error}</div>}

      {analysis && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md rounded-xl p-4 text-white border border-white/10">
            <p>Thirds: {(analysis.thirds_score * 100).toFixed(0)}%</p>
            <p className="text-3xl font-bold text-[#00FFD1]">{(analysis.composition_score * 100).toFixed(0)}%</p>
            <p className="text-sm text-gray-300">Composition Score</p>
            <p className="mt-2">Balance: {(analysis.balance_score * 100).toFixed(0)}%</p>
            <p>Symmetry: {(analysis.symmetry_score * 100).toFixed(0)}%</p>
            <p>Tension: {(analysis.tension_score * 100).toFixed(0)}%</p>
          </div>

          <div className="absolute left-1/3 top-0 w-[1px] h-full bg-[#00FFD1]/40" />
          <div className="absolute left-2/3 top-0 w-[1px] h-full bg-[#00FFD1]/40" />
          <div className="absolute top-1/3 left-0 h-[1px] w-full bg-[#00FFD1]/40" />
          <div className="absolute top-2/3 left-0 h-[1px] w-full bg-[#00FFD1]/40" />

          {analysis.detections?.map((det: any, idx: number) => {
            const left = (det.x1 / 640) * 100
            const top = (det.y1 / 480) * 100
            const width = ((det.x2 - det.x1) / 640) * 100
            const height = ((det.y2 - det.y1) / 480) * 100
            const centerX = (det.cx / 640) * 100
            const centerY = (det.cy / 480) * 100

            return (
              <div key={idx}>
                <div className="absolute border-2 border-[#00FFD1] rounded-md" style={{ left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%` }} />
                <div className="absolute bg-[#00FFD1] text-black text-xs px-2 py-1 rounded-md font-semibold whitespace-nowrap" style={{ left: `${left}%`, top: `${Math.max(top - 5, 0)}%` }}>
                  {det.class} {(det.confidence * 100).toFixed(0)}%
                </div>
                <div className="absolute w-4 h-4 rounded-full bg-[#FF4D6D] border-2 border-white" style={{ left: `${centerX}%`, top: `${centerY}%`, transform: "translate(-50%, -50%)" }} />
              </div>
            )
          })}

          <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-md rounded-xl p-4 text-white max-w-sm border border-white/10">
            <h3 className="font-semibold mb-2">AI Feedback</h3>
            <ul className="text-sm space-y-1">
              {analysis.feedback?.map((item: string, idx: number) => <li key={idx}>• {item}</li>)}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
