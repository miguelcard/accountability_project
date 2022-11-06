import React from 'react';
import { useHistory } from 'react-router-dom';
import { Link as RouterLink } from 'react-router-dom';
import heroImage from '../../assets/statics/images/Home/hero-image.png';
import '../../assets/styles/components/Home/heroBanner.css';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';

export const HeroBanner: React.FC = () => {

    let history = useHistory();

    const eventUp = () => {
        history.push('/register'); // needed?
    }
    // you can just remove the above and use the RouterLink in the button


    // What do these two do?
    // <Grid container></Grid>  -> in exaple it contains all the content of the webpage
    // <Grid item container></Grid>     -> has main content inside
    // <Grid item></Grid>           -> just the title is inside the this grid item
    // <Grid item></Grid>           -> then the a table below is also inside grid tag

    // hero content text and get-started button
    const heroText = (
        <Box sx={{ textAlign: 'left', mr:10}}> {/* in this box put a class for the gap between the texts and the button */}
            {/* <Box>     put a proper gap between this two elements*/}
                <h1 className='hero__primary-text'>
                    Accountability<br />
                    meets Partner.
                </h1>
            <p className='hero__secondary-text'>
                Improve your habits and achieve your goals<br />
                while taking your journey along with others
            </p>
            {/* </Box> */}

            <Button
                className='landing-header__action-buttons__item--primary'
                component={RouterLink}
                to={'/register'}
                key={'signup'}
            >
                Get Started
            </Button>
        </Box>
    );


    return (
        <>
            <Container maxWidth="xl">
                <Grid container
                    direction="row"
                    justifyContent="space-evenly"
                    alignItems="center"
                    sx={{ mt:10 }}
                >
                    <Grid container item xs={6} md={6}
                        sx={{ backgroundColor: 'red' }}
                        justifyContent="center"
                    >
                        {heroText}
                    </Grid>
                    <Grid item xs={6} md={6} sx={{ backgroundColor: 'blue' }}>
                        {/* maybe you dont need this box */}
                        <Box sx={{ textAlign: 'center' }}>
                            <img src={heroImage} alt="hero-image" className='hero__image' />
                        </Box>
                    </Grid>
                </Grid>
            </Container>



            {/* <div> for enclosing hero banner and image, manage responsiveness ( I would say on small screens put image below) */}
            {/*  Add component here for hero text */}
            {/* <button onClick={eventUp} >Get Started</button> */}
            {/* <Button
                className='landing-header__action-buttons__item--primary'
                component={RouterLink}
                to={actionButtons.signup.linkTo}
                key={actionButtons.signup.key}
                sx={{ color: 'white', display: { xs: 'none', sm: 'block' }, mr: 3, }}
            >
                Get Started
            </Button> */}
            {/* <div className="signIn">
                <p>Or, just <RouterLink to="/login" className="link-signin">SignIn</RouterLink></p>
            </div> */}


            {/* add image here */}
            {/* </div> */}
        </>
    )
}

export default HeroBanner;