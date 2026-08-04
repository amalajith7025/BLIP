type UploadProgressProps = {
  value: number
}

export function UploadProgress({ value }: UploadProgressProps) {
  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-foreground">We&apos;re preparing your data...</p>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-200"
          style={{ width: `${value}%` }}
          aria-hidden="true"
        />
      </div>
      <p className="text-xs text-muted-foreground">{value}%</p>
    </div>
  )
}
