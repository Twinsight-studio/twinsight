'use client'

import { useState } from 'react'
import Link from 'next/link'
import NavBar from '@/app/ui/NavBar'
import { Bars3Icon } from '@heroicons/react/24/outline'
import Logo from '@/app/ui/Logo'
import Sidebar from './Sidebar'

export default function PageLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  function toggleSwitch(): void {
    setSidebarOpen((prev) => !prev)
  }
  return (
    <>
      <div className="flex h-screen">
        <Sidebar sidebarOpen={sidebarOpen} onToggle={toggleSwitch} />
        <div className="flex flex-1 flex-col xl:pl-48">
          <NavBar />
          {/* Mobile Header */}
          <div className="border-border bg-surface sticky top-0 z-40 flex shrink-0 items-center gap-x-4 border-b px-4 shadow-sm xl:hidden">
            <button className="p-2.5" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Bars3Icon className="size-6" />
            </button>
            <Link className="flex h-17.5 flex-1 flex-col items-center justify-center" href="/">
              <Logo />
            </Link>
          </div>
          <div className="h-[calc(100%-70px)] overflow-auto">
            <div className="h-full">{children}</div>
          </div>
        </div>
      </div>
    </>
  )
}
