import Box from '@mui/material/Box'
import React from 'react'
import blob from '../../assets/statics/images/Home/home-blob.png';
import '../../assets/styles/components/Home/home.css';
import LandingNavbar from '../Headers/LandingNavbar';
import HeroBanner from './HeroBanner';

/**
 * Landing Page for unauthenticated users
 * @returns 
 */
const Home: React.FC = () => {

    return (
        <>
            {/* put all body inside a grid?? ... for now not needed ...*/}
            <LandingNavbar />
            <img src={blob} alt="blob" className='home__blob' />
            <Box className='home__hero-header' >
                <HeroBanner />
            </Box>

            {/* Below is jsut a temp solution to extend the colot of the above box and add the copyright text */}
            <Box sx={{ 
                display: "flex",
                alignItems: "flex-end", 
                justifyContent: "center",
                height: '245px', 
                backgroundColor: '#84CEC1' }}>
                <span
                    style={{
                        color: "#FFFFFF",
                        fontSize: 18,
                        marginBottom: 45,
                        textAlign: "center",
                    }}
                >a Miguel Cardenas production <br />
                    AvidHabits &copy; 2023
                </span>
            </Box>
            {/* FooterHome would go here or do layouts? */}
        </>
    )
}

export default Home
