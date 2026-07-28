import PageTitle from '@/app/ui/PageTitle'

export default function Page() {
  return (
    <div className="flex h-full">
      <main className="flex-1 p-5">
        <PageTitle pageTitle="自選股" pageSub="追蹤您關注的股票，並設定個人化提醒" />
      </main>
      <div className="border-border w-20 border-l"></div>
    </div>
  )
}
