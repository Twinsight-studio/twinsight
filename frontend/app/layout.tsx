import '@/app/ui/globals.css'

import type { Metadata } from 'next'
import { Providers } from '@/app/providers'
import PageLayout from '@/app/ui/PageLayout'
import { Noto_Sans_TC, Inter, IBM_Plex_Mono } from 'next/font/google'

const notoSansTC = Noto_Sans_TC({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-noto-sans-tc',
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const plexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-plex-mono',
})

// const geistSans = Geist({
//   variable: '--font-geist-sans',
//   subsets: ['latin'],
// })

// const geistMono = Geist_Mono({
//   variable: '--font-geist-mono',
//   subsets: ['latin'],
// })

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
    <html lang="zh-Hant" className={`${notoSansTC.variable} ${inter.variable} ${plexMono.variable} h-full antialiased`}>
      <body>
        <Providers>
          <PageLayout>{children}</PageLayout>
        </Providers>
      </body>
    </html>
  )
}
