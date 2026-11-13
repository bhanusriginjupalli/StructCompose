"use client"

import { useState } from "react"

const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "")

export default function ImageUploader({ onResult }: any) {
  const [image, setImage] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleUpload = async () => {
    if (!image) return
    if (!API_URL) {
      setError("The analysis service is not configured yet.")
      return
    }

    setLoading(true)
    setError("")
    const formData = new FormData()
    formData.append("file", image)

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || "Analysis request failed.")
      onResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the analysis service.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <input
        type="file"
        accept="image/*"
        className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-[#00FFD1] file:text-black file:font-semibold cursor-pointer"
        onChange={(e) => setImage(e.target.files?.[0] ?? null)}
      />
      <button
        onClick={handleUpload}
        disabled={!image || loading}
        className="w-full px-4 py-3 bg-[#00FFD1] text-black rounded-xl font-semibold hover:opacity-90 transition disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze Composition"}
      </button>
      {loading && <div className="text-sm text-gray-400">Running AI composition analysis...</div>}
      {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
    </div>
  )
}
