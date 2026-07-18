"use client"

import { useState } from "react"

export default function ImageUploader({

  onResult

}: any) {

  const [image, setImage] =
    useState<File | null>(null)

  const [loading, setLoading] =
    useState(false)

  const handleUpload = async () => {

    if (!image) return

    setLoading(true)

    const formData = new FormData()

    formData.append("file", image)

    try {

      const response = await fetch(

        "http://127.0.0.1:8000/analyze",

        {

          method: "POST",

          body: formData
        }
      )

      const data = await response.json()

      onResult(data)

    } catch (error) {

      console.error(error)
    }

    setLoading(false)
  }

  return (

    <div className="space-y-4">

      {/* FILE INPUT */}

      <input

        type="file"

        accept="image/*"

        className="
          block
          w-full
          text-sm
          text-gray-300
          file:mr-4
          file:py-2
          file:px-4
          file:rounded-xl
          file:border-0
          file:bg-[#00FFD1]
          file:text-black
          file:font-semibold
          cursor-pointer
        "

        onChange={(e) => {

          if (e.target.files) {

            setImage(
              e.target.files[0]
            )
          }
        }}
      />

      {/* BUTTON */}

      <button

        onClick={handleUpload}

        className="
          w-full
          px-4
          py-3
          bg-[#00FFD1]
          text-black
          rounded-xl
          font-semibold
          hover:opacity-90
          transition
        "

      >

        Analyze Composition

      </button>

      {/* LOADING */}

      {
        loading && (

          <div className="
            text-sm
            text-gray-400
          ">

            Running AI composition analysis...

          </div>
        )
      }

    </div>
  )
}