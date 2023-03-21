import React, { useState } from 'react';
import '../../../../assets/styles/components/Register/registerViewStyle.css'
import Container from '@mui/material/Container';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Link from '@mui/material/Link';
import InputLabel from '@mui/material/InputLabel';
import { RegisterNavbar } from '../../../Headers/RegisterNavbar';
import { FormikProps } from 'formik';
import { FormValues } from '../FormModel/formInitialValues';
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';

interface Props {
    formik: FormikProps<FormValues>;
}

const SignupFirstStepForm: React.FC<Props> = ({ formik }) => {

    const [showPassword, setShowPassword] = useState<boolean>(false);

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
                        onSubmit={formik.handleSubmit}
                        sx={{ mt: 1 }}
                    >
                        <InputLabel htmlFor="name" sx={{ fontWeight: 'bold' }}>
                            Name
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            type="text"
                            fullWidth
                            id="name"
                            name="name"
                            placeholder="Jack Sparrow"
                            autoComplete="name"
                            value={formik.values.name}
                            onChange={formik.handleChange}
                            error={formik.touched.name && Boolean(formik.errors.name)}
                            helperText={formik.touched.name && formik.errors.name}
                            autoFocus
                        />
                        <InputLabel htmlFor="email" sx={{ fontWeight: 'bold' }}>
                            Email
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            // type="email"
                            fullWidth
                            id="email"
                            name="email"
                            placeholder="sparrow@site.com"
                            autoComplete="email"
                            value={formik.values.email}
                            onChange={formik.handleChange}
                            error={formik.touched.email && Boolean(formik.errors.email)}
                            helperText={formik.touched.email && formik.errors.email}
                        />
                        <InputLabel htmlFor="password" sx={{ fontWeight: 'bold' }}>
                            Choose Password
                        </InputLabel>
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            className='register__text-input'
                            fullWidth
                            name="password"
                            placeholder="Minimum 8 characters"
                            type={showPassword ? "text" : "password"}
                            id="password"
                            autoComplete="new-password"
                            value={formik.values.password}
                            onChange={formik.handleChange}
                            error={formik.touched.password && Boolean(formik.errors.password)}
                            helperText={formik.touched.password && formik.errors.password}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            aria-label="toggle password"
                                            edge="end"
                                            onClick={() => setShowPassword(!showPassword)}
                                        >
                                            {showPassword ? (
                                                <VisibilityOffIcon />
                                            ) : (
                                                <VisibilityIcon />
                                            )}
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }}
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
                            sx={{ fontSize: '0.8em', textAlign: 'center' }}
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

export default SignupFirstStepForm
