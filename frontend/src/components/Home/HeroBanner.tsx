import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import heroImage from '../../assets/statics/images/Home/hero-image.png';
import '../../assets/styles/components/Home/heroBanner.css';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';

/**
 * Landing page hero section which includes hero text, action button and image
 * @returns
 */
export const HeroBanner: React.FC = () => {

    // hero content text and get-started button
    const heroText = (
        <Box className='hero__text-and-button-container' >
            <Box className='hero__text-container' >
                <h1 className='hero__primary-text'>
                    Accountability<br />
                    meets Partner.
                </h1>
                <p className='hero__secondary-text'>
                    Improve your habits and achieve your goals<br />
                    while taking your journey along with others.
                </p>
            </Box>
            <Button
                className='hero__primary-button'
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
            <Container maxWidth="xl" className='hero__container'>
                <Grid container
                    direction="row"
                    justifyContent="space-evenly"
                    alignItems="center"
                    sx={{ pt: 7 }}
                >
                    <Grid container item xs={6} md={6}
                        justifyContent="center"
                    >
                        {heroText}
                    </Grid>
                    <Grid item xs={6} md={6}
                        sx={{ textAlign: 'center' }}
                    >
                        <img src={heroImage} alt="hero" className='hero__image' />
                    </Grid>
                </Grid>
            </Container>
        </>
    )
}

export default HeroBanner;