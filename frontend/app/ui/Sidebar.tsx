'use client'

import { useState } from 'react'
import Link from 'next/link'
import NavLinks from '@/app/ui/NavLinks'
import { Bars3Icon, XMarkIcon, UserIcon, Cog8ToothIcon, BellIcon } from '@heroicons/react/24/outline'
import { Transition } from '@headlessui/react'
import Logo from '@/app/ui/Logo'
import DataStatus from '@/app/ui/DataStatus'

export default function Sidebar({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  return (
    <div className="bg-bg flex h-screen text-white">
      {/* Mobile sidebar */}
      <div
        className={`fixed inset-0 z-40 flex transition-transform duration-300 xl:hidden ${sidebarOpen ? 'translate-x-0 ease-out' : '-translate-x-full ease-in'} `}
        role="dialog"
        aria-modal="true"
      >
        <div className="bg-surface relative mr-16 flex w-full max-w-55 flex-1">
          <Transition
            show={sidebarOpen}
            enter="transition-opacity ease-linear duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="transition-opacity ease-linear duration-300"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="absolute top-0 left-full flex w-16 justify-center pt-5">
              <button type="button" className="-m-2.5 p-2.5" onClick={() => setSidebarOpen(false)}>
                <span className="sr-only">Close sidebar</span>
                <XMarkIcon className="h-6 w-6 text-white" aria-hidden="true" />
              </button>
            </div>
          </Transition>
          <div className="flex grow flex-col gap-y-2 overflow-y-auto px-5 py-2 text-white">
            <Link className="flex h-17.5 flex-col items-center justify-center" href="/">
              <Logo />
            </Link>
            <NavLinks callback={() => setSidebarOpen(false)} />
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="bg-surface border-right border-border z-40 hidden w-48 shrink-0 shadow-[5px_0_10px_5px_#0000005e] xl:fixed xl:inset-y-0 xl:flex xl:flex-col">
        <Link className="flex h-17.5 flex-col items-center justify-center" href="/">
          <Logo />
        </Link>
        <div className="flex flex-col gap-y-2 px-5 py-5 text-white">
          <NavLinks callback={() => setSidebarOpen(false)} />
        </div>
        <div className="mx-5 mt-auto flex flex-col items-center gap-y-1 py-4 text-xs">
          <DataStatus updatedAt="2025/05/21 15:30" status="live" />
        </div>
      </div>
      <div className="flex flex-1 flex-col xl:pl-48">
        <div className="bg-surface item-center hidden justify-end gap-5 px-5 py-5.5 shadow-[5px_0_10px_5px_#0000005e] xl:flex">
          <div>搜尋框</div>
          <button className="flex gap-x-2 self-center py-px">
            <UserIcon className="size-5.5" />
          </button>
          <button className="flex self-center py-px">
            <BellIcon className="size-5.5" />
          </button>
          <button className="self-center py-px">
            <Cog8ToothIcon className="size-6" />
          </button>
        </div>
        <div className="border-border bg-surface sticky top-0 z-40 flex shrink-0 items-center gap-x-4 border-b px-4 shadow-sm xl:hidden">
          <button className="p-2.5" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <Bars3Icon className="size-6" />
          </button>
          <Link className="flex h-17.5 flex-1 flex-col items-center justify-center" href="/">
            <Logo />
          </Link>
        </div>
        <div className="h-[calc(100%-48px)] overflow-auto">
          <main className="h-1000 p-5">{children}</main>
        </div>
      </div>
    </div>
  )
}
