import Image from 'next/image'

export default function Logo() {
  return (
    <>
      <div className="mt-2 flex items-end justify-center">
        <Image src="/images/twinsight_logo.svg" width={30} height={26} alt="TwInsight Logo" />
        <div className="ml-1 text-xl leading-4 font-bold tracking-wider text-white">
          Tw<span className="text-brand-500">Insight</span>
        </div>
      </div>
      <span className="mt-1 text-xs">台灣股市分析</span>
    </>
  )
}
