export type PreviewRow = {
  date: string
  region: string
  account: string
  productLine: string
  units: number
  revenue: string
  margin: string
}

export type DatasetRecord = {
  id: string
  name: string
  rows: number
  columns: number
  uploadDate: string
  status: "Ready"
  previewRows: PreviewRow[]
}
