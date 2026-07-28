import React from 'react'
import { UserIcon, Cog8ToothIcon, BellIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { useState } from 'react'
import { Field, Input } from '@headlessui/react'

// 定義搜尋資料型別
interface Item {
  id: number
  name: string
  category: string
}

export default function NavBar() {
  // 2. 紀錄輸入框中的搜尋字串
  const [query, setQuery] = useState('')

  return (
    <div className="bg-surface item-center hidden justify-end gap-5 px-5 py-4 shadow-[5px_0_10px_5px_#0000005e] xl:flex">
      <Field className="border-border focus-within:ring-brand-700 relative w-[20rem] rounded-lg border bg-gray-800 shadow-sm focus-within:ring-2">
        <Input
          className="w-full rounded-lg border-none py-2 pr-10 pl-3 text-sm leading-5 focus:outline-none"
          name="full_name"
          placeholder="輸入股票代號或名稱，快速加入自選股清單"
        />
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600">
          <MagnifyingGlassIcon className="w-5" />
        </div>
      </Field>
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
  )
}
