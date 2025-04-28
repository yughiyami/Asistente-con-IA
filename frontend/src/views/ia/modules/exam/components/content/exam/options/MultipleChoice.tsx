import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import React from 'react'

type Props = {
  options: string[]
  handler: (value: string) => void
}

export default function MultipleChoice({options, handler} : Props) {
  return (
    <RadioGroup name="answer" defaultValue="" className='p-4'>
      {options.map((option, index) => (
        <div key={index} className="flex items-center space-x-2">
          <RadioGroupItem value={option} 
            onClick={() => {handler(option)}}
          />
          <Label>{option}</Label>
        </div>
      ))}
    </RadioGroup>
  )
}
