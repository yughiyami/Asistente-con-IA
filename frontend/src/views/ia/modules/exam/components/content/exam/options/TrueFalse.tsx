import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import React, { useEffect } from 'react'

interface Props {
  handler: (value: boolean) => void
}

export default function TrueFalse({handler} : Props) {
  
  const [checked, setChecked] = React.useState(false)

  useEffect(() => {
    handler(checked)
  },[handler, checked])

  return (
    <div className="w-full flex items-center justify-center gap-4 p-4">
      <Switch
        checked={checked}
        onCheckedChange={setChecked}
      />
      <Label className="w-16">{checked ? "Verdadero" : "Falso"} </Label>
    </div>
  )
}
