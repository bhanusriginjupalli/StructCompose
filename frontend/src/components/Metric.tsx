export default function Metric({

  label,
  value

}: any) {

  return (

    <div>

      <div className="
        flex
        justify-between
        mb-1
      ">

        <span>{label}</span>

        <span>
          {(value * 100).toFixed(0)}%
        </span>

      </div>

      <div className="
        w-full
        h-2
        bg-white/10
        rounded-full
      ">

        <div

          className="
            h-full
            bg-[#00FFD1]
            rounded-full
          "

          style={{
            width: `${value*100}%`
          }}
        />

      </div>

    </div>
  )
}