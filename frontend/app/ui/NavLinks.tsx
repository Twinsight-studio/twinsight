'use client'

import { cn } from '@/lib/utils'
import { ChartPieIcon, CpuChipIcon, PresentationChartLineIcon, StarIcon } from '@heroicons/react/24/outline'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { name: '市場看板', href: '/dashboard', icon: PresentationChartLineIcon },
  { name: '籌碼追蹤', href: '/chips', icon: ChartPieIcon },
  { name: '智能選股', href: '/screener', icon: CpuChipIcon },
  { name: '自選股', href: '/watchlist', icon: StarIcon },
]

export default function NavLinks({ callback }: { callback: () => void }) {
  const pathname = usePathname()

  return (
    <>
      {links.map((link) => {
        const LinkIcon = link.icon
        return (
          <Link
            key={link.name}
            href={link.href}
            className={cn(
              'bg-surface hover:bg-brand-700 hover:text-brand-50 flex cursor-pointer items-center justify-start gap-2 rounded-xl p-[10px_20px] text-white',
              { 'text-brand-50 bg-brand-700': pathname === link.href },
            )}
            onClick={() => callback()}
          >
            <LinkIcon className="w-5" />
            <p>{link.name}</p>
          </Link>
        )
      })}
    </>
  )
}
