
import { Card, CardDescription, CardHeader } from "@/components/ui/card"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import React, { useEffect, useMemo, useRef } from "react"
import WordBlock from "../custom/WordBlock"
import { CreateWordleGame, GuessWordleWord } from "./services/Wordle"
import ReactMarkdown from 'react-markdown';

type WordleLetter = {
  value: string,
  status: "none" | "absent" | "present" | "correct"
}
type WordleAttempt = WordleLetter[]


const alphabet = "abcdefghijklmnopqrstuvwxyz✔✘"

export default function useWordle(){
  
  const [isOpen, setIsOpen] = React.useState(false)
  
  const [wordSize, setWordSize] = React.useState<number>(5)
  const [maxAttempts, setMaxAttempts] = React.useState<number>(3)
  const [cursor, setCursor] = React.useState(0)

  const [game_id, setGameId] = React.useState<string>("")
  const [hint, setHint] = React.useState<string>("")
  const [finalResult, setFinalResult] = React.useState("")
  const pending = useRef(false)

  const [topic, setTopic] = React.useState("procesador")
  const [difficulty, setDifficulty] = React.useState("medium")


  const newAttempt = useMemo(() => {
    const a : WordleAttempt = []
    for(let i = 0; i < wordSize; i++){
      a.push({
        value : "",
        status: "none"
      })
    }
    return a
  }, [wordSize])

  const [attemps, setAttemps] = React.useState<WordleAttempt[]>([])
  const [attemp, setAttemp] = React.useState<number>(0)

  useEffect(() => {
    if (pending.current || !isOpen) return
    pending.current = true

    const fetchData = async () => {
      const {max_attempts, word_length, game_id, topic_hint} = await CreateWordleGame({
        difficulty,
        topic
      })

      const newAttempt: WordleAttempt = []
      for(let i = 0; i < word_length; i++){
        newAttempt.push({
          value : "",
          status: "none"
        })
      }

      
      const a = [newAttempt]
      for(let i = 1; i < max_attempts; i++){
        a.push([])
      }

      setCursor(0)
      setMaxAttempts(max_attempts)
      setWordSize(word_length)
      setGameId(game_id)
      setAttemps(a)
      setHint(topic_hint)

      pending.current = false
    }

    fetchData()
    
  }, [ isOpen, difficulty, topic])

  useEffect(() => {
    if(!isOpen){
      setCursor(0)
      setHint("")
      setAttemp(0)
      setAttemps([])
      setWordSize(0)
      setMaxAttempts(0)
      setGameId("")
      setFinalResult("")
    }
  }, [isOpen])

  function open() {
    setIsOpen(true)
  }
  function close() {
    setIsOpen(false)
  }

  function chose(option: string){
    if (cursor >= wordSize) return
    const updatedAttemps = attemps
    updatedAttemps[attemp][cursor].value = option
    setCursor(cursor + 1)
    setAttemps(updatedAttemps)
  }


  function undo(){
    if(cursor <= 0) return 
    const updatedAttemps = attemps
    updatedAttemps[attemp][cursor - 1] .value = ""
    setCursor(cursor - 1)
    setAttemps(updatedAttemps)
  }

  async function verify(){
    if(cursor < wordSize) return

    const updatedAttemps = attemps
    const {results, game_over, win, explanation } = await GuessWordleWord(
      {
        game_id,
        word: attemps[attemp].map((e) => e.value).join("")
      }
    )

    results.forEach((e,i) => {
      updatedAttemps[attemp][i].status = e
    })

    if(win){
      setFinalResult("GANASTE !!!")
      setHint(explanation)
    } else if (game_over) {
      setFinalResult("PERDISTE ._.")
      setHint(explanation)
    } else {
      const newAttempt: WordleAttempt = []
        for(let i = 0; i < wordSize; i++){
          newAttempt.push({
            value : "",
            status: "none"
          })
        }

      updatedAttemps[attemp + 1] = newAttempt
      setCursor(0)
      setAttemp(attemp + 1)
      setAttemps(updatedAttemps)
    }



  }


  const Component = (
    <Dialog open={isOpen} onOpenChange={close}>
      <DialogContent>
        <DialogTitle>
          Wordle
        </DialogTitle>
        <div>
          <Card>
            <CardHeader>
              <CardDescription>
                {
                  finalResult ?
                  <marquee
                    className="text-xl text-white"
                  >
                    {finalResult}
                  </marquee> :
                  ""
                }
                <div
                  className="max-h-32 overflow-y-scroll"
                >
                  <ReactMarkdown 
                    >
                    {hint}
                  </ReactMarkdown>
                </div>
               
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        <div className="flex flex-row gap-2 flex-wrap">
          {attemps.map((e,i) => {
            return (
              <div key={i} className="flex gap-2 items-center justify-center w-full bg-primary-700 p-1 rounded-sm">
                {e.map((e,i) => {
                  return (
                    <WordBlock key={i} text={e.value}
                      className={
                        e.status === "present" ? "bg-amber-400" :
                        e.status === "correct" ? "bg-green-400" :
                        e.status === "absent" ? "bg-red-400" :
                        ""
                      }
                      // disabled={e.status === "absent"}
                      // variant={
                      //   e.status === "present" ? "ghost" :
                      //   e.status === "correct" ? "outline" :
                      //   "default"

                      // }
                    />
                  )
                })}

              </div>
            )
          })}
        </div>
        <div className="flex gap-1 flex-wrap">
          {alphabet.split("").map((e,i)=> {
            return <WordBlock text={e} key={i} 
            disabled={!!finalResult}
            onClick={
              e === "✘" ? () => undo() :
              e === "✔" ? () => verify() :
              () => chose(e)
            }/>
          })}
        </div>
      </DialogContent>
    </Dialog> 
  )

  return {
    Component,
    open,
    close,
    props: {
      topic,
      setTopic,
      difficulty,
      setDifficulty,
    }
  }
}