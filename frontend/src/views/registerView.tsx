import React from 'react';
import '../assets/styles/components/Register/registerViewStyle.css';
import Container from '@mui/material/Container';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import InputLabel from '@mui/material/InputLabel';
import { RegisterNavbar } from '../components/Headers/RegisterNavbar';

const RegisterView: React.FC = () => {
    return (
        <>
            <RegisterNavbar
                actionMessage={'Already have an account?'}
                buttonLinkTo={'/login'}
                buttonKey={'login'}
                buttonText={'Login'}
            />
            <Container component="main" maxWidth="xs">
                {/* CssBaseline porvides better css defaults from here*/}
                <CssBaseline />
                <Box
                    sx={{
                        marginTop: 8,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                    }}
                >
                    <Typography component="h1" variant="h5" className='register__action-text'
                        sx={{ pb: 3 }}
                    >
                        Let's get you started!
                    </Typography>
                    <Box
                        component="form"
                        // onSubmit={handleSubmit} 
                        sx={{ mt: 1 }}>
                        <InputLabel htmlFor="name" sx={{ fontWeight: 'bold' }}>
                            Name
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            type="text"
                            required
                            fullWidth
                            id="name"
                            name="name"
                            placeholder="Jack Sparrow"
                            autoComplete="name"
                            autoFocus
                        />
                        <InputLabel htmlFor="email" sx={{ fontWeight: 'bold' }}>
                            Email
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            type="email"
                            required
                            fullWidth
                            id="email"
                            name="email"
                            placeholder="sparrow@site.com"
                            autoComplete="email"
                        />
                        <InputLabel htmlFor="password" sx={{ fontWeight: 'bold' }}>
                            Choose Password
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            required
                            fullWidth
                            name="password"
                            placeholder="Minimum 8 characters"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            inputProps={{ minLength: 8 }}
                        />
                        <Button
                            className='register__form-button'
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3, mb: 3 }}
                        >
                            Continue
                        </Button>
                        {/* TODO: put terms and conditions and policy links */}
                        <Box
                            sx={{fontSize: '0.8em' }}
                        >
                            <p>Signing up for an account means you agree to our &nbsp;
                                <Link href="#" variant="body2">
                                    Privacy Policy
                                </Link>
                                &nbsp; and &nbsp;
                                <Link href="#" variant="body2">
                                    Terms of Service
                                </Link>
                                .
                            </p>
                        </Box>
                    </Box>
                </Box>
            </Container>
        </>
    )
}

export default RegisterView

// TODO / Future improvements:  (like with react-hook-form lib)
//  improve / beutify validation error messages instead of using the default html validators, see https://mui.com/material-ui/react-text-field/#validation
//  for password add checks while user is typing it, like dispaying message of what it is missing and bar of how strong it is