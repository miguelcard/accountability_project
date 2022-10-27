import React, { useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
    Collapse,
    Navbar,
    NavbarToggler,
    NavbarBrand,
    Nav,
    NavItem,
    NavLink
} from 'reactstrap';
import logotype from '../../assets/statics/images/Headers/avidhabits.png'
import '../../assets/styles/components/Header/headerStyle.css'

import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
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


const pages = ['Contact', 'About'];

const LandingHeader: React.FC = () => {

    const [anchorElNav, setAnchorElNav] = useState<null | HTMLElement>(null);

    const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorElNav(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        console.log('CloseNavMenu Triggered!');

        setAnchorElNav(null);
    };
    // I think above is not needed

    // for small screens:
    const [mobileOpen, setMobileOpen] = useState<boolean>(false);

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    // const handleDrawerClose = () => {
    //     setOpen(false);
    //   };

    return (
        <>
            <AppBar position="static">
                <Container maxWidth="xl">
                    <Toolbar disableGutters>
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
                            {/* put this style on css file! */}
                            <img src={logotype} alt="logo" style={{ width: "130px" }} />
                        </Link>
                        <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
                            {pages.map((page) => (
                                <Button
                                    // component={RouterLink}
                                    // to="/"
                                    key={page}
                                    onClick={handleCloseNavMenu}
                                    sx={{ my: 2, color: 'white', display: 'block' }}
                                >
                                    {page}
                                </Button>
                            ))}
                        </Box>
                        <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
                            <Button
                                component={RouterLink}
                                to="/login"
                                key="login"
                                sx={{ color: 'white', display: 'block' }}
                            >
                                Log in
                            </Button>
                            <Button
                                component={RouterLink}
                                to="/register"
                                key="signup"
                                sx={{ color: 'white', display: 'block' }}
                            >
                                Sign Up
                            </Button>
                        </Box>

                        {/*
                            Elements for extea small (xs) screenss and below:
                        */}
                        <Link
                            sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}
                            component={RouterLink}
                            to="/"
                        >
                            {/* put this style on css file! */}
                            <img src={logotype} alt="logo" style={{ width: "115px" }} />
                        </Link>

                        <Box sx={{ mr: 1, display: { xs: 'flex', md: 'none' } }}>
                            <Button
                                component={RouterLink}
                                to="/register"
                                key="signup"
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

            {/* Side Bar (Drawer) used for menu on small screens */}
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
                        display: { xs: 'block', md: 'none' },
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
                                {/* put this style on css file! */}
                                <img src={logotype} alt="logo" style={{ width: "120px", filter: "invert(100%)" }} />
                            </Link>
                            <IconButton
                                sx={{ float: 'right' }}
                                onClick={handleDrawerToggle}>
                                <CloseRoundedIcon />
                            </IconButton>
                        </Box>
                        <List>
                            {pages.map((item) => (
                                <ListItem key={item} disablePadding>
                                    <ListItemButton sx={{ textAlign: 'left' }}>
                                        <ListItemText primary={item} />
                                    </ListItemButton>
                                </ListItem>
                            ))}
                        </List>
                        <Box sx={{ p: 1 , textAlign: 'center'}}>
                            <Button
                                component={RouterLink}
                                to="/register"
                                key="signup"
                                sx={{ display: 'block' }}
                                variant="contained"
                            >
                                Sign Up
                            </Button>
                            <Button
                                component={RouterLink}
                                to="/login"
                                key="login"
                                sx={{ display: 'block' }}
                                variant="outlined"
                            >
                                Log in
                            </Button>
                        </Box>
                    </Box>
                </Drawer>
            </Box>
        </>
    );


    // const [isOpen, setIsOpen] = useState(false);
    // const toggleOpen = () => setIsOpen(!isOpen);

    // return (
    //     <>
    //         <Navbar  light expand="lg" className="nav-content">
    //             {
    //                 isOpen?
    //                     <NavbarBrand href="/" className="nav-logotype"><img src={logotype} alt="logo"/></NavbarBrand>
    //                 :
    //                 <div></div>
    //             }
    //             <NavbarToggler onClick={toggleOpen} />
    //             <Collapse isOpen={isOpen} navbar className="total-nav">
    //                     <Nav className="nav-items" navbar>
    //                         {/* <NavItem className="row-1">
    //                             <NavLink href="#" id="item">About</NavLink>
    //                         </NavItem> */}
    //                     </Nav>
    //                     {
    //                         !isOpen?
    //                             <>
    //                                 <div className="logo-nav-item">
    //                                     <Link to="/">
    //                                         <img src={logotype} alt="logo"/>
    //                                     </Link>
    //                                 </div>
    //                                 <div className="nav-left-items">
    //                                     <Link to="/login" id="login">Sign-In</Link>
    //                                 </div>
    //                             </>
    //                         :
    //                         <>
    //                             <div className="nav-left-items">
    //                                 <Link to="/login" id="login">Sign-In</Link>
    //                             </div>
    //                         </>
    //                     }
    //             </Collapse>
    //         </Navbar>
    //     </>
    // );
}

export default LandingHeader
