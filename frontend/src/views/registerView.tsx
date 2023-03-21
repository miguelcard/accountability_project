import React, { useEffect, useState } from 'react';
import '../assets/styles/components/Register/registerViewStyle.css';
import SignupFirstStepForm from '../components/Auth/Signup/Forms/SignupFirstStepForm';
import SignupSecondStepForm from '../components/Auth/Signup/Forms/SignupSecondStepForm';
import { FormValues, initialValues } from '../components/Auth/Signup/FormModel/formInitialValues';
import { useFormik } from 'formik';
import validationSchemas from '../components/Auth/Signup/FormModel/validationSchema';
import { useDispatch } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { sendDataRegisterAction } from '../redux/loginDucks';


const RegisterView: React.FC = () => {
    
    const dispatch = useDispatch();
    const history = useHistory();
    const [step, setStep] = useState<number>(1);
    const [formValues, setFormValues] = useState<FormValues>(initialValues);
    const [isLastStep, setIsLastStep] = useState<boolean>(false);

    const formik = useFormik({
        initialValues: initialValues,
        validationSchema: validationSchemas[step - 1],
        onSubmit: (values: FormValues, { setSubmitting }: any) => {
            handleFormsSubmit(values);
            setSubmitting(false);
        },
    });

    const handleFormsSubmit = (values: FormValues) => {
        switch (step) {
            case 1:
                setFormValues(values);
                setStep(2);
                break;
            case 2:
                setFormValues({ ...formValues, ...values }); // use state in react is Asynchronous! meaning that if you send the request right after you can send the old form values before the new ones are given! 
                setIsLastStep(true);
                break;
        }
    }

    // We use the useEffect hook before sending the request to ensure the latest formValues are sent
    useEffect(() => {

        async function registerUser() {
            if (isLastStep) {

                const formData = new FormData();
                formData.append('name', formValues.name);
                formData.append('email', formValues.email);
                formData.append('username', formValues.username);
                formData.append('password', formValues.password);
                // we send the same password twice because the backend expects 2 matching passwords and to keep the frontend form simple, we only ask for the password once
                formData.append('password2', formValues.password);

                const res: Response | any = await dispatch(sendDataRegisterAction(formData));

                if (res.status === 200) {
                    history.push('/profile');
                }
                // else handle possible errors?
            }
        }

        registerUser();

    }, [formValues, isLastStep]);

    return (
        <>
            {step === 1 && <SignupFirstStepForm formik={formik} />}
            {step === 2 && (
                <SignupSecondStepForm formik={formik} />
            )}
        </>
    );
}

export default RegisterView

// TODOS in prio order:
// NOTE: You could make a whole reusable component for both the login and the signup, which accept as input 1. the header, 2. the form to be sent,
// 3. a handle submit function (or something like that) to handle the login or signup logic, 4. the text below which has the terms and conditions
// for the signup and the forgot password? link for the login (like a MUI Box)