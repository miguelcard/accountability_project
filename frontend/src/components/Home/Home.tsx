import React from 'react'

import LandingNavMenu from '../Headers/LandingNavbar'
import HeroBanner from './HeroBanner'

// import 'bootstrap/dist/css/bootstrap.min.css'; // TODO: TO DELETE, check weird spacing in navbar when this is deleted!

const Home: React.FC = () => {

    return (
        <>
                {/* put all body inside a grid?? */}

                <LandingNavMenu />
                <HeroBanner />

                {/* put stain "mancha" image here */}





                {/*  How it works and Frequently asked questions are just nice to have things at the end 
                    TODO at end, just make a remote branch from here
                */}
                {/* this is a "nice" component but lets just leave it out for now, delete for now, make a branch at this point */}
                    {/* <HowItWorks/>   */}
                {/* FooterHome would go here   or do layouts? */}
        </>
    )
}

export default Home
