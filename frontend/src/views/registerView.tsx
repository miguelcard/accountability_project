import React, { useState } from 'react';
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
import { useHistory } from 'react-router-dom';
import { sendDataRegisterAction } from '../redux/loginDucks';

const RegisterView: React.FC = () => {

    const history = useHistory();
    const [userName, setName] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    const handleSubmit = async (e : React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        const bodyFormData = new FormData();
        bodyFormData.append('username', userName);
        bodyFormData.append('email', email);
        bodyFormData.append('password', password);
        // we send the same password twice because the backend expects 2 matching passwords and to keep the frontend form simple, we only ask for the password once
        bodyFormData.append('password2', password);

        const res: Response | any = await sendDataRegisterAction(bodyFormData)
        if (res.status === 200) {
            history.push('/profile')
        }
        // else needed?
    }

    // TODO when migrating to  Next Js .... put loading animation while the data is being sent / fetched / Loaded 

    return (
        <>
            <RegisterNavbar
                actionMessage={'Already have an account?'}
                buttonLinkTo={'/login'}
                buttonKey={'login'}
                buttonText={'Log In'}
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
                        onSubmit={handleSubmit} 
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
                            onChange={e => setName(e.target.value)}
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
                            onChange={e => setEmail(e.target.value)}
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
                            onChange={e => setPassword(e.target.value)}
                        />
                        <Button
                            className='register__form-button'
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ my: 3 }}
                        >
                            Continue
                        </Button>
                        {/* TODO: put terms and conditions and policy links */}
                        <Box
                            sx={{fontSize: '0.8em', textAlign: 'center' }}
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

// TODOS in prio order: 
// NOTE: You could make a whole reusable component for both the login and the signup, which accept as input 1. the header, 2. the form to be sent, 
// 3. a handle submit function (or something like that) to handle the login or signup logic, 4. the text below which has the terms and conditions 
// for the signup and the forgot password? link for the login (like a MUI Box)
// Other Future improvements:  (like with react-hook-form lib)
//  improve / beutify validation error messages instead of using the default html validators, see https://mui.com/material-ui/react-text-field/#validation
//  for password add checks while user is typing it, like dispaying message of what it is missing and bar of how strong it is