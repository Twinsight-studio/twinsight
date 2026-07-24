import React from 'react'

type StatusType = 'live' | 'offline' | 'updating'

interface DataStatusProps {
  updatedAt: string
  status: StatusType
}

const statusConfig: Record<StatusType, { label: string; dotColor: string; textColor: string; animate: boolean }> = {
  live: {
    label: '即時',
    dotColor: 'bg-green-500',
    textColor: 'text-green-400',
    animate: true,
  },
  offline: {
    label: '離線',
    dotColor: 'bg-gray-500',
    textColor: 'text-gray-400',
    animate: false,
  },
  updating: {
    label: '更新中',
    dotColor: 'bg-yellow-500',
    textColor: 'text-yellow-400',
    animate: true,
  },
}

export default function DataStatus({ updatedAt, status }: DataStatusProps) {
  const currentStatus = statusConfig[status]

  return (
    <>
      <p>資料更新</p>
      <p>{updatedAt}</p>
      <p>
        <span className="flex items-center gap-1.5">
          <span className="relative flex h-2.5 w-2.5">
            {currentStatus.animate && (
              <span
                className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${currentStatus.dotColor}`}
              />
            )}
            <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${currentStatus.dotColor}`} />
          </span>
          <span className={`text-sm ${currentStatus.textColor}`}>{currentStatus.label}</span>
        </span>
      </p>
    </>
  )
}
