import { Dialog, DialogContent } from '@/components/ui/dialog'
import { DialogTitle } from '@radix-ui/react-dialog'
import React, { useEffect, useRef } from 'react'
import WordBlock from '../custom/WordBlock'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { CreateHangmanGame, GuessHangmanWord } from './services/Hangman'
import Image from 'next/image'

const alphabet = "abcdefghijklmnopqrstuvwxyz"



export default function useHangManGame() {

  const [usedWords, setUsedWords] = React.useState<string[]>([])
  const [word, setWord] = React.useState<string>("_ _ _ _ _ _ _ _")
  const [correctWord, setCorrectWord] = React.useState<string>("")
  const [game_id, setGameId] = React.useState<string>("")
  const [remaining_attempts, setRemainingAttempts] = React.useState<number>(0)  
  const [clue, setClue] = React.useState<string>("....")
  const [argument, setArgument] = React.useState<string>("")
  const pending = useRef(false)
  const [isOpen, setIsOpen] = React.useState(false)
  const [topic, setTopic] = React.useState("procesador")
  const [difficulty, setDifficulty] = React.useState("medium")
  function resetGame() {
    setUsedWords([])
    setWord("_ _ _ _ _ _ _ _")
    setCorrectWord("")
    setGameId("")
    setClue("....")
  }

  useEffect(() => {
    if (pending.current) return
    pending.current = true
    resetGame()
    const fetchData = async () => {
      const {hidden_word, clue, game_id, max_attempts, argument} = await CreateHangmanGame({
        difficulty, topic
      })

      setGameId(game_id)
      setWord(hidden_word)
      setClue(clue)
      setArgument(argument)
      setRemainingAttempts(max_attempts)

      pending.current = false
    }

    fetchData()
  },[isOpen, topic, difficulty])

  function validateWord(word: string){
    if (pending.current) return
    pending.current = true
    
    const fetchData = async () => {
      const {correct, remaining_attempts, game_over, win, current_word, correct_word} = await GuessHangmanWord({game_id, guess: word})
      setWord(current_word)
      setUsedWords((prev) => [...prev, word])
      setRemainingAttempts(remaining_attempts)
      pending.current = false
      if (game_over){
        setCorrectWord(correct_word)
      }
      if (win){
        alert("Ganaste")
      }
    }

    fetchData()
  }

  function open() {
    setIsOpen(true)
  }
  function close() {
    setIsOpen(false)
  }

  const Component = (
    <Dialog open={isOpen} onOpenChange={close}>
      <DialogContent>
        <DialogTitle>
          HangMan
        </DialogTitle>
        <div>
          <Card>
            <CardHeader>
              <CardTitle>
                {clue}
              </CardTitle>
              <CardDescription>
                {correctWord ?? ""}
              </CardDescription>
            </CardHeader>
            <div className="flex px-4">
              <div className="w-1/3">
                <Image 
                  alt={"hangman"}
                  src={`/images/hangman/${7 - remaining_attempts}-frame.jpg`}
                  width={200}
                  height={200}
                />
              </div>
              <div className="w-2/3">
                <CardContent>
                  {word}
                </CardContent>
                
                <CardFooter>
                  <small>
                    {usedWords.length} / {alphabet.length} letras usadas <br />
                    {remaining_attempts} intentos restantes <br />
                    <span className="opacity-50 max-h-8 overflow-y-scroll">
                      {correctWord && argument}
                    </span>
                  </small>
                </CardFooter>
              </div>
            </div>
            
            
          </Card>
        </div>
        <div className="flex flex-row gap-2 flex-wrap">
          {alphabet.split("").map((letter, index) => (
            <WordBlock key={index} 
              text={letter} 
              onClick={() => {
                validateWord(letter)
              }}
              disabled={usedWords.includes(letter) || !!correctWord}
            />
          ))}
        </div>
      </DialogContent>
    </Dialog>      
  )

  return {
    Component,
    close,
    open,
    props: {
      topic,
      setTopic,
      difficulty,
      setDifficulty,
    }
  }
}
