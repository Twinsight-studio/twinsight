import React from 'react'

interface PageTitleProps {
  pageTitle: string
  pageSub?: string
}
export default function PageTitle({ pageTitle, pageSub }: PageTitleProps) {
  return (
    <>
      <h1 className="mb-1 text-2xl font-bold">{pageTitle}</h1>
      {pageSub && <div className="text-text-secondary mb-5 text-xs">{pageSub}</div>}
    </>
  )
}
