"use client"

import { useState } from "react"

import Panel from "@/components/Panel"
import Metric from "@/components/Metric"
import LiveFeed from "@/components/LiveFeed"
import ImageUploader from "@/components/ImageUploader"
import LiveCamera from "@/components/LiveCamera"

export default function Dashboard() {

  const [analysis, setAnalysis] =
    useState<any>(null)

  return (

    <main className="
      min-h-screen
      bg-[#0B0F19]
      text-white
      p-6
    ">

      {/* HEADER */}

      <div>

        <h1 className="
          text-4xl
          font-bold
        ">

          StructCompose

        </h1>

        <p className="
          text-gray-400
          mt-2
        ">

          AI Cinematic Composition Intelligence

        </p>

      </div>

      {/* MAIN GRID */}

      <div className="
        grid
        grid-cols-12
        gap-4
        mt-6
      ">

        {/* LEFT SIDE */}

        <div className="
          col-span-8
          space-y-4
        ">

          {/* LIVE VIEWFINDER */}

          <Panel title="Live Viewfinder">

            <LiveCamera />

          </Panel>

        </div>

        {/* RIGHT SIDE */}

        <div className="
          col-span-4
          space-y-4
        ">

          {/* METRICS */}

          <Panel title="Composition Metrics">

            <div className="space-y-4">

              <Metric
                label="Balance"
                value={
                  analysis?.balance_score || 0
                }
              />

              <Metric
                label="Tension"
                value={
                  analysis?.tension_score || 0
                }
              />

              <Metric
                label="Symmetry"
                value={
                  analysis?.symmetry_score || 0
                }
              />

            </div>

          </Panel>

          {/* IMAGE ANALYSIS */}

          <Panel title="AI Composition Analysis">

            <ImageUploader
              onResult={setAnalysis}
            />

          </Panel>

          {/* COMPOSITION SCORE */}

          {
            analysis && (

              <Panel title="Composition Score">

                <div className="
                  flex
                  items-center
                  justify-center
                  py-6
                ">

                  <div className="
                    text-5xl
                    font-bold
                    text-[#00FFD1]
                  ">

                    {(
                      analysis.composition_score
                      * 100
                    ).toFixed(0)}%

                  </div>

                </div>

              </Panel>
            )
          }

          {/* AI FEEDBACK */}

          {
            analysis && (

              <Panel title="AI Feedback">

                <ul className="
                  space-y-3
                  text-gray-300
                ">

                  {
                    analysis.feedback.map(

                      (
                        item: string,
                        idx: number
                      ) => (

                        <li
                          key={idx}
                          className="
                            bg-white/5
                            p-3
                            rounded-xl
                          "
                        >

                          • {item}

                        </li>
                      )
                    )
                  }

                </ul>

              </Panel>
            )
          }

        </div>

      </div>

    </main>
  )
}