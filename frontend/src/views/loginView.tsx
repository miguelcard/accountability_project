import React, { useState } from 'react'
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
import { Link as RouterLink } from 'react-router-dom'
import { sendDataLoginAction } from '../redux/loginDucks';
import { useHistory } from 'react-router-dom';


const LoginView: React.FC = () => {

    const history = useHistory();
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    const handleSubmit = async (e : React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const bodyFormData: FormData = new FormData()
        bodyFormData.append('email', email)
        bodyFormData.append('password', password)
        const res : Response | any = await sendDataLoginAction(bodyFormData);

        if (res.status === 200) {
            history.push('/profile');
        }
        // else do I do something here?
    }

    // TODO when migrating to  Next Js .... put loading animation while the data is being sent / fetched / Loaded 

    return (
        <>
            <RegisterNavbar
                actionMessage={`Don't have an account?`}
                buttonLinkTo={'/register'}
                buttonKey={'signup'}
                buttonText={'Sign up'}
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
                        Welcome back!
                    </Typography>
                    <Box
                        component="form"
                        onSubmit={handleSubmit} 
                        sx={{ mt: 1 }}>
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
                            autoFocus
                            onChange={e => setEmail(e.target.value)}
                        />
                        <InputLabel htmlFor="password" sx={{ fontWeight: 'bold' }}>
                            Password
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            required
                            fullWidth
                            name="password"
                            type="password"
                            id="password"
                            autoComplete="current-password"
                            placeholder="••••••••"
                            onChange={e => setPassword(e.target.value)}
                        />
                        <Button
                            className='register__form-button'
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ my: 3}}
                        >
                            Log In
                        </Button>
                        <Box
                            sx={{ fontSize: '0.8em' , textAlign: 'center'}}
                        >
                            <Link href="#" variant="body2">
                                Forgot Password?
                            </Link>
                        </Box>
                    </Box>
                </Box>
            </Container>
        </>
    )
}

export default LoginView

// Make a reusable component for all the duplicated code from here and registeView