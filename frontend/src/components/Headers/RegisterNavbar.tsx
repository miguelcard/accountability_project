import React from 'react';
import { Link as RouterLink } from 'react-router-dom'
import logotype from '../../assets/statics/images/Headers/avidhabits-secondary.png'
import AppBar from '@mui/material/AppBar';
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';
import Link from "@mui/material/Link";
import '../../assets/styles/components/Headers/registerNavbarStyle.css'
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';


interface Props {
    actionMessage?: string,
    buttonLinkTo?: string,
    buttonKey?: string,
    buttonText?: string,
}

export const RegisterNavbar: React.FC<Props> = (child) => {
    return (
        <>
            {/* use sticky navigation on (Desktop view mainly) when home page gets bigger <AppBar position="sticky" */}
            <AppBar position="static" elevation={0} className='register-header' >
                <Container maxWidth="xl" >
                    <Toolbar>
                        <Link
                            sx={{ flexGrow: 1 }}
                            component={RouterLink}
                            to="/"
                        >
                            <img src={logotype} alt="logo" className='register-header__logo' />
                        </Link>
                        <Box
                            className='register-header__action-elements'
                            sx={{ display: { xs: 'flex', md: 'flex' }, my: 2 }}
                        >

                            {child.actionMessage ? (
                                <>
                                    <Typography className='register-header__action-text' sx={{ my: 2, display: { xs: 'none', sm: 'none', md: 'flex' }, fontSize: '1em' }}>
                                        {child.actionMessage}
                                    </Typography>
                                    <Typography className='register-header__action-text' sx={{ my: 2, display: { xs: 'none', sm: 'flex', md: 'none' }, fontSize: '0.8em' }}>
                                        {child.actionMessage}
                                    </Typography>
                                </>
                            ) : (
                                null
                            )}

                            {(child.buttonKey && child.buttonLinkTo && child.buttonText) ? (
                                <Button
                                    className='register-header__action-elements__button--primary'
                                    component={RouterLink}
                                    to={child.buttonLinkTo}
                                    key={child.buttonKey}
                                >
                                    {child.buttonText}
                                </Button>
                            ) : (
                                null
                            )}
                        </Box>
                    </Toolbar>
                </Container>
            </AppBar>
        </>
    )
}
