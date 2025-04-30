import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { MultipleChoiceOption } from '@/types/exam'
import React, { useEffect } from 'react'

type Props = {
  options: MultipleChoiceOption[]
  handler: (value: string) => void
  correctAnswer?: string
  chosenAnswer?: string
}

export default function MultipleChoice({options, handler, correctAnswer, chosenAnswer} : Props) {

  const [value, setValue] = React.useState<string>("")
  
  useEffect(() => {
    handler(value)
  },[value, handler])

  useEffect(() => {
    setValue("")
  }, [options])

  return (
    <RadioGroup name="answer" defaultValue="" value={chosenAnswer ?? value} className='p-4'>
      {options.map(({key, value}, index) => (
        <div key={index} className={`flex items-center space-x-2 ${correctAnswer === key ? "text-green-500" : ""}`}
          onClick={() => {setValue(key)}}
        >
          <RadioGroupItem value={key} />
          <Label>{value}</Label>
        </div>
      ))}
    </RadioGroup>
  )
}
