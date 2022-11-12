import React, { useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import logotype from '../../assets/statics/images/Headers/avidhabits.png'
import '../../assets/styles/components/Headers/landingNavbarStyle.css'
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import CloseRoundedIcon from '@mui/icons-material/CloseRounded';
import Link from "@mui/material/Link";
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';

/**
 * Defines the structure of a list of Buttons or Links 
 */
interface LinkButtons {
    [key: string]: {
        name: string
        linkTo: string
        key?: string
        className?: string
        className2?: string
    }
}

/**
 * Resposive landing page navigation menu (top menu / navbar) thet the user first sees if he is not authenticated 
 * @returns landing page navigation menu
 */
const LandingNavbar: React.FC = () => {

    // Definition of NavBar pages and their links
    const navbarPages: LinkButtons = {
        contact: {
            name: 'Contact',
            linkTo: '/'
        },
        about: {
            name: 'About',
            linkTo: '/'
        }
    }

    // Action buttons definition
    const actionButtons: LinkButtons = {
        login: {
            name: 'Log in',
            linkTo: '/login',
            className: 'landing-header__action-buttons__item--secondary',
            className2: 'sidebar__action-buttons__item--secondary'
        },
        signup: {
            name: 'Sign Up',
            linkTo: '/register',
            key: 'signup',
            className: 'landing-header__action-buttons__item--primary'
        }
    }

    // for small screens:
    const [mobileOpen, setMobileOpen] = useState<boolean>(false);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    return (
        <>
             {/* use sticky navigation on (Desktop view mainly) when home page gets bigger <AppBar position="sticky" */}
            <AppBar position="static" elevation={0} className='landing-header' >
                <Container maxWidth="xl" >
                    <Toolbar>
                        {/*
                        The responsiveness of the elements can be handled by the display property, if xs: 'none' it means
                        the element is not shown on small screens, this way we can show or hide the blocks we need for each screen size.
                        we can further add rules for larger screen sizes if required (xs, sm, md, lg, xl...)
                        */}

                        {/*
                        Elements for medium (md) screens and above:
                        */}
                        <Link
                            sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' }, mr: 1 }}
                            component={RouterLink}
                            to="/"
                        >
                            <img src={logotype} alt="logo" className='landing-header__logo' />
                        </Link>
                        <Box
                            className='landing-header__menu'
                            sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}
                        >
                            {Object.entries(navbarPages).map(([key, page]) => (
                                <Button
                                    className='landing-header__menu__item'
                                    component={RouterLink}
                                    to={page.linkTo}
                                    key={key}
                                    sx={{ my: 2, color: 'white', display: 'block' }}
                                >
                                    {page.name}
                                </Button>
                            ))}
                        </Box>
                        <Box
                            className='landing-header__action-buttons'
                            sx={{ display: { xs: 'none', md: 'flex' } }} >
                            {Object.entries(actionButtons).map(([key, button]) => (
                                <Button
                                    className={button.className}
                                    component={RouterLink}
                                    to={button.linkTo}
                                    key={key}
                                >
                                    {button.name}
                                </Button>
                            ))}
                        </Box>

                        {/*
                            Elements for extra small (xs) screenss and below:
                        */}
                        <Link
                            sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}
                            component={RouterLink}
                            to="/"
                        >
                            <img src={logotype} alt="logo" className='landing-header__logo--small' />
                        </Link>
                        <Box sx={{ mr: 1, display: { xs: 'flex', md: 'none' } }}>
                            <Button
                                className='landing-header__action-buttons__item--primary'
                                component={RouterLink}
                                to={actionButtons.signup.linkTo}
                                key={actionButtons.signup.key}
                                sx={{ color: 'white', display: { xs: 'none', sm: 'block' }, mr: 3, }}
                            >
                                Get Started
                            </Button>
                            <IconButton
                                color="inherit"
                                aria-label="open drawer"
                                edge="start"
                                onClick={handleDrawerToggle}
                            >
                                <MenuIcon />
                            </IconButton>
                        </Box>
                    </Toolbar>
                </Container>
            </AppBar>

            {/* Sidebar (Drawer) used for menu on small screens */}
            <Box component="nav">
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    anchor="right"
                    ModalProps={{
                        keepMounted: true, // Better open performance on mobile.
                    }}
                    sx={{
                        display: { xs: 'flex', md: 'none' },
                        '& .MuiDrawer-paper': {
                            boxSizing: 'border-box',
                            width: '370px',
                            // below means that until 600px, which is xs size, then fill drawer to 100% widths
                            ['@media (max-width:600px)']: {
                                width: '100%',
                            }
                        },
                    }}
                >
                    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'left' }}>
                        <Box sx={{ p: 2, my: 2, style: 'inline-block' }}>
                            <Link
                                component={RouterLink}
                                to="/"
                            >
                                <img src={logotype} alt="logo" className='sidebar__logo' />
                            </Link>
                            <IconButton
                                sx={{ float: 'right' }}
                                onClick={handleDrawerToggle}>
                                <CloseRoundedIcon />
                            </IconButton>
                        </Box>
                        <List className='sidebar__menu__item'>
                            {Object.entries(navbarPages).map(([key, page]) => (
                                <ListItem key={key} disablePadding >
                                    <ListItemButton
                                        key={key}
                                        sx={{ textAlign: 'left' }}
                                        component={RouterLink}
                                        to={page.linkTo}
                                    >
                                        <ListItemText
                                            key={key}
                                            disableTypography={true}
                                            className='sidebar__menu__item'
                                            primary={page.name}
                                        />
                                    </ListItemButton>
                                </ListItem>
                            ))}
                        </List>
                        <Box
                            sx={{ p: 1, textAlign: 'center' }}
                        >
                            {Object.entries(actionButtons).slice(0).reverse().map(([key, button]) => (
                                <Button
                                    component={RouterLink}
                                    to={button.linkTo}
                                    key={key}
                                    sx={{ display: 'block', my: 1.5 }}
                                    className={`${button.className} ${button.className2}`}
                                >
                                    {button.name}
                                </Button>
                            ))}
                        </Box>
                    </Box>
                </Drawer>
            </Box>
        </>
    );
}

export default LandingNavbar