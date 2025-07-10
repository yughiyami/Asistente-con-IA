import { Dialog} from '@/components/ui/dialog'
import { useExamStore } from '@/store/exam'
import React from 'react'
import QuestionCard from './QuestionCard'
import ResultSummary from './ResultSummary'

export default function Exam() {
  
  const {
    exam,
    index,
  } = useExamStore()
  
  const [open, setOpen] = React.useState(false)
  React.useEffect(() => {
    if (exam) {
      setOpen(true)
    } else {
      setOpen(false)
    }
  },[exam])
  return (
    <Dialog open={open}>
      { index >= 0 && exam ? 
        <QuestionCard
          question={exam?.questions[index]}
          question_number={index + 1}
          total_questions={exam?.questions.length}
        />
        :
        <ResultSummary/> 
      }
    </Dialog>      
  )
}
