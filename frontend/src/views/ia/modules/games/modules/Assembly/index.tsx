import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import React, { useEffect, useRef } from "react"
import ReactMarkdown from 'react-markdown';
import { CreateAssemblyGame, GuessAssemblyWord } from "./services/Assembly";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

export default function useAssembly(){
  
  const [isOpen, setIsOpen] = React.useState(false)
  
  const [game_id, setGameId] = React.useState<string>("")
  const [code, setCode] = React.useState<string>("")
  const [architecture, setArchitecture] = React.useState<string>("")
  const [expected_behavior, setExpected_behaviour] = React.useState<string>("")
  const [hint, setHint] = React.useState<string>("")
  const [explanation, setExplanation] = React.useState<string>("")

  const [finalResult, setFinalResult] = React.useState("")
  
  const pending = useRef(false)

  const [difficulty, setDifficulty] = React.useState("medium")
  const response = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (pending.current || !isOpen) return
    pending.current = true

    const fetchData = async () => {
      const {game_id, expected_behavior, architecture, code, hint} = await CreateAssemblyGame({
        difficulty
      })

      setGameId(game_id)
      setArchitecture(architecture)
      setCode(code)
      setExpected_behaviour(expected_behavior)
      setHint(hint)
      setFinalResult("")
      setExplanation("")

      pending.current = false
    }
    fetchData()
    
  }, [isOpen, difficulty])

  useEffect(() => {
    if(!isOpen){
      setGameId("")
      setArchitecture("")
      setCode("")
      setExpected_behaviour("")
      setHint("")
      setExplanation("")
      setFinalResult("")
      if(response.current)
        response.current.value = ""
    }
  }, [isOpen])

  function open() {
    setIsOpen(true)
  }

  function close() {
    setIsOpen(false)
  }

  async function verify(){
    if(pending.current) return

    if((response.current?.value.length ?? 0 )<= 10){
      alert("No puedes dar una respuesta muy corta")
      return
    }
    pending.current = true

    const {correct, explanation: explication, correct_solution} = await GuessAssemblyWord({
      game_id,
      explanation: response.current?.value ?? ""
    })

    setCode(correct_solution || code)
    setFinalResult(correct ? "MUY BIEN !!!" : "Tienes trabajo pendiente, Continua !!!")
    setHint(correct ? "" : hint)
    setExplanation(explication)
    pending.current = false

    // if(cursor < wordSize) return

    // const updatedAttemps = attemps
    // const {results, game_over, win, explanation } = await GuessWordleWord(
    //   {
    //     game_id,
    //     word: attemps[attemp].map((e) => e.value).join("")
    //   }
    // )

    // results.forEach((e,i) => {
    //   updatedAttemps[attemp][i].status = e
    // })

    // if(win){
    //   setFinalResult("GANASTE !!!")
    //   setHint(explanation)
    // } else if (game_over) {
    //   setFinalResult("PERDISTE ._.")
    //   setHint(explanation)
    // } else {
    //   const newAttempt: WordleAttempt = []
    //     for(let i = 0; i < wordSize; i++){
    //       newAttempt.push({
    //         value : "",
    //         status: "none"
    //       })
    //     }

    //   updatedAttemps[attemp + 1] = newAttempt
    //   setCursor(0)
    //   setAttemp(attemp + 1)
    //   setAttemps(updatedAttemps)
    // }

  }


  const Component = (
    <Dialog open={isOpen} onOpenChange={close}>
      <DialogContent>
        <DialogTitle>
          Assembly
        </DialogTitle>
        <div>
          <Card>
            <CardHeader>
              <CardTitle>
                Explique el error del siguiente fragmento de codigo en Assebly <br/>
                <small className="opacity-50">
                  {architecture}
                </small>
              </CardTitle>
              <CardDescription>
                {
                  finalResult ?
                  <marquee
                    className="text-md text-white"
                  >
                    {finalResult}
                  </marquee> :
                  ""
                }
                <div
                  className="max-h-32 overflow-y-scroll"
                >
                  <p className="text-xs">
                    {hint}
                  </p>
                  <p>
                    {explanation}
                  </p>
                </div>
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        <div>
          <Card>
            <CardHeader>
              <CardTitle>
                Comportamiento esperado
              </CardTitle>
              <CardDescription>
                {expected_behavior}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex gap-2 flex-col">
              <pre className="bg-gray-800 p-2 rounded-sm border-white border text-[0.65rem]">
                {code}
              </pre>
              <Textarea ref={response} className="text-xs"/>
            </CardContent>
            <CardFooter>
                <Button onClick={verify}
                  disabled={pending.current || finalResult ===  "MUY BIEN !!!" }
                >
                  Enviar ✔
                </Button>
            </CardFooter>
          </Card>
        </div>
      </DialogContent>
    </Dialog> 
  )

  return {
    Component,
    open,
    close,
    props: {
      difficulty,
      setDifficulty,
    }
  }
}