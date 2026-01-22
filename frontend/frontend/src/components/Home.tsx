"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"

import Hero from "./Hero"
import Chat from "./Chat"
import Navbar from "./Navbar"

const Home = () => {
  const [started, setStarted] = useState(false)

  return (
    <div className="relative h-screen w-screen bg-red-950 overflow-hidden">
    <Navbar onHomeClick= {() => setStarted(false)}/>
      <AnimatePresence mode="wait">
        {!started ? (
          <motion.div
            key="hero"
            initial={{ y: 0, opacity: 1 }}
            exit={{ y: -200, opacity: 0 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
            className="absolute inset-0"
          >
            <Hero onStart={() => setStarted(true)} />
          </motion.div>
        ) : (
          <motion.div
            key="chat"
            initial={{ y: 200, opacity: 0 }}
            animate={{ y: 70, opacity: 1 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
            className="absolute inset-0"
          >
            <Chat />
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  )
}

export default Home
