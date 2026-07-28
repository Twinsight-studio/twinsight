import PageTitle from '@/app/ui/PageTitle'

export default function Page() {
  return (
    <div className="flex h-full">
      <main className="flex-1 p-5">
        <PageTitle pageTitle="搜尋個股" />
      </main>
      <div className="border-border w-20 border-l"></div>
    </div>
  )
}
