import '@/app/ui/globals.css'
import NavLinks from '@/app/ui/nav-links'
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import Image from 'next/image'
import Link from 'next/link'
import { Providers } from './providers'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'TwInsight',
  description: '台股觀察與選股工具',
  icons: [
    {
      rel: 'icon',
      url: '/favicon/favicon-96x96.png?v=1',
      sizes: '96x96',
      type: 'image/png',
    },
    { rel: 'icon', url: '/favicon/favicon.svg?v=1', type: 'image/svg+xml' },
    { rel: 'shortcut icon', url: '/favicon/favicon.ico?v=1' },
    {
      rel: 'apple-touch-icon',
      url: '/favicon/apple-touch-icon.png?v=1',
      sizes: '180x180',
    },
  ],
  applicationName: 'TwInsight',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="zh-Hant" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full bg-bg text-white">
        <Providers>
          <div className="flex h-screen">
            <div className="z-100 w-48 bg-surface border-right border-border shrink-0 shadow-[5px_0_10px_5px_#0000005e]">
              <Link className="p-5 flex items-end justify-center" href="/">
                <Image src="/images/twinsight_logo.svg" width={30} height={26} alt="TwInsight Logo" />
                <div className="ml-1 text-xl leading-4 font-bold tracking-wider text-white">
                  Tw<span className=" text-brand-500">Insight</span>
                </div>
              </Link>
              <div className="flex text-white flex-col mx-5 my-2 gap-y-2">
                <NavLinks />
              </div>
            </div>
            <div className="flex-1">
              <div className="px-5 py-6 bg-surface shadow-[5px_0_10px_5px_#0000005e] flex justify-end gap-5">
                <div>設定</div>
                <div>會員</div>
              </div>
              <div className="h-[calc(100%-48px)] overflow-scroll">
                <main className="p-5 h-1000">{children}</main>
              </div>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  )
}
