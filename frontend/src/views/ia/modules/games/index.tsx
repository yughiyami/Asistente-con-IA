import { Card, CardContent } from '@/components/ui/card'
import React from 'react'
import useHangManGame from './modules/Hangman'
import { Button } from '@/components/ui/button'
import useWordle from './modules/Wordle'
import Image from 'next/image'
import { ComboBox } from '@/components/ui/combobox'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import useAssembly from './modules/Assembly'
import useLogic from './modules/Logic'

export default function Game() {

  const {Component : HangMan,
    open: openHangMan,
    props : {
      topic: topicHangman,
      setTopic: setTopicHangman,
      difficulty: difficultyHangman,
      setDifficulty: setDifficultyHangman,
    }
  } = useHangManGame()

  const { Component : Wordle,
    open: openWordle,
    props : {
      topic: topicWordle,
      setTopic: setTopicWordle,
      difficulty: difficultyWordle,
      setDifficulty: setDifficultyWordle,
    }
  } = useWordle()

  const { Component: Assembly,
    open: openAssembly,

  } = useAssembly()

  const { Component: Logic,
    open: openLogic,
    props: {
      difficulty: difficultyLogic,
      setDifficulty: setDifficultyLogic,
    }
  } = useLogic()

  

  return (
    <>
      <div className="flex flex-row p-4  justify-around items-center flex-wrap gap-4">
        {/* Hangman */}
        <Card className="min-w-1/4 max-h-80 bg-primary-300 overflow-y-scroll" >
          <CardContent className='flex flex-col gap-2 items-center justify-center'>
            <Image
              src="/images/icons/hangman-icon.png"
              alt="hangman"
              width={150}
              height={150}
            />
            <p>
              Hangman
            </p>
            <Button onClick={openHangMan} className="w-full">
              Iniciar
            </Button>
            <details className='bg-primary-400 p-2 rounded-sm w-full'>
              <summary>
                Configuración
              </summary>
              <div className='p-2'>
                <div className="flex flex-col gap-2">
                  <Label>
                    Topico :{">"} 
                  </Label>
                  <ComboBox 
                    onChange={setTopicHangman}
                    value={topicHangman}
                    dataList={[
                      {
                        label: "procesador",
                        value: "procesador",
                      },
                      {
                        label: "memoria",
                        value: "memoria",
                      },
                      {
                        label: "entrada/salidaz",
                        value: "entrada_salida",
                      },
                      {
                        label: "ensamblador",
                        value: "ensamblador",
                      }
                    ]}
                  />
                  <Label> Dificultad :{">"} </Label>
                  <RadioGroup value={difficultyHangman} onValueChange={setDifficultyHangman}>
                    <Label>
                      <RadioGroupItem value="easy" />
                      Fácil
                    </Label>
                    <Label>
                      <RadioGroupItem value="medium" />
                      Medio
                    </Label>
                    <Label>
                      <RadioGroupItem value="hard" />
                      Dificil
                    </Label>
                  </RadioGroup>
                </div>
              </div>
            </details>
          </CardContent>
        </Card>
        {/* Wordle */}
        <Card className="min-w-1/4 max-h-80 bg-primary-300 overflow-y-scroll">
          <CardContent className="flex flex-col gap-2 items-center justify-center">
            <Image
              src="/images/icons/wordle-icon.png"
              alt="wordle"
              width={150}
              height={150}
            />
            <p>
              Wordle
            </p>
            <Button onClick={openWordle} className="w-full ">
              Iniciar
            </Button>
            <details className='bg-primary-400 p-2 rounded-sm w-full'>
              <summary>
                Configuración
              </summary>
              <div className='p-2'>
                <div className="flex flex-col gap-2">
                  <Label>
                    Topico :{">"} 
                  </Label>
                  <ComboBox 
                    onChange={setTopicWordle}
                    value={topicWordle}
                    dataList={[
                      {
                        label: "procesador",
                        value: "procesador",
                      },
                      {
                        label: "memoria",
                        value: "memoria",
                      },
                      {
                        label: "entrada/salidaz",
                        value: "entrada_salida",
                      },
                      {
                        label: "ensamblador",
                        value: "ensamblador",
                      }
                    ]}
                  />
                  <Label> Dificultad :{">"} </Label>
                  <RadioGroup value={difficultyWordle} onValueChange={setDifficultyWordle}>
                    <Label>
                      <RadioGroupItem value="easy" />
                      Fácil
                    </Label>
                    <Label>
                      <RadioGroupItem value="medium" />
                      Medio
                    </Label>
                    <Label>
                      <RadioGroupItem value="hard" />
                      Dificil
                    </Label>
                  </RadioGroup>
                </div>
              </div>
            </details>
          </CardContent>
        </Card>
        {/* Logic */}
       <Card className="min-w-1/4 max-h-80 bg-primary-300 overflow-y-scroll">
          <CardContent className="flex flex-col gap-2 items-center justify-center">
            <Image
              src="/images/icons/logic-icon.png"
              alt="logic"
              width={150}
              height={150}
            />
            <p>
              Logica
            </p>
            <Button onClick={openLogic} className="w-full ">
              Iniciar
            </Button>
            <details className='bg-primary-400 p-2 rounded-sm w-full'>
              <summary>
                Configuración
              </summary>
              <div className='p-2'>
                <div className="flex flex-col gap-2">
                  <Label> Dificultad :{">"} </Label>
                  <RadioGroup value={difficultyLogic} onValueChange={setDifficultyLogic}>
                    <Label>
                      <RadioGroupItem value="medium" />
                      Medio
                    </Label>
                    <Label>
                      <RadioGroupItem value="hard" />
                      Dificil
                    </Label>
                  </RadioGroup>
                </div>
              </div>
            </details>
          </CardContent>
        </Card>
        {/* Assembly */}
        <Card className="min-w-1/4 max-h-80 bg-primary-300 overflow-y-scroll overflow-y-scroll">
          <CardContent className="flex flex-col gap-2 items-center justify-center">
            <Image
              src="/images/icons/assembly-icon.png"
              alt="assembly"
              width={150}
              height={150}
            />
            <p>
              Assembly
            </p>
            <Button onClick={openAssembly} className="w-full">
              Iniciar
            </Button>
            <details className='bg-primary-400 p-2 rounded-sm w-full'>
              <summary>
                Configuración
              </summary>
              <div className='p-2'>
                <div className="flex flex-col gap-2">
                  <Label> Dificultad :{">"} </Label>
                  <RadioGroup value={difficultyWordle} onValueChange={setDifficultyWordle}>
                    <Label>
                      <RadioGroupItem value="easy" />
                      Fácil
                    </Label>
                    <Label>
                      <RadioGroupItem value="medium" />
                      Medio
                    </Label>
                    <Label>
                      <RadioGroupItem value="hard" />
                      Dificil
                    </Label>
                  </RadioGroup>
                </div>
              </div>
            </details>
          </CardContent>
        </Card>
      </div>
      {HangMan}
      {Wordle}
      {Assembly}
      {Logic}
    </>
  )
}
