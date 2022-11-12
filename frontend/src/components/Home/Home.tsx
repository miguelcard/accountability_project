import Box from '@mui/material/Box'
import React from 'react'
import blob from '../../assets/statics/images/Home/home-blob.png';
import '../../assets/styles/components/Home/home.css';
import LandingNavbar from '../Headers/LandingNavbar'
import HeroBanner from './HeroBanner'

// import 'bootstrap/dist/css/bootstrap.min.css'; // TODO: TO DELETE, check weird spacing in navbar when this is deleted!

const Home: React.FC = () => {

    return (
        <>
            {/* put all body inside a grid?? ... for now not needed ...*/}
            <LandingNavbar />
            <Box className='home__hero-header' >
                <HeroBanner />
            </Box>
            <img src={blob} alt="blob" className='home__blob' />





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
