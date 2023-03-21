import React from 'react'
import Typography from '@mui/material/Typography';
import { RegisterNavbar } from '../../../Headers/RegisterNavbar';
import { FormValues } from '../FormModel/formInitialValues';
import { Box, Button, Container, CssBaseline, TextField } from '@mui/material';
import { FormikProps } from 'formik';

interface Props {
    formik: FormikProps<FormValues>;
}

const SignupSecondStepForm: React.FC<Props> = ({ formik }) => {

    return (
        <>
            <RegisterNavbar />
            <Container component="main" maxWidth="sm">
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
                        Choose your username
                    </Typography>
                    <Typography component="h6" variant="h6" className='register__action-text--secondary'
                        sx={{ pb: 4 }}
                    >
                        Your username is how other community members will see you
                    </Typography>
                    <Box
                        component="form"
                        onSubmit={formik.handleSubmit}
                        sx={{ mt: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
                        style={{ width: 270 }}
                    >
                        <TextField
                            sx={{ mb: 2, mt: 0.5 }}
                            style={{ width: 270 }}
                            className='register__text-input'
                            type="text"
                            id="username"
                            name="username"
                            placeholder="username"
                            autoComplete='null'
                            spellCheck='false'
                            value={formik.values.username}
                            onChange={formik.handleChange}
                            error={formik.touched.username && Boolean(formik.errors.username)}
                            helperText={formik.touched.username && formik.errors.username}
                        />
                        <Button
                            className='register__form-button'
                            type='submit'
                            fullWidth
                            variant='contained'
                            sx={{ mt: 4 }}
                        >
                            Continue
                        </Button>
                    </Box>
                </Box>
            </Container>
        </>
    );
}

export default SignupSecondStepForm;