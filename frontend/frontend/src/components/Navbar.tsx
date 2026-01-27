import { FaInstagram } from "react-icons/fa";
import { SiDiscord } from "react-icons/si";
import { FaXTwitter } from "react-icons/fa6";

type NavbarProps = {
  onHomeClick: () => void
  started: boolean
}

const Navbar = ({onHomeClick, started} : NavbarProps) => {
  return (
    <div className={` text-white h-16 w-full  flex justify-between gap-12 p-5 z-30 transition-all duration-2000 ${started ? "bg-gray-950 backdrop-blur-2xl" : "bg-transparent"}`}>
        <div className='font-bold ml-5 mt-2 text-2xl'>
            <h1>Cyra</h1>
        </div>
        <div className='flex ml-15 px-10 py-5 justify-center items-center rounded-2xl  gap-10 bg-white/10 backdrop-blur-2xl border-white/20 shadow-lg'>
            <div
                className="cursor-pointer"
                onClick={onHomeClick}
            >
                Home
            </div>
            <div className="cursor-pointer">
                Support
            </div>
            <div className="cursor-pointer">
                Contact
            </div>
        </div>
        <div className='flex mr-5 mt-1 cursor-pointer gap-5'>
            <FaInstagram size={25}/>
            <SiDiscord size={25} />
            <FaXTwitter size={25}/>
        </div>
    </div>
  )
}

export default Navbar