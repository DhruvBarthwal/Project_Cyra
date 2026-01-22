import React from 'react'

type NavbarProps = {
  onHomeClick: () => void
}

const Navbar = ({onHomeClick} : NavbarProps) => {
  return (
    <div className='h-16 w-full text-[#ddc689] flex justify-between gap-12 p-5 z-30'>
        <div className='font-bold ml-5 text-2xl'>
            <h1>Alex</h1>
        </div>
        <div className='flex cursor-pointer ml-28 gap-10'>
            <div
                onClick={onHomeClick}
            >
                Home
            </div>
            <div>
                Support
            </div>
            <div>
                Contact
            </div>
        </div>
        <div className='flex cursor-pointer gap-5'>
            <div>Insta</div>
            <div>Discord</div>
            <div>twitter</div>
        </div>
    </div>
  )
}

export default Navbar