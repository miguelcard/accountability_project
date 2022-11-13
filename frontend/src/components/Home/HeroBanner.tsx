import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import heroImage from '../../assets/statics/images/Home/hero-image.png';
import '../../assets/styles/components/Home/heroBanner.css';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import useMediaQuery from '@mui/material/useMediaQuery';
import useTheme from '@mui/material/styles/useTheme';

/**
 * Landing page hero section which includes hero text, action button and image
 * @returns
 */
export const HeroBanner: React.FC = () => {

    // variable that tells us if screen is smaller than 'sm', i.e. extra small, used to apply a different style when true
    const theme = useTheme();
    const isXsScreenOrBelow = useMediaQuery(theme.breakpoints.down("sm"));
    const isSmScreenOrBelow = useMediaQuery(theme.breakpoints.down("md"));

    // hero content text and get-started button
    const heroText = (
        <Box className={`hero__text-and-button-container ${isSmScreenOrBelow ? 'hero__text-and-button-container--sm' : ''}`} >
            <Box className={`hero__text-container ${isXsScreenOrBelow ? 'hero__text-container--xs' : ''} `} >
                <h1 className={`hero__primary-text ${isXsScreenOrBelow ? 'hero__primary-text--xs' : ''} `} >
                    Accountability<br />
                    meets Partner.
                </h1>
                <p className='hero__secondary-text'>
                    Improve your habits and achieve your goals,{isXsScreenOrBelow ? ' ' : <br /> }
                    while taking your journey along with others.
                </p>
            </Box>
            <Box>
                <Button
                    className='hero__primary-button'
                    component={RouterLink}
                    to={'/register'}
                    key={'signup'}
                    >
                    Get Started
                </Button>
            </Box>
        </Box>
    );

    return (
        <>
            <Container maxWidth="xl" className='hero__container' >
                <Grid container
                    direction="row"
                    justifyContent="space-evenly"
                    alignItems="center"
                    sx={{ pt: 7 }}
                    rowSpacing={{ xs: 5, sm: 7}}
                >
                    <Grid container item md={6}
                        justifyContent="center"
                    >
                        {heroText}
                    </Grid>
                    <Grid item md={6}
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