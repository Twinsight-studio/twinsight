import '@/app/ui/globals.css'

import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Providers } from '@/app/providers'
import Sidebar from '@/app/ui/Sidebar'

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
  // const [sidebarOpen, setSidebarOpen] = useState(false)
  return (
    <html lang="zh-Hant" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full">
        <Providers>
          <Sidebar>{children}</Sidebar>
        </Providers>
      </body>
    </html>
  )
}
