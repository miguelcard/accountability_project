import React from 'react'
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import AdbIcon from '@mui/icons-material/Adb';
import Link from '@mui/material/Link';
import { Link as RouterLink } from 'react-router-dom'
import logotype from '../../assets/statics/images/Headers/avidhabits.png';
import underConstruction from '../../assets/statics/images/Temp/under-construction.png';
import {connect, useDispatch} from 'react-redux';
import { logoutAction } from '../../redux/loginDucks'
import { useHistory } from "react-router-dom";

const pages = ['Dashboard', 'My Scoreboards', 'Groups'];
const settings = ['Profile', 'Account', 'Dashboard', 'Logout'];
const TOTAL_LOGOUT_SUCCESS = 'TOTAL_LOGOUT_SUCCESS'

const TempProfile = ({ user, userUpdate, logoutAction, fetching }) => {

      const history = useHistory();
      const dispatch = useDispatch();
    const [anchorElNav, setAnchorElNav] = React.useState(null);
    const [anchorElUser, setAnchorElUser] = React.useState(null);


    const logout = async () => {
        logoutAction(user.authentication.token);
        dispatch({
          type: TOTAL_LOGOUT_SUCCESS,
        });
        localStorage.clear();
        history.push("/login");
      };


    const handleOpenNavMenu = (event) => {
        setAnchorElNav(event.currentTarget);
    };
    const handleOpenUserMenu = (event) => {
        setAnchorElUser(event.currentTarget);
    };

    const handleCloseNavMenu = () => {
        setAnchorElNav(null);
    };

    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    return (
        <>
            <AppBar position="static"
                className='landing-header'
            // sx={{ background: '#655dff'}}
            >
                <Container maxWidth="xl">
                    <Toolbar disableGutters>
                        <Link
                            sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' }, mr: 1 }}
                            component={RouterLink}
                            to="/"
                        >
                            <img src={logotype} alt="logo" className='landing-header__logo' />
                        </Link>


                        <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
                            <IconButton
                                size="large"
                                aria-label="account of current user"
                                aria-controls="menu-appbar"
                                aria-haspopup="true"
                                onClick={handleOpenNavMenu}
                                color="inherit"
                            >
                                <MenuIcon />
                            </IconButton>
                            <Menu
                                id="menu-appbar"
                                anchorEl={anchorElNav}
                                anchorOrigin={{
                                    vertical: 'bottom',
                                    horizontal: 'left',
                                }}
                                keepMounted
                                transformOrigin={{
                                    vertical: 'top',
                                    horizontal: 'left',
                                }}
                                open={Boolean(anchorElNav)}
                                onClose={handleCloseNavMenu}
                                sx={{
                                    display: { xs: 'block', md: 'none' },
                                }}
                            >
                                {pages.map((page) => (
                                    <MenuItem key={page} onClick={handleCloseNavMenu}>
                                        <Typography textAlign="center">{page}</Typography>
                                    </MenuItem>
                                ))}
                            </Menu>
                        </Box>
                        {/* <AdbIcon sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }} />
                        <Typography
                            variant="h5"
                            noWrap
                            component="a"
                            href=""
                            sx={{
                                mr: 2,
                                display: { xs: 'flex', md: 'none' },
                                flexGrow: 1,
                                fontFamily: 'monospace',
                                fontWeight: 700,
                                letterSpacing: '.3rem',
                                color: 'inherit',
                                textDecoration: 'none',
                            }}
                        >
                            LOGO
                        </Typography> */}
                        <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
                            {pages.map((page) => (
                                <Button
                                    key={page}
                                    onClick={handleCloseNavMenu}
                                    sx={{ my: 2, color: 'white', display: 'block' }}
                                >
                                    {page}
                                </Button>
                            ))}
                        </Box>

                        <Box sx={{ flexGrow: 0 }}>
                            <Tooltip title="Open settings">
                                <IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
                                    <Avatar alt="Memy Sharp" src="/static/images/avatar/2.jpg" />
                                </IconButton>
                            </Tooltip>
                            <Menu
                                sx={{ mt: '45px' }}
                                id="menu-appbar"
                                anchorEl={anchorElUser}
                                anchorOrigin={{
                                    vertical: 'top',
                                    horizontal: 'right',
                                }}
                                keepMounted
                                transformOrigin={{
                                    vertical: 'top',
                                    horizontal: 'right',
                                }}
                                open={Boolean(anchorElUser)}
                                onClose={handleCloseUserMenu}
                            >
                                {settings.map((setting) => (
                                    <MenuItem key={setting} onClick={logout}>
                                        <Typography textAlign="center">{setting}</Typography>
                                    </MenuItem>
                                ))}
                            </Menu>
                        </Box>
                    </Toolbar>
                </Container>
            </AppBar>
            <h1 style={{
                fontSize: '1.7rem',
                fontWeight: 'normal',
                textAlign: 'center',
                color: '#777',
                letterSpacing: '0.1rem',
                fontFamily: 'Circular Std, sans-serif',
                margin: '2rem 0',
                borderRadius: '1rem',
                padding: '1rem 2rem',
                display: 'inline-block'
            }}>
                Under Construction...
            </h1>
            <br />
            <img src={underConstruction} alt="under-construction" style={{ width: '500px', display: 'block', margin: '0 auto' }} />
        </>
    );
}

const mapStateToProps = (state) => {
    return {
      user: state.dataLogin.list,
      userUpdate: state.dataLogin.updatedList,
      fetching: state.dataLogin.fetching,
      languageList: state.dataLogin.languageList
    }
  }
  
  export default connect(mapStateToProps, { logoutAction })(TempProfile);