"use client"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import React, { useEffect, useMemo, useRef, useState } from "react"
import ReactMarkdown from 'react-markdown';
import { Button } from "@/components/ui/button";
import { CreateLogicGame, GuessLogicWord } from "./services/Logic";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { SimpleLogicGate } from "./components/Circuit";

export default function useLogic(){
  
  const [isOpen, setIsOpen] = React.useState(false)
  
  const [game_id, setGameId] = React.useState<string>("")
  const [question, setQuestion] = React.useState<string>("")
  const [description, setDescription] = React.useState<string>("")

  const [pattern, setPattern] = React.useState<("AND" | "XOR" | "NAND" | "XNOR" | "OR" | "NOR")[]>([])
  const [input_values, setInput_values] = React.useState<string[]>([])
  const [finalResult, setFinalResult] = React.useState("")
  
  const pending = useRef(false)

  const [difficulty, setDifficulty] = React.useState("medium")
  const [answers, setAnswers] = React.useState<boolean[][]>([])
  const [score, setScore] = useState<number | undefined>()

  const [externalInputs, setExternalInputs] = useState({
    "A": false,
    "B": false,
    "C": false
  });

  useEffect(() => {
    if (pending.current || !isOpen) return
    pending.current = true

    const fetchData = async () => {
      const {game_id, question, circuit} = await CreateLogicGame({
        difficulty
      })

      setGameId(game_id)
      setQuestion(question)
      setDescription(circuit.description)
      // TODO: set circuit
      function setPattern(inputs: string[], depth: number): boolean[][]{
        if(depth === inputs.length) return [[]]
        const gate = inputs[depth]
        const nextGates = setPattern(inputs, depth + 1)
        const response = []
        response.push(...nextGates.map((e) => [false, ...e]))
        response.push(...nextGates.map((e) => [true, ...e]))
        return response
      }

      const truthTable = setPattern(circuit.inputs, 0).map((e)=> [...e, false])
      setAnswers(truthTable)
      setInput_values(circuit.inputs)
      setFinalResult("")

    //   if(circuit && circuit.connectGates){
    //   for(let i=0; i < pattern.length - 1; i++){
    //     circuit.connectGates(i, i+1, "A")
    //   }
    // } else {
    // }
    
      pending.current = false
    }

    fetchData()
    
  }, [isOpen, difficulty])

  useEffect(() => {
    if(!isOpen){
      setGameId("")
      setGameId("")
      setQuestion("")
      setPattern([])
      setAnswers([])
      setDescription("")
      setInput_values([])
      setFinalResult("")
      setScore(undefined)
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
    pending.current = true

    const truth_table = answers.map((e) => ({
      inputs: e.slice(0, e.length - 1).reduce((acc, value, index) => {
        acc[input_values[index]] = value ? 1 : 0
        return acc
      }, {} as {[key: string]: (0|1)}),
      output: e[e.length - 1] ? 1 : 0 as (0|1)
    }))

    const {correct, score, expected_truth_table, explanation} = await GuessLogicWord({
      game_id,
      truth_table
    })

    setScore(score)
    setFinalResult(correct ? "MUY BIEN !!!" : "Tienes trabajo pendiente !!!")
    setDescription(explanation)
    // const {correct, explanation: explication, correct_solution} = await GuessAssemblyWord({
    //   game_id,
    //   explanation: response.current?.value ?? ""
    // })

    // setCode(correct_solution)
    // setFinalResult(correct ? "MUY BIEN !!!" : "Tienes trabajo pendiente !!!")
    // setHint(explication)
    // pending.current = false

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

    pending.current = false
  }


  const Component = (
    <Dialog open={isOpen} onOpenChange={close}>
      <DialogContent>
        <DialogTitle>
          Logic
        </DialogTitle>
        <div>
          <Card>
            <CardHeader>
              <CardTitle>
                {question ?? "Espere las instrucciones"}
              </CardTitle>
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
                  {score ? `Puntaje ${score}%` : ""}
                </div>
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        <div>
          <Card>
            <CardHeader>
              <CardTitle>
                {finalResult ? "Explicacion" : "Circuito"}
              </CardTitle>
              <CardDescription className="max-h-32 overflow-y-scroll">
                <ReactMarkdown>
                {description}
                </ReactMarkdown>
              </CardDescription>
            </CardHeader>
            <div className="m-4 flex gap-2">
              {pattern.map((e,i) => {
                return <div key={i} className="rounded-sm bg-primary-400 p-4">
                  <SimpleLogicGate 
                type={e}               
                />
                </div>
              })}
            </div>
            <CardContent className="flex gap-4 flex-col">
              <Label>
                Casos de Prueba
              </Label>
              <table>
                
              <thead>
                <tr>
                  {input_values?.map((e,i) => {
                    return <th key={i}>
                      {e}
                    </th>
                  })}
                  <th>
                    Salida
                  </th>
                </tr>
              </thead>
              <tbody>
                {answers?.map((e,i) => {
                  return <tr key={i}>
                    {e.map((value, index) => {
                      return <td key={index} align="center">
                        <div className="p-2 flex flex-row items-center justify-center gap-4">
                          <Switch 
                            disabled={pending.current || index !== e.length - 1}
                            checked={value} onCheckedChange={() => {
                              const newAnswers = answers
                              newAnswers[i][index] = !value
                              setAnswers([...newAnswers])
                            }}/>
                          <Label className="text-white">
                            {value ? "1" : "0"}
                          </Label>
                        </div>
                      </td>
                    })}
                  </tr>
                })}
              </tbody>
              </table>
            </CardContent>
            <CardFooter>
                <Button onClick={verify}
                  disabled={pending.current || !!finalResult }
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