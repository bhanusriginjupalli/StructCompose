export default function Panel({

  title,
  children

}: any) {

  return (

    <div className="
      bg-white/5
      backdrop-blur-xl
      border border-white/10
      rounded-2xl
      p-4
      shadow-xl
    ">

      <h2 className="
        text-xl
        font-semibold
        mb-4
      ">

        {title}

      </h2>

      {children}

    </div>
  )
}
